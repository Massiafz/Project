# Documentation Plan

## Developer Documentation:
Moksh, Massi, and Vincent will be responsible for writing and maintaining the developer documentation, including code documentation, system architecture, and setup guides.

## User / In-Application Documentation:
Massi, Bach, and Jason will also create the user manual, FAQs, and tooltips, ensuring the customer has clear guidance on using the album cataloging system.

# Code Documentation: 

```
class AlbumCatalogApp(tk.Tk):
    """
    The main application window for the BrightByte Music Cataloging Software.

    This class initializes the UI, loads user and album data, and manages different frames
    (Login, Signup, and Catalog). It also binds global mouse wheel events to enable smooth 
    scrolling in the catalog.
    """

    def on_enter_pressed(self, event):
        """
        Triggers the search function when the Enter key is pressed in the search bar.

        Args:
            event (tk.Event): The event object containing information about the key press.
        
        Returns:
            str: "break" to prevent the default behavior of inserting a newline in the search bar.
        """
        self.search()
        return "break"

    def on_global_mousewheel(self, event):
        """
        Redirects mouse wheel scrolling events to the catalog's canvas if it is visible.

        This ensures that users can scroll through the album catalog even if they are not
        directly hovering over the canvas.

        Args:
            event (tk.Event): The event object containing information about the scroll action.
        """
        catalog = self.frames["CatalogFrame"]
        if catalog.winfo_ismapped():
            canvas = catalog.canvas
            if event.num == 4:  # Linux scroll up
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux scroll down
                canvas.yview_scroll(1, "units")
            else:  # Windows/Mac scroll
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_users(self):
        """
        Loads user account information from a JSON file.

        Returns:
            dict: A dictionary containing stored user credentials (username, email, password).
        """
        if os.path.exists(USERS_JSON):
            with open(USERS_JSON, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_users(self):
        """
        Saves the current user data to the JSON file.

        This method ensures that new users or changes to user data persist across sessions.
        """
        with open(USERS_JSON, "w") as f:
            json.dump(self.users, f, indent=4)

    def save_albums(self):
        """
        Saves album data to a CSV file.

        This method ensures that any modifications to the album catalog are preserved for future use.
        """
        with open(ALBUMS_CSV, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, ["Ranking", "Album", "Artist Name", "Release Date",
                                              "Genres", "Average Rating", "Number of Ratings",
                                              "Number of Reviews", "Cover URL"])
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
        """
        Loads album data from a CSV file into a list of dictionaries.

        Each album entry contains metadata such as ranking, album name, artist name, genres,
        and release date.

        Returns:
            list: A list of dictionaries, where each dictionary represents an album's details.
        """
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
        Filters the album catalog based on a search query and the selected filter criteria.

        Args:
            search_query (str): The user-inputted search string.

        Sets:
            self.search_results: A filtered list of albums matching the search criteria.
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
                return search_query in album.get("Release Date", "").split("-")
            return False

        self.search_results = list(filter(matches_filter, self.albums.copy()))

    def show_frame(self, frame_name):
        """
        Switches the active frame in the application.

        Args:
            frame_name (str): The name of the frame to display.

        If switching to the CatalogFrame, the search filter dropdown is made visible.
        Otherwise, it is hidden.
        """
        frame = self.frames[frame_name]
        if frame_name == "CatalogFrame":
            self.filter_dropdown.pack(side="right", padx=10)
            frame.refresh_album_list()
        else:
            self.filter_dropdown.pack_forget()
        frame.tkraise()

    def search(self, no_refresh=False):
        """
        Performs a search operation based on the user’s query in the search bar.

        Args:
            no_refresh (bool, optional): If True, prevents the catalog from refreshing immediately.

        The method updates the search results and displays an error if no results are found.
        """
        query = self.search_bar.get("1.0", tk.END)
        self.load_search_query(query)
        if query.strip() and not self.search_results:
            messagebox.showerror("No Results", "No relevant results found for your search query.")
        frame = self.frames["CatalogFrame"]
        if not no_refresh:
            frame.refresh_album_list()
        frame.tkraise()

    def refresh_catalog(self):
        """
        Clears the search bar and resets the album catalog view.

        This method restores the catalog to its original state, displaying all albums.
        """
        self.search_bar.delete("1.0", tk.END)
        self.search("")
```

```
def login(self):
    """
    Handles user login authentication.

    Retrieves the username and password from entry fields and verifies them
    against the stored user credentials. If valid, the user is logged in,
    the UI is updated to show catalog-related controls, and the catalog frame
    is displayed. Otherwise, an error message is shown.
    """
    username = self.username_entry.get()
    password = self.password_entry.get()
    users = self.controller.users
    if username in users and users[username]["password"] == password:
        self.controller.current_user = username
        messagebox.showinfo("Login", "Login successful!")
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
    """
    Allows the user to proceed without logging in.

    Sets the current user as 'Guest' and updates the UI to display catalog-related
    controls before showing the catalog frame.
    """
    self.controller.current_user = "Guest"
    messagebox.showinfo("Guest Login", "Continuing as guest.")
    self.controller.search_button.pack(side="right", padx=10)
    self.controller.search_bar.pack(side="right")
    self.controller.filter_dropdown.pack(side="right", padx=10)
    self.controller.frames["CatalogFrame"].refresh_button.grid()
    self.controller.show_frame("CatalogFrame")

def signup(self):
    """
    Handles new user registration.

    Retrieves input from the signup form, validates the fields (e.g., checking
    for empty fields, email format, and password confirmation), and adds the new
    user to the stored credentials. If successful, the user is redirected to the login page.
    """
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

def refresh_album_list(self):
    """
    Refreshes the album catalog display.

    Clears the current album list and reloads album data from the controller.
    Uses a thread pool to handle image loading efficiently and updates the UI accordingly.
    """
    for existingAlbumItem in self.album_items:
        if existingAlbumItem is not None:
            existingAlbumItem.destroy()
    self.album_items = []
    if self.controller.search_results is not None:
        album_arr_to_use = self.controller.search_results
    else:
        album_arr_to_use = self.controller.albums
    for _ in range(len(album_arr_to_use)):
        self.album_items.append(None)
    self.album_cover_images = [None] * len(album_arr_to_use)
    self.selected_album = None
    currentRow = 0
    self.refresh_album_threads = []
    for index, album in enumerate(album_arr_to_use):
        future = self.executor.submit(self.thread_function_refresh_albums, index, album, currentRow)
        self.refresh_album_threads.append(future)
        currentRow += 1

def select_album(self, event, albumItem: tk.Frame):
    """
    Highlights the selected album in the catalog.

    Changes the background color of the selected album to indicate selection,
    while resetting all other albums to the default color.
    """
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
```

```
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re

class AlbumCatalog:
    
    def add_album(self):
        """
        Opens a window to add a new album to the catalog.

        The user can input details such as:
        - Artist Name
        - Album Name
        - Release Date
        - Genres
        - Album Cover (optional, via file selection dialog)

        If the required fields (Artist Name, Album Name, Release Date) are missing, an error message is shown.

        The new album is then added to the controller's album list and saved.

        Returns:
            None
        """
        pass  # Function implementation here

    def edit_album(self):
        """
        Opens a window to edit an existing album in the catalog.

        The user can modify:
        - Artist Name
        - Album Name
        - Release Date
        - Genres
        - Album Cover (either via URL or file selection)

        If the required fields (Artist Name, Album Name, Release Date) are missing, an error message is shown.

        The album details are updated in the controller and saved.

        Returns:
            None
        """
        pass  # Function implementation here

    def delete_album(self):
        """
        Deletes the currently selected album from the catalog.

        If no album is selected, an error message is displayed.
        A confirmation dialog is presented before deletion.

        The album is then removed from the controller's album list and saved.

        Returns:
            None
        """
        pass  # Function implementation here

    def edit_account(self):
        """
        Opens a window to allow the current user to edit their account details.

        The user can:
        - Change their username (if available)
        - Update their password (if correctly confirmed)

        If the current password is incorrect, an error message is shown.
        If the new password and confirmation do not match, an error is displayed.

        After validation, changes are saved to the user database.

        Returns:
            None
        """
        pass  # Function implementation here

    def logout(self):
        """
        Logs out the current user and returns to the login screen.

        - The logged-in user is cleared from the system.
        - The UI elements specific to a logged-in user are hidden.
        - The login frame is displayed.

        Returns:
            None
        """
        pass  # Function implementation here
```
```
def favourite_album(self):
    """
    Toggles the favourite status of the selected album for the logged-in user.

    If the user is not logged in, an error message is displayed.
    If no album is selected, an error message is shown.
    The album is added to or removed from the user's favourites list.
    Updates are saved to the user database.

    Returns:
        None
    """
    pass  # Function implementation here

def unfavourite_album(self):
    """
    Removes the selected album from the user's favourites list.

    If the user is not logged in, an error message is displayed.
    If no album is selected, an error message is shown.
    If the album is not in the favourites list, an error is displayed.
    The album is removed from the favourites list and updates are saved.

    Returns:
        None
    """
    pass  # Function implementation here

def favourites(self):
    """
    Retrieves and displays the user's favourite albums.

    If the user has no favourite albums, an error message is displayed.
    The favourite albums are added to the search results list.
    The catalog frame is refreshed and displayed.

    Returns:
        None
    """
    pass  # Function implementation here

def refresh_catalog(self):
    """
    Clears the search bar and refreshes the album catalog.

    - The search bar text is cleared.
    - The catalog is refreshed by performing a new search.

    Returns:
        None
    """
    pass  # Function implementation here
```
# System Architecture
![Screenshot 2025-03-13 112310](https://github.com/user-attachments/assets/1f9ce149-e0f3-41f3-b905-da9d08cb6c67)
![Screenshot 2025-03-04 213451](https://github.com/user-attachments/assets/dcf2bc50-284f-4300-8599-4d676abfbd3d)
![Screenshot 2025-03-01 180753](https://github.com/user-attachments/assets/fafed00a-bc28-443d-a95d-b1b30a71743a)





