import cv2
import numpy as np


class ImagePreprocessor:
    @staticmethod
    def preprocess_image_for_ocr(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        return equalized

    @staticmethod
    def dilate_mask(mask):
        kernel = np.ones((5, 5), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)
        return dilated_mask
