import tkinter as tk
from tkinter import ttk, messagebox
from scipy import stats

class NonParametricTests:
    def __init__(self, notebook, df):
        if df is None:
            messagebox.showwarning("Uyarı", "Veri yüklenmeden nonparametrik testler oluşturulamaz.")
            return
        self.df = df
        self.tab_nonparametric = ttk.Frame(notebook)
        notebook.add(self.tab_nonparametric, text='📉 Nonparametrik Testler')
        self.create_nonparametric_tab()

    def create_combobox(self, parent, label):
        tk.Label(parent, text=label).pack(anchor='w', padx=5)
        combo = ttk.Combobox(parent, values=list(self.df.columns))
        combo.pack(anchor='w', padx=5)
        return combo

    def create_nonparametric_tab(self):
        tests = [
            ("Mann-Whitney U Testi", stats.mannwhitneyu),
            ("Wilcoxon Testi", stats.wilcoxon),
            ("Kruskal-Wallis Testi", stats.kruskal),
            ("Friedman Testi", stats.friedmanchisquare)
        ]

        for test_name, test_func in tests:
            frame = ttk.LabelFrame(self.tab_nonparametric, text=test_name)
            frame.pack(fill="x", padx=10, pady=5)

            combo1 = self.create_combobox(frame, f"{test_name} için Değişken 1:")
            combo2 = self.create_combobox(frame, f"{test_name} için Değişken 2:")

            def run_test(c1=combo1, c2=combo2, f=test_func, n=test_name):
                try:
                    data1 = self.df[c1.get()].dropna()
                    data2 = self.df[c2.get()].dropna()
                    result = f(data1, data2)
                    messagebox.showinfo(n, f"{n} sonucu:\nStatistic={result.statistic:.4f}, p-value={result.pvalue:.4f}")
                except Exception as e:
                    messagebox.showerror("Hata", f"Test başarısız oldu: {e}")

            tk.Button(frame, text="Testi Uygula", command=run_test).pack(anchor='e', padx=5, pady=5)