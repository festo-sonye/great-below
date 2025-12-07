import os
import subprocess
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crochet_shop.settings")
    subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:5000"])
