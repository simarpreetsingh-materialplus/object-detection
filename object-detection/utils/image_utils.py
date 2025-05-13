# utils/image_utils.py:
import cv2
import base64
import numpy as np

def convert_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')
