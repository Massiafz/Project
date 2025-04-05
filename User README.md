# User README

## Welcome to BrightByte Music Cataloging Software

BrightByte is a desktop application designed for music enthusiasts to manage and explore a catalog of music albums. Whether you are logging in to manage your personal album list or browsing as a guest, the software offers a simple and interactive way to handle album information.

## Getting Started

### Step 1: Clone the Repository

Open your terminal or command prompt and run the following command:
```bash
git clone https://github.com/Massiafz/Project.git
```

### Step 2: Navigate to the Code Directory

Change your directory to where the application code is located:
```bash
cd Project/code
```

### Step 3: Run the Executable

- **For Mac/Linux Users:**
  ```bash
  ./brightbyte-linux
  ```
- **For Windows Users:**
  ```batch
  ./brightbyte-windows.exe
  ```
  Windows and Linux are able to run the executable from the file explorer but mac is not able to.

*These scripts will set up and launch the application on your system.*

## Features

### User Authentication

- **Login:** Enter your username and password to access full features.
- **Sign Up:** Create a new account by providing a username, email, and password.
- **Guest Access:** Continue as a guest with limited functionality (e.g., unable to add or edit albums).

### Album Catalog

- **View Albums:** Browse a list of albums with details such as artist name, release date, and genres.
- **Search & Filter:** Use the search bar and filter options to find albums by Album Name, Artist Name, Genres, or Release Date.
- **Album Details:** Click on an album to view more details and track listings.

### Album Management (For Logged-In Users)

- **Add Album:** Use the “Add Album” option to input album details, select or import an album cover, and add track listings.
- **Edit Album:** Modify album information and update track details.
- **Delete Album:** Remove albums from your catalog after confirming your choice.
- **Favourites:** Mark albums as favourites to quickly access your preferred music.

### Additional Functions

- **Track List View:** Open a dedicated window to view the tracklist for any selected album.
- **Edit Account:** Update your account details including password and username.
- **Logout:** Easily log out of your account, which resets the interface to the login screen.

## User Interface Overview

- **Navigation Bar:**  
  Located at the top of the window, featuring the BrightByte logo and title. Once logged in, additional buttons (Search, Favourites) become visible.
  
- **Search Area:**  
  A text box and filter dropdown allow you to search through the album catalog using various criteria.
  
- **Album List:**  
  A scrollable canvas displays album covers and details. Clicking on an album highlights it and allows further actions like editing or viewing tracks.

- **Control Buttons:**  
  Options for album actions (Add, Edit, Delete, Favourite, Unfavourite) and account management (Edit Account, Logout) are available below the album list.

## Troubleshooting

- **Image Loading:**  
  If album cover images do not load, a default image will be displayed.
- **Missing Data Files:**  
  Ensure that `users.json` and `cleaned_music_data.csv` exist in the project directory. The application will create empty files if they are not present.
- **Platform-Specific Issues:**  
  The build scripts are designed for Mac, Linux, and Windows. If you encounter issues, verify that you have the correct permissions to execute the scripts.

## Contact & Support

For further assistance or to report bugs, please contact the Technical Manager: massi.afzal@ontariotechu.net
