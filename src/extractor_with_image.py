from pdf2image import convert_from_path
import cv2
import numpy as np
import argparse
import pytesseract
import re

# Converte un file PDF in una serie di immagini, una per pagina.
# L'alto valore di dpi (punti per pollice) migliora la qualità dell'immagine per l'OCR.
def converti_pdf_in_immagini(pdf_path):
    return convert_from_path(pdf_path, dpi=300)

# Pre-elabora un'immagine per l'OCR convertendola in scala di grigi e applicando
# l'equalizzazione dell'istogramma per migliorare il contrasto del testo.
def pre_elabora_immagine_per_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    return equalized

# Dilata una maschera binaria per espandere le aree bianche e ridurre le aree nere.
# Utile per assicurarsi che l'evidenziazione copra completamente il testo.
def dilata_maschera(mask):
    kernel = np.ones((5,5),np.uint8)  
    dilated_mask = cv2.dilate(mask, kernel, iterations = 1)
    return dilated_mask

# Trova le aree evidenziate in giallo in un'immagine e tenta di estrarre il testo da esse.
# Utilizza la conversione in HSV per rilevare il giallo, dilata la maschera per coprire meglio il testo,
# e applica l'OCR al risultato.
def trova_evidenziazioni_gialle_e_estrai_testo(image):
    open_cv_image = np.array(image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([22, 93, 100])
    upper_yellow = np.array([45, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    dilated_mask = dilata_maschera(mask)
    
    masked_image = cv2.bitwise_and(open_cv_image, open_cv_image, mask=dilated_mask)
    preprocessed_image = pre_elabora_immagine_per_ocr(masked_image)
    
    custom_config = r'--oem 3 --psm 6 -l ita'
    text = pytesseract.image_to_string(preprocessed_image, config=custom_config)
    
    return text.strip()

# Rimuove multipli spazi bianchi e li sostituisce con un singolo spazio
def pulisci_testo(text):
    text = re.sub(r'\s+', ' ', text)
    return text

def main():
    parser = argparse.ArgumentParser(description="Estrai testo da aree evidenziate in giallo in un PDF.")
    parser.add_argument("pdf_path", help="Il percorso del file PDF da analizzare.")
    args = parser.parse_args()
    
    estrazioni = []
    immagini = converti_pdf_in_immagini(args.pdf_path)
    for num_pagina, immagine in enumerate(immagini):
        testo = trova_evidenziazioni_gialle_e_estrai_testo(immagine)
        testo_pulito = pulisci_testo(testo)
        if testo_pulito:
            estrazioni.append(f"Pagina {num_pagina + 1}: {testo_pulito}")
    
    with open('estrazioni_testo.txt', 'w') as file:
        for estrazione in estrazioni:
            file.write(f"- {estrazione}\n")

    print("Estrazioni completate e salvate in 'estrazioni_testo.txt'.")

if __name__ == "__main__":
    main()
