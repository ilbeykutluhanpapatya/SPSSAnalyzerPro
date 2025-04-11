
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from semopy import Model, semplot

class StructuralEquationModeler:
    def __init__(self, df=None, model_desc=None):
        if df is None or df.empty:
            raise ValueError("Veri çerçevesi (df) boş veya tanımsız. Lütfen önce veri yükleyin.")
        self.df = df
        self.model_desc = model_desc or self.auto_generate_model(df)

    def auto_generate_model(self, df):
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 4:
            return """ # Örnek model
            latent1 =~ {0} + {1}
            latent2 =~ {2} + {3}
            outcome ~ latent1 + latent2
            """.format(*numeric_cols[:4])
        else:
            block1 = " + ".join(numeric_cols[:3])
            block2 = " + ".join(numeric_cols[3:6])
            return f"""
            latent1 =~ {block1}
            latent2 =~ {block2}
            outcome ~ latent1 + latent2
            """

    def set_model_description(self, custom_model):
        self.model_desc = custom_model

    def fit_model(self):
        try:
            model = Model(self.model_desc)
            model.fit(self.df)
            self.result = model.inspect()
            print(self.result)
            return self.result
        except Exception as e:
            print("Model kurulurken hata oluştu:", e)
            return None

    def plot_model(self, filename="sem_model.png"):
        try:
            model = Model(self.model_desc)
            model.fit(self.df)
            semplot(model, filename.replace(".png", ""), plot_mean=False, show=False)
            print(f"Grafik kaydedildi: {filename}")
        except Exception as e:
            print("Grafik çiziminde hata:", e)
