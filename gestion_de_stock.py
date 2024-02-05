import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
import csv

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Poussin13",
    database="store",
)

cursor = mydb.cursor()

def generate_data(category_filter=None):
    if category_filter:
        cursor.execute("SELECT * FROM product WHERE category = %s", (category_filter,))
    else:
        cursor.execute("SELECT * FROM product")
    
    products = [row[1] for row in cursor.fetchall()]  # Assuming product name is in the second column
    quantities = [row[4] for row in cursor.fetchall()]  # Assuming quantity is in the fifth column

    x = range(len(products))
    y = np.random.rand(len(products))

    return x, y, products, quantities

def update_plot(category_filter=None):
    new_x, new_y, products, quantities = generate_data(category_filter)

    line.set_xdata(new_x)
    line.set_ydata(quantities)
    ax.set_xticks(new_x)
    ax.set_xticklabels(products, rotation=45, ha="right")
    canvas.draw()

def add_product():
    product_name = entry_name.get()
    product_price = entry_price.get()
    product_category = entry_category.get()

    if not product_name or not product_price or not product_category:
        messagebox.showwarning("Ajouter un produit", "Veuillez remplir tous les champs.")
        return

    sql = "INSERT INTO product (name, price, category) VALUES (%s, %s, %s)"
    val = (product_name, product_price, product_category)

    try:
        cursor.execute(sql, val)
        mydb.commit()
        messagebox.showinfo("Ajouter un produit", "Produit ajouté avec succès")
        update_plot()  # Mettre à jour le graphique après l'ajout du produit
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur", f"Erreur MySQL : {err.msg}")

def remove_product():
    selected_product = entry_name.get()
    if not selected_product:
        messagebox.showwarning("Supprimer un produit", "Veuillez sélectionner un produit à supprimer.")
        return

    sql = "DELETE FROM product WHERE name = %s"
    val = (selected_product,)

    try:
        cursor.execute(sql, val)
        mydb.commit()
        messagebox.showinfo("Supprimer un produit", f"Le produit {selected_product} a été supprimé avec succès.")
        update_plot()  # Mettre à jour le graphique après la suppression du produit
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur", f"Erreur MySQL : {err.msg}")

def update_product():
    selected_product = entry_name.get()
    if not selected_product:
        messagebox.showwarning("Modifier un produit", "Veuillez sélectionner un produit à modifier.")
        return

    new_price = entry_price.get()
    new_category = entry_category.get()

    sql = "UPDATE product SET price = %s, category = %s WHERE name = %s"
    val = (new_price, new_category, selected_product)

    try:
        cursor.execute(sql, val)
        mydb.commit()
        messagebox.showinfo("Modifier un produit", f"Le produit {selected_product} a été modifié avec succès.")
        update_plot()  # Mettre à jour le graphique après la modification du produit
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur", f"Erreur MySQL : {err.msg}")

def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Price", "Description", "Quantity", "Category"])
            
            cursor.execute("SELECT * FROM product")
            for row in cursor.fetchall():
                writer.writerow(row)

def apply_category_filter():
    selected_category = category_filter_combobox.get()
    update_plot(selected_category)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Tableau de Bord Gestion des Stocks")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0)

fig, ax = plt.subplots()
x, y, products, quantities = generate_data()
line, = ax.plot(x, y)
ax.set_xticks(x)
ax.set_xticklabels(products, rotation=45, ha="right")
ax.set_xlabel('Produits')
ax.set_ylabel('Stock de ballons disponible')
ax.set_title('Tableau de Bord Gestion des Stocks de ballons')

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0)

entry_name = ttk.Entry(root, width=20)
entry_name.grid(row=1, column=1, pady=5)
ttk.Label(root, text="Nom du produit").grid(row=1, column=0, pady=5)

entry_price = ttk.Entry(root, width=20)
entry_price.grid(row=2, column=1, pady=5)
ttk.Label(root, text="Prix du produit").grid(row=2, column=0, pady=5)

entry_category = ttk.Entry(root, width=20)
entry_category.grid(row=3, column=1, pady=5)
ttk.Label(root, text="Catégorie du produit").grid(row=3, column=0, pady=5)

add_button = ttk.Button(root, text="Ajouter un produit", command=add_product)
add_button.grid(row=4, column=0, pady=5)

remove_button = ttk.Button(root, text="Supprimer un produit", command=remove_product)
remove_button.grid(row=5, column=0, pady=5)

update_button = ttk.Button(root, text="Modifier un produit", command=update_product)
update_button.grid(row=6, column=0, pady=5)

export_button = ttk.Button(root, text="Exporter en CSV", command=export_to_csv)
export_button.grid(row=7, column=0, pady=5)

category_filter_combobox = ttk.Combobox(root, values=["", "Category1", "Category2", "Category3"])
category_filter_combobox.grid(row=8, column=0, pady=5)
category_filter_combobox.set("")

apply_filter_button = ttk.Button(root, text="Appliquer le filtre", command=apply_category_filter)
apply_filter_button.grid(row=9, column=0, pady=5)

update_plot_button = ttk.Button(root, text="Mettre à jour le stock", command=update_plot)
update_plot_button.grid(row=10, column=0, pady=10)

# Boucle principale pour lancer l'interface utilisateur
root.mainloop()

# Fermeture de la connexion à la fin de l'application
cursor.close()
mydb.close()
