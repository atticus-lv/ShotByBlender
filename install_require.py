import sys
import subprocess


def ensure_require():
    try:
        import PIL
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow==9.5.0'])
