import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")])
    if filepath:
        df = pd.read_csv(filepath)
        plot_data(df)

def plot_data(data):
    plt.clf()
    for column in data.columns:
        plt.plot(data[column], label=column)
    plt.xlabel('Х')
    plt.ylabel('У')
    plt.legend()
    canvas.draw()

root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")

load_button = tk.Button(root, text="Выбрать файл", command=load_file)
load_button.pack()

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

tk.mainloop()
