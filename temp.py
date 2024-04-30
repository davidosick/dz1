import tkinter as tk
from tkinter import ttk, filedialog

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.widgets import Slider

'''class Graph:
    def __init__(self, data):
        self.data = data

    def plot(self):
        plt.clf()
        plt.plot(self.data)
        plt.legend()
        plt.legend()
        canvas.draw()'''

class ComboboxSelection:
    VOLTAGE = 0
    AMPERE = 1

global voltage_numbers, ampere_numbers

global experiment_time
experiment_time: float

global selected_items
selected_items: list[int] = []

def timeformat(full_seconds: float) -> str:
    full_minutes = int(full_seconds // 60)
    full_hours   = int(full_minutes // 60)

    seconds = full_seconds % 60
    minutes = full_minutes % 60
    return f"{full_hours:02}:{minutes:02}:{seconds:.2f}"

def load_file() -> list[str] | None:
    if filepath := filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")]):
        with open(filepath, "r") as file:
            return file.read().strip().split('\n')

def parse_file_lines(lines: list[str]) -> list[list[float]]:
    return [[float(num.replace(',', '.'))
             for num in line.split('\t')]
             for i, line in enumerate(lines) if i % 2 == 0]

def load_file_voltage() -> None:
    global voltage_numbers
    if data := load_file():
        voltage_numbers = parse_file_lines(data)

        #plot_data(voltage_numbers)
        combobox.current(ComboboxSelection.VOLTAGE)
        update_graph_list(voltage_numbers, 'U')

def load_file_ampere() -> None:
    global ampere_numbers
    if data := load_file():
        ampere_numbers = parse_file_lines(data)

        #plot_data(ampere_numbers)
        combobox.current(ComboboxSelection.AMPERE)
        update_graph_list(ampere_numbers, 'I')

def clear_select() -> None:
    global selected_items
    selected_items = []
    match combobox.current():
        case ComboboxSelection.VOLTAGE:
            update_graph_list(voltage_numbers, 'U')
        case ComboboxSelection.AMPERE:
            update_graph_list(ampere_numbers, 'I')

def update_graph_list(data: list[list[float]], letter = '?') -> None:
    global selected_items, experiment_time
    selected_items = []

    length = len(data)
    tree.delete(*tree.get_children())
    for i in range(length):
        tree.insert("", tk.END, text=f"График {letter}({i + 1})")

    experiment_time = length / 10
    time_label.configure(text=f"Время: {timeformat(experiment_time)}")

def plot_data(data: list[list[float]], label: str) -> list[Line2D]:
    plt.clf()
    line_objects = [plt.plot(dataset, label=label)[0] for dataset in data]
    ax.grid(True)
    plt.xlabel("Время, сек")
    plt.ylabel(label)
    plt.legend(fontsize="x-large")
    canvas.draw()
    return line_objects  

def select_graph(event) -> None:
    global voltage_numbers, ampere_numbers
    match combobox.current():
        case ComboboxSelection.VOLTAGE:
            update_graph_list(voltage_numbers, "U")
            plot_data(voltage_numbers, "U")
        case ComboboxSelection.AMPERE:
            update_graph_list(ampere_numbers, "I")
            plot_data(ampere_numbers, "U")

'''def slider_on_change(val: float) -> None:
    ax.set_xlim(val, val + 10)  
    canvas.draw_idle()'''

def tree_on_select(event) -> None:
    global selected_items
    for item in tree.selection():
        item_text = tree.item(item, "text")
        if (sel_now := tree.index(item)) not in selected_items:
            selected_items.append(sel_now)
            tree.item(item, text=f"+ {item_text}")
        else:
            selected_items.remove(sel_now)
            tree.item(item, text=item_text[2:], tags="")

    filtered_data = []
    label = ""
    match combobox.current():
        case ComboboxSelection.VOLTAGE:
            filtered_data = [voltage_numbers[index] for index in selected_items]
            label = "U"
        case ComboboxSelection.AMPERE:
            filtered_data = [ampere_numbers[index] for index in selected_items]
            label = "I"

    update_cells_colors(plot_data(filtered_data, label))
    
    #print(filtered_data)

def update_cells_colors(line_objects: list[Line2D]) -> None:
    global selected_items
    for index, (item, line_object) in enumerate(zip(selected_items, line_objects)):
        tree.tag_configure(f'mytag_{index}', 
                           background=str(line_object.get_color()), 
                           foreground='white')
        tree.item(tree.get_children()[item], tags=(f'mytag_{index}',))

root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")

button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP)

load_button_voltage = tk.Button(button_frame, text="+ Данные напряжения (U)", command=load_file_voltage)
load_button_voltage.pack(side=tk.LEFT, padx=5)

load_button_ampere = tk.Button(button_frame, text="+ Данные силы тока (I)", command=load_file_ampere)
load_button_ampere.pack(side=tk.RIGHT, padx=5)

clear_select_button = tk.Button(button_frame, text="Очистить выбор", command=clear_select)
clear_select_button.pack(side=tk.RIGHT, padx=10)

combobox = ttk.Combobox(root, values=["Напряжение (U)", "Сила тока (I)"], state="readonly")
combobox.current(ComboboxSelection.VOLTAGE) 
combobox.pack()
combobox.bind("<<ComboboxSelected>>", select_graph)

tree = ttk.Treeview(root, selectmode=tk.EXTENDED)
tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.E) 

tree.configure(yscrollcommand=scrollbar.set)
tree.bind("<<TreeviewSelect>>", tree_on_select)

fig, ax = plt.subplots()
ax.grid(True)
plt.xlabel("Время, сек")
plt.ylabel("Y")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE)

time_label = ttk.Label(root, text=f"Время:")
time_label.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE)

'''slider_ax = plt.axes((0.1, 0.02, 0.8, 0.03))  
slider = Slider(slider_ax, "X", 0, 130000, valinit=0)  
slider.on_changed(slider_on_change)'''

root.mainloop()
