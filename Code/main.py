#necessary imports
import tkinter as tk 
from tkinter import messagebox  #for pop-up messages
from tkinter import ttk  #aesthetics
import csv  #to handle CSV file reading/writing
import json  #to handle JSON file reading/writing
import os  #for operating system file/path interactions
from PIL import Image, ImageTk #for album image editing
import re # for email regex

# Constant file names for persistent storage.
USERS_JSON = "./users.json"  #stores user login information after they create an account.
ALBUMS_CSV = "cleaned_music_data.csv"

PRIMARY_BACKGROUND_COLOUR = "#527cc5"
NAV_BAR_BACKGROUND_COLOUR = "#345db7"
NAV_BAR_SHADOW_1_COLOUR = "#244d97"
NAV_BAR_SHADOW_2_COLOUR = "#143d87"

# Main application class that manages the window and frames.
class AlbumCatalogApp(tk.Tk):  #inherits from tk.Tk. This is the main application window.
    def __init__(self):  #constructor
        # Initialize the Tk parent class to set up the base GUI window.
        super().__init__()  #ensure the parent class is initalized first. The parent class is tk.Tk.

        # Configure the main window title and dimensions.
        self.title("BrightByte Music Cataloging Software")  #title of the window
        self.geometry("1280x720")  #size of the window

        image = Image.open("BrightByteLogo.png")
        image = image.crop((0, 1080 * 0.25, 1080, 1080 * 0.75))
        image = image.resize((125, 75), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(image)
        self.iconphoto(True, self.image)
        
        nav_bar = tk.Frame(self, bg=NAV_BAR_BACKGROUND_COLOUR)
        nav_bar.pack(fill="x", side="top")

        shadow = tk.Frame(self, bg=NAV_BAR_SHADOW_1_COLOUR, height=5)
        shadow.pack(fill="x", side="top")

        shadow2 = tk.Frame(self, bg=NAV_BAR_SHADOW_2_COLOUR, height=5)
        shadow2.pack(fill="x", side="top")

        logo = tk.Label(nav_bar, image=self.image, bg=NAV_BAR_BACKGROUND_COLOUR)
        logo.pack(side="left", padx=15, pady=15)

        title = tk.Label(nav_bar, text="BrightByte Music Cataloging Software", font=("Helvetica", 22, "bold"), fg="white", bg=NAV_BAR_BACKGROUND_COLOUR)
        title.pack(anchor="w", padx=5, pady=40)
        
        # Initialize ttk style for a consistent and modern look.
        style = ttk.Style(self)
        style.theme_use("clam")  #set a modern theme for the GUI
        # Configure styling for different widget types.
        style.configure("TFrame", background=PRIMARY_BACKGROUND_COLOUR)
        style.configure("TLabel", background=PRIMARY_BACKGROUND_COLOUR, foreground="white", font=("Helvetica", 12, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TEntry", padding=5)
        
        # Load stored user account information from a JSON file.
        self.users = self.load_users()
        self.current_user = None  # This will store the username of the currently logged-in user.
        
        # Load album data from a CSV file into a list of dictionaries.
        self.albums = self.load_albums_from_csv()
        
        # Create a container frame to hold all the different pages (Login, Signup, Catalog).
        container = ttk.Frame(self)  #creates a frame to hold different pages (login, signup, catalog).
        container.pack(side="top", fill="both", expand=True)  #makes the frame take up all available space
        
        # Configure grid properties to allow dynamic resizing of the contained frames.
        container.grid_rowconfigure(0, weight=1)  #Allows the frames rows to expand and contract with the window.
        container.grid_columnconfigure(0, weight=1)  #Allows the frames columns to expand and contract with the window.
        
        # Dictionary to hold references to the different frames.
        self.frames = {}  #creates a dictionary to store frames. This allows us to switch between frames, without having to destroy and recreate them.
        
        # Iterate through each frame class to instantiate and store them in the frames dictionary.
        for F in (LoginFrame, SignupFrame, CatalogFrame):  #loops through our different frame classes.
            frame = F(parent=container, controller=self)  #creates an instance of the frame.
            #parent=container → Makes the frame part of the container frame (which holds all frames).
            #controller=self → Passes a reference to the main AlbumCatalogApp class, so frames can switch views.
            self.frames[F.__name__] = frame  #stores the frame in the frames dictionary. The key is the class name.
            
            frame.anchor("n")
            frame.grid(row=0, column=0, sticky="nsew", pady=35)
                
        # Set the initial frame to be the Login screen.
        self.show_frame("LoginFrame")  #Shows the first frame.
    
    # Reads user accounts from a JSON file. If the file does not exist or is invalid, an empty dictionary is returned.
    def load_users(self):
        if os.path.exists(USERS_JSON):
            with open(USERS_JSON, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    # Log error or fallback to empty user database.
                    return {}
        return {}

    # Saves the users dictionary to users.json.
    def save_users(self):
        with open(USERS_JSON, "w") as f:
            json.dump(self.users, f, indent=4)

    # Reads album data from the CSV file. It ensures the values do not contain whitespaces.
    # Returns a list of dictionaries where each one represents an album.
    # Only specific columns are selected from the CSV file. Other (irrelevant) information is not used and does not appear in the catalog.
    def load_albums_from_csv(self):
        albums = []
        if os.path.exists(ALBUMS_CSV):
            with open(ALBUMS_CSV, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # For each row, create a dictionary with only the desired keys.
                    album = {
                        "Ranking": row.get("Ranking", "").strip(),
                        "Album": row.get("Album", "").strip(),
                        "Artist Name": row.get("Artist Name", "").strip(),
                        "Release Date": row.get("Release Date", "").strip(),
                        "Genres": row.get("Genres", "").strip(),
                        "Average Rating": row.get("Average Rating", "").strip(),
                        "Number of Ratings": row.get("Number of Ratings", "").strip(),
                        "Number of Reviews": row.get("Number of Reviews", "").strip()
                    }
                    albums.append(album)
        else: 
            print("The file does not exist.")
        return albums
    
    # Retrieves the requested frame from the stored frames.
    # If the frame is CatalogFrame it refreshes the album list to ensure the latest data is displayed.
    # It raises the selected frame to the front, making it the active view.
    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        # Special refresh logic for the catalog view to update album list contents.
        if frame_name == "CatalogFrame":
            frame.refresh_album_list()
        # Bring the selected frame to the top.
        frame.tkraise()


# This class produces the login frame. It allows users to enter their username and password.
# It also has a button to switch to the sign up frame.
# When the login button is clicked, the entered username and password are checked against the stored user accounts.
# If the login is successful, the user is taken to the catalog frame.
# If the login fails, an error message is displayed.
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller  # Keep reference to the main application controller.
        # self.configure(padding=20)  # Add padding around the frame for aesthetics.
        
        # Header label for the login form.
        header = ttk.Label(self, text="Login", style="Header.TLabel")
        header.grid(row=1, column=0, columnspan=2, pady=(0,15))
        
        # Username label and entry field.
        ttk.Label(self, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Password label and entry field (with masked input).
        ttk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Button to trigger login functionality.
        login_btn = ttk.Button(self, text="Login", command=self.login)
        login_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Button to switch to the sign-up frame.
        switch_btn = ttk.Button(self, text="Sign Up", command=lambda: controller.show_frame("SignupFrame"))
        switch_btn.grid(row=5, column=0, columnspan=2, pady=5)
    
    def login(self):
        # Retrieve input from entry fields.
        username = self.username_entry.get()
        password = self.password_entry.get()
        users = self.controller.users  # Reference to loaded user data.
        
        # Check if the username exists and the password matches.
        if username in users and users[username]["password"] == password:
            self.controller.current_user = username  # Set the current user.
            messagebox.showinfo("Login", "Login successful!")
            self.controller.show_frame("CatalogFrame")  # Switch to the catalog frame.
            # Clear the entry fields after successful login.
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid username or password.")


# This class produces the sign up frame. It allows users to create a new account by entering a username and password.
# When the create account button is clicked, the entered username and password are checked for validity.
# If the username already exists, an error message is displayed.
# If the passwords do not match, an error message is displayed.
# If the username or password fields are empty, an error message is displayed.
# If the account is created successfully, the user is taken to the login frame.
class SignupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller  # Reference to the main application controller.
        # self.configure(padding=20)
        
        # Header label for the sign up form.
        header = ttk.Label(self, text="Sign Up", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, pady=(0,15))
        
        # Username label and entry field.
        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Email label and entry field.
        ttk.Label(self, text="Email:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Password label and entry field.
        ttk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Confirm password label and entry field.
        ttk.Label(self, text="Confirm Password:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.confirm_password_entry = ttk.Entry(self, show="*")
        self.confirm_password_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Button to trigger account creation.
        create_btn = ttk.Button(self, text="Create Account", command=self.signup)
        create_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Button to go back to the login frame.
        back_btn = ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginFrame"))
        back_btn.grid(row=6, column=0, columnspan=2, pady=5)
    
    def signup(self):
        # Retrieve input values for new account creation.
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Check if username, email, and password fields are non-empty.
        if not username or not password or not email:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        # Check if the username already exists.
        if username in self.controller.users:
            messagebox.showerror("Error", "Username already exists.")
            return

        # Check if both password entries match.
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Check if the email is proper or valid.
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is None:
            messagebox.showerror("Error", "Email is invalid.")
            return

        # Create new user account and save to the persistent JSON file.
        self.controller.users[username] = {"email": email, "password": password}
        self.controller.save_users()
        messagebox.showinfo("Sign Up", "Account created successfully!")
        # Redirect user back to the login frame.
        self.controller.show_frame("LoginFrame")
        # Clear the entry fields.
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)



# This class produces the catalog frame. It displays a list of albums with their artist name, album name, genres, and release date.
# It has buttons to add, edit, and delete albums.
# It also has a button to edit the current user's account.
# When the logout button is clicked, the user is logged out and taken to the login frame.
class CatalogFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller  # Reference to the main application controller.
        # self.configure(padding=20)
        
        # Configure grid properties to allow the album list to expand with the window.
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header label for the catalog view.
        header = tk.Label(self, text="Album Catalog", font=("Helvetica", 18, "bold"), fg="white", bg=PRIMARY_BACKGROUND_COLOUR)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Create a sub-frame for the album list and its scrollbar.
        # self.list_frame.grid_rowconfigure(0, weight=1)
        # self.list_frame.grid_columnconfigure(0, weight=1)

        self.selected_album = None
        self.album_items = []
        self.album_cover_images = []
        
        # Create a listbox to display album information.
        # self.album_listbox = tk.Listbox(None, width=80, height=10, font=("Helvetica", 10)) # self.list_frame
        # self.album_listbox.pack(side="left", fill="both", expand=True)
        
        canvas = tk.Canvas(self, bg=NAV_BAR_SHADOW_1_COLOUR)
        canvas.grid(row=1, column=0, sticky="nsew")
        
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.list_frame = tk.Frame(canvas, bg=NAV_BAR_SHADOW_1_COLOUR)
        self.list_frame.anchor("n")
        self.list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfig(window, width=event.width))
        
        window = canvas.create_window((canvas.winfo_width() // 2, 0), window=self.list_frame, anchor="n")
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    
        # self.album_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons for album actions (Add, Edit, Delete) and account editing/logging out.
        buttonFrame = tk.Frame(self, bg=PRIMARY_BACKGROUND_COLOUR)
        buttonFrame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        buttonFrame.anchor("center")

        add_btn = ttk.Button(buttonFrame, text="Add Album", command=self.add_album)
        add_btn.grid(row=0, column=0, padx=5, pady=10)
        
        edit_album_btn = ttk.Button(buttonFrame, text="Edit Album", command=self.edit_album)
        edit_album_btn.grid(row=0, column=1, padx=5, pady=10)
        
        delete_btn = ttk.Button(buttonFrame, text="Delete Album", command=self.delete_album)
        delete_btn.grid(row=0, column=2, padx=5, pady=10)
        
        edit_account_btn = ttk.Button(buttonFrame, text="Edit Account", command=self.edit_account)
        edit_account_btn.grid(row=0, column=3, padx=5, pady=10)
        
        logout_btn = ttk.Button(buttonFrame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=4, padx=5, pady=10)
    
    # Refreshes the album list display to show the current album data.
    def refresh_album_list(self):
        # Clear current list contents.
        # self.album_listbox.delete(0, tk.END)
        # # Loop through each album and format its display string.
        # for idx, album in enumerate(self.controller.albums):
        #     album_info = (f"{idx+1}. Artist Name: {album.get('Artist Name', '')} | "
        #                   f"Album: {album.get('Album', '')} | "
        #                   f"Genres: {album.get('Genres', '')} | "
        #                   f"Release Date: {album.get('Release Date', '')}")
        #     self.album_listbox.insert(tk.END, album_info)
        
        for existingAlbumItem in self.album_items:
            existingAlbumItem.destroy()
        
        self.album_items.clear()
        self.album_cover_images.clear()
        self.selected_album = None

        currentRow = 0
        for index, album in enumerate(self.controller.albums):
            if index > 100:
                break

            albumName = album.get("Album")
            artistName = album.get("Artist Name")
            genres = album.get("Genres")
            releaseDate = album.get("Release Date")

            albumItem = tk.Frame(self.list_frame, bg=NAV_BAR_SHADOW_2_COLOUR)
            albumItem.grid(row=currentRow, column=0, padx=15, pady=15)
            albumItem.grid_propagate(False)
            
            albumCover = Image.open("Eric.png")
            albumCover = albumCover.resize((150, 150), Image.LANCZOS)
            albumCover = ImageTk.PhotoImage(image=albumCover)
            
            coverLabel = tk.Label(albumItem, image=albumCover, bg="white")
            coverLabel.pack(side="left")

            labelFrame = tk.Frame(albumItem, name="labelFrame", bg=NAV_BAR_SHADOW_2_COLOUR, width=400, height=100)
            labelFrame.pack(fill="both", side="left", padx=(15, 15), pady=(30, 0))
            labelFrame.pack_propagate(False)

            albumNameLabel = tk.Label(labelFrame, name="albumNameLabel", text=albumName, bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica", 12, "bold"), anchor="w")
            albumNameLabel.pack(fill="x")

            artistNameLabel = tk.Label(labelFrame, name="artistNameLabel", text=f"By: {artistName}", bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica", 10, "bold"), anchor="w")
            artistNameLabel.pack(fill="x")

            genresLabel = tk.Label(labelFrame, name="genresLabel", text=f"Genres: {genres}", bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica", 10, "bold"), anchor="w")
            genresLabel.pack(fill="x")

            releaseDateLabel = tk.Label(labelFrame, name="releaseDateLabel", text=f"Released: {releaseDate}", bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica", 10, "bold"), anchor="w")
            releaseDateLabel.pack(fill="x")

            self.album_items.append(albumItem)
            self.album_cover_images.append(albumCover)

            for thing in [albumItem, labelFrame, albumNameLabel, artistNameLabel, genresLabel, releaseDateLabel, coverLabel]:
                thing.bind("<Button-1>", lambda event, item=albumItem: self.select_album(event, item))

            currentRow += 1
            
    def select_album(self, event, albumItem: tk.Frame):
        for item in self.album_items:
            item.config(bg=NAV_BAR_SHADOW_2_COLOUR)
            item.nametowidget("labelFrame").config(bg=NAV_BAR_SHADOW_2_COLOUR)

            for widgetName in ["albumNameLabel", "artistNameLabel", "genresLabel", "releaseDateLabel"]:
                item.nametowidget("labelFrame").nametowidget(widgetName).config(bg=NAV_BAR_SHADOW_2_COLOUR)
                

        albumItem.config(bg=PRIMARY_BACKGROUND_COLOUR)
        albumItem.nametowidget("labelFrame").config(bg=PRIMARY_BACKGROUND_COLOUR)

        for widgetName in ["albumNameLabel", "artistNameLabel", "genresLabel", "releaseDateLabel"]:
            albumItem.nametowidget("labelFrame").nametowidget(widgetName).config(bg=PRIMARY_BACKGROUND_COLOUR)
        
        self.selected_album = albumItem
    
    # Opens a new window to add a new album to the catalog.
    def add_album(self):
        # Create a top-level window that will behave like a modal dialog.
        add_win = tk.Toplevel(self)
        add_win.title("Add Album")
        add_win.configure(background="#f0f0f0")
        add_win.grab_set()  # Prevents user interaction with the main window while open.
        
        # Create and place labels and entry fields for album details.
        ttk.Label(add_win, text="Artist Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        artist_entry = ttk.Entry(add_win)
        artist_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Album:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        album_entry = ttk.Entry(add_win)
        album_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Release Date:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        release_entry = ttk.Entry(add_win)
        release_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Genres:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        genres_entry = ttk.Entry(add_win)
        genres_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Internal function to save the new album when the button is clicked.
        def save_album():
            artist = artist_entry.get().strip()
            album_name = album_entry.get().strip()
            release_date = release_entry.get().strip()
            genres = genres_entry.get().strip()
            # Validate that required fields are not empty.
            if not artist or not album_name or not release_date:
                messagebox.showerror("Error", "Artist Name, Album, and Release Date are required.")
                return
            # Create a new album dictionary from the provided data.
            new_album = {
                "Artist Name": artist,
                "Album": album_name,
                "Release Date": release_date,
                "Genres": genres
            }
            # Append the new album to the album list in the controller.
            self.controller.albums.append(new_album)
            # Refresh the displayed album list.
            self.refresh_album_list()
            # Close the add album window.
            add_win.destroy()
        
        # Button to trigger saving of the new album.
        ttk.Button(add_win, text="Save Album", command=save_album).grid(row=4, column=0, columnspan=2, pady=10)
    
    # Opens a new window to edit the selected album's details.
    def edit_album(self):
        if not self.selected_album:
            messagebox.showerror("Error", "Please select an album to edit.")
            return
        index = self.album_items.index(self.selected_album)  # Get the index of the selected album.
        album = self.controller.albums[index]
        
        # Create a modal dialog for editing album details.
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Album")
        edit_win.configure(background="#f0f0f0")
        edit_win.grab_set()
        
        # Populate fields with current album details.
        ttk.Label(edit_win, text="Artist Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        artist_entry = ttk.Entry(edit_win)
        artist_entry.insert(0, album.get("Artist Name", ""))
        artist_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Album:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        album_entry = ttk.Entry(edit_win)
        album_entry.insert(0, album.get("Album", ""))
        album_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Release Date:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        release_entry = ttk.Entry(edit_win)
        release_entry.insert(0, album.get("Release Date", ""))
        release_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Genres:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        genres_entry = ttk.Entry(edit_win)
        genres_entry.insert(0, album.get("Genres", ""))
        genres_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Internal function to update album details based on user input.
        def update_album():
            updated_artist = artist_entry.get().strip()
            updated_album = album_entry.get().strip()
            updated_release = release_entry.get().strip()
            updated_genres = genres_entry.get().strip()
            # Validate required fields.
            if not updated_artist or not updated_album or not updated_release:
                messagebox.showerror("Error", "Artist Name, Album, and Release Date are required.")
                return
            # Update the album information in the controller's album list.
            self.controller.albums[index] = {
                "Artist Name": updated_artist,
                "Album": updated_album,
                "Release Date": updated_release,
                "Genres": updated_genres
            }
            # Refresh the album list display.
            self.refresh_album_list()
            # Close the edit window.
            edit_win.destroy()
        
        # Button to trigger the album update.
        ttk.Button(edit_win, text="Update Album", command=update_album).grid(row=4, column=0, columnspan=2, pady=10)
    
    # Deletes the selected album after confirmation.
    def delete_album(self):
        if not self.selected_album:
            messagebox.showerror("Error", "Please select an album to delete.")
            return
        index = self.album_items.index(self.selected_album)
        # Ask the user to confirm deletion.
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected album?")
        if confirm:
            # Remove the album from the list and refresh the display.
            del self.controller.albums[index]
            self.refresh_album_list()
    
    # Opens a new window to allow the user to update their account information.
    def edit_account(self):
        current_user = self.controller.current_user
        if not current_user:
            messagebox.showerror("Error", "No user is logged in.")
            return
        
        # Create a modal dialog for account editing.
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Account")
        edit_win.configure(background="#f0f0f0")
        edit_win.grab_set()
        
        # Field to verify the current password before allowing any changes.
        ttk.Label(edit_win, text="Current Password:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        current_pass_entry = ttk.Entry(edit_win, show="*")
        current_pass_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # New username field (optional).
        ttk.Label(edit_win, text="New Username:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        new_username_entry = ttk.Entry(edit_win)
        new_username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # New password field.
        ttk.Label(edit_win, text="New Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        new_pass_entry = ttk.Entry(edit_win, show="*")
        new_pass_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Confirm new password field.
        ttk.Label(edit_win, text="Confirm New Password:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        confirm_new_pass_entry = ttk.Entry(edit_win, show="*")
        confirm_new_pass_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Internal function to update account information after validating inputs.
        def update_account():
            current_pass = current_pass_entry.get()
            new_username = new_username_entry.get().strip()
            new_pass = new_pass_entry.get()
            confirm_new_pass = confirm_new_pass_entry.get()
            
            # Verify the current password is correct.
            if self.controller.users[current_user]["password"] != current_pass:
                messagebox.showerror("Error", "Current password is incorrect.")
                return
            
            # Update username if a new one is provided and is different.
            updated_username = current_user
            if new_username and new_username != current_user:
                # Check if the new username is already in use.
                if new_username in self.controller.users:
                    messagebox.showerror("Error", "Username already exists.")
                    return
                # Transfer the user's data to the new username.
                user_info = self.controller.users.pop(current_user)
                self.controller.users[new_username] = user_info
                updated_username = new_username
                self.controller.current_user = new_username
            
            # Update password if new password fields are provided.
            if new_pass or confirm_new_pass:
                if new_pass != confirm_new_pass:
                    messagebox.showerror("Error", "New passwords do not match.")
                    return
                if not new_pass:
                    messagebox.showerror("Error", "New password cannot be empty.")
                    return
                self.controller.users[updated_username]["password"] = new_pass
            
            # Save the updated user information to persistent storage.
            self.controller.save_users()
            messagebox.showinfo("Success", "Account updated successfully!")
            # Close the account editing window.
            edit_win.destroy()
        
        # Button to trigger the account update process.
        ttk.Button(edit_win, text="Update Account", command=update_account).grid(row=4, column=0, columnspan=2, pady=10)
    
    # Logs out the current user and returns to the login frame.
    def logout(self):
        self.controller.current_user = None  # Reset current user.
        messagebox.showinfo("Logout", "You have been logged out.")
        self.controller.show_frame("LoginFrame")

# Entry point of the application.
if __name__ == "__main__":
    app = AlbumCatalogApp()  # Instantiate the main application window.
    app.mainloop()  # Start the Tkinter event loop to listen for user events.
