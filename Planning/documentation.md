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

# System Architecture
![Screenshot 2025-03-13 112310](https://github.com/user-attachments/assets/1f9ce149-e0f3-41f3-b905-da9d08cb6c67)
![Screenshot 2025-03-04 213451](https://github.com/user-attachments/assets/dcf2bc50-284f-4300-8599-4d676abfbd3d)
![Screenshot 2025-03-01 180753](https://github.com/user-attachments/assets/fafed00a-bc28-443d-a95d-b1b30a71743a)

# 📌 Setup Guide: Install, Configure, and Run BrightByte Music Cataloging Software

## 📖 Overview
BrightByte Music Cataloging Software is a Python-based application that helps users manage and browse a catalog of music albums. This guide provides step-by-step instructions to install, configure, and run the software.

---
## 🔧 Prerequisites
Before proceeding, ensure the following dependencies are installed:

### ✅ Python 3
Check if Python is installed by running:
```sh
python --version
```
If not installed, download it from [python.org](https://www.python.org/downloads/).

### ✅ pip (Python Package Manager)
Verify pip installation with:
```sh
pip --version
```

### ✅ Git
Ensure Git is installed by running:
```sh
git --version
```
If not installed, download Git from [git-scm.com](https://git-scm.com/downloads).

---
## 📥 Installation & Setup

### 1️⃣ Clone the Repository
Open a terminal and run:
```sh
git clone https://github.com/Massiafz/Project.git
cd Project
```

### 2️⃣ Install Dependencies
Install required Python libraries with:
```sh
pip install -r requirements.txt
```
Alternatively, if a `Makefile` is provided, install dependencies using:
```sh
make install
```
> 💡 **Note:** Windows users without `make` should use `pip install -r requirements.txt`.

---
## 🚀 Running the Software

### 1️⃣ Run the Program
Navigate to the directory containing `main.py`:
```sh
cd Code
```
Run the application with:
```sh
python main.py
```
Or explicitly using Python 3:
```sh
python3 main.py
```

### 2️⃣ Running Data Processing & Analysis *(If applicable)*
If data processing is included, run:
```sh
make process
make plot
```
> 💡 **Note:** Windows users may need to replace `make` commands with direct Python script execution.

---
## ✅ Running Tests *(If applicable)*
If tests exist, execute:
```sh
make test
```
> *(Currently, no `test` target is defined in the `Makefile`. Add it if needed.)*

---
## 🧹 Cleaning Up
To remove temporary files and cached data:
```sh
make clean
```
> 💡 You may be prompted for confirmation before deletion.

---
## 📌 Additional Notes
- Ensure all required data files (e.g., `data.csv`) are in the correct directories before running the application.
- Windows users may need to use `python` instead of `python3`, and `pip` instead of `pip3`.
- Additional setup may be required for deployment.

---
🎵 **Enjoy using BrightByte Music Cataloging Software!** 🎶


## 🛠️ Troubleshooting & Debugging Guide

### 📖 Overview
This guide provides solutions to common installation, configuration, and runtime issues encountered while using this software. Follow the steps outlined below to diagnose and resolve problems efficiently.

---

## 🔧 1. Installation Issues

### ❌ Problem: Error Installing Dependencies
**Solution:**
1. Verify that Python and pip are correctly installed:
   ```sh
   python --version
   pip --version
   ```
2. If these commands fail, install or reinstall Python from the [official Python website](https://www.python.org/).
3. If errors occur when installing from `requirements.txt`, try upgrading pip:
   ```sh
   python -m pip install --upgrade pip
   ```
4. Ensure all package names are correctly specified in `requirements.txt`.

### ❌ Problem: Makefile Commands Fail (Linux/macOS)
**Solution:**
1. Check if `make` is installed:
   ```sh
   make --version
   ```
2. If missing, install it using:
   - **Ubuntu/Debian:**
     ```sh
     sudo apt install make
     ```
   - **macOS (Homebrew):**
     ```sh
     brew install make
     ```

---

## 🚀 2. Running Issues

### ❌ Problem: Application Does Not Start
**Solution:**
1. Ensure you are in the correct project directory:
   ```sh
   cd path/to/project/Code
   ```
2. Try running the script manually:
   ```sh
   python main.py
   ```
3. If dependencies are missing, reinstall them:
   ```sh
   pip install -r requirements.txt
   ```

### ❌ Problem: Missing Data Files (e.g., `data.csv`)
**Solution:**
1. Verify that all required data files exist in the expected directories.
2. If missing, obtain the necessary files from the project owner or use sample data if available.

---

## ⚙️ 3. Configuration Issues

### ❌ Problem: Configuration Settings Not Applying
**Solution:**
1. Ensure configuration files (e.g., JSON, CSV) are in the correct directory.
2. Check if they contain valid and properly formatted data.
3. If using environment variables, verify that API keys or database credentials are correctly specified.

---

## 🐞 4. Debugging Tips

### ❌ Problem: Unexpected Behavior or Crashes
**Solution:**
1. **Check Error Logs:** Review output logs for error messages.
2. **Enable Debug Mode:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
3. **Reproduce the Error:** Identify the exact steps leading to the issue.
4. **Use a Debugger:**
   ```python
   import pdb; pdb.set_trace()
   ```

---

## 🔍 5. Common Errors and Solutions

### ❌ Error: `ModuleNotFoundError`
**Solution:**
1. Ensure all dependencies are installed:
   ```sh
   pip install -r requirements.txt
   ```
2. Reinstall a specific missing package:
   ```sh
   pip install <module_name>
   ```

### ❌ Error: Permission Denied (on Files or Directories)
**Solution:**
1. Ensure the user has the necessary permissions:
   ```sh
   chmod 777 <file_or_directory>
   ```
2. Run the command with administrator privileges:
   - **Windows:** Open Command Prompt as Administrator.
   - **Linux/macOS:** Prefix commands with `sudo`:
     ```sh
     sudo python main.py
     ```

---

## 📞 6. Contact and Support
If you continue to face issues, provide the following details when seeking support:
- **Error messages or logs**
- **Your operating system and Python version**
- **Steps to reproduce the issue**

This guide should help resolve most common issues efficiently. 🚀

## 📝 User / In-Application Documentation

### 📖 Overview
This section provides the necessary information for users to effectively interact with the software. It includes an overview of the application’s key features, how to use them, and what to expect at different stages of interaction.

---

## 🚀 1. Getting Started

### 🎵 Launching the Application
Once the software is installed and configured, launch the application by running the `main.py` file. This will open the program’s user interface (UI), where you can start interacting with the cataloging system.

```sh
python main.py
```

### 📂 First-Time Setup
If this is your first time using the software, you may be prompted to upload your music data (e.g., album names, artist details). Ensure your files are in the correct format (CSV or another supported format) and follow the on-screen instructions for the initial setup.

---

## 🔑 2. Key Features

### 🎼 Album Cataloging
Users can add new albums to the catalog by specifying details such as album name, artist, release date, and genre. The interface provides fields to input this data.

#### How to Add an Album:
1. Click the **“Add Album”** button in the main menu.
2. Fill out the album details in the form (e.g., album name, artist, genre).
3. Click **“Save”** to add the album to the catalog.

### 🔍 Search & Filter
The application allows users to search for specific albums or filter by artist, genre, or release year.

#### How to Search:
1. Enter the search term in the search bar at the top of the screen.
2. Results will automatically update based on your search query.

#### How to Filter:
1. Click the **“Filter”** button.
2. Choose the filter options (e.g., filter by genre, artist, etc.).
3. Apply the filter to see relevant results.

### 📑 Viewing Albums
Once you’ve added albums, you can view the entire catalog in a table or grid layout, depending on your preferences. The view can be sorted by album name, artist, or year of release.

---

## ⚙️ 3. Settings & Configuration

### 🎨 Customizing the Interface
Users can customize the application’s layout, theme, or language by navigating to the settings section. There, they can choose display preferences such as switching between light and dark modes.

### 💾 Data Backup & Import/Export
To ensure data is safely stored, users can export their catalog to a CSV file. This allows you to back up the data or share it with others.

#### How to Export Data:
1. Go to the **“Settings”** menu.
2. Select the **“Export Data”** option.
3. Choose the file format (e.g., CSV) and save the file to your desired location.

---

## 🛠️ 4. Troubleshooting & Support
If you encounter issues using the application, refer to the **Troubleshooting & Debugging Guide** section of the README, or contact support for further assistance. Common issues include missing data files, improper configurations, or unexpected application behavior.

---

## 🏆 Who Should Read This?
This documentation is intended for users of all technical levels. Whether you’re a beginner or an experienced user, this guide will help you understand how to operate the software effectively. The **Getting Started** section is particularly useful for new users, while the **Advanced Features** section provides more in-depth instructions for experienced users.

---

## ✍️ Who Wrote This?
This user documentation is written by the development team with contributions from technical writers to ensure clarity and accessibility. Developers have provided technical explanations, while the content has been tailored to user needs based on feedback and common queries.


# BrightByte Music Cataloging Software - User Manual

## 1. Introduction
Welcome to the BrightByte Music Cataloging Software! This application helps users efficiently catalog their music collection, search for specific albums, and manage album data. This guide provides step-by-step instructions on installation, setup, and common tasks.

## 2. Installation & Setup
### 2.1 Clone the Repository
Ensure Git is installed on your system. If not, download and install it from [git-scm.com](https://git-scm.com/).

Clone the repository to your local machine using:
```bash
git clone https://github.com/Massiafz/Project.git
```
Navigate to the project directory:
```bash
cd Project
```

### 2.2 Install Dependencies
Open a terminal in the project directory and run:
```bash
make install
```
This will install the necessary Python libraries and other dependencies.

### 2.3 Running the Software
Start the application by executing:
```bash
python main.py
```
This launches the BrightByte Music Cataloging Software and opens the main window.

## 3. Using the Software
### 3.1 Logging In or Signing Up
- **Login:** Enter your username and password on the login page and click "Login."
- **Sign Up:** Click "Sign Up," fill in the necessary details, and submit the form.
- **Continue as Guest:** Click "Continue as Guest" to browse the catalog without logging in.

### 3.2 Adding an Album to the Catalog
1. Navigate to the Album Catalog page.
2. Click "Add Album" to open the album form.
3. Enter the following details:
   - **Album Name:** Title of the album
   - **Artist Name:** Name of the artist
   - **Release Date:** Format YYYY-MM-DD
   - **Genres:** Specify genres (e.g., Rock, Pop)
   - **Cover URL:** Provide a URL for the album cover
4. Click "Save" to add the album.

### 3.3 Searching and Filtering Albums
- **Search:** Use the search bar to find albums by name, artist, or other details.
- **Apply Filters:**
  1. Click the "Filter" dropdown menu.
  2. Choose filters (e.g., Album Name, Artist, Genres, Release Date).
  3. The search results will update accordingly.

### 3.4 Viewing and Managing the Album Catalog
- **View Albums:** The catalog displays album details like name, artist, release date, and genre.
- **Sort Albums:** Click column headers to sort by album name or release date.
- **Edit or Delete Albums:**
  - Click "Edit" to modify album details, then "Save."
  - Click "Delete" to remove an album (confirmation required).

### 3.5 Exporting and Importing Data
- **Export Data:**
  1. Go to "Settings."
  2. Click "Export Data."
  3. Choose a format (e.g., CSV) and save the file.
- **Import Data:**
  1. Go to "Settings."
  2. Click "Import Data."
  3. Upload a properly formatted CSV file.

### 3.6 Customizing the Application
- **Change Theme:** Navigate to "Settings > Appearance" to switch between light and dark themes.
- **Language Settings:** Change the application language in "Settings."

## 4. Troubleshooting
- **Application Doesn’t Open:** Ensure dependencies are installed and Python is correctly set up.
- **Search Results Are Empty:** Check the query and filters. Ensure the album exists in the catalog.
- **Data Import Issues:** Verify CSV formatting (columns like Album Name, Artist Name, etc.).

## 5. Logging Out and Exiting
- Click "Log Out" in the navigation bar to log out.
- Close the window or use a keyboard shortcut (e.g., Alt+F4 on Windows) to exit.

## 6. Conclusion
Now that you've set up and learned to use BrightByte Music Cataloging Software, you can easily manage your album collection. If you need assistance, refer to the troubleshooting section or contact support.








