import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider

def load_file() -> None:
    filepath = filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")])
    if filepath:
        with open(filepath, "r") as file:
            text = file.read()

        data = text.strip().split('\n')

        plot_data([[float(num.replace(',', '.')) 
                    for num in line.split('\t')] 
                    for line in data])

def plot_data(data: list[float]) -> None:
    plt.clf()
    plt.plot(data)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    canvas.draw()

def slider_on_change_handler(val: float) -> None:
    ax.set_xlim(val, val + 10)  
    canvas.draw_idle()

root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")

load_button = tk.Button(root, text="Выбрать файл", command=load_file)
load_button.pack()

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

slider_ax = plt.axes((0.1, 0.02, 0.8, 0.03))  
slider = Slider(slider_ax, "X", 0, 130000, valinit=0)  
slider.on_changed(slider_on_change_handler)

root.mainloop()
