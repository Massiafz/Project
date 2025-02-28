# account_manager.py
import csv
import os
from dataclasses import dataclass, asdict

@dataclass
class Account:
    username: str
    password: str
    email: str
    id: int

    def __str__(self):
        return f"Account(username={self.username}, email={self.email}, id={self.id})"

class AccountManager:
    def __init__(self, filename="users.csv"):
        self.filename = filename
        self.accounts = self.load_accounts()

    def load_accounts(self):
        accounts = []
        if os.path.exists(self.filename):
            with open(self.filename, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Convert all keys to lowercase for consistency
                    row = {key.lower(): value for key, value in row.items()}

                    # Ensure ID is an integer
                    account_id = int(row["id"]) if row.get("id") and row["id"].isdigit() else self.get_next_id()

                    # Ensure row is converted into an Account object
                    account = Account(
                        username=row["username"].strip().lower(),
                        password=row["password"],
                        email=row["email"],
                        id=account_id
                    )
                    accounts.append(account)
        return accounts



    def save_accounts(self):
        with open(self.filename, "w", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["username", "password", "email", "id"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for account in self.accounts:
                if isinstance(account, Account):  # ✅ Ensure it's a dataclass instance
                    writer.writerow(asdict(account))
                else:
                    print(f"Warning: Skipping non-dataclass object {account}")


    def add_account(self, account: Account):
        if self.get_account(account.username):
            print(f"Account with username '{account.username}' already exists.")
            return False
        self.accounts.append(account)
        self.save_accounts()
        return True

    def update_account(self, **kwargs):
        """Update account details for a given username."""
        username = kwargs.get("username")  # Get the username to update
        acc = self.get_account(username)
        if not acc:
            print(f"Account with username '{username}' not found.")
            return None

        # Prevent duplicate usernames if changing
        if "username" in kwargs and kwargs["username"] != acc.username:
            if self.get_account(kwargs["username"]):
                print(f"Username '{kwargs['username']}' is already taken.")
                return None

        # Update attributes dynamically
        for key, value in kwargs.items():
            if hasattr(acc, key) and value:
                setattr(acc, key, value)

        # Save changes
        self.save_accounts()
        return acc


    def get_account(self, username: str):
        for acc in self.accounts:
            if acc.username == username:
                return acc
        return None

if __name__ == '__main__':
    manager = AccountManager("users.csv")
    
    # Example usage
    #THis is for testing
    # new_acc = Account(username="alice", password="secret123", email="alice@example.com", id=1)
    # if manager.add_account(new_acc):
    #     print("Account created:", new_acc)
    
    # updated_acc = manager.update_account("alice", email="alice.new@example.com")
    # if updated_acc:
    #     print("Updated account:", updated_acc)

    # acc = manager.get_account("alice")
    # if acc:
    #     print("Retrieved account:", acc)
