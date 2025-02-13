import tkinter as tk
from tkinter import filedialog, ttk, colorchooser
from cvteste import processar_pdf

palavras_chave = [
    "matricula", "número", "rua", "lote", "quadra", "cidade", "estado", "área", "privativa", "comum", "total", 
    "vaga", "garagem", "condomínio", "iptu", "imovel", "tombado", "avenida", "av.", "rua", "r.", "estrada", "est.", 
    "rodovia", "rod.", "terreno", "lote", "quadra", "q.", "bloco", "apartamento", "apto", "apt.", "cnm", "CNM", 
    "galpão", "galpao", "sala", "loja", "casa", "edifício", "edificio", "misto", "comercial", "residencial", "industrial", 
    "rural", "urbano", "área", "terreno", "predio", "prédio", "sala", "loja", "galpão", "galpao", "construida", 
    "construída", "construcao", "APP", "app", "área",
    "APP", "app", "área", "fração", "ideal", "fração ideal", "fração de terreno", "fração de terreno ideal",
    "fração ", "fracao", "fracao ideal", "fracao de terreno", "fracao de terreno ideal", "fracao ideal",
]

class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reader")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")
        
        self.pdf_files = []
        self.palavra_especifica = ""
        self.cor_especifica = (1, 1, 1)  # Amarelo como cor padrão
        
        ttk.Label(root, text="Selecione os arquivos PDF:", font=("Arial", 12)).pack(pady=10)
        
        self.upload_button = ttk.Button(root, text="Selecionar PDFs", command=self.upload_files)
        self.upload_button.pack(pady=5)
        
        self.file_listbox = tk.Listbox(root, width=60, height=10, bg="white", fg="black")
        self.file_listbox.pack(pady=10)
        
        ttk.Label(root, text="Palavra Específica:", font=("Arial", 12)).pack(pady=5)
        self.palavra_entry = ttk.Entry(root, width=40)
        self.palavra_entry.pack(pady=5)
        
        ttk.Label(root, text="Cor para Destacar:", font=("Arial", 12)).pack(pady=5)
        self.cor_button = ttk.Button(root, text="Escolher Cor", command=self.escolher_cor)
        self.cor_button.pack(pady=5)
        
        self.process_button = ttk.Button(root, text="Processar PDFs", command=self.process_pdf)
        self.process_button.pack(pady=10)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(root, text="", font=("Arial", 10), foreground="green")
        self.status_label.pack(pady=5)

    def upload_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            self.pdf_files.extend(files)
            self.update_file_listbox()

    def update_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.pdf_files:
            self.file_listbox.insert(tk.END, file.split("/")[-1])

    def escolher_cor(self):
        cor = colorchooser.askcolor()[0]
        if cor:
            self.cor_especifica = (cor[0] / 255, cor[1] / 255, cor[2] / 255)  # Converte para valores entre 0 e 1

    def process_pdf(self):
        if not self.pdf_files:
            self.status_label.config(text="Nenhum arquivo selecionado!", foreground="red")
            return

        self.palavra_especifica = [palavra.strip() for palavra in self.palavra_entry.get().split(',')]

        self.progress["maximum"] = len(self.pdf_files)
        
        for i, pdf_file in enumerate(self.pdf_files):
            processar_pdf(pdf_file, f'pdf_destacado_{i + 1}.pdf', palavras_chave, self.palavra_especifica, self.cor_especifica)
            self.progress["value"] = i + 1
            self.status_label.config(text=f"Processado: {pdf_file.split('/')[-1]}")
            self.root.update_idletasks()
        
        self.status_label.config(text="Processamento concluído!", foreground="green")
        self.pdf_files.clear()
        self.update_file_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderApp(root)
    root.mainloop()