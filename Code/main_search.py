# ---------------------------------------------------------------------------
# Import necessary modules and libraries
# ---------------------------------------------------------------------------
import tkinter as tk                      # Tkinter: Python's standard GUI toolkit for building graphical interfaces.
from tkinter import messagebox            # For displaying pop-up messages (information, warnings, errors).
from tkinter import ttk                   # For themed widgets that provide a modern look and feel.
from tkinter import filedialog
import csv                                # To handle reading from and writing to CSV files (used for album data).
import json                               # To handle reading from and writing to JSON files (used for user account data).
import os                                 # For interacting with the operating system.
from PIL import Image, ImageTk            # Pillow for image processing.
import re                                 # For regular expression operations.
from urllib.request import urlopen, Request # For making HTTP requests.
import io                                 # For I/O operations.
import threading

# ---------------------------------------------------------------------------
# Define constants for file paths and theme colours
# ---------------------------------------------------------------------------
USERS_JSON = "users.json"               # JSON file that stores user login information.
ALBUMS_CSV = "cleaned_music_data.csv"       # CSV file containing album catalog data.

# Define colour constants for UI consistency
PRIMARY_BACKGROUND_COLOUR = "#527cc5"       # Primary background colour for the app.
NAV_BAR_BACKGROUND_COLOUR = "#345db7"         # Background colour for the navigation bar.
NAV_BAR_SHADOW_1_COLOUR = "#244d97"           # First shadow colour below the navigation bar.
NAV_BAR_SHADOW_2_COLOUR = "#143d87"           # Second shadow colour below the navigation bar.

# Precompile URL pattern regex once for efficiency.
URL_PATTERN = re.compile(
    r'^(https?|ftp):\/\/'  
    r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z]{2,6}'
    r'\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$'
)

# ---------------------------------------------------------------------------
# Main Application Class: AlbumCatalogApp
# ---------------------------------------------------------------------------
class AlbumCatalogApp(tk.Tk):
    """
    Main application class inheriting from Tk.
    Sets up the main window, configures styling, loads user and album data,
    and manages the different pages (Login, Signup, Catalog).
    """
    def __init__(self):
        super().__init__()
        
        self.title("BrightByte Music Cataloging Software")
        self.geometry("1280x720")
        
        # -----------------------------------------------------------------------
        # Load and set the window icon/logo.
        # -----------------------------------------------------------------------
        image = Image.open("BrightByteLogo.png")
        image = image.crop((0, 1080 * 0.25, 1080, 1080 * 0.75))
        image = image.resize((125, 75), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(image)
        self.iconphoto(True, self.image)
        
        # -----------------------------------------------------------------------
        # Create the navigation bar.
        # -----------------------------------------------------------------------
        nav_bar = tk.Frame(self, bg=NAV_BAR_BACKGROUND_COLOUR)
        nav_bar.pack(fill="x", side="top")
        
        shadow = tk.Frame(self, bg=NAV_BAR_SHADOW_1_COLOUR, height=5)
        shadow.pack(fill="x", side="top")
        shadow2 = tk.Frame(self, bg=NAV_BAR_SHADOW_2_COLOUR, height=5)
        shadow2.pack(fill="x", side="top")
        
        logo = tk.Label(nav_bar, image=self.image, bg=NAV_BAR_BACKGROUND_COLOUR)
        logo.pack(side="left", padx=15, pady=15)
        
        title = tk.Label(
            nav_bar,
            text="BrightByte Music Cataloging Software",
            font=("Helvetica", 22, "bold"),
            fg="white",
            bg=NAV_BAR_BACKGROUND_COLOUR
        )
        title.pack(anchor="w", padx=5, pady=40)
        
        # -----------------------------------------------------------------------
        # Set up search widgets (search bar, button, and filter dropdown).
        # -----------------------------------------------------------------------
        self.search_button = tk.Button(nav_bar, text="Search", command=self.search)
        self.search_button.pack_forget()
        
        self.search_bar = tk.Text(nav_bar, font=("Calibri",12), height=1, width=50)
        self.search_bar.pack_forget()
        # Bind the Enter/Return key to trigger search.
        self.search_bar.bind("<Return>", self.on_enter_pressed)
        
        # Dropdown for search filters (removed "All" option; default is "Album Name").
        self.search_filter = tk.StringVar(value="Album Name")
        self.filter_dropdown = ttk.Combobox(
            nav_bar,
            textvariable=self.search_filter,
            values=["Album Name", "Artist Name", "Genres", "Release Date"],
            state="readonly",
            width=15
        )
        self.filter_dropdown.pack_forget()
        
        # -----------------------------------------------------------------------
        # Set up ttk styling.
        # -----------------------------------------------------------------------
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=PRIMARY_BACKGROUND_COLOUR)
        style.configure("TLabel", background=PRIMARY_BACKGROUND_COLOUR, foreground="white", font=("Helvetica", 12, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TEntry", padding=5)
        
        # -----------------------------------------------------------------------
        # Load persistent data: users and albums.
        # -----------------------------------------------------------------------
        self.users = self.load_users()
        self.current_user = None
        self.search_results = None
        self.albums = self.load_albums_from_csv()
        
        # -----------------------------------------------------------------------
        # Create container for pages.
        # -----------------------------------------------------------------------
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (LoginFrame, SignupFrame, CatalogFrame):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.anchor("n")
            frame.grid(row=0, column=0, sticky="nsew", pady=35)
                
        self.show_frame("LoginFrame")
    
    def on_enter_pressed(self, event):
        """Called when the Return key is pressed in the search bar."""
        self.search()  # Trigger the search function.
        return "break"  # Prevent insertion of a newline.
    
    def load_users(self):
        if os.path.exists(USERS_JSON):
            with open(USERS_JSON, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}
    
    def save_users(self):
        with open(USERS_JSON, "w") as f:
            json.dump(self.users, f, indent=4)
    
    def save_albums(self):
        with open(ALBUMS_CSV, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, ["Ranking","Album","Artist Name","Release Date","Genres","Average Rating","Number of Ratings","Number of Reviews","Cover URL"])
            writer.writeheader()
            for album in self.albums:
                writer.writerow({
                    "Ranking": album["Ranking"],
                    "Album": album["Album"],
                    "Artist Name": album["Artist Name"],
                    "Release Date": album["Release Date"],
                    "Genres": album["Genres"],
                    "Average Rating": album["Average Rating"],
                    "Number of Ratings": album["Number of Ratings"],
                    "Number of Reviews": album["Number of Reviews"],
                    "Cover URL": album["Cover URL"]
                })
    
    def load_albums_from_csv(self):
        albums = []
        if os.path.exists(ALBUMS_CSV):
            with open(ALBUMS_CSV, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    album = {
                        "Ranking": row.get("Ranking", "").strip(),
                        "Album": row.get("Album", "").strip(),
                        "Artist Name": row.get("Artist Name", "").strip(),
                        "Release Date": row.get("Release Date", "").strip(),
                        "Genres": row.get("Genres", "").strip(),
                        "Average Rating": row.get("Average Rating", "").strip(),
                        "Number of Ratings": row.get("Number of Ratings", "").strip(),
                        "Number of Reviews": row.get("Number of Reviews", "").strip(),
                        "Cover URL": row.get("Cover URL", "").strip()
                    }
                    albums.append(album)
        else:
            print("The file does not exist.")
        return albums
    
    def load_search_query(self, search_query):
        """
        Filters albums based on the search query and selected filter.
        """
        self.search_results = []
        search_query = search_query.lower().strip() if search_query else None
        selected_filter = self.search_filter.get()
        
        def matches_filter(album):
            if search_query is None:
                return True
            if selected_filter == "Album Name":
                return search_query in album.get("Album", "").lower()
            if selected_filter == "Artist Name":
                return search_query in album.get("Artist Name", "").lower()
            if selected_filter == "Genres":
                return search_query in album.get("Genres", "").lower()
            if selected_filter == "Release Date":
                # Check if search query is present in any part of the release date split by "-"
                return search_query in album.get("Release Date", "").split("-")
            return False
        
        self.search_results = list(filter(matches_filter, self.albums.copy()))
    
    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        if frame_name == "CatalogFrame":
            self.filter_dropdown.pack(side="right", padx=10)  # Show the filter dropdown
            frame.refresh_album_list()  # Refresh the album catalog
        else:
            self.filter_dropdown.pack_forget()  # Hide the filter dropdown
        frame.tkraise()
    
    def search(self, no_refresh=False):
        query = self.search_bar.get("1.0", tk.END)
        self.load_search_query(query)
        if query.strip() and not self.search_results:
            messagebox.showerror("No Results", "No relevant results found for your search query.")
        frame = self.frames["CatalogFrame"]
        if not no_refresh:
            frame.refresh_album_list()
        frame.tkraise()
    
    def refresh_catalog(self):
        self.search_bar.delete("1.0", tk.END)
        self.search("")

# ---------------------------------------------------------------------------
# LoginFrame: The login page that allows users to sign in or continue as a guest.
# ---------------------------------------------------------------------------
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller
        
        header = ttk.Label(self, text="Login", style="Header.TLabel")
        header.grid(row=1, column=0, columnspan=2, pady=(0,15))
        
        ttk.Label(self, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        login_btn = ttk.Button(self, text="Login", command=self.login)
        login_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        switch_btn = ttk.Button(self, text="Sign Up", command=lambda: controller.show_frame("SignupFrame"))
        switch_btn.grid(row=5, column=0, columnspan=2, pady=5)
        
        guest_btn = ttk.Button(self, text="Continue as Guest", command=self.continue_as_guest)
        guest_btn.grid(row=6, column=0, columnspan=2, pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        users = self.controller.users
        
        if username in users and users[username]["password"] == password:
            self.controller.current_user = username
            messagebox.showinfo("Login", "Login successful!")
            # Show search widgets and refresh button upon login.
            self.controller.search_button.pack(side="right", padx=10)
            self.controller.search_bar.pack(side="right")
            self.controller.filter_dropdown.pack(side="right", padx=10)
            self.controller.frames["CatalogFrame"].refresh_button.grid()
            self.controller.show_frame("CatalogFrame")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid username or password.")
    
    def continue_as_guest(self):
        self.controller.current_user = "Guest"
        messagebox.showinfo("Guest Login", "Continuing as guest.")
        self.controller.search_button.pack(side="right", padx=10)
        self.controller.search_bar.pack(side="right")
        self.controller.filter_dropdown.pack(side="right", padx=10)
        self.controller.frames["CatalogFrame"].refresh_button.grid()
        self.controller.show_frame("CatalogFrame")

# ---------------------------------------------------------------------------
# SignupFrame: The sign-up page for creating a new user account.
# ---------------------------------------------------------------------------
class SignupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller
        
        header = ttk.Label(self, text="Sign Up", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, pady=(0,15))
        
        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self, text="Email:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self, text="Confirm Password:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.confirm_password_entry = ttk.Entry(self, show="*")
        self.confirm_password_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        create_btn = ttk.Button(self, text="Create Account", command=self.signup)
        create_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        back_btn = ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginFrame"))
        back_btn.grid(row=6, column=0, columnspan=2, pady=5)
    
    def signup(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not username or not password or not email:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return
        
        if username in self.controller.users:
            messagebox.showerror("Error", "Username already exists.")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is None:
            messagebox.showerror("Error", "Email is invalid.")
            return
        
        self.controller.users[username] = {"email": email, "password": password}
        self.controller.save_users()
        messagebox.showinfo("Sign Up", "Account created successfully!")
        self.controller.show_frame("LoginFrame")
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)

# ---------------------------------------------------------------------------
# CatalogFrame: Displays the list of albums and provides album management options.
# ---------------------------------------------------------------------------
class CatalogFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller
        
        # Initialize a cache to store loaded album cover images.
        self.album_cover_cache = {}
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header = tk.Label(self, text="Album Catalog", font=("Helvetica", 18, "bold"), fg="white", bg=PRIMARY_BACKGROUND_COLOUR)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        canvas = tk.Canvas(self, bg=NAV_BAR_SHADOW_1_COLOUR)
        canvas.grid(row=1, column=0, sticky="nsew")
        
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.list_frame = tk.Frame(canvas, bg=NAV_BAR_SHADOW_1_COLOUR)
        self.list_frame.anchor("n")
        self.list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window = canvas.create_window((canvas.winfo_width() // 2, 0), window=self.list_frame, anchor="n")
        canvas.bind("<Configure>", lambda event: canvas.itemconfig(window, width=event.width))
        # Bind mouse wheel events for both Windows/macOS and Linux.
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        canvas.bind("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
    
        self.selected_album = None
        self.album_items = []
        self.album_cover_images = []
        
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
        
        self.refresh_button = ttk.Button(buttonFrame, text="Refresh", command=self.controller.refresh_catalog)
        self.refresh_button.grid(row=0, column=5, padx=5, pady=10)
        self.refresh_button.grid_remove()
    
    def thread_function_refresh_albums(self, index, album, currentRow):
        albumName = album.get("Album")
        artistName = album.get("Artist Name")
        genres = album.get("Genres")
        releaseDate = album.get("Release Date")
        
        albumItem = tk.Frame(self.list_frame, bg=NAV_BAR_SHADOW_2_COLOUR)
        albumItem.grid(row=currentRow, column=0, padx=15, pady=15)
        albumItem.grid_propagate(False)
        
        albumCover = Image.open("Eric.png")
        albumURL = album.get("Cover URL")

        url_pattern = re.compile(
            r'^(https?|ftp):\/\/'  # Match 'http://', 'https://', or 'ftp://'
            r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z]{2,6}'  # Domain name
            r'\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$'  # Additional URL components
        )

        if not url_pattern.match(albumURL) and albumURL != "" and albumURL != None:
            albumCover = Image.open(albumURL)
        
        elif albumURL != "" and albumURL != None:
            try:
                req = Request(albumURL, headers={"User-Agent": "Mozilla/5.0"})
                
                response = urlopen(req)

                albumCoverData = response.read()
                albumCover = Image.open(io.BytesIO(albumCoverData))
            
            except Exception as e:
                print(f"Failed to load album cover: {e}")

        albumCover = albumCover.resize((150, 150), Image.LANCZOS)
        albumCover = ImageTk.PhotoImage(image=albumCover)
        
        coverLabel = tk.Label(albumItem, image=albumCover, bg="white")
        coverLabel.pack(side="left")
        
        labelFrame = tk.Frame(albumItem, name="labelFrame", bg=NAV_BAR_SHADOW_2_COLOUR, width=400, height=100)
        labelFrame.pack(fill="both", side="left", padx=(15,15), pady=(30,0))
        labelFrame.pack_propagate(False)
        
        albumNameLabel = tk.Label(labelFrame, name="albumNameLabel", text=albumName, bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica",12,"bold"), anchor="w")
        albumNameLabel.pack(fill="x")
        
        artistNameLabel = tk.Label(labelFrame, name="artistNameLabel", text=f"By: {artistName}", bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica",10,"bold"), anchor="w")
        artistNameLabel.pack(fill="x")
        
        genresLabel = tk.Label(labelFrame, name="genresLabel", text=f"Genres: {genres}", bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica",10,"bold"), anchor="w")
        genresLabel.pack(fill="x")
        
        releaseDateLabel = tk.Label(labelFrame, name="releaseDateLabel", text=f"Released: {releaseDate}", bg=NAV_BAR_SHADOW_2_COLOUR, fg="white", font=("Helvetica",10,"bold"), anchor="w")
        releaseDateLabel.pack(fill="x")
        
        self.album_items[index] = albumItem
        self.album_cover_images[index] = albumCover
        
        for widget in [albumItem, labelFrame, albumNameLabel, artistNameLabel, genresLabel, releaseDateLabel, coverLabel]:
            widget.bind("<Button-1>", lambda event, item=albumItem: self.select_album(event, item))
    
    def refresh_album_list(self):
        self.refresh_album_threads = []
        for existingAlbumItem in self.album_items:
            if existingAlbumItem is not None:
                existingAlbumItem.destroy()
        self.album_items = []
        if self.controller.search_results is not None:
            album_arr_to_use = self.controller.search_results
        else:
            album_arr_to_use = self.controller.albums
        for i in range(len(album_arr_to_use)):
            self.album_items.append(None)
        self.album_cover_images = [None] * len(album_arr_to_use)
        self.selected_album = None
        currentRow = 0
        for index, album in enumerate(album_arr_to_use):
            thread = threading.Thread(target=self.thread_function_refresh_albums, args=(index, album, currentRow), daemon=True)
            self.refresh_album_threads.append(thread)
            currentRow += 1
        for thread in self.refresh_album_threads:
            thread.start()
    
    def select_album(self, event, albumItem: tk.Frame):
        for item in self.album_items:
            if item is not None:
                item.config(bg=NAV_BAR_SHADOW_2_COLOUR)
                item.nametowidget("labelFrame").config(bg=NAV_BAR_SHADOW_2_COLOUR)
                for widgetName in ["albumNameLabel", "artistNameLabel", "genresLabel", "releaseDateLabel"]:
                    item.nametowidget("labelFrame").nametowidget(widgetName).config(bg=NAV_BAR_SHADOW_2_COLOUR)
        albumItem.config(bg=PRIMARY_BACKGROUND_COLOUR)
        albumItem.nametowidget("labelFrame").config(bg=PRIMARY_BACKGROUND_COLOUR)
        for widgetName in ["albumNameLabel", "artistNameLabel", "genresLabel", "releaseDateLabel"]:
            albumItem.nametowidget("labelFrame").nametowidget(widgetName).config(bg=PRIMARY_BACKGROUND_COLOUR)
        self.selected_album = albumItem
    
    def add_album(self):
        add_win = tk.Toplevel(self)
        add_win.title("Add Album")
        add_win.configure(background="#f0f0f0")
        add_win.grab_set()
        
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

        self.current_file_path = ""
        def open_filedialog_album_cover():
            self.current_file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("Image Files", ["*.png","*.jpg","*.jpeg","*.gif"]), ("All Files", "*.*")], initialdir="./album_covers")
            if self.current_file_path:
                self.current_file_path = os.path.relpath(self.current_file_path, start=os.getcwd())
                file_label.config(text=f"Selected file: {self.current_file_path}")
            else:
                file_label.config(text="No file selected.")

        ttk.Label(add_win, text="Album Cover:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        album_url_entry = ttk.Entry(add_win)
        album_url_entry.grid(row=4, column=1, padx=5, pady=5)
        album_image_entry = ttk.Button(add_win, text="Import File", command=open_filedialog_album_cover)
        album_image_entry.grid(row=4, column=2, padx=5, pady=5)
        file_label = tk.Label(add_win, text="No file selected.")
        file_label.grid(row=4, column=3, padx=5, pady=5)
        
        def save_album():
            artist = artist_entry.get().strip()
            album_name = album_entry.get().strip()
            release_date = release_entry.get().strip()
            genres = genres_entry.get().strip()
            cover_url = album_url_entry.get().strip()
            if self.current_file_path != "":
                cover_url = self.current_file_path
            if not artist or not album_name or not release_date:
                messagebox.showerror("Error", "Artist Name, Album, and Release Date are required.")
                return
            new_album = {
                "Ranking": 0,
                "Artist Name": artist,
                "Album": album_name,
                "Release Date": release_date,
                "Genres": genres,
                "Average Rating": 0,
                "Number of Ratings": 0,
                "Number of Reviews": 0,
                "Cover URL": cover_url
            }
            self.controller.albums.append(new_album)
            self.controller.save_albums()
            self.refresh_album_list()
            add_win.destroy()
        
        ttk.Button(add_win, text="Save Album", command=save_album).grid(row=5, column=0, columnspan=2, pady=10)
    
    def edit_album(self):
        if not self.selected_album:
            messagebox.showerror("Error", "Please select an album to edit.")
            return
        index = self.album_items.index(self.selected_album)
        album = self.controller.albums[index]
        
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Album")
        edit_win.configure(background="#f0f0f0")
        edit_win.grab_set()
        
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

        self.current_file_path = ""
        def open_filedialog_album_cover():
            self.current_file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("Image Files", ["*.png","*.jpg","*.jpeg","*.gif"]), ("All Files", "*.*")], initialdir="./album_covers")
            if self.current_file_path:
                self.current_file_path = os.path.relpath(self.current_file_path, start=os.getcwd())
                file_label.config(text=f"Selected file: {self.current_file_path}")
            else:
                file_label.config(text="No file selected.")

        ttk.Label(edit_win, text="Album Cover:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        album_url_entry = ttk.Entry(edit_win)
        album_url_entry.grid(row=4, column=1, padx=5, pady=5)
        album_image_entry = ttk.Button(edit_win, text="Import File", command=open_filedialog_album_cover)
        album_image_entry.grid(row=4, column=2, padx=5, pady=5)
        file_label = tk.Label(edit_win, text="No file selected.")
        file_label.grid(row=4, column=3, padx=5, pady=5)

        if URL_PATTERN.match(album.get("Cover URL", "")):
            album_url_entry.insert(0, album.get("Cover URL", ""))
        elif album.get("Cover URL", "") != "" and album.get("Cover URL", "") is not None:
            self.current_file_path = album.get("Cover URL", "")
            file_label.config(text=f"Selected file: {self.current_file_path}")
        
        def update_album():
            updated_artist = artist_entry.get().strip()
            updated_album = album_entry.get().strip()
            updated_release = release_entry.get().strip()
            updated_genres = genres_entry.get().strip()
            cover_url = album_url_entry.get().strip()
            if self.current_file_path != "":
                cover_url = self.current_file_path
            if not updated_artist or not updated_album or not updated_release:
                messagebox.showerror("Error", "Artist Name, Album, and Release Date are required.")
                return
            self.controller.albums[index] = {
                "Ranking": album["Ranking"],
                "Artist Name": updated_artist,
                "Album": updated_album,
                "Release Date": updated_release,
                "Genres": updated_genres,
                "Average Rating": album["Average Rating"],
                "Number of Ratings": album["Number of Ratings"],
                "Number of Reviews": album["Number of Reviews"],
                "Cover URL": cover_url
            }
            self.controller.save_albums()
            self.refresh_album_list()
            edit_win.destroy()
        
        ttk.Button(edit_win, text="Update Album", command=update_album).grid(row=5, column=0, columnspan=2, pady=10)
    
    def delete_album(self):
        if not self.selected_album:
            messagebox.showerror("Error", "Please select an album to delete.")
            return
        index = self.album_items.index(self.selected_album)
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected album?")
        if confirm:
            del self.controller.albums[index]
            self.controller.save_albums()
            self.refresh_album_list()
    
    def edit_account(self):
        current_user = self.controller.current_user
        if not current_user:
            messagebox.showerror("Error", "No user is logged in.")
            return
        
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Account")
        edit_win.configure(background="#f0f0f0")
        edit_win.grab_set()
        
        ttk.Label(edit_win, text="Current Password:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        current_pass_entry = ttk.Entry(edit_win, show="*")
        current_pass_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="New Username:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        new_username_entry = ttk.Entry(edit_win)
        new_username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="New Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        new_pass_entry = ttk.Entry(edit_win, show="*")
        new_pass_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Confirm New Password:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        confirm_new_pass_entry = ttk.Entry(edit_win, show="*")
        confirm_new_pass_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def update_account():
            current_pass = current_pass_entry.get()
            new_username = new_username_entry.get().strip()
            new_pass = new_pass_entry.get()
            confirm_new_pass = confirm_new_pass_entry.get()
            
            if self.controller.users[current_user]["password"] != current_pass:
                messagebox.showerror("Error", "Current password is incorrect.")
                return
            
            updated_username = current_user
            if new_username and new_username != current_user:
                if new_username in self.controller.users:
                    messagebox.showerror("Error", "Username already exists.")
                    return
                user_info = self.controller.users.pop(current_user)
                self.controller.users[new_username] = user_info
                updated_username = new_username
                self.controller.current_user = new_username
            
            if new_pass or confirm_new_pass:
                if new_pass != confirm_new_pass:
                    messagebox.showerror("Error", "New passwords do not match.")
                    return
                if not new_pass:
                    messagebox.showerror("Error", "New password cannot be empty.")
                    return
                self.controller.users[updated_username]["password"] = new_pass
            
            self.controller.save_users()
            messagebox.showinfo("Success", "Account updated successfully!")
            edit_win.destroy()
        
        ttk.Button(edit_win, text="Update Account", command=update_account).grid(row=4, column=0, columnspan=2, pady=10)
    
    def logout(self):
        self.controller.current_user = None
        messagebox.showinfo("Logout", "You have been logged out.")
        self.controller.search_button.pack_forget()
        self.controller.search_bar.pack_forget()
        self.controller.filter_dropdown.pack_forget()
        self.refresh_button.grid_remove()

if __name__ == "__main__":
    app = AlbumCatalogApp()
    app.mainloop()
