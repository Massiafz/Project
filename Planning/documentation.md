# Documentation Plan

### Developer Documentation:
Moksh, Massi, and Vincent will be responsible for writing and maintaining the developer documentation, including code documentation, system architecture, and setup guides.

### User / In-Application Documentation:
Massi, Bach, and Jason will also create the user manual, FAQs, and tooltips, ensuring the customer has clear guidance on using the album cataloging system.

## Code Documentation: 

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
