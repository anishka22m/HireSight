import os
from pdfminer.high_level import extract_text
import pytesseract
from PIL import Image

# Set this if needed (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# FOLDERS
INPUT_FOLDER = "datasets\\resumes_new"
OUTPUT_FOLDER = "datasets\\convertedresumes"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -------------------------
# EXTRACTION FUNCTIONS
# -------------------------

def extract_pdf(path):
    try:
        return extract_text(path)
    except:
        return ""

def extract_image(path):
    try:
        img = Image.open(path)
        return pytesseract.image_to_string(img)
    except:
        return ""

# -------------------------
# MAIN CONVERSION
# -------------------------

def convert_all():
    total = 0
    skipped = 0

    for file in os.listdir(INPUT_FOLDER):
        input_path = os.path.join(INPUT_FOLDER, file)

        print(f"Processing: {file}")

        text = ""

        if file.endswith(".pdf"):
            text = extract_pdf(input_path)

        elif file.endswith((".png", ".jpg", ".jpeg", ".webp")):
            text = extract_image(input_path)

        else:
            print("Unsupported format, skipping")
            skipped += 1
            continue

        if not text or len(text) < 50:
            print("Low content, skipped")
            skipped += 1
            continue

        # Save as .txt
        output_file = os.path.splitext(file)[0] + ".txt"
        output_path = os.path.join(OUTPUT_FOLDER, output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        total += 1

    print("\n=== CONVERSION SUMMARY ===")
    print(f"Converted: {total}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    convert_all()