import tkinter as tk
import tkinter.filedialog as filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider

def load_file() -> None:
    filepath = filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")])
    if filepath:
        with open(filepath, "r") as file:
            plot_data([
                float(num.replace(",", ".")) 
                for line in file.readlines() if line.strip() 
                for num in line.split("\t")
            ])

def plot_data(data: list[float]) -> None:
    fig.clear()
    fig.add_axes((0.1, 0.1, 0.8, 0.8))
    fig.axes[0].set_xlim(0, 10)
    fig.axes[0].plot(data)
    canvas.draw()

def slider_on_change_handler(val: float) -> None:
    fig.axes[0].set_xlim(val, val + 10)
    canvas.draw()

root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")

frm = tk.Frame(master=root)
frm.grid()

load_button = tk.Button(master=frm, text="Выбрать файл", command=load_file)
load_button.grid(column=0, row=0)

fig = plt.figure(figsize=(640 / 100, 480 / 100))
fig.add_axes((0.1, 0.1, 0.8, 0.8))
fig.axes[0].set_xlim(0, 10)
canvas = FigureCanvasTkAgg(master=frm, figure=fig)
canvas.get_tk_widget().grid(column=0, row=1)

slider_fig = plt.figure(figsize=(640 / 100, 48 / 100))
slider_fig.add_axes((0.1, 0, 0.8, 1))
slider = Slider(slider_fig.axes[0], "", 0, 130000, valinit=0)
slider.on_changed(slider_on_change_handler)
slider_canvas = FigureCanvasTkAgg(master=frm, figure=slider_fig)
slider_canvas.get_tk_widget().grid(column=0, row=2)

root.mainloop()
