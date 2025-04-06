# Developer README: Technical Breakdown of BrightByte Music Cataloging Software

## Overview

BrightByte Music Cataloging Software is a Python desktop application built using Tkinter. It provides a comprehensive GUI for managing a music album catalog, including user authentication, album management (adding, editing, deleting), search/filter functionality, and asynchronous image loading. This document offers a detailed technical breakdown of the code, its architecture, and the main components.

### Developed By BrightByte:
- **Project Manager:** Bach Nguyen (100926453)
- **Technical Manager:** Massi Afzal (100911029)
- **Software Quality Lead:** Moksh Patel (100916422)
- **Back-End Lead:** Jason Guan (100927182)
- **Front-End Lead:** Vincent Tseng (100912590)

## Getting Started

### Step 1: Clone the Repository

Open your terminal or command prompt and run the following command:
```bash
git clone https://github.com/Massiafz/Project.git
```

### Step 2: Navigate to the Code Directory

Change your directory to where the application code is located:
```bash
cd Project
```

### Step 3: Run the Executable

- **For Linux Users:**
  ```bash
  ./brightbyte-linux
  ```
- **For Windows Users:**
  ```batch
  ./brightbyte-windows
  ```
- **For Mac Users:**
  ```batch
  ./brightbyte-mac
  ```
  Windows and Linux are able to run the executable from the file explorer but mac is not able to.

*These scripts will set up and launch the application on your system.*
## Project Structure

- **/Project/code/main.py**  
  This is the single main file that contains:
  - **Module Imports:** GUI components, file and network operations, image processing, concurrency, and regular expressions.
  - **Global Constants & Variables:** File paths, UI colour definitions, precompiled URL regex, and login state variables.
  - **Helper Functions:** For loading users, handling login/logout, and checking login status.
  - **Main Application Class (`AlbumCatalogApp`):** Inherits from `tk.Tk` and manages the overall application window and frame switching.
  - **GUI Frames:**  
    - `LoginFrame`: For user authentication (login/guest).
    - `SignupFrame`: For new user registration.
    - `CatalogFrame`: For displaying and managing the album catalog, including search and album operations.

## Detailed Code Breakdown

### Module Imports and Global Definitions

- **Imports:**
  - **Tkinter & ttk:** For building and styling the GUI.
  - **filedialog & messagebox:** For file selection dialogs and popup messages.
  - **CSV & JSON:** For reading/writing album data and user data.
  - **OS & RE:** For file operations and validating URL formats.
  - **PIL (Pillow):** For image processing (resizing, loading images into Tkinter).
  - **Networking:** `urlopen` and `Request` to fetch remote album cover images.
  - **Concurrency:** `ThreadPoolExecutor` to perform asynchronous image loading to keep the UI responsive.
  
- **Global Constants:**
  - `USERS_JSON` and `ALBUMS_CSV`: File paths for persistent storage.
  - UI colour constants: For primary backgrounds, navigation bar, and shadow effects.
  - `URL_PATTERN`: A precompiled regular expression to validate URLs.
  
- **Global Variables:**
  - `current_user` and `is_logged_in`: Used to track the authentication state.

### Helper Functions

- **load_users:**  
  Checks if the `users.json` file exists and loads user data. If not, it creates an empty file and returns an empty list.

- **login:**  
  Iterates through the user list to validate credentials. On success, it updates `current_user` and sets `is_logged_in` to `True`.

- **logout:**  
  Resets `current_user` and `is_logged_in`, displays a logout message, and attempts to reset UI elements (such as hiding search widgets) before returning to the login frame.

- **check_login:**  
  Returns the current login state (whether a user is authenticated).

### The `AlbumCatalogApp` Class

This class serves as the central controller of the application by extending `tk.Tk`.

#### Initialization (`__init__`)

- **Window Setup:**  
  Sets the title, window size, and attempts to load a custom icon using Pillow. A fallback dummy image is created if the icon is not available.
  
- **Navigation Bar Creation:**  
  Builds a top navigation bar with a logo, title, and placeholders for additional UI elements (search, favourites) that become visible upon login.
  
- **Data Loading:**  
  Calls helper functions to load user data (`load_users()`) and album data (`load_albums_from_csv()`) from CSV.
  
- **Frame Management:**  
  Initializes the three primary frames (`LoginFrame`, `SignupFrame`, and `CatalogFrame`) within a container. Initially, the `LoginFrame` is raised.
  
- **Global Bindings:**  
  Sets up mouse wheel event bindings for scrolling through the album catalog.

#### Data Management Functions

- **load_albums_from_csv:**  
  Reads the album catalog from a CSV file, creating a list of dictionaries—each representing an album with fields such as "Album", "Artist Name", "Release Date", etc.

- **save_albums:**  
  Writes the current state of the album catalog back to the CSV file.

#### Search and Navigation

- **load_search_query:**  
  Filters the album list based on the user’s search query and selected filter criteria (e.g., Album Name, Artist Name, Genres, or Release Date).
  
- **search:**  
  Retrieves input from the search bar, applies filtering, refreshes the album catalog display, and raises the `CatalogFrame`.

- **show_frame:**  
  Raises a specific frame (e.g., switching between Login, Signup, and Catalog) and manages the visibility of UI components like the filter dropdown.

### GUI Frames

#### LoginFrame

- **Components:**  
  Input fields for username and password, along with buttons for Login, switching to Signup, and guest access.
  
- **Functionality:**  
  Validates credentials using the `login` function, updates global state, and makes search/favourites buttons visible on successful login.

#### SignupFrame

- **Components:**  
  Input fields for username, email, password, and password confirmation.
  
- **Functionality:**  
  Validates that inputs are non-empty, passwords match, and that the email is in the correct format before creating a new user account and saving it to `users.json`.

#### CatalogFrame

- **Main Features:**
  - **Display of Albums:**  
    Uses a scrollable canvas and a nested frame to display each album's cover image and details (artist, album name, genres, release date).
    
  - **Asynchronous Image Loading:**  
    Utilizes `ThreadPoolExecutor` to load album cover images in separate threads. Covers are cached to prevent repeated loading.
    
  - **Album Operations:**  
    Implements functions for viewing the track list, favouriting/unfavouriting, adding new albums, editing, and deleting albums. The UI employs dialogs for file selection and user input.
    
  - **Control Buttons:**  
    Provides buttons for various operations including track viewing, album editing, and account management.

### Multithreading and Performance

- **ThreadPoolExecutor:**  
  The CatalogFrame uses a pool of 4 worker threads to load album images asynchronously. This prevents the UI from freezing while images are loaded from either local storage or remote URLs.
  
- **Image Caching:**  
  A cache is maintained to store loaded images, reducing redundant network requests and image processing operations on subsequent accesses.

### Build Files: 

For Linux: 
```
./build-linux.sh
```
For Windows: 
```
./build-windows.bat
```
For Mac:
```
./build-mac.sh
```

## Conclusion

This technical breakdown covers the structure and functionality of BrightByte Music Cataloging Software. The application is designed to be a self-contained solution for managing a music catalog, with emphasis on user interaction, data persistence, and responsive UI through asynchronous processing. Each module and function is carefully structured to support a robust and user-friendly experience.

