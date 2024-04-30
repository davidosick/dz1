import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk 
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

VOLTAGE = 0
AMPERE = 1

global voltage_numbers, ampere_numbers

def load_file_voltage() -> None:
    global voltage_numbers
    data = load_file()

    voltage_numbers = [[float(num.replace(',', '.')) 
                        for num in line.split('\t')] 
                        for line in data]

    #plot_data(voltage_numbers)
    combobox.current(VOLTAGE)
    update_graph_list(voltage_numbers, 'U')

def load_file_ampere() -> None:
    global ampere_numbers
    data = load_file()

    ampere_numbers = [[float(num.replace(',', '.')) 
                        for num in line.split('\t')] 
                        for line in data]

    #plot_data(ampere_numbers)
    combobox.current(AMPERE)
    update_graph_list(ampere_numbers, 'I')

def load_file() -> list:
    filepath = filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")])
    if filepath:
        with open(filepath, "r") as file:
            text = file.read()

        data = text.strip().split('\n')
        return data
    
def update_graph_list(data, letter = '?') -> None:
    global selected_items
    selected_items = []
    tree.delete(*tree.get_children())
    for i in range(1, len(data)):
        tree.insert("", "end", text=f"График {letter}({i})")

def plot_data(data: list[list[float]]) -> None:
    plt.clf()
    for dataset in data:
        plt.plot(dataset)
    plt.legend()
    canvas.draw()


def select_graph(event):
    global voltage_numbers, ampere_numbers
    selection = combobox.current() 
    if selection == VOLTAGE:
        update_graph_list(voltage_numbers, 'U')
        #plot_data(voltage_numbers)
    elif selection == AMPERE:
        update_graph_list(ampere_numbers, 'I')
        #plot_data(ampere_numbers)
    plot_data(selected_items)

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
combobox.current(VOLTAGE) 
combobox.pack()
combobox.bind("<<ComboboxSelected>>", select_graph)

global selected_items
selected_items = []
def tree_on_select(event):
    global selected_items
    
    for item in tree.selection():
        sel_now = tree.index(item)+1
        item_text = tree.item(item, "text")
        if sel_now not in selected_items:
            selected_items.append(sel_now)
            tree.item(tree.selection(), text=f"+ {item_text}")
        else:
            selected_items.remove(sel_now)
            tree.item(tree.selection(), text=item_text[2:])

    filtered_data = []
    for index in selected_items:
        if combobox.current() == VOLTAGE:
            filtered_data.append(voltage_numbers[index - 1]) 
        elif combobox.current() == AMPERE:
            filtered_data.append(ampere_numbers[index - 1])


    plot_data(filtered_data)
    print(filtered_data)


tree = ttk.Treeview(root, selectmode="extended")
tree.pack(side=tk.RIGHT, fill="both", expand=True)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y", anchor="e") 

tree.configure(yscrollcommand=scrollbar.set)

tree.bind("<<TreeviewSelect>>", tree_on_select)


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
