import tkinter as tk
from tkinter import messagebox
import re
from Back_End.Account_Creation.Account import Account, AccountManager


# Instantiate the back-end account manager with the CSV file location.
acc_manager = AccountManager("Back_End/Account_Creation/users.csv")

def validate_email(email: str) -> bool:
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def open_login_window(window: tk.Tk, current_account: dict, buttons: dict) -> None:
    login_window = tk.Toplevel(window)
    login_window.title("Login")
    login_window.geometry("400x250")
    login_window.transient(window)
    login_window.grab_set() 
    print("open_login_window called")
  

    tk.Label(login_window, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(login_window, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)

    username_entry = tk.Entry(login_window, font=("Helvetica", 12))
    password_entry = tk.Entry(login_window, font=("Helvetica", 12), show="*")
    username_entry.grid(row=0, column=1, padx=10, pady=10)
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    def do_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if login(username, password):
            current_account["username"] = username
            buttons["in"][0].grid()  # Show logout button
            for btn in buttons["out"]:
                btn.grid_remove()  # Hide login & sign-up
            login_window.destroy()

    tk.Button(login_window, text="Login", font=("Helvetica", 12), command=do_login).grid(row=3, column=0, columnspan=2, pady=10)
    login_window.wait_window()

def open_sign_up_window(window: tk.Tk, current_account: dict, buttons: dict) -> None:
    sign_up_window = tk.Toplevel(window)
    sign_up_window.title("Sign Up")
    sign_up_window.geometry("400x300")
    sign_up_window.transient(window)
    sign_up_window.grab_set()

    tk.Label(sign_up_window, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(sign_up_window, text="Email:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
    tk.Label(sign_up_window, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10)
    
    username_entry = tk.Entry(sign_up_window, font=("Helvetica", 12))
    email_entry = tk.Entry(sign_up_window, font=("Helvetica", 12))
    password_entry = tk.Entry(sign_up_window, font=("Helvetica", 12), show="*")
    username_entry.grid(row=0, column=1, padx=10, pady=10)
    email_entry.grid(row=1, column=1, padx=10, pady=10)
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    def do_signup():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        if sign_up(username, email, password):
            sign_up_window.destroy()
    tk.Button(sign_up_window, text="Sign Up", font=("Helvetica", 12), command=do_signup).grid(row=4, column=0, columnspan=2, pady=10)
    sign_up_window.wait_window()

def open_edit_account_window(window: tk.Tk, current_account: dict) -> None:
    if "username" not in current_account:
        messagebox.showerror("Error", "You must be logged in to edit your account.")
        return

    edit_window = tk.Toplevel(window)
    edit_window.title("Edit Account - Update Details")
    edit_window.geometry("400x300")
    edit_window.transient(window)
    edit_window.grab_set()

    tk.Label(edit_window, text="New Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(edit_window, text="New Email:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
    tk.Label(edit_window, text="New Password:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10)

    username_entry = tk.Entry(edit_window, font=("Helvetica", 12))
    email_entry = tk.Entry(edit_window, font=("Helvetica", 12))
    password_entry = tk.Entry(edit_window, font=("Helvetica", 12), show="*")

    # Pre-fill fields with current values
    username_entry.insert(0, current_account["username"])
    email_entry.insert(0, acc_manager.get_account(current_account["username"]).email)

    username_entry.grid(row=0, column=1, padx=10, pady=10)
    email_entry.grid(row=1, column=1, padx=10, pady=10)
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    
    def do_edit():
        new_username = username_entry.get().strip()
        new_email = email_entry.get().strip()
        new_password = password_entry.get().strip()

        old_username = current_account["username"]  # Get the currently logged-in username
        account = acc_manager.get_account(old_username)  # Fetch current account data

        if not account:
            messagebox.showerror("Error", "Could not find your account.")
            return

        # Store the updated values in a dictionary ONLY if they changed
        updates = {"username": old_username}  # Keep track of the old username

        # Check if the username has changed
        if new_username and new_username != old_username:
            if acc_manager.get_account(new_username):
                messagebox.showerror("Username Taken", "This username is already in use.")
                return
            updates["username"] = new_username  # Update the username in the dictionary

        # Check if the email has changed and validate it
        if new_email and new_email != account.email:
            if not validate_email(new_email):
                messagebox.showerror("Invalid Email", "Please enter a valid email address.")
                return
            updates["email"] = new_email

        # Check if the password has changed
        if new_password and new_password != account.password:
            updates["password"] = new_password

        # If no updates, show a message and return
        if len(updates) == 1:  # Only contains "username" (old one), meaning no updates
            messagebox.showinfo("No Changes", "No updates were made.")
            return

        # Apply updates (pass only the modified fields)
        updated_account = acc_manager.update_account(**updates)

        # If username was changed, update session
        if "username" in updates and updates["username"] != old_username:
            current_account["username"] = updates["username"]

        messagebox.showinfo("Success", "Account details updated successfully!")
        edit_window.destroy()


    tk.Button(edit_window, text="Save Changes", font=("Helvetica", 12), command=do_edit).grid(row=3, column=0, columnspan=2, pady=10)
    edit_window.wait_window()


def login(username: str, password: str) -> bool:
    account = acc_manager.get_account(username)
    if account is None:
        messagebox.showerror("Login Failed", "User does not exist. Please sign up.")
        return False
    elif account.password == password:
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        return True
    else:
        messagebox.showerror("Login Failed", "Password incorrect.")
        return False
def logout(current_account: dict, buttons: dict):
    if "username" in current_account:
        del current_account["username"]  # Remove the logged-in user
    buttons["in"][0].grid_remove()
    for btn in buttons["out"]:
        btn.grid()

    messagebox.showinfo("Logout Successful", "You have been logged out.")

def logout(current_account: dict, buttons: dict):
    if "username" in current_account:
        del current_account["username"]  # Remove the logged-in user
    buttons["in"][0].grid_remove()
    for btn in buttons["out"]:
        btn.grid()

    messagebox.showinfo("Logout Successful", "You have been logged out.")
    
def logout(current_account: dict, buttons: dict):
    """Logs out the current user and updates the UI."""
    if "username" in current_account:
        del current_account["username"]  # Remove the logged-in user
    
    # Hide logout button, show login & sign-up buttons
    buttons["in"][0].grid_remove()  
    for btn in buttons["out"]:
        btn.grid()
    
    messagebox.showinfo("Logout Successful", "You have been logged out.")


def sign_up(username: str, email: str, password: str) -> bool:
    if acc_manager.get_account(username) is not None:
        messagebox.showerror("Signup Failed", "Username already exists.")
        return False
    # Ensure no other account uses the same email.
    for acc in acc_manager.accounts:
        if acc.email == email:
            messagebox.showerror("Signup Failed", "Email already in use.")
            return False
    if not validate_email(email):
        messagebox.showerror("Invalid Email", "Please enter a valid email address.")
        return False
    new_id = max([acc.id for acc in acc_manager.accounts], default=0) + 1
    new_account = Account(username=username, password=password, email=email, id=new_id)
    acc_manager.add_account(new_account)
    messagebox.showinfo("Account Created", f"Account for {username} created successfully!")
    return True

def main():
    window = tk.Tk()
    window.title("Account Management")
    window.geometry("500x400")
    
    tk.Button(window, text="Login", font=("Helvetica", 12), command=lambda: open_login_window(window)).pack(pady=10)
    tk.Button(window, text="Sign Up", font=("Helvetica", 12), command=lambda: open_sign_up_window(window)).pack(pady=10)
    tk.Button(window, text="Edit Account", font=("Helvetica", 12), command=lambda: open_edit_account_window(window)).pack(pady=10)
    tk.Button(window, text="Exit", font=("Helvetica", 12), command=window.destroy).pack(pady=10)
    
    window.mainloop()

if __name__ == "__main__":
    main()
