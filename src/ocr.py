import cv2
import numpy as np
import pytesseract

from image_processor import ImagePreprocessor


class OCRProcessor:
    def find_yellow_highlights_and_extract_text(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([22, 93, 100])
        upper_yellow = np.array([45, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        dilated_mask = ImagePreprocessor.dilate_mask(mask)

        masked_image = cv2.bitwise_and(image, image, mask=dilated_mask)
        preprocessed_image = ImagePreprocessor.preprocess_image_for_ocr(masked_image)

        custom_config = r"--oem 3 --psm 6 -l ita"
        text = pytesseract.image_to_string(preprocessed_image, config=custom_config)

        return text.strip()
