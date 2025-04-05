# ---------------------------------------------------------------------------
# Import necessary modules and libraries
# ---------------------------------------------------------------------------
import tkinter as tk                      # Tkinter: Python's standard GUI toolkit for building graphical interfaces.
from tkinter import messagebox            # For displaying pop-up messages.
from tkinter import ttk                   # For themed widgets.
from tkinter import filedialog            # For file dialogs (open/save dialogs).
import csv                                # For CSV file operations.
import json                               # For JSON file operations.
import os                                 # For operating system interactions (e.g., file checking).
from PIL import Image, ImageTk            # Pillow for image processing and interfacing with Tkinter images.
import re                                 # For regular expressions.
from urllib.request import urlopen, Request # For making HTTP requests to fetch resources from the web.
import io                                 # For in-memory I/O operations.
import threading                         # For multi-threading operations.
from concurrent.futures import ThreadPoolExecutor  # For managing a pool of threads (fixed-size thread pool).

# ---------------------------------------------------------------------------
# Define constants for file paths and theme colours
# ---------------------------------------------------------------------------
USERS_JSON = "./Code/users.json"               # File path for storing user login data in JSON format.
ALBUMS_CSV = "./Code/cleaned_music_data.csv"       # File path for storing album catalog data in CSV format.

# UI colour constants.
PRIMARY_BACKGROUND_COLOUR = "#527cc5"       # Primary background colour used across the UI.
NAV_BAR_BACKGROUND_COLOUR = "#345db7"         # Background colour for the navigation bar.
NAV_BAR_SHADOW_1_COLOUR = "#244d97"           # First shadow colour for the navigation bar.
NAV_BAR_SHADOW_2_COLOUR = "#143d87"           # Second shadow colour for the navigation bar.

# Precompile URL regex for efficiency.
URL_PATTERN = re.compile(
    r'^(https?|ftp):\/\/'                      # Matches URL schemes: http, https, or ftp.
    r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z]{2,6}'  # Matches domain names with valid characters.
    r'\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$'         # Matches optional paths, queries, and fragments.
)

# Global variable to track login state.
current_user = None   # Holds the current user's data (e.g., username or user object).
is_logged_in = False  # Boolean flag to indicate whether a user is logged in.

# Function to load users from JSON.
def load_users():
    # Check if the users JSON file exists.
    if os.path.exists('./Code/users.json'):
        with open('./Code/users.json', 'r') as file:
            # Load and return user data from the JSON file.
            return json.load(file)
    else:
        # Create an empty users file if it doesn't exist.
        with open('./Code/users.json', 'w') as file:
            json.dump([], file)
        # Return an empty list indicating no users.
        return []

# Login function to authenticate a user.
def login(username, password):
    global current_user, is_logged_in  # Declare modification of global variables.

    users = load_users()  # Load current users from the JSON file.
    
    for user in users:
        # Check for matching username and password.
        # Note: In production, passwords should be hashed and securely verified.
        if user['username'] == username and user['password'] == password:
            current_user = user   # Set the authenticated user as the current user.
            is_logged_in = True   # Update the global login state.
            return True          # Return True indicating successful login.
    
    # Return False if authentication fails.
    return False

# Logout function to sign out a user.
def logout():
    global current_user, is_logged_in  # Declare modification of global variables.
    current_user = None  # Reset the current user.
    is_logged_in = False  # Update the login state to logged out.
    print(f"DEBUG: User logged out. is_logged_in = {is_logged_in}")  # Debug output.
    messagebox.showinfo("Logout", "You have been logged out.")  # Show a pop-up informing the user.
    # The following lines reference self.controller and self.refresh_button;
    # note that 'self' is not defined in this global function which might be an oversight.
    self.controller.search_button.pack_forget()  
    self.controller.search_bar.pack_forget()
    self.controller.filter_dropdown.pack_forget()
    self.refresh_button.grid_remove()
    # Return to the LoginFrame after logging out.
    self.controller.show_frame("LoginFrame")

# Function to check if a user is currently logged in.
def check_login():
    print(f"DEBUG: check_login called, is_logged_in = {is_logged_in}, current_user = {current_user}")  # Debug output.
    return is_logged_in  # Return the current login state.

# ---------------------------------------------------------------------------
# Main Application Class: AlbumCatalogApp
# ---------------------------------------------------------------------------
class AlbumCatalogApp(tk.Tk):
    def __init__(self):
        # Initialize the main Tkinter window.
        super().__init__()
        
        self.title("BrightByte Music Cataloging Software")  # Set the window title.
        self.geometry("1280x720")  # Set the window size.
        
        # Load and set the window icon.
        # If "BrightByteLogo.png" exists, load it; otherwise, create a fallback dummy image.
        if os.path.exists("./Code/BrightByteLogo.png"):
            image = Image.open("./Code/BrightByteLogo.png")
        else:
            # Create a plain gray dummy image for testing or fallback purposes.
            image = Image.new("RGB", (1080, 1080), color=(200, 200, 200))
        # Crop the image to focus on the desired area.
        image = image.crop((0, int(1080 * 0.25), 1080, int(1080 * 0.75)))
        # Resize the image using a high-quality resampling algorithm.
        image = image.resize((125, 75), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(image)  # Convert image for use with Tkinter.
        try:
            # Attempt to set the window icon.
            self.iconphoto(True, self.image)
        except Exception as e:
            # If setting the icon fails (e.g., in test environments), log a warning.
            print("Warning: could not set iconphoto:", e)
        
        # Create the navigation bar at the top of the window.
        nav_bar = tk.Frame(self, bg=NAV_BAR_BACKGROUND_COLOUR)
        nav_bar.pack(fill="x", side="top")  # Fill horizontally at the top.
        shadow = tk.Frame(self, bg=NAV_BAR_SHADOW_1_COLOUR, height=5)
        shadow.pack(fill="x", side="top")  # First shadow below the nav bar.
        shadow2 = tk.Frame(self, bg=NAV_BAR_SHADOW_2_COLOUR, height=5)
        shadow2.pack(fill="x", side="top")  # Second shadow below the nav bar.
        logo = tk.Label(nav_bar, image=self.image, bg=NAV_BAR_BACKGROUND_COLOUR)
        logo.pack(side="left", padx=15, pady=15)  # Place the logo on the left side.
        title = tk.Label(nav_bar, text="BrightByte Music Cataloging Software",
                         font=("Helvetica", 22, "bold"), fg="white", bg=NAV_BAR_BACKGROUND_COLOUR)
        title.pack(anchor="w", padx=5, pady=40)  # Place the title with left alignment.
        
        # Set up search and favourites widgets (initially hidden).
        self.favourites_button = tk.Button(nav_bar, text="Favourites", command=self.favourites)
        self.favourites_button.pack_forget()  # Hide until needed.
        self.search_button = tk.Button(nav_bar, text="Search", command=self.search)
        self.search_button.pack_forget()  # Hide until needed.
        self.search_bar = tk.Text(nav_bar, font=("Calibri", 12), height=1, width=50)
        self.search_bar.pack_forget()  # Hide until needed.
        self.search_bar.bind("<Return>", self.on_enter_pressed)  # Bind the Enter key to trigger a search.
        self.search_filter = tk.StringVar(value="Album Name")  # Default search filter.
        self.filter_dropdown = ttk.Combobox(nav_bar, textvariable=self.search_filter,
                                            values=["Album Name", "Artist Name", "Genres", "Release Date"],
                                            state="readonly", width=15)
        self.filter_dropdown.pack_forget()  # Hide until needed.
        
        # Set up ttk styling for consistent appearance.
        style = ttk.Style(self)
        style.theme_use("clam")  # Use the 'clam' theme.
        style.configure("TFrame", background=PRIMARY_BACKGROUND_COLOUR)
        style.configure("TLabel", background=PRIMARY_BACKGROUND_COLOUR, foreground="white",
                        font=("Helvetica", 12, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TEntry", padding=5)
        
        # Load persistent data for users and albums.
        self.users = self.load_users()  # Load users from the JSON file.
        self.current_user = None  # Initialize the current user as None.
        self.search_results = None  # Placeholder for search results.
        self.albums = self.load_albums_from_csv()  # Load album data from the CSV file.
        
        # Create a container frame for multiple pages.
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)  # Allow row expansion.
        container.grid_columnconfigure(0, weight=1)  # Allow column expansion.
        self.frames = {}  # Dictionary to hold frames by name.
        for F in (LoginFrame, SignupFrame, CatalogFrame):
            frame = F(parent=container, controller=self)  # Instantiate each frame.
            self.frames[F.__name__] = frame  # Store frame using its class name as key.
            frame.anchor("n")  # Anchor content to the top.
            frame.grid(row=0, column=0, sticky="nsew", pady=35)  # Place frame in grid.
                
        self.show_frame("LoginFrame")  # Display the login frame initially.
        
        # Bind global mouse wheel events to enable scrolling in the catalog.
        self.bind_all("<MouseWheel>", self.on_global_mousewheel)
        self.bind_all("<Button-4>", self.on_global_mousewheel)  # For Linux scroll up.
        self.bind_all("<Button-5>", self.on_global_mousewheel)  # For Linux scroll down.
    
    def on_enter_pressed(self, event):
        """Trigger search when Enter is pressed in the search bar."""
        self.search()  # Call the search method.
        return "break"  # Prevent insertion of a newline in the Text widget.
    
    def on_global_mousewheel(self, event):
        """Forward mouse wheel events to the CatalogFrame's canvas if it is visible."""
        catalog = self.frames["CatalogFrame"]  # Get the catalog frame.
        if catalog.winfo_ismapped():
            canvas = catalog.canvas  # Retrieve the canvas widget.
            if event.num == 4:  # Linux scroll up.
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux scroll down.
                canvas.yview_scroll(1, "units")
            else:
                # Windows and Mac OS: adjust scroll based on event.delta.
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_users(self):
        """Load users from the USERS_JSON file."""
        if os.path.exists(USERS_JSON):
            with open(USERS_JSON, "r") as f:
                try:
                    return json.load(f)  # Return the parsed JSON data.
                except json.JSONDecodeError:
                    return {}  # Return empty dict if JSON is malformed.
        return {}  # Return empty dict if file does not exist.
    
    def save_users(self):
        """Save the current users data to the USERS_JSON file."""
        with open(USERS_JSON, "w") as f:
            json.dump(self.users, f, indent=4)  # Write formatted JSON data.
    
    def save_albums(self):
        """Save the current albums data to the ALBUMS_CSV file."""
        with open(ALBUMS_CSV, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, ["Ranking", "Album", "Artist Name", "Release Date",
                                                "Genres", "Average Rating", "Number of Ratings",
                                                "Number of Reviews", "Cover URL", "Tracklist", "Deezer_ID"])
            writer.writeheader()  # Write the CSV header.
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
                    "Cover URL": album["Cover URL"],
                    "Tracklist": album["Tracklist"],
                    "Deezer_ID": album["Deezer_ID"]
                })
    
    def load_albums_from_csv(self):
        """Load album data from the ALBUMS_CSV file and return as a list of dictionaries."""
        albums = []  # Initialize list to hold album data.
        if os.path.exists(ALBUMS_CSV):
            with open(ALBUMS_CSV, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Construct an album dictionary with stripped string values.
                    album = {
                        "Ranking": (row.get("Ranking") or "").strip(),
                        "Album": (row.get("Album") or "").strip(),
                        "Artist Name": (row.get("Artist Name") or "").strip(),
                        "Release Date": (row.get("Release Date") or "").strip(),
                        "Genres": (row.get("Genres") or "").strip(),
                        "Average Rating": (row.get("Average Rating") or "").strip(),
                        "Number of Ratings": (row.get("Number of Ratings") or "").strip(),
                        "Number of Reviews": (row.get("Number of Reviews") or "").strip(),
                        "Cover URL": (row.get("Cover URL") or "").strip(),
                        "Tracklist": (row.get("Tracklist") or "").strip(),
                        "Deezer_ID": (row.get("Deezer_ID") or "").strip()
                    }
                    albums.append(album)
        else:
            print("The file does not exist.")  # Log if the CSV file is missing.
        return albums
    
    def load_search_query(self, search_query):
        """Filter albums based on the search query and selected filter criteria."""
        self.search_results = []  # Reset search results.
        search_query = search_query.lower().strip() if search_query else None  # Normalize the query.
        selected_filter = self.search_filter.get()  # Get the currently selected filter.
        
        def matches_filter(album):
            """Determine if the album matches the search query based on the selected filter."""
            if search_query is None:
                return True  # If no query is provided, include all albums.
            if selected_filter == "Album Name":
                return search_query in album.get("Album", "").lower()
            if selected_filter == "Artist Name":
                return search_query in album.get("Artist Name", "").lower()
            if selected_filter == "Genres":
                return search_query in album.get("Genres", "").lower()
            if selected_filter == "Release Date":
                return search_query in album.get("Release Date", "").split("-")
            return False
        
        # Filter the albums list using the matches_filter function.
        self.search_results = list(filter(matches_filter, self.albums.copy()))
    
    def show_frame(self, frame_name):
        """Bring the specified frame to the front and manage search widget visibility."""
        frame = self.frames[frame_name]  # Retrieve the frame by its name.
        if frame_name == "CatalogFrame":
            # When displaying the catalog, ensure the filter dropdown is visible.
            self.filter_dropdown.pack(side="right", padx=10)
            frame.refresh_album_list()  # Refresh the album list.
        else:
            # Hide the filter dropdown on other frames.
            self.filter_dropdown.pack_forget()
        frame.tkraise()  # Raise the selected frame to the top.
    
    def search(self, no_refresh=False):
        """Perform a search based on the query from the search bar."""
        query = self.search_bar.get("1.0", tk.END)  # Get the text from the search bar.
        self.load_search_query(query)  # Filter albums based on the query.
        if query.strip() and not self.search_results:
            # Inform the user if the search returns no results.
            messagebox.showerror("No Results", "No relevant results found for your search query.")
        frame = self.frames["CatalogFrame"]
        if not no_refresh:
            frame.refresh_album_list()  # Refresh the album display if needed.
        frame.tkraise()  # Bring the catalog frame to the front.
    
    def favourites(self):
        """Display the favourite albums for the currently logged-in user."""
        self.search_results = []  # Reset search results.
        
        # Check if the current user has a 'favourites' list.
        if not "favourites" in self.users[current_user]:
            messagebox.showerror("No Results", "No favourites yet.")
        else:
            # Iterate over each favourite album ID and add the matching album to search_results.
            for id in self.users[current_user]["favourites"]:
                for album in self.albums:
                    if album["Deezer_ID"] == id:
                        self.search_results.append(album)
                        break
                
        frame = self.frames["CatalogFrame"]
        frame.refresh_album_list()  # Refresh the catalog to show favourites.
        frame.tkraise()  # Bring the catalog frame to the front.
    
    def refresh_catalog(self):
        """Reset the search bar and refresh the album catalog display."""
        self.search_bar.delete("1.0", tk.END)  # Clear the search bar.
        self.search("")  # Execute an empty search to reload the catalog.

# ---------------------------------------------------------------------------
# LoginFrame: Allows users to log in or continue as guest.
# ---------------------------------------------------------------------------
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        # Initialize the login frame with the primary background colour.
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller  # Reference to the main application controller.
        
        header = ttk.Label(self, text="Login", style="Header.TLabel")
        header.grid(row=1, column=0, columnspan=2, pady=(0,15))  # Place header label.
        
        # Username label and input field.
        ttk.Label(self, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Password label and input field.
        ttk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Login button to authenticate the user.
        login_btn = ttk.Button(self, text="Login", command=self.login)
        login_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Button to switch to the sign-up frame.
        switch_btn = ttk.Button(self, text="Sign Up", command=lambda: controller.show_frame("SignupFrame"))
        switch_btn.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Button to continue as a guest user.
        guest_btn = ttk.Button(self, text="Continue as Guest", command=self.continue_as_guest)
        guest_btn.grid(row=6, column=0, columnspan=2, pady=5)
    
    def login(self):
        """Attempt to log in using the provided username and password."""
        username = self.username_entry.get()  # Retrieve username.
        password = self.password_entry.get()  # Retrieve password.
        users = self.controller.users  # Get user data from the controller.
        if username in users and users[username]["password"] == password:
            self.controller.current_user = username  # Set the current user.
            # Update global login state variables.
            global current_user, is_logged_in
            current_user = username
            is_logged_in = True
            print(f"DEBUG: User '{username}' logged in successfully. is_logged_in = {is_logged_in}")
            messagebox.showinfo("Login", "Login successful!")  # Inform the user of success.
            # Display the search and favourites buttons now that the user is logged in.
            self.controller.favourites_button.pack(side="right", padx=10)
            self.controller.search_button.pack(side="right", padx=10)
            self.controller.search_bar.pack(side="right")
            self.controller.filter_dropdown.pack(side="right", padx=10)

            self.controller.frames["CatalogFrame"].edit_album_btn.grid(row=0, column=4, padx=5, pady=10)
            self.controller.frames["CatalogFrame"].delete_btn.grid(row=0, column=5, padx=5, pady=10)
            self.controller.frames["CatalogFrame"].add_btn.grid(row=0, column=3, padx=5, pady=10)
            self.controller.frames["CatalogFrame"].favourite_btn.grid(row=0, column=1, padx=5, pady=10)
            self.controller.frames["CatalogFrame"].unfavourite_btn.grid(row=0, column=2, padx=5, pady=10)
            self.controller.frames["CatalogFrame"].edit_account_btn.grid(row=0, column=6, padx=5, pady=10)

            self.controller.frames["CatalogFrame"].refresh_button.grid()
            self.controller.show_frame("CatalogFrame")  # Switch to the catalog frame.
            # Clear the input fields.
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            # Display an error if credentials are invalid.
            messagebox.showerror("Error", "Invalid username or password.")
    
    def continue_as_guest(self):
        """Allow the user to continue as a guest with limited privileges."""
        self.controller.current_user = "Guest"  # Set current user as "Guest".
        # Update global login state: guests are not allowed to edit albums.
        global current_user, is_logged_in
        current_user = "Guest"
        is_logged_in = False  # Guests are not considered fully logged in.
        messagebox.showinfo("Guest Login", "Continuing as guest. Note: Guests cannot add, edit, or delete albums.")
        # Display search UI elements for guest users.
        self.controller.search_button.pack(side="right", padx=10)
        self.controller.search_bar.pack(side="right")
        self.controller.filter_dropdown.pack(side="right", padx=10)

        self.controller.frames["CatalogFrame"].edit_album_btn.grid_forget()
        self.controller.frames["CatalogFrame"].delete_btn.grid_forget()
        self.controller.frames["CatalogFrame"].add_btn.grid_forget()
        self.controller.frames["CatalogFrame"].favourite_btn.grid_forget()
        self.controller.frames["CatalogFrame"].unfavourite_btn.grid_forget()
        self.controller.frames["CatalogFrame"].edit_account_btn.grid_forget()

        self.controller.frames["CatalogFrame"].refresh_button.grid()
        self.controller.show_frame("CatalogFrame")  # Switch to the catalog frame.

# ---------------------------------------------------------------------------
# SignupFrame: Allows users to create a new account.
# ---------------------------------------------------------------------------
class SignupFrame(tk.Frame):
    def __init__(self, parent, controller):
        # Initialize the sign-up frame with the primary background colour.
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller  # Reference to the main application controller.
        
        header = ttk.Label(self, text="Sign Up", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, pady=(0,15))  # Place header label.
        
        # Username label and input field.
        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Email label and input field.
        ttk.Label(self, text="Email:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Password label and input field.
        ttk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Confirm Password label and input field.
        ttk.Label(self, text="Confirm Password:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.confirm_password_entry = ttk.Entry(self, show="*")
        self.confirm_password_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Button to create the account.
        create_btn = ttk.Button(self, text="Create Account", command=self.signup)
        create_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Button to return to the login frame.
        back_btn = ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginFrame"))
        back_btn.grid(row=6, column=0, columnspan=2, pady=5)
    
    def signup(self):
        """Create a new user account after validating input fields."""
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        # Check that required fields are not empty.
        if not username or not password or not email:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return
        # Check if the username already exists.
        if username in self.controller.users:
            messagebox.showerror("Error", "Username already exists.")
            return
        # Verify that the passwords match.
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        # Validate the email format using a regular expression.
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is None:
            messagebox.showerror("Error", "Email is invalid.")
            return
        # Create the new user account.
        self.controller.users[username] = {"email": email, "password": password}
        self.controller.save_users()  # Save the new user data.
        messagebox.showinfo("Sign Up", "Account created successfully!")
        self.controller.show_frame("LoginFrame")  # Return to the login frame.
        # Clear the input fields.
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)

# ---------------------------------------------------------------------------
# CatalogFrame: Displays the album catalog.
# ---------------------------------------------------------------------------
class CatalogFrame(tk.Frame):
    def __init__(self, parent, controller):
        # Initialize the catalog frame with the primary background colour.
        super().__init__(parent, bg=PRIMARY_BACKGROUND_COLOUR)
        self.controller = controller  # Reference to the main application controller.
        
        # Initialize a cache for album cover images to avoid reloading.
        self.album_cover_cache = {}
        # Create a thread pool executor to manage concurrent image loading.
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Configure grid layout for dynamic resizing.
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header = tk.Label(self, text="Album Catalog", font=("Helvetica", 18, "bold"),
                          fg="white", bg=PRIMARY_BACKGROUND_COLOUR)
        header.grid(row=0, column=0, sticky="ew", pady=(0,15))  # Place header label.
        
        # Create a canvas to hold the list of album items.
        self.canvas = tk.Canvas(self, bg=NAV_BAR_SHADOW_1_COLOUR)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        # Create a vertical scrollbar for the canvas.
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create an inner frame (list_frame) that will contain album items.
        self.list_frame = tk.Frame(self.canvas, bg=NAV_BAR_SHADOW_1_COLOUR)
        self.list_frame.anchor("n")  # Anchor its contents to the top.
        # Bind configuration changes to update the scrollable region of the canvas.
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # Create a window in the canvas to embed the list_frame.
        window = self.canvas.create_window((self.canvas.winfo_width()//2, 0), window=self.list_frame, anchor="n")
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfig(window, width=event.width))
        # Bind mouse wheel events to the canvas when the mouse enters.
        self.canvas.bind("<Enter>", lambda event: self.canvas.focus_set())
        # Global mouse wheel bindings are managed by the main application.
        
        self.selected_album = None  # Tracks the currently selected album.
        self.album_items = []  # List to store references to album item widgets.
        self.album_cover_images = []  # List to store PhotoImage references for album covers.
        
        # Create a frame for control buttons.
        buttonFrame = tk.Frame(self, bg=PRIMARY_BACKGROUND_COLOUR)
        buttonFrame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        buttonFrame.anchor("center")  # Center the button frame.
        
        # Create and position control buttons for various album operations.
        tracks_btn = ttk.Button(buttonFrame, text="Tracks", command=self.tracks_album)
        tracks_btn.grid(row=0, column=0, padx=5, pady=10)
        self.favourite_btn = ttk.Button(buttonFrame, text="Favourite Album", command=self.favourite_album)
        self.favourite_btn.grid(row=0, column=1, padx=5, pady=10)
        self.unfavourite_btn = ttk.Button(buttonFrame, text="Unfavourite Album", command=self.unfavourite_album)
        self.unfavourite_btn.grid(row=0, column=2, padx=5, pady=10)  # Button for unfavouriting albums.
        self.add_btn = ttk.Button(buttonFrame, text="Add Album", command=self.add_album)
        self.add_btn.grid(row=0, column=3, padx=5, pady=10)
        self.edit_album_btn = ttk.Button(buttonFrame, text="Edit Album", command=self.edit_album)
        self.edit_album_btn.grid(row=0, column=4, padx=5, pady=10)
        self.delete_btn = ttk.Button(buttonFrame, text="Delete Album", command=self.delete_album)
        self.delete_btn.grid(row=0, column=5, padx=5, pady=10)
        self.edit_account_btn = ttk.Button(buttonFrame, text="Edit Account", command=self.edit_account)
        self.edit_account_btn.grid(row=0, column=6, padx=5, pady=10)
        logout_btn = ttk.Button(buttonFrame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=7, padx=5, pady=10)
        self.refresh_button = ttk.Button(buttonFrame, text="Refresh", command=self.controller.refresh_catalog)
        self.refresh_button.grid(row=0, column=8, padx=5, pady=10)
        self.refresh_button.grid_remove()  # Hide the refresh button initially.

    
    def thread_function_refresh_albums(self, index, album, currentRow):
        """Thread function to load and display a single album item."""
        albumName = album.get("Album")  # Retrieve album name.
        artistName = album.get("Artist Name")  # Retrieve artist name.
        genres = album.get("Genres")  # Retrieve album genres.
        releaseDate = album.get("Release Date")  # Retrieve release date.
        
        # Create a frame to represent an album item.
        albumItem = tk.Frame(self.list_frame, bg=NAV_BAR_SHADOW_2_COLOUR)
        albumItem.grid(row=currentRow, column=0, padx=15, pady=15)
        albumItem.grid_propagate(False)  # Prevent automatic resizing.
        
        # Load the album cover image with caching.
        albumURL = album.get("Cover URL", "").strip()
        if albumURL:
            if albumURL in self.album_cover_cache:
                albumCover = self.album_cover_cache[albumURL]  # Use cached image.
            else:
                try:
                    if URL_PATTERN.match(albumURL):
                        # Fetch image via HTTP if albumURL is a valid URL.
                        req = Request(albumURL, headers={"User-Agent": "Mozilla/5.0"})
                        response = urlopen(req)
                        albumCoverData = response.read()
                        image_obj = Image.open(io.BytesIO(albumCoverData))
                    else:
                        # Otherwise, treat albumURL as a local file path.
                        image_obj = Image.open(albumURL)
                    image_obj = image_obj.resize((150,150), Image.LANCZOS)  # Resize the image.
                    albumCover = ImageTk.PhotoImage(image_obj)
                    self.album_cover_cache[albumURL] = albumCover  # Cache the image.
                except Exception as e:
                    print(f"Failed to load album cover for {albumURL}: {e}")  # Log error.
                    albumCover = self.album_cover_cache.get("default")
                    if albumCover is None:
                        default_img = Image.open("./Code/Eric.png")
                        default_img = default_img.resize((150,150), Image.LANCZOS)
                        albumCover = ImageTk.PhotoImage(default_img)
                        self.album_cover_cache["default"] = albumCover  # Cache the default image.
        else:
            # Use default image if no album URL is provided.
            albumCover = self.album_cover_cache.get("default")
            if albumCover is None:
                default_img = Image.open("./Code/Eric.png")
                default_img = default_img.resize((150,150), Image.LANCZOS)
                albumCover = ImageTk.PhotoImage(default_img)
                self.album_cover_cache["default"] = albumCover
        
        # Create a label widget to display the album cover image.
        coverLabel = tk.Label(albumItem, image=albumCover, bg="white")
        coverLabel.pack(side="left")
        
        # Create a frame to hold album details (labels).
        labelFrame = tk.Frame(albumItem, name="labelFrame", bg=NAV_BAR_SHADOW_2_COLOUR, width=400, height=100)
        labelFrame.pack(fill="both", side="left", padx=(15,15), pady=(30,0))
        labelFrame.pack_propagate(False)
        
        # Create and pack labels for album name, artist, genres, and release date.
        albumNameLabel = tk.Label(labelFrame, name="albumNameLabel", text=albumName, bg=NAV_BAR_SHADOW_2_COLOUR,
                                   fg="white", font=("Helvetica",12,"bold"), anchor="w")
        albumNameLabel.pack(fill="x")
        artistNameLabel = tk.Label(labelFrame, name="artistNameLabel", text=f"By: {artistName}", bg=NAV_BAR_SHADOW_2_COLOUR,
                                    fg="white", font=("Helvetica",10,"bold"), anchor="w")
        artistNameLabel.pack(fill="x")
        genresLabel = tk.Label(labelFrame, name="genresLabel", text=f"Genres: {genres}", bg=NAV_BAR_SHADOW_2_COLOUR,
                                fg="white", font=("Helvetica",10,"bold"), anchor="w")
        genresLabel.pack(fill="x")
        releaseDateLabel = tk.Label(labelFrame, name="releaseDateLabel", text=f"Released: {releaseDate}", bg=NAV_BAR_SHADOW_2_COLOUR,
                                    fg="white", font=("Helvetica",10,"bold"), anchor="w")
        releaseDateLabel.pack(fill="x")
        
        # Store the album item and its cover image in corresponding lists.
        self.album_items[index] = albumItem
        self.album_cover_images[index] = albumCover
        
        # Bind a click event to each widget in the album item to enable selection.
        for widget in [albumItem, labelFrame, albumNameLabel, artistNameLabel, genresLabel, releaseDateLabel, coverLabel]:
            widget.bind("<Button-1>", lambda event, item=albumItem: self.select_album(event, item))
    
    def refresh_album_list(self, no_threading = False):
        """Clear and repopulate the album list display based on current data or search results."""
        # Destroy any existing album item widgets.
        for existingAlbumItem in self.album_items:
            if existingAlbumItem is not None:
                existingAlbumItem.destroy()
        self.album_items = []  # Reset the list of album items.
        if self.controller.search_results is not None:
            album_arr_to_use = self.controller.search_results  # Use filtered search results.
        else:
            album_arr_to_use = self.controller.albums  # Use the full album catalog.
        # Initialize album_items with placeholders.
        for _ in range(len(album_arr_to_use)):
            self.album_items.append(None)
        self.album_cover_images = [None] * len(album_arr_to_use)  # Initialize cover image list.
        self.selected_album = None  # Reset the selected album.
        currentRow = 0  # Start at the first grid row.
        # List to hold future objects if threading is used.
        self.refresh_album_threads = []
        for index, album in enumerate(album_arr_to_use):
            if no_threading:
                # If threading is disabled, load album item synchronously.
                self.thread_function_refresh_albums(index, album, currentRow)
                currentRow += 1
                continue
            
            # Submit the album refresh function to the thread pool.
            future = self.executor.submit(self.thread_function_refresh_albums, index, album, currentRow)
            self.refresh_album_threads.append(future)
            currentRow += 1
        # No explicit wait is required for thread futures.
    
    def select_album(self, event, albumItem: tk.Frame):
        """Handle album selection by updating UI to highlight the selected album."""
        # Reset background colours for all album items.
        for item in self.album_items:
            if item is not None:
                item.config(bg=NAV_BAR_SHADOW_2_COLOUR)
                item.nametowidget("labelFrame").config(bg=NAV_BAR_SHADOW_2_COLOUR)
                for widgetName in ["albumNameLabel", "artistNameLabel", "genresLabel", "releaseDateLabel"]:
                    item.nametowidget("labelFrame").nametowidget(widgetName).config(bg=NAV_BAR_SHADOW_2_COLOUR)
        # Set the background colour of the selected album item.
        albumItem.config(bg=PRIMARY_BACKGROUND_COLOUR)
        albumItem.nametowidget("labelFrame").config(bg=PRIMARY_BACKGROUND_COLOUR)
        for widgetName in ["albumNameLabel", "artistNameLabel", "genresLabel", "releaseDateLabel"]:
            albumItem.nametowidget("labelFrame").nametowidget(widgetName).config(bg=PRIMARY_BACKGROUND_COLOUR)
        self.selected_album = albumItem  # Update the selected album reference.
    
    def tracks_album(self):
        """Open a new window displaying the tracklist of the selected album."""
        tracks_win = tk.Toplevel(self)
        tracks_win.title("Tracks")
        tracks_win.configure(background="#f0f0f0")
        
        if not self.selected_album:
            # Ensure an album is selected before showing tracks.
            messagebox.showerror("Error", "Please select an album to edit.")
            return
        index = self.album_items.index(self.selected_album)  # Get the index of the selected album.
        album = self.controller.albums[index]
        tracklist = album["Tracklist"].split("; ")  # Split the tracklist into individual tracks.
        
        for i in range(0, len(tracklist)):
            # Create and place a label for each track.
            ttk.Label(tracks_win, text=tracklist[i]).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
    def favourite_album(self):
        """Toggle the favourite status of the selected album."""
        print(f"DEBUG: favourite_album called. Login check result: {check_login()}")
        if not check_login():
            # Ensure the user is logged in before favouriting.
            messagebox.showerror("Error", "You must be logged in to favourite or unfavourite an album.")
            return

        if not self.selected_album:
            # Ensure an album is selected.
            messagebox.showerror("Error", "Please select an album to favourite or unfavourite.")
            return

        # Determine the correct album list to use (filtered search results or full catalog).
        album_list = self.controller.search_results if self.controller.search_results else self.controller.albums
        index = self.album_items.index(self.selected_album)
        album = album_list[index]

        # Check if the user's favourites list exists; if not, initialize it.
        if "favourites" not in self.controller.users[current_user]:
            self.controller.users[current_user]["favourites"] = []

        # Toggle the album's favourite status.
        if album["Deezer_ID"] in self.controller.users[current_user]["favourites"]:
            self.controller.users[current_user]["favourites"].remove(album["Deezer_ID"])
            messagebox.showinfo("Success", f"Album '{album['Album']}' has been removed from your favourites.")
        else:
            self.controller.users[current_user]["favourites"].append(album["Deezer_ID"])
            messagebox.showinfo("Success", f"Album '{album['Album']}' has been added to your favourites.")

        # Save the updated favourites list.
        self.controller.save_users()
    
    def unfavourite_album(self):
        """Remove the selected album from the user's favourites."""
        print(f"DEBUG: unfavourite_album called. Login check result: {check_login()}")
        if not check_login():
            # Only logged in users can unfavourite albums.
            messagebox.showerror("Error", "You must be logged in to unfavourite an album.")
            return

        if not self.selected_album:
            # Ensure an album is selected.
            messagebox.showerror("Error", "Please select an album to unfavourite.")
            return

        # Determine the album list to use (search results or full catalog).
        album_list = self.controller.search_results if self.controller.search_results else self.controller.albums
        index = self.album_items.index(self.selected_album)
        album = album_list[index]

        # Ensure the user has a favourites list.
        if "favourites" not in self.controller.users[current_user]:
            messagebox.showerror("Error", "You have no favourites to unfavourite.")
            return

        # Remove the album from favourites if it is present.
        if album["Deezer_ID"] in self.controller.users[current_user]["favourites"]:
            self.controller.users[current_user]["favourites"].remove(album["Deezer_ID"])
            self.controller.save_users()
            messagebox.showinfo("Success", f"Album '{album['Album']}' has been removed from your favourites.")
        else:
            messagebox.showerror("Error", f"Album '{album['Album']}' is not in your favourites.")
    
    def add_album(self):
        """Open a new window to add a new album to the catalog."""
        print(f"DEBUG: add_album called. Login check result: {check_login()}")
        if not check_login():
            # Only logged in users can add an album.
            messagebox.showerror("Error", "You must be logged in to add an album")
            return
        
        # Create a new top-level window for adding an album.
        add_win = tk.Toplevel(self, bg=PRIMARY_BACKGROUND_COLOUR)
        add_win.title("Add Album")
        add_win.grab_set()  # Make the window modal.
        
        # Create labels and entry fields for album details.
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
        
        self.current_file_path = ""  # Variable to store selected album cover file path.
        def open_filedialog_album_cover():
            """Open a file dialog to select an album cover image."""
            self.current_file_path = filedialog.askopenfilename(
                title="Select a File",
                filetypes=[("Image Files", ["*.png","*.jpg","*.jpeg","*.gif"]), ("All Files", "*.*")],
                initialdir="./Code")
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

        ttk.Label(add_win, text="Tracks:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        tracks_list = tk.Listbox(add_win)
        tracks_list.grid(row=5, column=1, padx=5, pady=5)

        def add_track() -> None:
            """Add a new track to the tracks list."""
            if tracks_list_add_entry.get() != "":
                track_name = tracks_list_add_entry.get()
                tracks_list.insert(tk.END, f"{tracks_list.size() + 1}. {track_name}")
                tracks_list_add_entry.delete(0, tk.END)

        def delete_track() -> None:
            """Delete the selected track and re-index the remaining tracks."""
            if len(tracks_list.curselection()) == 1:
                indexToDelete = tracks_list.curselection()[0]
                newIndexedTracks = []
                i = indexToDelete + 1
                for track_string in tracks_list.get(indexToDelete + 1, tk.END):
                    if len(track_string.split('. ')) > 1:
                        newIndexedTracks.append(f"{i}. {track_string.split('. ')[1]}")
                        i += 1
                
                tracks_list.delete(indexToDelete, tk.END)

                for track_string in newIndexedTracks:
                    tracks_list.insert(tk.END, track_string)

        tracks_list_delete_button = ttk.Button(add_win, text="Delete Selected Track", command=delete_track)
        tracks_list_delete_button.grid(row=5, column=2, padx=5, pady=5)
        tracks_list_add_entry = ttk.Entry(add_win)
        tracks_list_add_entry.grid(row=5, column=3, padx=5, pady=5)
        tracks_list_add_button = ttk.Button(add_win, text="Add Track", command=add_track)
        tracks_list_add_button.grid(row=5, column=4, padx=5, pady=5)

        def save_album():
            """Save the new album to the catalog and update the CSV file."""
            artist = artist_entry.get().strip()
            album_name = album_entry.get().strip()
            release_date = release_entry.get().strip()
            genres = genres_entry.get().strip()
            cover_url = album_url_entry.get().strip()
            track_list_string = ""

            # Concatenate all tracks into a single string separated by semicolons.
            for track_string in tracks_list.get(0, tk.END):
                track_list_string = track_list_string + track_string + "; "

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
                "Cover URL": cover_url,
                "Tracklist": track_list_string,
                "Deezer_ID": ""
            }
            self.controller.albums.append(new_album)  # Add the new album to the catalog.
            self.controller.save_albums()  # Save albums to the CSV file.
            self.refresh_album_list()  # Refresh the displayed album list.
            add_win.destroy()  # Close the add album window.
        
        ttk.Button(add_win, text="Save Album", command=save_album).grid(row=6, column=0, columnspan=2, pady=10)
    
    def edit_album(self, force=False):
        """Open a window to edit the selected album's details."""
        print(f"DEBUG: edit_album called. Login check result: {check_login()}")
        if not force:
            if not check_login():
                messagebox.showerror("Error", "You must be logged in to edit an album")
                return
                
            if not self.selected_album:
                messagebox.showerror("Error", "Please select an album to edit.")
                return
        
        index = self.album_items.index(self.selected_album)  # Get the index of the selected album.
        album = self.controller.albums[index]
        
        # Create a new window for editing album details.
        edit_win = tk.Toplevel(self, bg=PRIMARY_BACKGROUND_COLOUR)
        edit_win.title("Edit Album")
        edit_win.grab_set()  # Make the window modal.
        
        # Create labels and pre-populated entry fields for album details.
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
        
        self.current_file_path = ""  # Reset the file path for the album cover.
        def open_filedialog_album_cover():
            """Open a file dialog to select a new album cover."""
            self.current_file_path = filedialog.askopenfilename(
                title="Select a File",
                filetypes=[("Image Files", ["*.png","*.jpg","*.jpeg","*.gif"]), ("All Files", "*.*")],
                initialdir="./Code")
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
        
        # Determine whether to populate the cover URL as a web URL or a local file.
        if URL_PATTERN.match(album.get("Cover URL", "")):
            album_url_entry.insert(0, album.get("Cover URL", ""))
        elif album.get("Cover URL", "") != "" and album.get("Cover URL", "") is not None:
            self.current_file_path = album.get("Cover URL", "")
            file_label.config(text=f"Selected file: {self.current_file_path}")

        ttk.Label(edit_win, text="Tracks:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        tracks_list = tk.Listbox(edit_win)
        tracks_list.grid(row=5, column=1, padx=5, pady=5)

        # Populate the tracks list with existing track data.
        for track_string in album.get("Tracklist").split(";"):
            if track_string.strip() != "":
                tracks_list.insert(tk.END, track_string)

        def add_track() -> None:
            """Add a new track to the tracks list."""
            if tracks_list_add_entry.get() != "":
                track_name = tracks_list_add_entry.get()
                tracks_list.insert(tk.END, f"{tracks_list.size() + 1}. {track_name}")
                tracks_list_add_entry.delete(0, tk.END)

        def delete_track() -> None:
            """Delete the selected track and update track numbering."""
            if len(tracks_list.curselection()) == 1:
                indexToDelete = tracks_list.curselection()[0]
                newIndexedTracks = []
                i = indexToDelete + 1
                for track_string in tracks_list.get(indexToDelete + 1, tk.END):
                    if len(track_string.split('. ')) > 1:
                        newIndexedTracks.append(f"{i}. {track_string.split('. ')[1]}")
                        i += 1
                
                tracks_list.delete(indexToDelete, tk.END)

                for track_string in newIndexedTracks:
                    tracks_list.insert(tk.END, track_string)

        tracks_list_delete_button = ttk.Button(edit_win, text="Delete Selected Track", command=delete_track)
        tracks_list_delete_button.grid(row=5, column=2, padx=5, pady=5)
        tracks_list_add_entry = ttk.Entry(edit_win)
        tracks_list_add_entry.grid(row=5, column=3, padx=5, pady=5)
        tracks_list_add_button = ttk.Button(edit_win, text="Add Track", command=add_track)
        tracks_list_add_button.grid(row=5, column=4, padx=5, pady=5)
        
        def update_album():
            """Update the album with new details from the edit form."""
            updated_artist = artist_entry.get().strip()
            updated_album = album_entry.get().strip()
            updated_release = release_entry.get().strip()
            updated_genres = genres_entry.get().strip()
            cover_url = album_url_entry.get().strip()
            track_list_string = ""

            # Concatenate the tracks into a single string.
            for track_string in tracks_list.get(0, tk.END):
                track_list_string = track_list_string + track_string + "; "

            if self.current_file_path != "":
                cover_url = self.current_file_path
            if not updated_artist or not updated_album or not updated_release:
                messagebox.showerror("Error", "Artist Name, Album, and Release Date are required.")
                return
            # Update the album details in the controller's album list.
            self.controller.albums[index] = {
                "Ranking": album["Ranking"],
                "Artist Name": updated_artist,
                "Album": updated_album,
                "Release Date": updated_release,
                "Genres": updated_genres,
                "Average Rating": album["Average Rating"],
                "Number of Ratings": album["Number of Ratings"],
                "Number of Reviews": album["Number of Reviews"],
                "Cover URL": cover_url,
                "Tracklist": track_list_string,
                "Deezer_ID": ""
            }
            self.controller.save_albums()  # Save the updated album list.
            self.refresh_album_list()  # Refresh the display.
            edit_win.destroy()  # Close the edit window.
        
        ttk.Button(edit_win, text="Update Album", command=update_album).grid(row=6, column=0, columnspan=2, pady=10)
    
    def delete_album(self, force=False):
        """Delete the selected album from the catalog."""
        print(f"DEBUG: delete_album called. Login check result: {check_login()}")
        if not force:
            if not check_login():
                messagebox.showerror("Error", "You must be logged in to delete an album")
                return
                
            if not self.selected_album:
                messagebox.showerror("Error", "Please select an album to delete.")
                return
        
        index = self.album_items.index(self.selected_album)  # Get the index of the selected album.
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected album?")
        if confirm:
            del self.controller.albums[index]  # Remove the album from the list.
            self.controller.save_albums()  # Save the updated album list.
            self.refresh_album_list()  # Refresh the display.
    
    def edit_account(self):
        """Open a window to allow the user to edit their account details."""
        current_user = self.controller.current_user
        if not current_user:
            messagebox.showerror("Error", "No user is logged in.")
            return
        
        # Create a new window for editing account details.
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Account")
        edit_win.configure(background="#f0f0f0")
        edit_win.grab_set()  # Make the window modal.
        
        # Create fields for current password, new username, and new password.
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
            """Update the user's account details after validating current credentials."""
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
                # Change the username by updating the key in the users dictionary.
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
                self.controller.users[updated_username]["password"] = new_pass  # Update the password.
            
            self.controller.save_users()  # Save updated user data.
            messagebox.showinfo("Success", "Account updated successfully!")
            edit_win.destroy()  # Close the edit account window.
        
        ttk.Button(edit_win, text="Update Account", command=update_account).grid(row=4, column=0, columnspan=2, pady=10)
    
    def logout(self):
        """Log out the current user and reset UI elements accordingly."""
        self.controller.current_user = None  # Clear the controller's current user.
        # Reset global login state variables.
        global current_user, is_logged_in
        current_user = None
        is_logged_in = False
        print(f"DEBUG: User logged out. is_logged_in = {is_logged_in}")
        messagebox.showinfo("Logout", "You have been logged out.")
        # Hide buttons and fields that are only visible to logged in users.
        self.controller.favourites_button.pack_forget()
        self.controller.search_button.pack_forget()
        self.controller.search_bar.pack_forget()
        self.controller.filter_dropdown.pack_forget()
        self.refresh_button.grid_remove()
        # Return to the login frame.
        self.controller.show_frame("LoginFrame")

if __name__ == "__main__":
    app = AlbumCatalogApp()  # Create an instance of the main application.
    app.mainloop()  # Start the Tkinter event loop.
