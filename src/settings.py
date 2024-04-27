from pathlib import Path

# The folder for the file outputs
OUTPUT_FODER = Path.cwd() / '../output/'

# Extracted text filename
OUTPUT_FILENAME = OUTPUT_FODER / 'text_extractions.txt'
OUTPUT_FILENAME.parent.mkdir(exist_ok=True, parents=True)

# How many threads use for pdf2image processing?
PDF2IMAGE_THREADS_COUNT = 6
