import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk

all_entries = []

def save_and_print_entries(entries):
    data = {}
    fields = ["Potencia (Watts)", "Voltaje (V)", "Corriente (Amperios)", "Tiempo utilizado (Horas)"]
    for field, entry in zip(fields, entries):
        data[field] = entry.get()
    print(data)


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
    # Verifica si todas las entradas están llenas
        if all(entry.get() for entry in entries):
            save_and_print_entries(entries)  # Añade esta línea
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
        canvas.delete(image_references[element])
        canvas.delete(line_references[element])
        img_positions.remove((image_references[element], line_references[element]))
        img_count -= 1
    else:
        img = element_to_image[element]

        line_id = canvas.create_line(img_x, img_y, img_x, bus_y, fill="black", width=2)
        line_references[element] = line_id

        img_id = canvas.create_image(img_x, img_y, image=img)
        image_references[element] = img_id

        img_positions.append((img_id, line_id))
        img_count += 1
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


# Función para limpiar todos los campos
def clear_all():
    global img_count, img_positions
    
    # Desmarcar todos los checkboxes y eliminar imágenes asociadas
    for element, var in zip(elementos, checkbox_vars):
        if var.get() == 1:
            var.set(0)
            on_checkbox_click(element, var)
    
    # Limpiar entradas
    for entry in all_entries:
        entry.delete(0, tk.END)

root = tk.Tk()
root.title("Programa")

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
    ("Largo del cable:", 10),
    ("Dinero a pagar: $", 11),
    ("Denominación:", 12),
    ("Calibre Calculado:", 13)
]

for text, r in info_rows:
    tk.Label(root, text=text).grid(row=r, column=0, sticky="w", padx=10, pady=2)
    entry = tk.Entry(root)
    entry.grid(row=r, column=0, padx=10, pady=2, sticky="e")
    all_entries.append(entry)  # Agregamos cada entrada a la lista


clear_button = tk.Button(root, text="Limpiar Todo", command=clear_all)
clear_button.grid(row=13, column=1, padx=10, pady=10, columnspan=2, sticky="n")

calc_button = tk.Button(root, text="Calcular", command=calculate)  
calc_button.grid(row=14, column=1, padx=10, pady=20, columnspan=2, sticky="n")

root.mainloop()
