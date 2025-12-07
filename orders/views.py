from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import json
from datetime import datetime
from decimal import Decimal
from .models import Order, Payment, OrderStatusHistory, DeliveryConfirmation, Notification
from shop.models import SellerReview
from .notifications import send_notification_email, send_seller_review_notification_email, send_delivery_confirmation_email
from .mpesa import MpesaClient


def initiate_mpesa_payment(request, order_code):
    """
    Initiate M-PESA STK Push payment for order
    """
    order = get_object_or_404(Order, order_code=order_code)
    payment = order.payment
    
    # Auto-initiate STK push on GET request
    if request.method == 'GET':
        phone_number = order.customer_phone
        
        # Initialize M-PESA client
        mpesa = MpesaClient()
        
        # Initiate STK push
        result = mpesa.initiate_stk_push(
            phone_number=phone_number,
            amount=payment.deposit_amount if payment else order.total_amount,
            order_code=order_code
        )
        
        if result.get('success'):
            # Save the checkout request ID for later verification
            if payment:
                payment.checkout_request_id = result.get('checkout_request_id')
                payment.save()
            
            messages.success(
                request,
                f"M-PESA prompt sent to {phone_number}. Please enter your PIN to complete payment."
            )
        else:
            messages.error(
                request,
                f"M-PESA Error: {result.get('error', 'Unknown error')}"
            )
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', order.customer_phone)
        
        # Initialize M-PESA client
        mpesa = MpesaClient()
        
        # Initiate STK push
        result = mpesa.initiate_stk_push(
            phone_number=phone_number,
            amount=payment.deposit_amount if payment else order.total_amount,
            order_code=order_code
        )
        
        if result.get('success'):
            # Save the checkout request ID for later verification
            if payment:
                payment.checkout_request_id = result.get('checkout_request_id')
                payment.save()
            
            messages.success(
                request,
                f"M-PESA prompt sent to {phone_number}. Please enter your PIN to complete payment."
            )
            return redirect('orders:order_status', order_code=order_code)
        else:
            messages.error(
                request,
                f"M-PESA Error: {result.get('error', 'Unknown error')}"
            )
            return redirect('orders:order_status', order_code=order_code)
    
    context = {
        'order': order,
        'payment': payment,
        'deposit_amount': payment.deposit_amount if payment else order.total_amount,
        'phone_number': order.customer_phone,
    }
    
    return render(request, 'orders/mpesa_payment.html', context)


@csrf_exempt
def mpesa_payment_callback(request):
    """
    Handle M-PESA payment callback/webhook
    Receives payment confirmation from M-PESA Daraja API
    """
    if request.method == 'POST':
        try:
            # Parse JSON from request body
            data = json.loads(request.body)
            print(f"M-PESA Callback Received: {json.dumps(data, indent=2)}")
            
            # Extract M-PESA callback response
            # The structure is: {"Body": {"stkCallback": {...}}}
            callback_body = data.get('Body', {})
            stk_callback = callback_body.get('stkCallback', {})
            
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            merchant_request_id = stk_callback.get('MerchantRequestID')
            
            # Try to get CallbackMetadata for additional info
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])
            
            # Extract transaction details from metadata
            mpesa_receipt = None
            transaction_date = None
            phone_number = None
            
            for item in items:
                name = item.get('Name')
                value = item.get('Value')
                
                if name == 'MpesaReceiptNumber':
                    mpesa_receipt = value
                elif name == 'TransactionDate':
                    transaction_date = value
                elif name == 'PhoneNumber':
                    phone_number = value
            
            print(f"Payment Status: Code={result_code}, Description={result_desc}")
            print(f"CheckoutRequestID: {checkout_request_id}")
            
            # Find payment by checkout_request_id
            try:
                payment = Payment.objects.get(checkout_request_id=checkout_request_id)
                order = payment.order
                
                if result_code == 0 or str(result_code) == '0':
                    # Payment successful (ResultCode 0 = success)
                    payment.deposit_paid = True
                    payment.status = 'completed'
                    payment.deposit_transaction_id = mpesa_receipt
                    payment.save()
                    
                    order.status = 'payment_confirmed'
                    order.save()
                    
                    # Create status history
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='payment_confirmed',
                        note=f'Payment confirmed via M-PESA. Receipt: {mpesa_receipt}'
                    )
                    
                    # Create notification for customer
                    Notification.objects.create(
                        user=order.customer if order.customer else None,
                        email=order.customer_email if not order.customer else None,
                        order=order,
                        type='payment_received',
                        message=f'Payment confirmed! Receipt: {mpesa_receipt}'
                    )
                    
                    print(f"✓ Payment confirmed for order {order.order_code}")
                else:
                    # Payment failed or was cancelled
                    payment.status = 'failed'
                    payment.save()
                    
                    # Create status history
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='payment_failed',
                        note=f'Payment failed: {result_desc}'
                    )
                    
                    print(f"✗ Payment failed for order {order.order_code}: {result_desc}")
                    
            except Payment.DoesNotExist:
                print(f"Warning: Payment not found for CheckoutRequestID {checkout_request_id}")
                # Still return success to acknowledge receipt
                pass
                
            # Always return success to M-PESA (to acknowledge receipt)
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
            
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error in callback: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error processing M-PESA callback: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)


def check_payment_status_api(request, order_code):
    """
    API endpoint to check M-PESA payment status
    Used for polling instead of relying on callbacks
    """
    if request.method == 'GET':
        try:
            order = get_object_or_404(Order, order_code=order_code)
            payment = order.payment
            
            if not payment:
                return JsonResponse({
                    'success': False,
                    'payment_status': 'no_payment',
                    'message': 'No payment record found for this order'
                })
            
            # If payment is already confirmed, return success
            if payment.status == 'completed' or payment.deposit_paid:
                return JsonResponse({
                    'success': True,
                    'payment_status': 'completed',
                    'message': 'Payment confirmed',
                    'order_status': order.status
                })
            
            # If payment is pending, check status with M-PESA
            if payment.checkout_request_id:
                mpesa = MpesaClient()
                result = mpesa.check_transaction_status(payment.checkout_request_id)
                
                if result.get('success'):
                    # Parse the response
                    response_data = result.get('response', {})
                    result_code = response_data.get('ResultCode')
                    
                    # ResultCode 0 = success, 1 = failed
                    if result_code == 0 or str(result_code) == '0':
                        # Payment successful
                        payment.deposit_paid = True
                        payment.status = 'completed'
                        payment.save()
                        
                        order.status = 'payment_confirmed'
                        order.save()
                        
                        OrderStatusHistory.objects.create(
                            order=order,
                            status='payment_confirmed',
                            note='Payment confirmed via M-PESA polling check'
                        )
                        
                        return JsonResponse({
                            'success': True,
                            'payment_status': 'completed',
                            'message': 'Payment confirmed',
                            'order_status': order.status
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'payment_status': 'pending',
                            'message': 'Payment is still pending',
                            'order_status': order.status
                        })
                else:
                    # API call failed, return pending status
                    return JsonResponse({
                        'success': False,
                        'payment_status': 'pending',
                        'message': 'Unable to verify payment status. Please try again.',
                        'order_status': order.status
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'payment_status': 'pending',
                    'message': 'Payment not yet initiated',
                    'order_status': order.status
                })
                
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'payment_status': 'error',
                'message': 'Order not found'
            }, status=404)
        except Exception as e:
            print(f"Error checking payment status: {str(e)}")
            return JsonResponse({
                'success': False,
                'payment_status': 'error',
                'message': f'Error checking payment status: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def order_confirmation(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    context = {
        'order': order,
    }
    return render(request, 'orders/order_confirmation.html', context)


def track_order(request):
    if request.method == 'POST':
        order_code = request.POST.get('order_code', '').strip().upper()
        if order_code:
            try:
                order = Order.objects.get(order_code=order_code)
                return redirect('orders:order_status', order_code=order.order_code)
            except Order.DoesNotExist:
                messages.error(request, 'Order not found. Please check your order code.')
    
    return render(request, 'orders/track_order.html')


def order_status(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    status_history = order.status_history.all()
    
    # Check if user is the seller of this order
    is_seller = False
    if request.user.is_authenticated:
        # Check if any of the order's products belong to this seller
        seller_products = order.items.filter(product__seller=request.user).exists()
        is_seller = seller_products
    
    if request.method == 'POST' and is_seller:
        new_status = request.POST.get('new_status', '').strip()
        note = request.POST.get('note', '').strip()
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Create status history record
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                note=note
            )
            
            messages.success(request, f'Order status updated to {order.get_status_display()}')
            return redirect('orders:order_status', order_code=order.order_code)
    
    context = {
        'order': order,
        'status_history': status_history,
        'is_seller': is_seller,
        'can_update': is_seller,
    }
    return render(request, 'orders/order_status.html', context)


@login_required
def confirm_delivery(request, order_code):
    """Customer confirms delivery of order"""
    order = get_object_or_404(Order, order_code=order_code)
    
    # Check if user is the customer who placed the order
    # Support both customer FK and customer_email matching
    is_customer = (order.customer == request.user) or (order.customer_email == request.user.email)
    
    if not is_customer:
        messages.error(request, 'You are not authorized to confirm this delivery.')
        return redirect('accounts:customer_dashboard')
    
    # Check if order is in delivered status
    if order.status != 'delivered':
        messages.error(request, 'This order has not been marked as delivered yet.')
        return redirect('orders:order_status', order_code=order_code)
    
    if request.method == 'POST':
        # Get or create delivery confirmation
        delivery_conf, created = DeliveryConfirmation.objects.get_or_create(order=order)
        
        confirmation_note = request.POST.get('confirmation_note', '').strip()
        
        delivery_conf.customer_confirmed = True
        delivery_conf.confirmed_at = timezone.now()
        delivery_conf.confirmation_note = confirmation_note
        delivery_conf.save()
        
        # Create notification for seller
        notification = Notification.objects.create(
            user=order.items.first().product.seller,
            notification_type='delivery_pending',
            title=f'Delivery Confirmed - {order.order_code}',
            message=f'Customer has confirmed delivery of order {order.order_code}',
            order=order
        )
        
        # Send email to seller
        send_delivery_confirmation_email(
            order.items.first().product.seller,
            order,
            request.user
        )
        
        messages.success(request, 'Delivery confirmed! You can now leave a review.')
        return redirect('orders:leave_review', order_code=order_code)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/confirm_delivery.html', context)


@login_required
def leave_review(request, order_code):
    """Customer leaves a review for the seller"""
    order = get_object_or_404(Order, order_code=order_code)
    
    # Check if user is the customer
    # Support both customer FK and customer_email matching
    is_customer = (order.customer == request.user) or (order.customer_email == request.user.email)
    
    if not is_customer:
        messages.error(request, 'You are not authorized to review this order.')
        return redirect('accounts:customer_dashboard')
    
    # Check if delivery is confirmed
    if not hasattr(order, 'delivery_confirmation') or not order.delivery_confirmation.customer_confirmed:
        messages.error(request, 'You must confirm delivery before leaving a review.')
        return redirect('orders:confirm_delivery', order_code=order_code)
    
    # Get the seller (from first product)
    seller = order.items.first().product.seller
    
    # Check if review already exists
    existing_review = SellerReview.objects.filter(order=order, customer=request.user).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        if existing_review:
            # Update existing review
            existing_review.rating = int(rating)
            existing_review.title = title
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, 'Review updated successfully!')
        else:
            # Create new review
            review = SellerReview.objects.create(
                seller=seller,
                customer=request.user,
                order=order,
                rating=int(rating),
                title=title,
                comment=comment,
                is_verified_purchase=True
            )
            messages.success(request, 'Thank you for your review!')
            
            # Create notification for seller
            notification = Notification.objects.create(
                user=seller,
                notification_type='review_request',
                title=f'New Review from {request.user.first_name}',
                message=f'You received a {rating}-star review for order {order.order_code}',
                order=order
            )
            
            # Send email to seller about review
            send_seller_review_notification_email(seller, review)
        
        return redirect('accounts:customer_dashboard')
    
    rating_choices = [
        (5, 'Excellent'),
        (4, 'Very Good'),
        (3, 'Good'),
        (2, 'Fair'),
        (1, 'Poor'),
    ]
    
    context = {
        'order': order,
        'seller': seller,
        'existing_review': existing_review,
        'rating_choices': rating_choices,
    }
    return render(request, 'orders/leave_review.html', context)
