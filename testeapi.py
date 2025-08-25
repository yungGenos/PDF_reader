from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import requests
import unicodedata

app = Flask(__name__)

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def normalizar_texto(texto):
    texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto_normalizado.lower()

@app.route('/processar_pdf', methods=['POST'])
def processar_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido"}), 400

    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    palavras_chave = ['cep', 'logradouro', 'endereco']
    palavras_encontradas = {"cep": [], "logradouro": [], "endereco": []}
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes()))
        dados = pytesseract.image_to_data(img, lang='por', output_type=pytesseract.Output.DICT)

        for i in range(len(dados['text'])):
            texto = dados['text'][i].strip()
            texto_normalizado = normalizar_texto(texto)

            for palavra in palavras_chave:
                if palavra in texto_normalizado:
                    numero = extrair_numero_proximo(dados, i)
                    if numero:
                        palavras_encontradas[palavra].append(numero)

    return jsonify(palavras_encontradas)

def extrair_numero_proximo(dados, indice):
    padrao_cep = r"\b\d{5}-?\d{3}\b"
    texto_proximo = dados['text'][indice].strip()
    
    if re.search(padrao_cep, texto_proximo):
        return texto_proximo
    return None

if __name__ == '__main__':
    app.run(debug=True, port=5000)
