import re
from tqdm import tqdm


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text


def start_progress_bar(total):
    return tqdm(total=total, desc="Elaborazione", unit="pagina")
