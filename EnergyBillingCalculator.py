import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import Calculations as calc 

all_entries = []

elements_data = []


def save_and_print_entries(entries, element):
    data = {"Element": element}  # Guarda también el nombre del elemento
    fields = ["Potencia (Watts)", "Voltaje (V)", "Corriente (Amperios)", "Tiempo utilizado (Horas)"]
    for field, entry in zip(fields, entries):
        data[field] = float(entry.get())

    # Eliminar datos antiguos del mismo elemento si existen
    elements_data[:] = [d for d in elements_data if d.get("Element") != element]
    elements_data.append(data)

    # Imprimir los datos extraídos de las entradas
    print("Datos de entrada:", elements_data)

def create_popup(element, checkbox_var):
    window = tk.Toplevel(root)
    window.title("Ingresar Datos")

    fields = ["Potencia (Watts):", "Voltaje (V):", "Corriente (Amperios):", "Tiempo utilizado (Horas):"]
    
    # Lista para almacenar las referencias de las entradas
    entries = []
    for field in fields:
        tk.Label(window, text=field).pack(pady=5)
        entry = tk.Entry(window)
        entry.pack(pady=5)
        entries.append(entry)

    def submit():
        if all(entry.get() for entry in entries):
            save_and_print_entries(entries, element)  # Pasa el elemento aquí
            window.destroy()
        else:
            tk.messagebox.showwarning("Advertencia", "Por favor, llena todos los campos o presiona cancelar.")


    def cancel():
        checkbox_var.set(0)
        on_checkbox_click(element, checkbox_var)
        window.destroy()
    
    def on_closing():
        # Advertencia si el usuario intenta cerrar la ventana sin llenar la información
        tk.messagebox.showwarning("Advertencia", "Por favor, llena todos los campos o presiona cancelar.")

    tk.Button(window, text="Aceptar", command=submit).pack(side="left", padx=10, pady=10)
    tk.Button(window, text="Cancelar", command=cancel).pack(side="right", padx=10, pady=10)
    
    # Establece la función on_closing como el controlador del evento de cierre de la ventana
    window.protocol("WM_DELETE_WINDOW", on_closing)


def on_checkbox_click(element, checkbox_var):
    global img_count, img_positions

    selected_count = sum(var.get() for var in checkbox_vars)
    if selected_count > 10:
        tk.messagebox.showwarning("Advertencia", "Solo puedes seleccionar hasta 10 checkboxes.")
        checkbox_var.set(0)
        return

    row = img_count // 2
    col = img_count % 2
    img_x = 60 + row * 80
    img_y = bus_y + (60 if col == 0 else -60)

    if not checkbox_var.get():
        # Antes de intentar eliminar las referencias, verificamos si realmente existen en los diccionarios
        if element in image_references:
            canvas.delete(image_references[element])
            del image_references[element]  # Es importante eliminar la clave para evitar referencias muertas
        if element in line_references:
            canvas.delete(line_references[element])
            del line_references[element]  # Lo mismo aplica aquí

        # Ahora deberíamos verificar si el elemento está en 'img_positions' antes de intentar eliminarlo
        for img_position in img_positions:
            if img_position[0] == element:
                img_positions.remove(img_position)
                break

        img_count -= 1
    else:
        img = element_to_image[element]

        line_id = canvas.create_line(img_x, img_y, img_x, bus_y, fill="black", width=2)
        line_references[element] = line_id

        img_id = canvas.create_image(img_x, img_y, image=img)
        image_references[element] = img_id

        img_positions.append((img_id, line_id))
        img_count += 1
        #elements_data.clear()  # Limpia los datos existentes antes de abrir un nuevo popup
        create_popup(element, checkbox_var)


def calculate():

    selected_count = sum(var.get() for var in checkbox_vars)
    
    # Obtiene el largo del cable
    cable_length = all_entries[0].get()

    # Verifica si hay al menos una checkbox seleccionada y no más de 10
    if not (1 <= selected_count <= 10):
        tk.messagebox.showwarning("Advertencia", "Por favor, selecciona entre 1 y 10 checkboxes.")
        return

    # Verifica si el largo del cable está vacío
    if not cable_length:
        tk.messagebox.showwarning("Advertencia", "Por favor, introduce el largo del cable.")
        return
    
    print(f"Largo del cable: {cable_length} m")


    # Variables para la suma de energias, voltaje y corriente
    total_energy_value = 0
    total_voltage_value = 0
    total_current_value = 0

    # Por cada elemento en elements_data cacula la energia, voltaje y corriente total (suma de datos)
    for data in elements_data:

        potency = data["Potencia (Watts)"]
        hours = data["Tiempo utilizado (Horas)"]
        energy = calc.calculate_energy(potency, hours)
        total_energy_value += energy
        
        total_voltage_value += data["Voltaje (V)"]
        total_current_value += data["Corriente (Amperios)"]

    # Imprimir datos intermedios para depuración
    print(f"Energía total: {total_energy_value}")
    print(f"Voltaje total: {total_voltage_value}")
    print(f"Corriente total: {total_current_value}")

    # Calculamos el costo con la energia total obtenida
    total_energy_cost = calc.calculate_cost(total_energy_value)
    print(f"Costo de energía total: {total_energy_cost}")

    # Usar el total de voltaje, corriente y largo del cable para calcular el calibre
    diameter_calibre = calc.calculate_calibre(float(cable_length), total_voltage_value, total_current_value)
    print(f"Diámetro del calibre calculado: {diameter_calibre}")

    # Buscar el calibre más cercano en el diccionario `calibre_data`
    closest_calibre = min(calc.calibre_data.keys(), key=lambda k: abs(calc.calibre_data[k]["Diametro"] - diameter_calibre))
    print(f"Calibre más cercano encontrado: {closest_calibre}")

    # Antes de mostrar los resultados, limpia las entradas de resultados
    for i in range(1, 4):
        all_entries[i].delete(0, tk.END)

    # Mostrar los resultados en las entradas correspondientes
    all_entries[1].insert(0, total_energy_cost) # Dinero a pagar
    all_entries[2].insert(0, "Baja Tensión Simple Social (BTSS)")  # Tipo de tarifa 
    all_entries[3].insert(0, closest_calibre)          # Diámetro en términos de calibre
    elements_data.clear()


# Función para limpiar todos los campos
def clear_all():
    global img_count, img_positions

    elements_data.clear()
    
    # Desmarcar todos los checkboxes y eliminar imágenes asociadas
    for element, var in zip(elementos, checkbox_vars):
        if var.get() == 1:
            var.set(0)
            on_checkbox_click(element, var)
    
    # Limpiar entradas
    for entry in all_entries:
        entry.delete(0, tk.END)
    
        elements_data.clear()


root = tk.Tk()
root.title("EnergyBillingCalculator")

img_count = 0
img_positions = []
checkbox_vars = [tk.IntVar() for _ in range(20)]
image_references = {}
line_references = {}

# Lista de elementos
elementos = [
    "Bombilla LED", "Bombilla incandescente", "Televisor (LCD/LED)", "Ordenador portátil", 
    "Ordenador de escritorio", "Monitor", "Router de internet", "Módem", 
    "Teléfono móvil (carga)", "Tableta (carga)", "Consola de videojuegos", "Impresora", 
    "Microondas", "Refrigerador", "Lavadora", "Secadora de ropa", 
    "Ventilador", "Aire acondicionado", "Sistema de calefacción", "Aspiradora"
]

folder_path = "./imagenes/"
image_paths = [folder_path + "imagen{}.png".format(i+1) for i in range(20)]
images = [ImageTk.PhotoImage(Image.open(img_path).resize((50, 50))) for img_path in image_paths]
element_to_image = {element: img for element, img in zip(elementos, images)}

canvas = tk.Canvas(root, bg="white", width=450, height=250, bd=2, relief="groove")
canvas.grid(row=0, column=0, rowspan=10, padx=10, pady=10)

bus_y = 125

canvas.create_line(40, bus_y, 450, bus_y, fill="black", width=2)

energy_img = ImageTk.PhotoImage(Image.open(folder_path + "energia.png").resize((40, 40)))
canvas.create_image(30, bus_y, image=energy_img)

for index, (item, var) in enumerate(zip(elementos, checkbox_vars)):
    col = 1 if index < 10 else 2
    row = index % 10
    checkbox = tk.Checkbutton(root, text=item, variable=var,
                              command=lambda element=item, var=var: on_checkbox_click(element, var))
    checkbox.grid(row=row, column=col, sticky="w", padx=5, pady=2)

info_rows = [
    ("Largo del cable (Metros):", 10),
    ("Dinero a pagar: Q/día", 11),
    ("Tipo de tarifa:", 12),
    ("Diámetro (en términos de calibre):", 13)
]

for text, r in info_rows:
    tk.Label(root, text=text).grid(row=r, column=0, sticky="w", padx=10, pady=2)
    entry = tk.Entry(root)
    entry.grid(row=r, column=0, padx=10, pady=2, sticky="e")
    all_entries.append(entry) 


clear_button = tk.Button(root, text="Limpiar Todo", command=clear_all)
clear_button.grid(row=13, column=1, padx=10, pady=10, columnspan=2, sticky="n")

calc_button = tk.Button(root, text="Calcular", command=calculate)  
calc_button.grid(row=14, column=1, padx=10, pady=20, columnspan=2, sticky="n")

root.mainloop()
