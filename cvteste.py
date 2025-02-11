import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import unicodedata
from time import sleep

# Configurações do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def normalizar_texto(texto):
    """
    Normaliza o texto, removendo acentos e caracteres especiais.
    Exemplo: "matrícula" -> "matricula", "número" -> "numero".
    """
    texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto_normalizado.lower()

def processar_pdf(pdf_path, output_pdf, palavras_chave):
    """
    Processa o PDF, procurando por palavras-chave e destacando-as.
    
    :param pdf_path: Caminho do PDF de entrada.
    :param output_pdf: Caminho do PDF de saída com destaques.
    :param palavras_chave: Lista de palavras a serem procuradas.
    """
    doc = fitz.open(pdf_path)
    print('Um total de ', len(doc), ' páginas')
    sleep(1.5)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 1. Converter página para imagem (alta resolução)
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes()))
        
        # 2. Extrair dados do OCR
        dados = pytesseract.image_to_data(img, lang='por', output_type=pytesseract.Output.DICT)
        
        # 3. Normalizar palavras-chave
        palavras_chave_normalizadas = [normalizar_texto(palavra) for palavra in palavras_chave]
        
        # 4. Procurar por palavras-chave
        for i in range(len(dados['text'])):
            texto = dados['text'][i].strip()
            texto_normalizado = normalizar_texto(texto)
            
            for palavra, palavra_normalizada in zip(palavras_chave, palavras_chave_normalizadas):
                if palavra_normalizada in texto_normalizado:
                    # 5. Obter coordenadas do texto
                    x, y, w, h = dados['left'][i], dados['top'][i], dados['width'][i], dados['height'][i]
                    
                    # 6. Converter coordenadas para o sistema do PDF
                    fator_x = page.rect.width / pix.width
                    fator_y = page.rect.height / pix.height
                    
                    retangulo = fitz.Rect(
                        x * fator_x,
                        y * fator_y,
                        (x + w) * fator_x,
                        (y + h) * fator_y
                    )
                    
                    # 7. Adicionar destaque
                    page.add_highlight_annot(retangulo)
                    
                    # 8. Extrair número (se existir)
                    numero = extrair_numero_proximo(dados, i)
                    if numero:
                        print(f"Página {page_num+1}: Palavra '{palavra}' encontrada com número - {numero}")
                    else:
                        print(f"Página {page_num+1}: Palavra '{palavra}' encontrada.")
                    
    # Salvar PDF modificado
    doc.save(output_pdf)
    print(f"PDF destacado salvo como: {output_pdf}")

def extrair_numero_proximo(dados, indice):
    """
    Procura padrões numéricos nas proximidades do texto detectado.
    
    :param dados: Dados do OCR retornados pelo Tesseract.
    :param indice: Índice da palavra detectada.
    :return: Número encontrado ou None.
    """
    padrao = r"\b\d[\d\.\/-]+\d\b"
    
    # Verifica linha atual
    texto = dados['text'][indice]
    if re.search(padrao, texto):
        return re.findall(padrao, texto)[0]
    
    # Verifica linhas adjacentes
    for offset in [-1, 1]:
        novo_indice = indice + offset
        if 0 <= novo_indice < len(dados['text']):
            texto = dados['text'][novo_indice]
            if re.search(padrao, texto):
                return re.findall(padrao, texto)[0]
    return None

# Lista de palavras-chave para procurar
palavras_chave = [
    "matricula", "número", "rua", "lote", "quadra",
    "cidade", "estado", "área", "privativa", "comum", "total", 
    "vaga", "garagem", "condomínio", "iptu", "imovel","tombado",
    "avenida", "av.", "rua", "r.", "estrada", "est.", "rodovia", "rod.",
    "terreno", "lote", "quadra", "q.", "bloco", "apartamento", "apto", "apt.",
    "cnm", "CNM", "galpão", "galpao", "sala", "loja", "casa", "edifício", "edificio",
    "misto", "comercial", "residencial", "industrial", "rural", "urbano", "área", "terreno",
    "predio", "prédio","sala", "loja", "galpão", "galpao", "construida", "construída", "construcao",
]

# Uso
if __name__ == "__main__":
    pdfs = ['teste_luan.pdf']
    for i, pdf in enumerate(pdfs):
        processar_pdf(pdf, f"documento_destacado{i+ 1}.pdf", palavras_chave)