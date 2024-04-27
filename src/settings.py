from pathlib import Path

# The folder for the file outputs
OUTPUT_FODER = Path.cwd() / '../output/'

# Extracted text filename
OUTPUT_FILENAME = OUTPUT_FODER / 'text_extractions.txt'
OUTPUT_FILENAME.parent.mkdir(exist_ok=True, parents=True)
