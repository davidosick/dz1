import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from itertools import accumulate

class ComboboxSelection:
    VOLTAGE = 0
    CURRENT = 1
    INSTANT_POWER = 2
    ACTIVE_POWER = 3
    REACTIVE_POWER = 4
    FULL_POWER = 5


    all = [0, 1, 2, 3, 4, 5]


TITLES: dict[int, str] = {
    ComboboxSelection.VOLTAGE: "Напряжение",
    ComboboxSelection.CURRENT: "Сила тока",
    ComboboxSelection.INSTANT_POWER: "Мгновенная мощность",
    ComboboxSelection.ACTIVE_POWER: "Активная мощность",
    ComboboxSelection.REACTIVE_POWER: "Реактивная мощность",
    ComboboxSelection.FULL_POWER: "Полная мощность"
}

LABELS: dict[int, str] = {
    ComboboxSelection.VOLTAGE: "U",
    ComboboxSelection.CURRENT: "I",
    ComboboxSelection.INSTANT_POWER: "p",
    ComboboxSelection.ACTIVE_POWER: "P",
    ComboboxSelection.REACTIVE_POWER: "Q",
    ComboboxSelection.FULL_POWER: "S"
}

global NUMBERS
NUMBERS: dict[int, list[list[float]]] = {
    ComboboxSelection.VOLTAGE: [],
    ComboboxSelection.CURRENT: [],
    ComboboxSelection.INSTANT_POWER: [],
    ComboboxSelection.ACTIVE_POWER: [],
    ComboboxSelection.REACTIVE_POWER: [],
    ComboboxSelection.FULL_POWER: []
}

global experiment_time
experiment_time: float

global selected_items
selected_items: list[int]


def time_format(full_seconds: float) -> str:
    if full_seconds == 0:
        return "нет"

    full_minutes = int(full_seconds // 60)
    full_hours = int(full_minutes // 60)

    seconds = full_seconds % 60
    minutes = full_minutes % 60
    return f"{full_hours:02}:{minutes:02}:{seconds:.2f}"


def load_file() -> list[str] | None:
    if filepath := filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")]):
        with open(filepath, "r") as file:
            return file.readlines()


def parse_file_lines(lines: list[str]) -> list[list[float]]:
    return [[float(num.replace(',', '.'))
             for num in line.split('\t')]
            for i, line in enumerate(lines) if i % 2 == 0]


def load_file_voltage() -> None:
    global NUMBERS
    if data := load_file():
        NUMBERS[ComboboxSelection.VOLTAGE] = parse_file_lines(data)

        combobox.current(ComboboxSelection.VOLTAGE)
        clear_scene()


def load_file_current() -> None:
    global NUMBERS
    if data := load_file():
        NUMBERS[ComboboxSelection.CURRENT] = parse_file_lines(data)

        combobox.current(ComboboxSelection.CURRENT)
        clear_scene()


def load_file_instant_power() -> None:
    global NUMBERS
    voltage_numbers = NUMBERS[ComboboxSelection.VOLTAGE]
    current_numbers = NUMBERS[ComboboxSelection.CURRENT]
    if len(current_numbers) <= 0 or len(voltage_numbers) <= 0:
        messagebox.showerror("Ошибка", "Вы не загрузили значения напряжения или силы тока")
    else:
        NUMBERS[ComboboxSelection.INSTANT_POWER] = calculate_instant_power(voltage_numbers, current_numbers)

        combobox.current(ComboboxSelection.INSTANT_POWER)
        clear_scene()


def calculate_instant_power(voltage_numbers: list[list[float]], 
                            current_numbers: list[list[float]]) -> list[list[float]]:
    return [[voltage * current
             for voltage, current in zip(voltage_data, current_data)]
            for voltage_data, current_data in zip(voltage_numbers, current_numbers)]

def load_file_active_power() -> None:
    global NUMBERS
    voltage_numbers = NUMBERS[ComboboxSelection.VOLTAGE]
    current_numbers = NUMBERS[ComboboxSelection.CURRENT]
    if len(current_numbers) <= 0 or len(voltage_numbers) <= 0:
        messagebox.showerror("Ошибка", "Вы не загрузили значения напряжения или силы тока")
    else:
        NUMBERS[ComboboxSelection.INSTANT_POWER] = calculate_instant_power(voltage_numbers, current_numbers)
        NUMBERS[ComboboxSelection.ACTIVE_POWER] = calculate_active_power(NUMBERS[ComboboxSelection.INSTANT_POWER])

        combobox.current(ComboboxSelection.ACTIVE_POWER)
        clear_scene()


def calculate_active_power(instant_power_numbers: list[list[float]]) -> list[list[float]]:
    return [[instant_power / ((i + 1) / 10 / 80)
             for i, instant_power in enumerate(accumulate(instant_power_data))]
            for instant_power_data in instant_power_numbers]

def load_file_reactive_power() -> None:
    global NUMBERS
    voltage_numbers = NUMBERS[ComboboxSelection.VOLTAGE]
    current_numbers = NUMBERS[ComboboxSelection.CURRENT]
    if len(current_numbers) <= 0 or len(voltage_numbers) <= 0:
        messagebox.showerror("Ошибка", "Вы не загрузили значения напряжения или силы тока")
    else:
        NUMBERS[ComboboxSelection.INSTANT_POWER] = calculate_instant_power(voltage_numbers, current_numbers)
        NUMBERS[ComboboxSelection.ACTIVE_POWER] = calculate_active_power(NUMBERS[ComboboxSelection.INSTANT_POWER])
        NUMBERS[ComboboxSelection.FULL_POWER] = calculate_full_power(voltage_numbers, current_numbers)
        NUMBERS[ComboboxSelection.REACTIVE_POWER] = calculate_reactive_power(NUMBERS[ComboboxSelection.ACTIVE_POWER], 
                                                                             NUMBERS[ComboboxSelection.FULL_POWER])

        combobox.current(ComboboxSelection.REACTIVE_POWER)
        clear_scene()


def calculate_reactive_power(active_power_numbers: list[list[float]],
                             full_power_numbers: list[list[float]]) -> list[list[float]]:
    return [[abs(full_power**2 - active_power**2)**(1/2)
             for full_power, active_power in zip(full_power_data, active_power_data)]
            for full_power_data, active_power_data in zip(full_power_numbers, active_power_numbers)]


def load_file_full_power() -> None:
    global NUMBERS
    voltage_numbers = NUMBERS[ComboboxSelection.VOLTAGE]
    current_numbers = NUMBERS[ComboboxSelection.CURRENT]
    if len(current_numbers) <= 0 or len(voltage_numbers) <= 0:
        messagebox.showerror("Ошибка", "Вы не загрузили значения напряжения или силы тока")
    else:
        NUMBERS[ComboboxSelection.FULL_POWER] = calculate_full_power(voltage_numbers, current_numbers)

        combobox.current(ComboboxSelection.FULL_POWER)
        clear_scene()
    

def calculate_full_power(voltage_numbers: list[list[float]],
                         current_numbers: list[list[float]]) -> list[list[float]]:
    return [[voltage * current / ((i + 1) / 10 / 80)**2
             for i, (voltage, current) in enumerate(accumulate(map(lambda a: (a[0]**2, a[1]**2), 
                                                                   zip(voltage_data, current_data)), 
                                                               lambda a, b: (a[0] + b[0], a[1] + b[1])))]
            for voltage_data, current_data in zip(voltage_numbers, current_numbers)]


def clear_scene() -> None:
    update_scene()
    plot_data(selected_items)  # просто чистим холст


def update_scene() -> None:
    update_graph_list()
    update_time()

def update_graph_list() -> None:
    global selected_items, experiment_time
    selected_items = []


    tree.delete(*tree.get_children())
    for i in range(len(NUMBERS[combobox.current()])):
        tree.insert("", tk.END, text=f"График {LABELS[combobox.current()]}({i + 1})")


def update_time() -> None:
    experiment_time = len(NUMBERS[combobox.current()]) / 10
    time_label.configure(text=f"Время: {time_format(experiment_time)}")


def plot_data(data: list[int]) -> list[Line2D]:
    plt.clf()

    if len(data) <= 0:
        line_objects = []
    else:
        time_seconds = [i / 10 / 80 for i in range(80)]  # из задания длина всегда 80
        line_objects = [plt.plot(time_seconds, NUMBERS[combobox.current()][i],
                                 label=f"{LABELS[combobox.current()]}({i + 1})")[0]
                        for i in data]

        plt.legend(fontsize="x-large")

    set_plot()
    canvas.draw()
    return line_objects


def combobox_on_select(_) -> None:
    clear_scene()


def clear_on_select() -> None:
    clear_scene()


def tree_on_select(_) -> None:
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
        tree.selection_remove(item)

    update_cells_colors(plot_data(selected_items))


def update_cells_colors(line_objects: list[Line2D]) -> None:
    for index, (item, line_object) in enumerate(zip(selected_items, line_objects)):
        tree.tag_configure(f'mytag_{index}',
                           background=str(line_object.get_color()),
                           foreground='white')
        tree.item(tree.get_children()[item], tags=(f'mytag_{index}',))


def set_plot():
    plt.grid(True)
    plt.xlabel("Время, сек")
    plt.xlim((0, 1 / 10))
    plt.ylabel(LABELS[combobox.current()])


root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")

button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP)

for i, command in {
    ComboboxSelection.VOLTAGE: load_file_voltage,
    ComboboxSelection.CURRENT: load_file_current,
    ComboboxSelection.INSTANT_POWER: load_file_instant_power,
    ComboboxSelection.ACTIVE_POWER: load_file_active_power,
    ComboboxSelection.REACTIVE_POWER: load_file_reactive_power,
    ComboboxSelection.FULL_POWER: load_file_full_power
}.items():
    load_button = tk.Button(button_frame, command=command, text=f"+ {TITLES[i]} ({LABELS[i]})")
    load_button.pack(side=tk.LEFT, padx=5)

combobox = ttk.Combobox(root, state="readonly", values=[f"{TITLES[i]} ({LABELS[i]})" for i in ComboboxSelection.all])
combobox.current(ComboboxSelection.VOLTAGE)
combobox.pack()
combobox.bind("<<ComboboxSelected>>", combobox_on_select)

tree_frame = tk.Frame(root)
tree_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

clear_button = tk.Button(tree_frame, text="Очистить выбор", command=clear_on_select)
clear_button.pack(side=tk.TOP)

tree = ttk.Treeview(tree_frame, selectmode=tk.EXTENDED)
tree.heading("#0", text="Выбор графиков:")
tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.W)

tree.configure(yscrollcommand=scrollbar.set)
tree.bind("<<TreeviewSelect>>", tree_on_select)

fig = plt.figure()
set_plot()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE)

time_label = ttk.Label(root, text=f"Время: {time_format(0)}")
time_label.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE)

root.mainloop()
