import tkinter as tk
from Front_End.Account_Creation.AccountCreationFrontEnd import *
from Back_End.Account_Creation.Account import *

# Dictionary to store the currently logged-in user
current_account = {}

def main():
    window = tk.Tk()
    window.title("Sahar's Music Cataloging Software")
    window.geometry("1280x720")

    window.columnconfigure(0, weight=0)
    window.columnconfigure(1, weight=1)
    window.rowconfigure(1, weight=1)

    # Top frame
    top_frame = tk.Frame(window)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    top_frame.columnconfigure(0, weight=1)

    title_label = tk.Label(top_frame, text="Sahar's Music Cataloging Software", font=("Helvetica", 26, "bold"))
    title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    login_button = tk.Button(top_frame, text="Login", font=("Helvetica", 12),
                              command=lambda: open_login_window(window, current_account, buttons))
    login_button.grid(row=0, column=1, padx=5, pady=20)

    sign_up_button = tk.Button(top_frame, text="Sign Up", font=("Helvetica", 12),
                                command=lambda: open_sign_up_window(window, current_account, buttons))
    sign_up_button.grid(row=0, column=2, padx=5, pady=20)

    sign_up_button.config(command=lambda: open_sign_up_window(window, current_account, buttons))

    logout_button = tk.Button(top_frame, text="Logout", font=("Helvetica", 12),
                               command=lambda: logout(current_account, buttons))
    logout_button.grid(row=0, column=3, padx=5, pady=20)
    logout_button.grid_remove()

    buttons = {
        "in": [logout_button],
        "out": [login_button, sign_up_button]
    }

    # Sidebar
    left_side_panel = tk.Frame(window, bg="lightblue", width=200)
    left_side_panel.grid(row=1, column=0, sticky="ns")
    left_side_panel.grid_propagate(False)

    edit_acc_button = tk.Button(
        left_side_panel,
        text="Edit Account",
        font=("Arial", 12),
        bg="lightgray",
        command=lambda: open_edit_account_window(window, current_account)
    )
    edit_acc_button.pack(pady=10, padx=10)

    main_content = tk.Frame(window, bg="white")
    main_content.grid(row=1, column=1, sticky="nsew")

    window.mainloop()

if __name__ == "__main__":
    main()
