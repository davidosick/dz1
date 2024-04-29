import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk 
#from matplotlib.widgets import Slider

global voltage_numbers, ampere_numbers

def load_file_voltage() -> None:
    global voltage_numbers
    data = load_file()

    voltage_numbers = [[float(num.replace(',', '.')) 
                        for num in line.split('\t')] 
                        for line in data]

    plot_data(voltage_numbers)
    combobox.current(0)

def load_file_ampere() -> None:
    global ampere_numbers
    data = load_file()

    ampere_numbers = [[float(num.replace(',', '.')) 
                        for num in line.split('\t')] 
                        for line in data]

    plot_data(ampere_numbers)
    combobox.current(1)

def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")])
    if filepath:
        with open(filepath, "r") as file:
            text = file.read()

        data = text.strip().split('\n')
        return data

def plot_data(data: list[float]) -> None:
    plt.clf()
    plt.plot(data)
    plt.legend()
    canvas.draw()

def select_graph(event):
    global voltage_numbers, ampere_numbers
    selection = combobox.current() 
    if selection == 0:
        plot_data(voltage_numbers)
    elif selection == 1:
        plot_data(ampere_numbers)

'''def slider_on_change_handler(val: float) -> None:
    ax.set_xlim(val, val + 10)  
    canvas.draw_idle()'''

root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")


button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP)

load_button_voltage = tk.Button(button_frame, text="+ Данные напряжения (U)", command=load_file_voltage)
load_button_voltage.pack(side=tk.LEFT, padx=5)

load_button_voltage = tk.Button(button_frame, text="+ Данные силы тока (I)", command=load_file_ampere)
load_button_voltage.pack(side=tk.RIGHT, padx=5)

combobox = ttk.Combobox(root, values=["Напряжение (U)", "Сила тока (I)"], state="readonly")
combobox.current(0) 
combobox.pack()
combobox.bind("<<ComboboxSelected>>", select_graph)

fig, ax = plt.subplots()
ax.grid(True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
plt.xlabel("X")
plt.ylabel("Y")

'''slider_ax = plt.axes((0.1, 0.02, 0.8, 0.03))  
slider = Slider(slider_ax, "X", 0, 130000, valinit=0)  
slider.on_changed(slider_on_change_handler)'''

root.mainloop()
