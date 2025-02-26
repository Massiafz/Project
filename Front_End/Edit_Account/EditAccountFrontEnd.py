import tkinter as tk
from tkinter import messagebox

def open_edit_account_window(window: tk.Tk, account: dict) -> None:
    if account == {}:
        messagebox.showerror(title="Not Logged In", message="Please log in to continue.")
        return

    edit_account_window = tk.Toplevel(window)
    edit_account_window.title("Edit Account")
    edit_account_window.geometry("400x250")
    edit_account_window.transient(window)
    edit_account_window.grab_set()

    # Credential labels and entry fields
    tk.Label(edit_account_window, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(edit_account_window, text="Email:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
    tk.Label(edit_account_window, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10)
    
    username_entry = tk.Entry(edit_account_window, font=("Helvetica", 12))
    email_entry = tk.Entry(edit_account_window, font=("Helvetica", 12))
    password_entry = tk.Entry(edit_account_window, font=("Helvetica", 12), show="*")

    username_entry.insert(0, "massi")
    email_entry.insert(0, "massi@massi.com")
    password_entry.insert(0, "test")

    username_entry.grid(row=0, column=1, padx=10, pady=10)
    email_entry.grid(row=1, column=1, padx=10, pady=10)
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    confirm_button = tk.Button(
        edit_account_window,
        text="Confirm",
        font=("Helvetica", 12),
        command=lambda: edit_account(username_entry.get(), email_entry.get(), password_entry.get())
    ).grid(row=3, column=0, columnspan=2, pady=10)

    delete_account_button = tk.Button(
        edit_account_window,
        text="Delete Account",
        font=("Helvetica", 8),
        command=lambda: delete_account(0, "massi")
    ).grid(row=5, column=1, columnspan=3, padx=(200, 5), pady=(30, 5))

def edit_account(username: str, email: str, password: str) -> None:
    messagebox.showinfo(title="Account Edit Successful", message=f"You have successfully edited your account: {username}.")

def delete_account(id: int, username: str) -> None:
    result = messagebox.askokcancel(title="Confirm Delete Account", message=f"Delete account for {username}?")
    
    if result:
        messagebox.showinfo(title="Account Delete Successful", message=f"You have successfully deleted your account: {username}.")
