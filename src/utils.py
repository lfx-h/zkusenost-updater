import math
import numpy as np
import os
import sys
import logging

def is_empty_or_nan(value):
    if value is None:
        return True
    if isinstance(value, str) and value == "":
        return True
    if isinstance(value, (float, int)) and (math.isnan(value) or value == 0):
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    return False

def setup_logger(filename="pipeline.log"):
    os.makedirs(os.path.dirname(f"logs/{filename}"), exist_ok=True)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.errors = 'replace'

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f"logs/{filename}", mode='a', delay=False, encoding='utf-8'),
            console_handler
        ]
    )