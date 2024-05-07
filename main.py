import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy

import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os
from itertools import accumulate

class Spectrum:
    additional_window : tk.Tk
    graph_frame : ttk.Frame
    lines_frame : ttk.Frame
    cls_button : ttk.Button
    tree_lines : ttk.Treeview
    scrollbar_spectrum : ttk.Scrollbar
    canvas_spectrum : FigureCanvasTkAgg
    fig_spectrum : Figure
    all_values : list[list[float]]
    selected_lines : list[int]
    current_numbers : list[list[float]]

    def prepare_to_create(self) -> None:
        if len(NUMBERS[ComboboxSelection.CURRENT]) <= 0:
            messagebox.showerror("Ошибка", "Вы не загрузили значение силы тока")
        else:
            self.create_additional_window()

    def create_additional_window(self) -> None:
        self.additional_window = tk.Tk()
        self.additional_window.title("График спектра сигнала")
        # self.additional_window.geometry("800x500")

        self.graph_frame = ttk.Frame(self.additional_window)
        self.graph_frame.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=tk.TRUE)

        # frame for list of lines
        self.lines_frame = ttk.Frame(self.additional_window)
        self.lines_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

        # creation of button for clearing the scene and selected chart lines to display
        self.cls_button = ttk.Button(self.lines_frame, text="Очистить выбор", command=self.clear_list_on_select)
        self.cls_button.pack(side=tk.TOP)

        # creation of list of views for every line that chart can be displayed
        self.tree_lines = ttk.Treeview(self.lines_frame, selectmode=tk.EXTENDED)
        self.tree_lines.heading("#0", text="Выбор графиков:")
        self.tree_lines.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

        # creation of scrollbar
        self.scrollbar_spectrum = ttk.Scrollbar(self.lines_frame, orient=tk.VERTICAL, command=self.tree_lines.yview)
        self.scrollbar_spectrum.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.W)

        self.tree_lines.configure(yscrollcommand=self.scrollbar_spectrum.set)
        self.tree_lines.bind("<<TreeviewSelect>>", self.tree_lines_on_select)

        self.fig_spectrum = plt.figure()
        self.fig_spectrum.add_axes((0.2, 0.2, 0.6, 0.6))
        self.set_plot_spectrum()

        self.canvas_spectrum = FigureCanvasTkAgg(self.fig_spectrum, master=self.additional_window)
        self.canvas_spectrum.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)
        self.get_values()
        self.plot_data_spectrum()

    def get_values(self):
        self.current_numbers = NUMBERS[ComboboxSelection.CURRENT]
        if len(self.current_numbers) <= 0:
            messagebox.showerror("Ошибка", "Вы не загрузили значение силы тока")
        else:
            self.all_values = self.get_list_of_spectrum_elements()
            self.clear_scene()

    def get_list_of_spectrum_elements(self) -> list[list[float]]:
        return [[current_elem
                 for current_elem in numpy.fft.fft(current_line_data, 64)]
                for current_line_data in self.current_numbers]
    
    def update_chart_list(self) -> None:
        self.selected_lines = []

        self.tree_lines.delete(*self.tree_lines.get_children())
        for i in range(len(self.all_values)):
            self.tree_lines.insert("", tk.END, text=f"График спектра ({i + 1})")

    def plot_data_spectrum(self) -> list[Line2D]:
        # removes the figure
        self.fig_spectrum.clear()
        self.fig_spectrum.add_axes((0.2, 0.2, 0.6, 0.6))
        
        if len(self.selected_lines) > 0:
            line_objects = [
                self.fig_spectrum.axes[0].stem(
                    numpy.arange(len(spectrum.all_values[i])), 
                    numpy.abs(spectrum.all_values[i]),
                    label=f"|FI|({i + 1})",
                    linefmt=f'C{index}', markerfmt=f'o', basefmt=f'C{index}').baseline
                for index, i in enumerate(self.selected_lines)
            ]
            self.fig_spectrum.legend()
        else:
            line_objects = []
        
        self.set_plot_spectrum()
        self.canvas_spectrum.draw()
        return line_objects
    
    def update_cells_colors(self, line_objects: list[Line2D]) -> None:
        for index, (item, line_object) in enumerate(zip(self.selected_lines, line_objects)):
            self.tree_lines.tag_configure(f'mytag_{index}',
                background=to_hex(line_object.get_color()),
                foreground='white'
            )
            self.tree_lines.item(self.tree_lines.get_children()[item], tags=(f'mytag_{index}',))
    
    def clear_list_on_select(self):
        self.clear_scene()
    
    def tree_lines_on_select(self, _) -> None:
        if len(self.tree_lines.selection()) <= 0:
            return

        for item in self.tree_lines.selection():
            item_text = self.tree_lines.item(item, "text")
            if (sel_now := self.tree_lines.index(item)) not in self.selected_lines:
                self.selected_lines.append(sel_now)
                self.tree_lines.item(item, text=f"+ {item_text}")
            else:
                self.selected_lines.remove(sel_now)
                self.tree_lines.item(item, text=item_text[2:], tags="")
            self.tree_lines.selection_remove(item)

        self.update_cells_colors(self.plot_data_spectrum())

    def set_plot_spectrum(self):
        self.fig_spectrum.axes[0].grid(True)
        self.fig_spectrum.axes[0].set_xlabel("Частота, Гц")
        self.fig_spectrum.axes[0].set_ylabel("Амплитуда")
        self.fig_spectrum.axes[0].set_xlim((0,32))
    
    def clear_scene(self):
        self.update_chart_list()
        self.plot_data_spectrum()

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


# consume time in seconds and represents it in string
# that consists of hours, minutes and seconds.
def time_format(full_seconds: float) -> str:
    if full_seconds == 0:
        return "нет"

    full_minutes = int(full_seconds // 60)
    full_hours = int(full_minutes // 60)

    seconds = full_seconds % 60
    minutes = full_minutes % 60
    return f"{full_hours:02}:{minutes:02}:{seconds:.2f}"


# reads data from file, that we may peak in filedialog menu
# returns list of strings (or null)
def load_file() -> list[str] | None:
    if filepath := filedialog.askopenfilename(filetypes=[("TXT файлы", "*.txt")]):
        with open(filepath, "r") as file:
            return file.readlines()


# this method parses given list and fetches elements in
# even lines (that are not duplicates)

# returns 2-dimensional array of float numbers
def parse_file_lines(lines: list[str]) -> list[list[float]]:
    return [[float(num.replace(',', '.')) # substitutes commas by dots
             for num in line.split('\t')]
            for i, line in enumerate(lines) if i % 2 == 0]


def load_file_voltage() -> None:
    global NUMBERS
    if data := load_file():
        NUMBERS[ComboboxSelection.VOLTAGE] = parse_file_lines(data)
        # combobox.current(int newindex) sets the combobox
        # value to the element at position newindex in the list of values
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

        dump_to_file()


# calculates instant power elements by multiplication of voltage and current
# getting 2 lists -> one list of multiplication numbers
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

        dump_to_file()


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

        dump_to_file()


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

        dump_to_file()


def calculate_full_power(voltage_numbers: list[list[float]],
                         current_numbers: list[list[float]]) -> list[list[float]]:
    return [[voltage * current / ((i + 1) / 10 / 80)**2
             for i, (voltage, current) in enumerate(accumulate(map(lambda a, b: (a**2, b**2),
                                                                   voltage_data, current_data),
                                                               lambda a, b: (a[0] + b[0], a[1] + b[1])))]
            for voltage_data, current_data in zip(voltage_numbers, current_numbers)]


def dump_to_file() -> None:
    numbers = NUMBERS[combobox.current()]
    filename = f"./output/{LABELS[combobox.current()]}_{combobox.current()}.txt"

    if not os.path.exists("./output/"):
        os.mkdir("./output/")


    with open(filename, "w") as f:
        for numbers_data in numbers:
            f.write(f"{"\t".join([str(number).replace(".", ",") for number in numbers_data])}\n")


# draw new thing on canvas, consists of 2 steps
# 1. Clear the canvas and create description for axis, updates time, etc.
# 2. Draw new chart
def clear_scene() -> None:
    update_scene()
    plot_data(selected_items)


# prepares the diagram description and updates time
def update_scene() -> None:
    update_graph_list()
    update_time()

# clears selected items for drawing,
                        #  clears the scene and puts new X-axis description
def update_graph_list() -> None:
    global selected_items, experiment_time
    selected_items = []

    tree.delete(*tree.get_children())
    for i in range(len(NUMBERS[combobox.current()])):
        tree.insert("", tk.END, text=f"График {LABELS[combobox.current()]}({i + 1})")


# frequency = 800 measures/second, 80 measures in every line
# -> 10 lines = 1 second -> experiment time = number of lines / 10.
# + data formatting
def update_time() -> None:
    experiment_time = len(NUMBERS[combobox.current()]) / 10
    time_label.configure(text=f"Продолжительность эксперимента: {time_format(experiment_time)}")


# clear the canvas and draw new element(s)
def plot_data(data: list[int]) -> list[Line2D]:
    # removes the figure
    graph_fig.clear()
    graph_fig.add_axes((0.2, 0.2, 0.6, 0.6))

    if len(data) <= 0:
        line_objects = []
    else:
        time_seconds = [i / 10 / 80 for i in range(80)]  # length of the row is always 80
        line_objects = [graph_fig.axes[0].plot(time_seconds, NUMBERS[combobox.current()][i],
                                 label=f"{LABELS[combobox.current()]}({i + 1})")[0]
                        for i in data]

        graph_fig.legend(fontsize="x-large")

    update_plot_info()
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
                           background=to_hex(line_object.get_color()),
                           foreground='white')
        tree.item(tree.get_children()[item], tags=(f'mytag_{index}',))


def update_plot_info():
    graph_fig.axes[0].grid(True)
    graph_fig.axes[0].set_xlabel("Время, сек")
    graph_fig.axes[0].set_ylabel(LABELS[combobox.current()])
    graph_fig.axes[0].set_xlim((slider_min.val, slider_max.val))
    graph_canvas.draw()


def sliders_on_change(_: float) -> None:
    update_plot_info()


#creating main window
#root is a reference to manipulate main frame
root = tk.Tk()
root.title("ДЗ1 by ТыШаКаТя")

#put the frame for buttons inside parent's top-level widget
button_frame = ttk.Frame(root)
button_frame.pack(side=tk.TOP)

#creating buttons for each operation
for i, command in {
    ComboboxSelection.VOLTAGE: load_file_voltage,
    ComboboxSelection.CURRENT: load_file_current,
    ComboboxSelection.INSTANT_POWER: load_file_instant_power,
    ComboboxSelection.ACTIVE_POWER: load_file_active_power,
    ComboboxSelection.REACTIVE_POWER: load_file_reactive_power,
    ComboboxSelection.FULL_POWER: load_file_full_power
}.items():
    load_button = ttk.Button(button_frame, command=command, text=f"+ {TITLES[i]} ({LABELS[i]})")
    load_button.pack(side=tk.LEFT, padx=5)

spectrum = Spectrum()
# spectrumm button, opens new window
spectrumButton = ttk.Button(root, text="Получить спектр", command=spectrum.prepare_to_create)
spectrumButton.pack()

#Combobox is a widget that combines a text field
# with a pop-down list of values
combobox = ttk.Combobox(root, state="readonly", values=[f"{TITLES[i]} ({LABELS[i]})" for i in ComboboxSelection.all])

# by default the combobox is specified by voltage int representation
combobox.current(ComboboxSelection.VOLTAGE)
combobox.pack()
combobox.bind("<<ComboboxSelected>>", combobox_on_select)

#
tree_frame = ttk.Frame(root)
tree_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

#creation of button for clearing the scene and selected chart lines to display
clear_button = ttk.Button(tree_frame, text="Очистить выбор", command=clear_on_select)
clear_button.pack(side=tk.TOP)

#creation of list of views for every line that chart can be displayed
tree = ttk.Treeview(tree_frame, selectmode=tk.EXTENDED)
tree.heading("#0", text="Выбор графиков:")
tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

#creation of scrollbar
scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.W)

tree.configure(yscrollcommand=scrollbar.set)
tree.bind("<<TreeviewSelect>>", tree_on_select)

###paint bars using matplotlib dependency

#create a figure
graph_fig = plt.figure()
graph_fig.add_axes((0.2, 0.2, 0.6, 0.6))

#canvas that is used to be painted on
graph_canvas = FigureCanvasTkAgg(graph_fig, master=root)
graph_fig.axes[0].grid(True)
graph_fig.axes[0].set_xlabel("Время, сек")
graph_fig.axes[0].set_ylabel(LABELS[combobox.current()])
graph_fig.axes[0].set_xlim((0, 1/10))
graph_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)

# sets up sliders for graph
slider_fig = plt.figure(figsize=(6.4, 0.48))
slider_fig.add_axes((0.2, 0.5, 0.6, 0.3))
slider_fig.add_axes((0.2, 0.2, 0.6, 0.3))
slider_min = Slider(slider_fig.axes[0], "", 0, 1/10,
                    valinit=0, valstep=1/20/10,
                    initcolor="none", closedmax=False)
slider_max = Slider(slider_fig.axes[1], "", 0, 1/10,
                    valinit=1/10, valstep=1/20/10,
                    initcolor="none", closedmin=False)
slider_min.slidermax = slider_max
slider_max.slidermin = slider_min
slider_min.on_changed(sliders_on_change)
slider_max.on_changed(sliders_on_change)
slider_canvas = FigureCanvasTkAgg(slider_fig, master=root)
slider_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)

#time label
time_label = ttk.Label(root, text=f"Продолжительность эксперимента: {time_format(0)}")
time_label.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)

# starting our frame application
root.mainloop()
