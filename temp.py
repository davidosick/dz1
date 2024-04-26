import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider

def load_file():
    global numbers
    filepath = filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")])
    if filepath:
        with open(filepath, "r") as file:
            text = file.read()

        lines = text.split('\n')

        numbers = []

        for line in lines:
            if not line.strip():
                continue
            numbers.extend([float(num.replace(',', '.')) for num in line.split('\t')])

        plot_data(numbers)

def plot_data(data):
    plt.clf()
    plt.plot(data)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    canvas.draw()

def update(val):
    ax.set_xlim(slider.val, slider.val + 10)  # Обновляем диапазон значений по оси x
    canvas.draw_idle()

root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")

load_button = tk.Button(root, text="Выбрать файл", command=load_file)
load_button.pack()

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

slider_ax = plt.axes([0.1, 0.02, 0.8, 0.03])  # Создаем место для ползунка
slider = Slider(slider_ax, 'X', 0, 130000, valinit=0)  # Создаем ползунок
slider.on_changed(update)  

tk.mainloop()
