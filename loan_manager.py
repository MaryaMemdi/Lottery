import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import random

# Initialize the main window
root = tk.Tk()
root.title("Loan Payment Manager")

# Create a list to store user information
users = []
file_name = "payments.xlsx"

# Function to load the existing data from the excel file
def load_data():
    global users
    try:
        df = pd.read_excel(file_name)
        users = df.to_dict('records')
    except FileNotFoundError:
        users = []

# Function to save the current data to the excel file
def save_data():
    df = pd.DataFrame(users)
    df.to_excel(file_name, index=False)

# Function to add a new user
def add_user():
    name = name_entry.get()
    if name:
        users.append({"name": name, "paid": False})
        save_data()
        update_user_list()
        name_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter a user name.")

# Function to update the user list display
def update_user_list():
    user_list.delete(*user_list.get_children())
    for user in users:
        user_list.insert("", "end", values=(user["name"], "Yes" if user["paid"] else "No"))

# Function to mark a user as paid
def mark_paid():
    selected_item = user_list.selection()
    if selected_item:
        user_name = user_list.item(selected_item[0], 'values')[0]
        for user in users:
            if user["name"] == user_name:
                user["paid"] = True
                break
        save_data()
        update_user_list()

# Function to display unpaid users
def show_unpaid():
    unpaid_list.delete(*unpaid_list.get_children())
    for user in users:
        if not user["paid"]:
            unpaid_list.insert("", "end", values=(user["name"],))

# Function to conduct the lottery
def conduct_lottery():
    unpaid_users = [user for user in users if not user["paid"]]
    if unpaid_users:
        winner = random.choice(unpaid_users)
        messagebox.showinfo("Lottery Winner", f"The winner is {winner['name']}")
        users.remove(winner)
        save_data()
        update_user_list()
    else:
        messagebox.showinfo("Lottery", "No users available for the lottery.")

# Load existing data
load_data()

# Create the UI elements
name_label = tk.Label(root, text="User Name:")
name_label.grid(row=0, column=0, padx=10, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=10, pady=5)
add_button = tk.Button(root, text="Add User", command=add_user)
add_button.grid(row=0, column=2, padx=10, pady=5)

user_list = ttk.Treeview(root, columns=("Name", "Paid"), show="headings")
user_list.heading("Name", text="Name")
user_list.heading("Paid", text="Paid")
user_list.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

mark_paid_button = tk.Button(root, text="Mark as Paid", command=mark_paid)
mark_paid_button.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

unpaid_label = tk.Label(root, text="Unpaid Users:")
unpaid_label.grid(row=3, column=0, padx=10, pady=5)
unpaid_list = ttk.Treeview(root, columns=("Name",), show="headings")
unpaid_list.heading("Name", text="Name")
unpaid_list.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

show_unpaid_button = tk.Button(root, text="Show Unpaid Users", command=show_unpaid)
show_unpaid_button.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

lottery_button = tk.Button(root, text="Conduct Lottery", command=conduct_lottery)
lottery_button.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

# Populate the user list initially
update_user_list()

# Start the main loop
root.mainloop()
