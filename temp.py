import tkinter as tk
from tkinter import ttk 
from tkinter import Event, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.widgets import Slider

global voltage_numbers, ampere_numbers
global voltage_numbers_time, ampere_numbers_time

def timeformat(full_seconds: float) -> str:
    full_minutes = int(full_seconds // 60)
    full_hours   = int(full_minutes // 60)
    
    seconds = full_seconds % 60
    minutes = full_minutes % 60
    return f"{full_hours:02}:{minutes:02}:{seconds:.2f}"

def parse_file_lines(lines: list[str]) -> list[list[float]]:
    return [[float(num.replace(',', '.'))
             for num in line.split('\t')] 
             for i, line in enumerate(lines) if i % 2 == 0]

def load_file_voltage() -> None:
    global voltage_numbers, voltage_numbers_time
    if data := load_file():
        voltage_numbers = parse_file_lines(data)
        voltage_numbers_time = timeformat(len(data) / 10)
        plot_data(voltage_numbers)
        label.configure(text=str(voltage_numbers_time))
        combobox.current(0)

def load_file_ampere() -> None:
    global ampere_numbers, ampere_numbers_time
    if data := load_file():
        ampere_numbers = parse_file_lines(data)
        ampere_numbers_time = timeformat(len(data) / 10)
        plot_data(ampere_numbers)
        label.configure(text=str(ampere_numbers_time))
        combobox.current(1)

def load_file() -> list[str] | None:
    filepath = filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")])
    if filepath:
        with open(filepath, "r") as file:
            text = file.read()

        return text.strip().split('\n')

def plot_data(data: list[list[float]]) -> None:
    plt.clf()
    plt.plot(data)
    ax.grid(True)
    plt.xlabel("X")
    plt.ylabel("Y")
    canvas.draw()

def select_graph(event):
    global voltage_numbers, ampere_numbers
    global voltage_numbers_time, ampere_numbers_time
    match combobox.current():
        case 0 if voltage_numbers:
            plot_data(voltage_numbers)
            label.configure(text=f"{label_text} {voltage_numbers_time}")
        case 1 if ampere_numbers:
            plot_data(ampere_numbers)
            label.configure(text=f"{label_text} {ampere_numbers_time}")

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
plt.xlabel("X")
plt.ylabel("Y")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

label_text = "Время: "
label = ttk.Label(root, text=f"{label_text}")
label.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE)

'''slider_ax = plt.axes((0.1, 0.02, 0.8, 0.03))  
slider = Slider(slider_ax, "X", 0, 130000, valinit=0)  
slider.on_changed(slider_on_change_handler)'''

root.mainloop()
