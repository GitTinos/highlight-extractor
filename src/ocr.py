import cv2
import numpy as np
import pytesseract

from image_processor import ImagePreprocessor


class OCRProcessor:
    def find_yellow_highlights_and_extract_text(self, image):
        open_cv_image = np.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([20, 80, 80])
        upper_yellow = np.array([50, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        dilated_mask = ImagePreprocessor.dilate_mask(mask)

        masked_image = cv2.bitwise_and(open_cv_image, open_cv_image, mask=dilated_mask)
        preprocessed_image = ImagePreprocessor.preprocess_image_for_ocr(masked_image)

        custom_config = r"--oem 3 --psm 11 -l ita"
        text = pytesseract.image_to_string(preprocessed_image, config=custom_config)

        return text.strip()
