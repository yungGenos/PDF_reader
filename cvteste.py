import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import unicodedata

# Configurações do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def normalizar_texto(texto):
    """
    Normaliza o texto, removendo acentos e caracteres especiais.
    Exemplo: "matrícula" -> "matricula", "número" -> "numero".
    """
    texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto_normalizado.lower()

def processar_pdf(pdf_path, output_pdf, palavras_chave, palavra_especifica=None, cor_especifica=(1, 1, 0)):
    """
    Processa o PDF, procurando por palavras-chave e destacando-as com cores personalizadas.
    
    :param pdf_path: Caminho do PDF de entrada.
    :param output_pdf: Caminho do PDF de saída com destaques.
    :param palavras_chave: Lista de palavras a serem procuradas.
    :param palavra_especifica: Palavra específica para destacar com uma cor personalizada (opcional).
    :param cor_especifica: Cor para destacar a palavra específica (tupla RGB) (opcional, padrão é verde).
    """
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 1. Converter página para imagem (alta resolução)
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes()))
        
        # 2. Extrair dados do OCR
        dados = pytesseract.image_to_data(img, lang='por', output_type=pytesseract.Output.DICT)
        
        # 3. Normalizar palavras-chave e palavra específica
        palavras_chave_normalizadas = [normalizar_texto(palavra) for palavra in palavras_chave]
        if palavra_especifica:
            palavra_especifica_normalizada = [normalizar_texto(palavra_especifica_unica) for palavra_especifica_unica in palavra_especifica]
        else:
            palavra_especifica_normalizada = None
        
        # 4. Procurar por palavras-chave e palavra específica
        for i in range(len(dados['text'])):
            texto = dados['text'][i].strip()
            texto_normalizado = normalizar_texto(texto)
            
            # Verifica a palavra específica
            if palavra_especifica_normalizada and any(palavra in texto_normalizado for palavra in palavra_especifica_normalizada):
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
                
                # 7. Adicionar destaque com a cor específica
                highlight = page.add_highlight_annot(retangulo)
                highlight.set_colors(stroke=cor_especifica)  # Define a cor do destaque
                highlight.update()
                
                print(f"Página {page_num+1}: Palavra específica '{palavra_especifica}' encontrada.")
            
            # Verifica as palavras-chave
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
                    
                    # 7. Adicionar destaque padrão (cor vermelha)
                    highlight = page.add_highlight_annot(retangulo)
                    highlight.set_colors(stroke=(1, 1, 0))  # Vermelho como cor padrão
                    highlight.update()
                    
                    # 8. Extrair número (se existir)
                    # numero = extrair_numero_proximo(dados, i)
                    # if numero:
                    #     print(f"Página {page_num+1}: Palavra '{palavra}' encontrada com número - {numero}")
                    # else:
                    #     print(f"Página {page_num+1}: Palavra '{palavra}' encontrada.")
                    
    # Salvar PDF modificado
    doc.save(output_pdf)
    print(f"PDF destacado salvo como: {output_pdf}")

# def extrair_numero_proximo(dados, indice):
#     """
#     Procura padrões numéricos nas proximidades do texto detectado.
    
#     :param dados: Dados do OCR retornados pelo Tesseract.
#     :param indice: Índice da palavra detectada.
#     :return: Número encontrado ou None.
#     """
#     padrao = r"\b\d[\d\.\/-]+\d\b"
    
#     # Verifica linha atual
#     texto = dados['text'][indice]
#     if re.search(padrao, texto):
#         return re.findall(padrao, texto)[0]
    
#     # Verifica linhas adjacentes
#     for offset in [-1, 1]:
#         novo_indice = indice + offset
#         if 0 <= novo_indice < len(dados['text']):
#             texto = dados['text'][novo_indice]
#             if re.search(padrao, texto):
#                 return re.findall(padrao, texto)[0]
#     return None