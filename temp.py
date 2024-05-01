import tkinter as tk
from tkinter import ttk, filedialog

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ComboboxSelection:
    VOLTAGE = 0
    AMPERE = 1
    INSTANT_POWER = 2  # Опция для мгновенных мощностей


global voltage_numbers, ampere_numbers, instant_power_data

global experiment_time
experiment_time: float

global selected_items


def time_format(full_seconds: float) -> str:
    full_minutes = int(full_seconds // 60)
    full_hours = int(full_minutes // 60)

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

        combobox.current(ComboboxSelection.VOLTAGE)
        update_graph_list(voltage_numbers, 'U')


def load_file_ampere() -> None:
    global ampere_numbers
    if data := load_file():
        ampere_numbers = parse_file_lines(data)

        combobox.current(ComboboxSelection.AMPERE)
        update_graph_list(ampere_numbers, 'I')


def load_file_instant_power() -> None:
    global voltage_numbers, ampere_numbers, instant_power_data
    if voltage_numbers and ampere_numbers:
        instant_power_data = [calculate_instantaneous_power(voltage_line, current_line) for voltage_line, current_line in zip(voltage_numbers, ampere_numbers)]
        update_graph_list(range(1, len(instant_power_data) + 1), 'Мгновенная мощность')


def calculate_instantaneous_power(voltage_data: list[float], current_data: list[float]) -> list[float]:
    return [voltage * current for voltage, current in zip(voltage_data, current_data)]


def clear_select() -> None:
    global selected_items
    selected_items = []
    match combobox.current():
        case ComboboxSelection.VOLTAGE:
            update_graph_list(voltage_numbers, 'U')
        case ComboboxSelection.AMPERE:
            update_graph_list(ampere_numbers, 'I')
        case ComboboxSelection.INSTANT_POWER:
            update_graph_list(instant_power_data, 'Мгновенная мощность')
    plot_data(selected_items, "U")  # просто чистим холст


def update_graph_list(data: list[list[float]], letter='?') -> None:
    global selected_items, experiment_time
    selected_items = []

    length = len(data)
    tree.delete(*tree.get_children())
    for i in range(length):
        tree.insert("", tk.END, text=f"График {letter}({i + 1})")

    experiment_time = length / 10
    time_label.configure(text=f"Время: {time_format(experiment_time)}")


def plot_data(data: list[list[float]], label: str) -> list[Line2D]:
    plt.clf()
    time_seconds = [i / 800 for i in range(1, len(data[0]) + 1)]

    if label in ["U", "I"]:
        line_objects = [plt.plot(time_seconds, dataset,
                                 label=f"{label}({(voltage_numbers.index(datas) + 1 if label == 'U' else ampere_numbers.index(datas) + 1)})")[
                            0]
                        for datas, dataset in zip(data, voltage_numbers if label == 'U' else ampere_numbers)]
    elif label == "Мгновенная мощность":
        line_objects = [plt.plot(time_seconds, p_data, label="Мгновенная мощность")[0] for p_data in data]

    ax.grid(True)
    plt.xlabel("Время, сек")
    plt.ylabel(label)
    plt.legend(fontsize="x-large")
    canvas.draw()
    return line_objects


def select_graph(event) -> None:
    global voltage_numbers, ampere_numbers, selected_items
    match combobox.current():
        case ComboboxSelection.VOLTAGE:
            update_graph_list(voltage_numbers, "U")
        case ComboboxSelection.AMPERE:
            update_graph_list(ampere_numbers, "I")
        case ComboboxSelection.INSTANT_POWER:
            update_graph_list(instant_power_data, "Мгновенная мощность")
    plot_data(selected_items, "U")  # просто чистим холст


def tree_on_select(event) -> None:
    if len(tree.selection()) <= 0:
        return
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
        case ComboboxSelection.INSTANT_POWER:
            filtered_data = [instant_power_data[index] for index in selected_items]
            label = "Мгновенная мощность"

    update_cells_colors(plot_data(filtered_data, label))
    tree.selection_remove(item)


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

load_button_instant_power = tk.Button(button_frame, text="+ Мгновенные мощности", command=load_file_instant_power)
load_button_instant_power.pack(side=tk.RIGHT, padx=5)

clear_select_button = tk.Button(button_frame, text="Очистить выбор", command=clear_select)
clear_select_button.pack(side=tk.RIGHT, padx=10)

combobox = ttk.Combobox(root, values=["Напряжение (U)", "Сила тока (I)", "Мгновенная мощность"], state="readonly")
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

root.mainloop()