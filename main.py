import fitz  # PyMuPDF
import pytesseract
import io
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

# Função para extrair imagens de um PDF
def extract_images_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)

    return images

# Função para extrair texto de uma imagem usando Tesseract
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image, lang='por')  # 'por' para português
    return text

# Caminho para o PDF
pdf_path = "Matricula_2025020716192045351820862 (1).pdf"

# Extrair imagens do PDF
images = extract_images_from_pdf(pdf_path)

# Extrair texto de cada imagem
for i, image in enumerate(images):
    print(f"Texto da imagem {i+1}:")
    text = extract_text_from_image(image)
    print(text)
    print("-" * 40)