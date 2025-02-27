import os
import pandas as pd
# import csv

def load_users():
    """
    Load users from CSV into a pandas DataFrame.
    If the file doesn't exist, create an empty DataFrame with the required columns.
    """
    filename = "Back_End\\Account_Creation\\users.csv"
    if os.path.exists(filename):
        users_df = pd.read_csv(filename)
    else:
        users_df = pd.DataFrame(columns=["username", "password", "email"])
        users_df.to_csv(filename, index=False)
    return users_df.to_dict()

def save_users(users_df: dict):
    """Save the users DataFrame back to CSV."""
    filename = "Back_End\\Account_Creation\\users.csv"
    users_df = pd.DataFrame(users_df)
    users_df.to_csv(filename, index=False)

users_df = pd.DataFrame(load_users())

# Testing
print(users_df)
print(users_df.to_dict())
print(users_df.to_dict()["Username"])
print(users_df.to_dict()["Username"].values())






















# def check_login(users_df):
#     """
#     Check login credentials.
#     Prompts for username and password and returns a tuple (result, username) where:
#       - result is True if login is successful,
#       - False if password is incorrect,
#       - None if username is not found.
#     """
#     username = input("Enter username: ").strip()
#     password = input("Enter password: ").strip()
    
#     user_row = users_df[users_df["username"] == username]
#     if user_row.empty:
#         print("User does not exist.")
#         return None, username
#     else:
#         stored_password = user_row.iloc[0]["password"]
#         if stored_password == password:
#             print("Login successful!")
#             return True, username
#         else:
#             print("Password incorrect.")
#             return False, username

# def create_account(users_df, filename):
#     """
#     Creates a new account.
#     Prompts the user for a username, password, and email,
#     then appends the information to the DataFrame and saves it.
#     """
#     username = input("Enter new username: ").strip()
#     if username in users_df["username"].values:
#         print("User already exists!")
#         return users_df
#     password = input("Enter new password: ").strip()
#     email = input("Enter your email: ").strip()
    
#     new_user = pd.DataFrame({"username": [username], "password": [password], "email": [email]})
#     users_df = pd.concat([users_df, new_user], ignore_index=True)
#     save_users(users_df, filename)
#     print("Account created successfully!")
#     return users_df

# def edit_account(users_df, filename):
#     """
#     Edits an existing account by updating the email.
#     Prompts for the username and the new email, then updates the record.
#     """
#     username = input("Enter your username to update email: ").strip()
#     user_row = users_df[users_df["username"] == username]
#     if user_row.empty:
#         print("User does not exist.")
#         return users_df
#     new_email = input("Enter your new email: ").strip()
#     users_df.loc[users_df["username"] == username, "email"] = new_email
#     save_users(users_df, filename)
#     print("Email updated successfully!")
#     return users_df

# while True:
#     print("\nMenu:")
#     print("1. Login")
#     print("2. Sign Up")
#     print("3. Edit Account (Update Email)")
#     print("4. Exit")
#     choice = input("Choose an option: ").strip()
    
#     if choice == "1":
#         result, username = check_login(users_df)
#         if result is None:
#             print("User not found. Please sign up.")
#         elif result is True:
#             print(f"Welcome, {username}!")
#         # If login fails due to incorrect password, the user may try again.
        
#     elif choice == "2":
#         users_df = create_account(users_df, filename)
        
#     elif choice == "3":
#         users_df = edit_account(users_df, filename)
        
#     elif choice == "4":
#         print("Exiting program.")
#         break
#     else:
#         print("Invalid option, please try again.")