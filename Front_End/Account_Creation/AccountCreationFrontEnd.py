import tkinter as tk
from tkinter import messagebox
import re
from Back_End.Account_Creation.AccountCreationBackEnd import *

# Reads csv into dictionary of dictionaries
users = load_users()

def validate_email(email: str) -> bool:
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def open_login_window(window: tk.Tk, account: dict, buttons: dict) -> None:
    login_window = tk.Toplevel(window)
    login_window.title("Login")
    login_window.geometry("400x250")
    login_window.transient(window)
    login_window.grab_set()

    # Credential labels and entry fields
    tk.Label(login_window, text="Username/Email:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(login_window, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)

    username_entry = tk.Entry(login_window, font=("Helvetica", 12))
    password_entry = tk.Entry(login_window, font=("Helvetica", 12), show="*")

    username_entry.grid(row=0, column=1, padx=10, pady=10)
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(
        login_window,
        text="Login",
        font=("Helvetica", 12),
        command=lambda: [login(username_entry.get(), password_entry.get(), account, buttons), login_window.destroy()]
    ).grid(row=3, column=0, columnspan=2, pady=10)

    # Wait until the login window is closed
    login_window.wait_window()

def open_sign_up_window(window: tk.Tk, account: dict, buttons: dict) -> None:
    sign_up_window = tk.Toplevel(window)
    sign_up_window.title("Sign Up")
    sign_up_window.geometry("400x250")
    sign_up_window.transient(window)
    sign_up_window.grab_set()

    # Credential labels and entry fields
    tk.Label(sign_up_window, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(sign_up_window, text="Email:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
    tk.Label(sign_up_window, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10)
    
    username_entry = tk.Entry(sign_up_window, font=("Helvetica", 12))
    email_entry = tk.Entry(sign_up_window, font=("Helvetica", 12))
    password_entry = tk.Entry(sign_up_window, font=("Helvetica", 12), show="*")

    username_entry.grid(row=0, column=1, padx=10, pady=10)
    email_entry.grid(row=1, column=1, padx=10, pady=10)
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Button(
        sign_up_window,
        text="Sign Up",
        font=("Helvetica", 12),
        command=lambda: [sign_up(username_entry.get(), email_entry.get(), password_entry.get(), account, buttons), sign_up_window.destroy()]
    ).grid(row=3, column=0, columnspan=2, pady=10)

    sign_up_window.wait_window()

def login(username: str, password: str, account: dict, buttons: dict) -> None:
    if username in users["Username"].values() and users["Password"].values():
        account["username"] = username
        
        for button in buttons["out"]:
            button.grid_remove()
        
        buttons["in"][0].grid(row=0, column=1, padx=5, pady=20)

        messagebox.showinfo(title="Login Successful", message=f"Welcome, {username}.")
    
    else:
        messagebox.showerror(title="Invalid Login", message="Invalid credentials, please try again.")

def sign_up(username: str, email: str, password: str, account: dict, buttons: dict) -> None:
    # Check if the username already exists
    if username in users["Username"].values() or email in users["Email"].values():
        messagebox.showerror(title="Username Already Exists", message="Username already exists, please try another.")
        return

    # Check if email is ok
    if not validate_email(email):
        messagebox.showerror(title="Invalid Email", message="Email is invalid, please try another.")
        return

    # Ask the user for confirmation before proceeding
    result = messagebox.askokcancel(title="Confirm Sign Up", message=f"Create account for {username}?")
    
    if result:
        new_id = max(users["ID"].values()) + 1
        users["Username"].update({new_id: username})
        users["Password"].update({new_id: password})
        users["Email"].update({new_id: email})
        users["ID"].update({new_id: new_id})
        
        # Temporary print function to see dictionary after new user is added
        print(users)
        
        # Update csv with new account
        save_users(users)
        
        login(username, password, account, buttons)

def logout(account: dict, buttons: dict):
    account.clear()
    
    column = 1
    for button in buttons["out"]:
        button.grid(row=0, column=column, padx=5, pady=20)
        column += 1

    buttons["in"][0].grid_remove()
