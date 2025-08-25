import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import unicodedata

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def normalizar_texto(texto):
    """
    Normaliza o texto, removendo acentos e caracteres especiais.
    Exemplo: "matrícula" -> "matricula", "número" -> "numero".
    """
    texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto_normalizado.lower()

def processar_pdf(pdf_path, output_pdf, palavras_atencao, palavras_chave, palavra_especifica=None, cor_especifica=(1, 1, 0)):
    cep = []
    endereco = []
    logradouro = []
    doc = fitz.open(pdf_path)
    palavras_encontrada = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Converter página para imagem (alta resolução)
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes()))

        # Extrair dados do OCR
        dados = pytesseract.image_to_data(img, lang='eng', output_type=pytesseract.Output.DICT)

        # Normalizar palavras-chave e palavra específica
        palavras_chave_normalizadas = [normalizar_texto(p) for p in palavras_chave]
        palavras_atencao_normalizadas = [normalizar_texto(p) for p in palavras_atencao]

        if palavra_especifica:
            palavra_especifica_normalizada = [normalizar_texto(p) for p in palavra_especifica]
        else:
            palavra_especifica_normalizada = None

        # Loop com tratamento de palavras hifenizadas
        i = 0
        while i < len(dados['text']):
            texto_atual = dados['text'][i].strip()
            texto_normalizado = normalizar_texto(texto_atual)

            # Verifica se termina com hífen e junta com a próxima palavra
            if texto_atual.endswith('-') and i + 1 < len(dados['text']):
                proxima_palavra = dados['text'][i + 1].strip()
                texto_completo = normalizar_texto(texto_atual[:-1] + proxima_palavra)
                i += 1  # Avança um extra
            else:
                texto_completo = texto_normalizado

            # Coleta coordenadas
            x, y, w, h = dados['left'][i], dados['top'][i], dados['width'][i], dados['height'][i]
            
            # Pula se as coordenadas são inválidas
            if w <= 0 or h <= 0 or x < 0 or y < 0:
                i += 1
                continue
            
            fator_x = page.rect.width / pix.width
            fator_y = page.rect.height / pix.height

            retangulo = fitz.Rect(
                x * fator_x,
                y * fator_y,
                (x + w) * fator_x,
                (y + h) * fator_y
            )
            
            # Valida se o retângulo é válido
            if retangulo.is_empty or retangulo.is_infinite:
                i += 1
                continue

            # Palavra específica (ex: verde)
            if palavra_especifica_normalizada and any(p in texto_completo for p in palavra_especifica_normalizada):
                try:
                    highlight = page.add_highlight_annot(retangulo)
                    highlight.set_colors(stroke=cor_especifica)
                    highlight.update()
                except ValueError as e:
                    print(f"Erro ao destacar palavra específica: {e}")

            # Palavra-chave ou de atenção
            for palavra, palavra_normalizada in zip(palavras_chave, palavras_chave_normalizadas):
                if palavra_normalizada in texto_completo:
                    if palavra_normalizada in palavras_atencao_normalizadas:
                        cor = (1, 0, 0)  # Vermelho
                        palavras_encontrada.append(palavra)
                    else:
                        cor = (1, 1, 0)  # Amarelo

                    try:
                        highlight = page.add_highlight_annot(retangulo)
                        highlight.set_colors(stroke=cor)
                        highlight.update()
                    except ValueError as e:
                        print(f"Erro ao destacar palavra-chave '{palavra}': {e}")

            i += 1

    doc.save(output_pdf)
    return set(palavras_encontrada)

# def extrair_numero_proximo(dados, indice):
#     """
#     Procura padrões numéricos ou endereços nas proximidades do texto detectado.

#     :param dados: Dados do OCR retornados pelo Tesseract.
#     :param indice: Índice da palavra detectada.
#     :return: Número ou texto encontrado, ou None.
#     """
#     padrao_com_pontos = r":\s*(\S.*)"  # Captura valores após " : "
#     padrao_numerico = r"\b\d[\d\-/]+\d\b"  # Captura padrões numéricos como "8888-888"
#     padrao_cep = r"\b\d{5}-?\d{3}\b"  # Agora captura CEP no formato "12345-678" ou "12345678"

#     palavras_chave = [
#         'logradouro', 'número', 'bairro', 'cidade', 'estado', 'cep',
#         'log.', 'n.', 'cep.', 'endereço', 'end.', 'end', 'imóvel', 'imovel'
#     ]

#     palavras_chave_formatadas = [
#         'endereço:', 'end.', 'imóvel:', 'imovel:', 'cep:'
#     ]

#     # Obtém a palavra atual
#     palavra_atual = dados['text'][indice].strip().lower()
#     print(f"Verificando palavra: {palavra_atual}")  # Debug

#     # Se a palavra está na lista de interesse
#     if palavra_atual in palavras_chave or any(palavra_atual.startswith(chave) for chave in palavras_chave_formatadas):
        
#         # Verifica na mesma linha
#         texto_atual = dados['text'][indice].lower()
#         match = re.search(padrao_com_pontos, texto_atual)
#         if match:
#             return match.group(1)

#         # Tenta verificar até 3 linhas abaixo
#         for i in range(1, 4):
#             novo_indice = indice + i
#             if 0 <= novo_indice < len(dados['text']):
#                 texto_proximo = dados['text'][novo_indice].strip()
                
#                 # Ignorar linhas vazias
#                 if not texto_proximo:
#                     continue

#                 # Verifica se há ":" e captura o texto depois
#                 match = re.search(padrao_com_pontos, texto_proximo)
#                 if match:
#                     return match.group(1)

#                 # Se for um logradouro, captura qualquer texto que pareça um endereço
#                 if palavra_atual in ["logradouro", "endereço", "imóvel"] and len(texto_proximo) > 3:
#                     return texto_proximo

#                 # Se for um CEP, procura pelo formato correto
#                 if "cep" in palavra_atual:
#                     match = re.search(padrao_cep, texto_proximo)
#                     if match:
#                         return match.group(0)

#                 # Se for um número válido, retorna ele
#                 match = re.search(padrao_numerico, texto_proximo)
#                 if match:
#                     return match.group(0)
                

#     print("Nenhum dado encontrado")  # Debug
#     return None


if __name__ == '__main__':
    processar_pdf()