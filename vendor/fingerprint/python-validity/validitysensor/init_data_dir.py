import os

PYTHON_VALIDITY_DATA_DIR = '/var/lib/python-validity/'

def init_data_dir():
    os.makedirs(PYTHON_VALIDITY_DATA_DIR, mode=0o700, exist_ok=True)

