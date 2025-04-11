import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from sem_model import StructuralEquationModeler

class SEMGuiWindow:
    def __init__(self, df):
        self.df = df
        self.top = tk.Toplevel()
        self.top.title("Yapısal Eşitlik Modeli Görselleştirme")
        self.top.geometry("800x600")

        self.draw_ui()

    def draw_ui(self):
        # Modeli çiz ve PNG oluştur
        try:
            sem = StructuralEquationModeler(self.df)
            sem.plot_model("sem_model.png")
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            self.top.destroy()
            return

        # Görüntüyü yükle ve göster
        try:
            img = Image.open("sem_model.png")
            img = img.resize((750, 500), Image.Resampling.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(img)

            self.label = tk.Label(self.top, image=self.tk_img)
            self.label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Resim Yükleme Hatası", str(e))

        # Kaydet butonu
        tk.Button(self.top, text="📥 PNG Olarak Kaydet", command=self.save_image).pack(pady=10)

    def save_image(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if file_path:
                img = Image.open("sem_model.png")
                img.save(file_path)
                messagebox.showinfo("Başarılı", "Görsel kaydedildi!")
        except Exception as e:
            messagebox.showerror("Kaydetme Hatası", str(e))
