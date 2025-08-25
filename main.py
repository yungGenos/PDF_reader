import fitz  # PyMuPDF
import pytesseract
import io
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_images_from_pdf(pdf_path):
    """
    Extrai as imagens de cada página do PDF.
    Retorna uma lista de tuplas: (número_da_página, imagem)
    """
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
            images.append((page_num, image))
    return images

def extract_text_from_image(image):
    """
    Extrai o texto de uma imagem usando o Tesseract com linguagem em português.
    """
    text = pytesseract.image_to_string(image, lang='por')
    return text

def extrair_numero_matricula(text):
    """
    Procura pela palavra "matricula" (ignorando caixa) no texto e retorna o número associado.
    A busca é feita na própria linha onde a palavra foi encontrada; se não houver número,
    tenta na linha imediatamente anterior e, em seguida, na próxima.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "matricula" in line.lower():
            # Tenta extrair um número na própria linha
            match = re.search(r'\d[\d\.\-\/]*', line)
            if match:
                return match.group(0)
           
            if i > 0:
                match = re.search(r'\d[\d\.\-\/]*', lines[i-1])
                if match:
                    return match.group(0)
           
            if i < len(lines)-1:
                match = re.search(r'\d[\d\.\-\/]*', lines[i+1])
                if match:
                    return match.group(0)
    return None


pdf_path = "Matricula_2025021010155139376025857.pdf"


images = extract_images_from_pdf(pdf_path)


for page_num, image in images:
    print(f"Processando a página {page_num+1}...")
    text = extract_text_from_image(image)
    numero = extrair_numero_matricula(text)
    if numero:
        print(f"Na página {page_num+1}, número da matrícula encontrado: {numero}")
    else:
        print(f"Na página {page_num+1}, a palavra 'matricula' ou seu número não foram encontrados.")
    print("-" * 40)
