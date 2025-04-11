import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pyreadstat
import seaborn as sns
import matplotlib.pyplot as plt
import self
from scipy import stats
from sklearn.linear_model import LinearRegression
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import os
from nonp import NonParametricTests
from sem_model import StructuralEquationModeler
from sem_gui import SEMGuiWindow





# Menü veya butonla açmak için:






class SPSSAnalyzerProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SPSS Analyzer Pro - illbeyyofficial powered by ikpakademi")
        self.root.geometry("1000x600")
        self.df = None

        self.setup_ui()

    def setup_ui(self):
        self.create_logo()
        self.create_menu()
        self.create_tabs()
        self.create_status_bar()

    def resize_image_with_aspect(self, image, max_width):
        w_percent = (max_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        return image.resize((max_width, h_size), Image.Resampling.LANCZOS)

    def create_logo(self):
        try:
            logo_path = os.path.join(os.getcwd(), "ikpakademi.png")
            image = Image.open(logo_path)
            image = self.resize_image_with_aspect(image, max_width=180)
            self.logo_img = ImageTk.PhotoImage(image)
            self.logo_label = tk.Label(self.root, image=self.logo_img, bg=self.root['bg'])
            self.logo_label.pack(pady=5)
        except Exception as e:
            print(f"Logo yüklenemedi: {e}")

    def create_menu(self):
        self.file_types = [("SPSS files", "*.sav"), ("Excel files", "*.xls *.xlsx")]
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Aç", command=self.load_data_file)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        self.root.config(menu=menubar)

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.tab_summary = ttk.Frame(self.notebook)
        self.tab_graph = ttk.Frame(self.notebook)
        self.tab_regression = ttk.Frame(self.notebook)
        self.tab_tests = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_summary, text='📊 Veri Özeti')
        self.notebook.add(self.tab_graph, text='📈 Görselleştirme')
        self.notebook.add(self.tab_regression, text='📐 Regresyon')
        self.notebook.add(self.tab_tests, text='⚖️ Testler')
        self.chi_button = tk.Button(self.tab_tests, text="Ki-Kare Testi", command=self.perform_chi_square)
        self.chi_button.pack(pady=10)
        # ✅ Yapısal Eşitlik Modeli Butonu
        tk.Button(self.root, text="Yapısal Eşitlik Modeli", command=lambda: StructuralEquationModeler(self.root, self.df)).pack(
            pady=5)


        self.text_summary = tk.Text(self.tab_summary)
        self.text_summary.pack(fill='both', expand=True)


        # Veri Özeti Sekmesinde Yapısal Eşitlik Modeli Butonu
        def open_sem():
            if self.df is not None:
                try:
                    sem = StructuralEquationModeler(self.df)
                    sem.plot_model()
                    messagebox.showinfo("Başarılı", "Model başarıyla çizildi (sem_model.png)")
                except Exception as e:
                    messagebox.showerror("Hata", str(e))
            else:
                messagebox.showwarning("Uyarı", "Lütfen önce bir veri dosyası yükleyin.")

        tk.Button(self.tab_summary, text="📐 Yapısal Eşitlik Modeli Oluştur", command=open_sem).pack(pady=10)

        self.graph_button = tk.Button(self.tab_graph, text="Korelasyon Matrisi", command=self.show_correlation)
        self.graph_button.pack(pady=10)

        self.reg_button = tk.Button(self.tab_regression, text="Lineer Regresyon", command=self.linear_regression)
        self.reg_button.pack(pady=10)

        self.test_button = tk.Button(self.tab_tests, text="T-Testi", command=self.perform_ttest)
        self.test_button.pack(pady=10)

        self.anova_button = tk.Button(self.tab_tests, text="ANOVA (tek yönlü)", command=self.perform_anova)
        self.anova_button.pack(pady=10)

        self.chi_button = tk.Button(self.tab_tests, text="Ki-Kare Testi", command=self.perform_chi_square)
        self.chi_button.pack(pady=10)

    def create_status_bar(self):
        self.status = tk.Label(self.root, text="Veri seti yüklenmedi", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data_file(self):
        self.nonparametric_tab = NonParametricTests(self.notebook, self.df)
        file_path = filedialog.askopenfilename(filetypes=self.file_types)
        if file_path:
            try:
                if file_path.endswith('.sav'):
                    self.df, _ = pyreadstat.read_sav(file_path)
                elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
                    self.df = pd.read_excel(file_path)
                if self.df is not None:
                        self.nonparametric_tab = NonParametricTests(self.notebook, self.df)

                else:
                    raise ValueError("Desteklenmeyen dosya formatı")

                self.text_summary.delete("1.0", tk.END)
                self.text_summary.insert(tk.END, self.df.describe(include='all').to_string())
                self.status.config(text=f"Yüklendi: {file_path}")
                self.create_advanced_tab()
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya yüklenemedi: {e}")

    def create_advanced_tab(self):
        try:
            self.notebook.forget(self.tab_advanced)
        except:
            pass
        self.tab_advanced = ttk.Frame(self.notebook)
        canvas = tk.Canvas(self.tab_advanced)
        scrollbar = ttk.Scrollbar(self.tab_advanced, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.scrollable_advanced_frame = scrollable_frame
        self.notebook.add(self.tab_advanced, text='🧪 İleri Analizler')

        def create_combobox(parent, label):
            tk.Label(parent, text=label).pack(anchor='w')
            combo = ttk.Combobox(parent, values=list(self.df.columns))
            combo.pack(anchor='w', padx=5, pady=2)
            return combo

        # Normal Dağılım Testi (Shapiro)
        frame1 = ttk.LabelFrame(self.scrollable_advanced_frame, text="Shapiro-Wilk Normal Dağılım Testi")
        frame1.pack(fill='x', padx=10, pady=5)
        tk.Label(frame1, text="Verinin normal dağılıma uygunluğunu test eder.\nÖrnek: Bir sınavın puanlarının normal dağılıp dağılmadığını test eder.").pack(anchor='w')
        combo_shapiro = create_combobox(frame1, "Değişken seç:")
        def run_shapiro():
            try:
                data = self.df[combo_shapiro.get()].dropna()
                stat, p = stats.shapiro(data)
                messagebox.showinfo("Shapiro-Wilk Sonucu", f"İstatistik: {stat:.4f}, p-değeri: {p:.4f}")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(frame1, text="Testi Uygula", command=run_shapiro).pack(anchor='e')

        # Spearman Korelasyonu
        frame2 = ttk.LabelFrame(self.scrollable_advanced_frame, text="Spearman Sıra Korelasyonu")
        frame2.pack(fill='x', padx=10, pady=5)
        tk.Label(frame2, text="Sıralı iki değişken arasındaki ilişkiyi test eder.\nÖrnek: Yaş ve memnuniyet düzeyi gibi sıralı veriler.").pack(anchor='w')
        combo_sp1 = create_combobox(frame2, "Değişken 1:")
        combo_sp2 = create_combobox(frame2, "Değişken 2:")
        def run_spearman():
            try:
                data1 = self.df[combo_sp1.get()].dropna()
                data2 = self.df[combo_sp2.get()].dropna()
                stat, p = stats.spearmanr(data1, data2)
                messagebox.showinfo("Spearman Korelasyonu", f"Rho: {stat:.4f}, p-değeri: {p:.4f}")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(frame2, text="Testi Uygula", command=run_spearman).pack(anchor='e')

        # Kendall's Tau
        frame3 = ttk.LabelFrame(self.scrollable_advanced_frame, text="Kendall's Tau Korelasyonu")
        frame3.pack(fill='x', padx=10, pady=5)
        tk.Label(frame3, text="Küçük örneklemler için sıralı veri korelasyonu.\nÖrnek: Küçük gruplarda başarı sıralaması ve sınav notu ilişkisi.").pack(anchor='w')
        combo_k1 = create_combobox(frame3, "Değişken 1:")
        combo_k2 = create_combobox(frame3, "Değişken 2:")
        def run_kendall():
            try:
                data1 = self.df[combo_k1.get()].dropna()
                data2 = self.df[combo_k2.get()].dropna()
                stat, p = stats.kendalltau(data1, data2)
                messagebox.showinfo("Kendall's Tau", f"Tau: {stat:.4f}, p-değeri: {p:.4f}")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(frame3, text="Testi Uygula", command=run_kendall).pack(anchor='e')

        # Güven Aralığı
        frame4 = ttk.LabelFrame(self.scrollable_advanced_frame, text="Ortalama için 95% Güven Aralığı")
        frame4.pack(fill='x', padx=10, pady=5)
        tk.Label(frame4, text="Veri grubunun ortalaması için güven aralığı hesaplar.\nÖrnek: Öğrencilerin sınav ortalaması ± hata payı.").pack(anchor='w')
        combo_ci = create_combobox(frame4, "Değişken seç:")
        def run_confidence_interval():
            try:
                data = self.df[combo_ci.get()].dropna()
                mean = data.mean()
                sem = stats.sem(data)
                ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=sem)
                messagebox.showinfo("Güven Aralığı", f"Ortalama: {mean:.2f}\n95% CI: ({ci[0]:.2f}, {ci[1]:.2f})")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(frame4, text="Hesapla", command=run_confidence_interval).pack(anchor='e')

        # Outlier Tespiti (Z-Score)
        frame5 = ttk.LabelFrame(self.scrollable_advanced_frame, text="Outlier (Aykırı Değer) Tespiti")
        frame5.pack(fill='x', padx=10, pady=5)
        tk.Label(frame5, text="Z-Score yöntemiyle uç değerleri belirler.\nÖrnek: Z > 3 olan öğrenciler aykırı olarak işaretlenir.").pack(anchor='w')


        combo_outlier = create_combobox(frame5, "Değişken seç:")
        def run_outlier():
            try:
                data = self.df[combo_outlier.get()].dropna()
                z_scores = stats.zscore(data)
                outliers = data[(abs(z_scores) > 3)]
                messagebox.showinfo("Outlier Sonuçları", f"Toplam aykırı değer: {len(outliers)} {outliers.to_string(index=False)}")

            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(frame5, text="Tespiti Yap", command=run_outlier).pack(anchor='e')

        # Boxplot & Histogram Görselleştirme
        frame6 = ttk.LabelFrame(self.scrollable_advanced_frame, text="Boxplot ve Histogram")
        frame6.pack(fill='x', padx=10, pady=5)
        tk.Label(frame6, text="Veri dağılımını görsel olarak analiz etmenizi sağlar.\nÖrnek: Notların dağılımı ve olası aykırı değerler.").pack(anchor='w')


        combo_plot = create_combobox(frame6, "Değişken seç:")
        def run_visuals():
            try:
                import matplotlib.pyplot as plt
                data = self.df[combo_plot.get()].dropna()
                fig, axs = plt.subplots(1, 2, figsize=(10, 4))
                axs[0].boxplot(data)
                axs[0].set_title("Boxplot")
                axs[1].hist(data, bins=10, color='skyblue', edgecolor='black')
                axs[1].set_title("Histogram")
                plt.suptitle(combo_plot.get())
                plt.tight_layout()
                plt.show()
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(frame6, text="Grafikleri Göster", command=run_visuals).pack(anchor='e')

        # PDF Raporlama
        frame7 = ttk.LabelFrame(self.scrollable_advanced_frame, text="Veri Özeti PDF Raporu")
        frame7.pack(fill='x', padx=10, pady=5)
        tk.Label(frame7, text="Veri setinin temel istatistiksel özetini PDF olarak dışa aktarır.\nÖrnek: Ortalama, medyan, std sapma gibi değerleri içerir.").pack(anchor='w')

        def export_pdf():
            try:
                filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
                if filename:
                    c = canvas.Canvas(filename)
                    text = self.df.describe().to_string()
                    lines = text.split("")
                    y = 800
                    for line in lines:
                        c.drawString(30, y, line)
                        y -= 15
                    c.save()
                    messagebox.showinfo("Başarılı", "PDF raporu oluşturuldu!")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(frame7, text="PDF Olarak Kaydet", command=export_pdf).pack(anchor='e')

    def show_correlation(self):
        if self.df is not None:
            fig = plt.Figure(figsize=(6, 5), dpi=100)
            ax = fig.add_subplot(111)
            sns.heatmap(self.df.corr(), annot=True, cmap='coolwarm', ax=ax)
            ax.set_title("Korelasyon Matrisi")
            self.plot_graph(fig)

    def plot_graph(self, fig):
        for widget in self.tab_graph.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(fig, master=self.tab_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)

    def linear_regression(self):
        if self.df is not None:
            numeric = self.df.select_dtypes(include=['float64', 'int64'])
            if numeric.shape[1] >= 2:
                X = numeric.iloc[:, [0]].dropna()
                y = numeric.iloc[:, 1].dropna()
                model = LinearRegression()
                model.fit(X, y)
                r2 = model.score(X, y)
                coef = model.coef_[0]
                intercept = model.intercept_
                messagebox.showinfo("Regresyon Sonuçları", f"R^2: {r2:.4f}\nKatsayı: {coef:.4f}\nSabit: {intercept:.4f}")

    def perform_ttest(self):
        if self.df is not None:
            numeric = self.df.select_dtypes(include=['float64', 'int64'])
            if numeric.shape[1] >= 2:
                t_stat, p_val = stats.ttest_ind(numeric.iloc[:, 0].dropna(), numeric.iloc[:, 1].dropna())
                messagebox.showinfo("T-Testi", f"t={t_stat:.4f}, p={p_val:.4f}")

    def perform_anova(self):
        if self.df is not None:
            numeric = self.df.select_dtypes(include=['float64', 'int64'])
            if numeric.shape[1] >= 3:
                group1 = numeric.iloc[:, 0].dropna()
                group2 = numeric.iloc[:, 1].dropna()
                group3 = numeric.iloc[:, 2].dropna()
                f_stat, p_val = stats.f_oneway(group1, group2, group3)
                messagebox.showinfo("ANOVA", f"F={f_stat:.4f}, p={p_val:.4f}")

    def perform_chi_square(self):
        if self.df is not None:
            categorical = self.df.select_dtypes(include=['object'])
            if categorical.shape[1] >= 2:
                table = pd.crosstab(categorical.iloc[:, 0], categorical.iloc[:, 1])
                chi2, p, dof, expected = stats.chi2_contingency(table)
                messagebox.showinfo("Ki-Kare Testi", f"Chi²={chi2:.4f}, p={p:.4f}, df={dof}")

        def create_nonparametric_tab(NonParatricTest):
            if self.df is None:
                return

            try:
                self.notebook.forget(self.tab_nonparametric)
            except:
                pass
            self.tab_nonparametric = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_nonparametric, text='📉 Nonparametrik Testler')

            tests = [
                ("Mann-Whitney U Testi", stats.mannwhitneyu),
                ("Wilcoxon Testi", stats.wilcoxon),
                ("Kruskal-Wallis Testi", stats.kruskal),
                ("Friedman Testi", stats.friedmanchisquare)
            ]

            for test_name, test_func in tests:
                frame = ttk.LabelFrame(self.tab_nonparametric, text=test_name)
                frame.pack(fill="x", padx=10, pady=5)

                tk.Label(frame, text=f"{test_name} için Değişken 1:").pack(anchor='w', padx=5)
                combo1 = ttk.Combobox(frame, values=list(self.df.columns))
                combo1.pack(anchor='w', padx=5)

                tk.Label(frame, text=f"{test_name} için Değişken 2:").pack(anchor='w', padx=5)
                combo2 = ttk.Combobox(frame, values=list(self.df.columns))
                combo2.pack(anchor='w', padx=5)

                def run_test(c1=combo1, c2=combo2, f=test_func, n=test_name):
                    try:
                        data1 = self.df[c1.get()].dropna()
                        data2 = self.df[c2.get()].dropna()
                        result = f(data1, data2)
                        messagebox.showinfo(n, f"{n} sonucu:\nStatistic={result.statistic:.4f}, p-value={result.pvalue:.4f}")
                    except Exception as e:
                        messagebox.showerror("Hata", f"Test başarısız oldu: {e}")

                tk.Button(frame, text="Testi Uygula", command=run_test).pack(anchor='e', padx=5, pady=5)
if __name__ == "__main__":
    root = tk.Tk()
    app = SPSSAnalyzerProApp(root)
    root.mainloop()


