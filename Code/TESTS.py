"""
Test Suite for BrightByte Music Cataloging Software
======================================================

This suite has been updated to simulate proper login state, correctly reference global variables,
and now includes tests for the favourites functionality.
"""

import unittest                   # Import the unittest module for creating and running tests.
import tempfile                   # Import tempfile to create temporary files and directories.
import os                         # Import os for file and directory operations.
import json                       # Import json to read/write JSON files.
import csv                        # Import csv for CSV file operations.
import tkinter as tk              # Import tkinter for GUI operations (used in the main application).
from tkinter import ttk           # Import ttk for themed tkinter widgets.
from unittest.mock import patch   # Import patch to replace parts of the system under test with mock objects.
from PIL import Image             # Import Image from Pillow to work with images.
import main                       # Import the main application module (assumed to be in main.py).

class TestAlbumCatalogApp(unittest.TestCase):
    def setUp(self):
        """
        Setup temporary files and override global constants for testing.
        Also, patch out image loading and track Toplevel window creation.
        """
        # Create a temporary directory for test files.
        self.test_dir = tempfile.TemporaryDirectory()
        # Define paths for the temporary users and albums files.
        self.users_file = os.path.join(self.test_dir.name, "users.json")
        self.albums_file = os.path.join(self.test_dir.name, "cleaned_music_data.csv")
        
        # Override the file paths in the main module to point to our temporary files.
        main.USERS_JSON = self.users_file
        main.ALBUMS_CSV = self.albums_file

        # Write a sample album CSV file with one album entry for testing.
        with open(self.albums_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Ranking", "Album", "Artist Name", "Release Date",
                                                     "Genres", "Average Rating", "Number of Ratings",
                                                     "Number of Reviews", "Cover URL"])
            writer.writeheader()  # Write header row to the CSV.
            writer.writerow({
                "Ranking": "1",
                "Album": "Test Album",
                "Artist Name": "Test Artist",
                "Release Date": "2021-01-01",
                "Genres": "Pop",
                "Average Rating": "5",
                "Number of Ratings": "100",
                "Number of Reviews": "50",
                "Cover URL": ""
            })
        
        # Write an empty users file (JSON) to simulate no existing users.
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump({}, f)
        
        # Patch the Image.open function in the main module to avoid issues with missing image files.
        self.patcher_image_open = patch("main.Image.open", return_value=Image.new("RGB", (125, 75)))
        self.mock_image_open = self.patcher_image_open.start()

        # --- Patch Toplevel creation to track instances ---
        # Initialize a list to store created Toplevel window instances.
        self.created_toplevels = []
        # Save the original tk.Toplevel constructor from the main module.
        self.original_Toplevel = main.tk.Toplevel
        # Define a fake Toplevel constructor that wraps the original and stores each instance.
        def fake_Toplevel(*args, **kwargs):
            instance = self.original_Toplevel(*args, **kwargs)
            self.created_toplevels.append(instance)
            return instance
        # Patch tk.Toplevel in the main module with our fake_Toplevel.
        self.patcher_toplevel = patch("main.tk.Toplevel", side_effect=fake_Toplevel)
        self.mock_toplevel = self.patcher_toplevel.start()
        # ---------------------------------------------------------------

        # Instantiate the main application but do not start the main loop.
        self.app = main.AlbumCatalogApp()
        # Withdraw the window to keep tests headless (no GUI shown).
        self.app.withdraw()

    def tearDown(self):
        """
        Stop patches, destroy the app instance, and clean up temporary files.
        """
        # Stop the patchers to restore original functions.
        self.patcher_image_open.stop()
        self.patcher_toplevel.stop()
        # Destroy the application instance to clean up resources.
        self.app.destroy()
        # Clean up the temporary directory.
        self.test_dir.cleanup()

    # =======================
    # Clear Box Tests (CB)
    # =======================

    def test_load_users_no_file(self):
        """
        CB Test 1: Verify that load_users() returns an empty dict when users.json does not exist.
        """
        # Remove the users file if it exists.
        if os.path.exists(self.users_file):
            os.remove(self.users_file)
        # Call load_users() from the application.
        users = self.app.load_users()
        # Check that an empty dict is returned.
        self.assertEqual(users, {}, "Expected empty dict when users.json does not exist")

    def test_load_users_invalid_json(self):
        """
        CB Test 2: Verify that load_users() handles invalid JSON by returning an empty dict.
        """
        # Write invalid JSON content to the users file.
        with open(self.users_file, "w", encoding="utf-8") as f:
            f.write("invalid json")
        # Call load_users() which should handle the invalid JSON gracefully.
        users = self.app.load_users()
        # Expect an empty dict as the result.
        self.assertEqual(users, {}, "Expected empty dict when users.json contains invalid JSON")

    def test_load_albums_from_csv_valid(self):
        """
        CB Test 3: Verify that load_albums_from_csv() correctly parses a valid CSV file.
        """
        # Call load_albums_from_csv() to load albums from the sample CSV.
        albums = self.app.load_albums_from_csv()
        # Assert that there is one album loaded.
        self.assertEqual(len(albums), 1, "Expected one album in CSV")
        # Verify that the album name matches the sample data.
        self.assertEqual(albums[0]["Album"], "Test Album", "Album name should match sample CSV data")

    # ============================
    # Translucent Box Tests (TB)
    # ============================

    def test_login_success(self):
        """
        TB Test 4: Simulate a successful login by inserting valid credentials.
        """
        # Pre-populate the application's user dictionary with valid credentials.
        self.app.users = {"testuser": {"password": "pass123", "email": "test@example.com"}}
        # Access the LoginFrame from the application's frames.
        login_frame = self.app.frames["LoginFrame"]
        # Clear and set the username entry field.
        login_frame.username_entry.delete(0, tk.END)
        login_frame.username_entry.insert(0, "testuser")
        # Clear and set the password entry field.
        login_frame.password_entry.delete(0, tk.END)
        login_frame.password_entry.insert(0, "pass123")
        # Call the login method to attempt authentication.
        login_frame.login()
        # Verify that current_user is set correctly after a successful login.
        self.assertEqual(self.app.current_user, "testuser", "Login should set current_user to 'testuser'")

    def test_signup_creates_account(self):
        """
        TB Test 5: Simulate the sign-up process using valid user information.
        """
        # Access the SignupFrame from the application's frames.
        signup_frame = self.app.frames["SignupFrame"]
        # Clear and set the username entry field.
        signup_frame.username_entry.delete(0, tk.END)
        signup_frame.username_entry.insert(0, "newuser")
        # Clear and set the email entry field.
        signup_frame.email_entry.delete(0, tk.END)
        signup_frame.email_entry.insert(0, "new@example.com")
        # Clear and set the password entry field.
        signup_frame.password_entry.delete(0, tk.END)
        signup_frame.password_entry.insert(0, "newpass")
        # Clear and set the confirm password entry field.
        signup_frame.confirm_password_entry.delete(0, tk.END)
        signup_frame.confirm_password_entry.insert(0, "newpass")
        # Call the signup method to create the new account.
        signup_frame.signup()
        # Verify that the new user is now present in the application's users dictionary.
        self.assertIn("newuser", self.app.users, "Signup should add 'newuser' to the users dictionary")

    def test_add_album_integration(self):
        """
        TB Test 6: Simulate adding an album through the CatalogFrame.
        """
        # Set the application and global login state to simulate a logged-in user.
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True

        # Access the CatalogFrame.
        catalog_frame = self.app.frames["CatalogFrame"]
        # Clear any previously recorded Toplevel windows.
        self.created_toplevels.clear()
        # Call add_album to simulate opening the Add Album window.
        catalog_frame.add_album()
        # Verify that a Toplevel window was created.
        self.assertTrue(len(self.created_toplevels) > 0, "Add Album should open a Toplevel window")
        # Get the most recently created Toplevel window.
        add_win = self.created_toplevels[-1]
        # Retrieve all entry widgets from the Toplevel window.
        entry_widgets = [child for child in add_win.winfo_children() 
                         if isinstance(child, (tk.Entry, ttk.Entry))]
        # Clear all entry fields.
        for widget in entry_widgets:
            widget.delete(0, tk.END)
        # Insert test data into the entry fields.
        entry_widgets[0].insert(0, "Artist Test")
        entry_widgets[1].insert(0, "Album Test")
        entry_widgets[2].insert(0, "2022-02-02")
        entry_widgets[3].insert(0, "Rock")
        # Patch the file dialog to return an empty string (simulate no file selected).
        with patch("main.filedialog.askopenfilename", return_value=""):
            # Retrieve all buttons from the Toplevel window.
            buttons = [child for child in add_win.winfo_children() if isinstance(child, ttk.Button)]
            # Find and invoke the "Save Album" button.
            for btn in buttons:
                if "Save Album" in btn.cget("text"):
                    btn.invoke()
                    break
        # Verify that the new album is added to the application's album list.
        self.assertTrue(any(album["Album"] == "Album Test" for album in self.app.albums),
                        "The album 'Album Test' should be added to the albums list.")

    # =======================
    # Opaque Box Tests (OB)
    # =======================

    def test_end_to_end_workflow(self):
        """
        OB Test 7: Simulate a full end-to-end workflow:
        - Sign up a new user, log in, add an album, search for it, then log out.
        """
        # Simulate user sign-up.
        signup_frame = self.app.frames["SignupFrame"]
        signup_frame.username_entry.delete(0, tk.END)
        signup_frame.username_entry.insert(0, "user1")
        signup_frame.email_entry.delete(0, tk.END)
        signup_frame.email_entry.insert(0, "user1@example.com")
        signup_frame.password_entry.delete(0, tk.END)
        signup_frame.password_entry.insert(0, "password1")
        signup_frame.confirm_password_entry.delete(0, tk.END)
        signup_frame.confirm_password_entry.insert(0, "password1")
        signup_frame.signup()
        self.assertIn("user1", self.app.users, "Sign up should add 'user1' to users.")
        
        # Switch to LoginFrame and simulate login.
        self.app.show_frame("LoginFrame")
        login_frame = self.app.frames["LoginFrame"]
        login_frame.username_entry.delete(0, tk.END)
        login_frame.username_entry.insert(0, "user1")
        login_frame.password_entry.delete(0, tk.END)
        login_frame.password_entry.insert(0, "password1")
        login_frame.login()
        self.assertEqual(self.app.current_user, "user1", "Login should set current_user to 'user1'.")
        
        # Simulate adding an album.
        catalog_frame = self.app.frames["CatalogFrame"]
        self.app.current_user = "user1"
        main.current_user = "user1"
        main.is_logged_in = True

        self.created_toplevels.clear()
        catalog_frame.add_album()
        self.assertTrue(len(self.created_toplevels) > 0, "Add Album should open a Toplevel window")
        add_win = self.created_toplevels[-1]
        entry_widgets = [child for child in add_win.winfo_children() 
                         if isinstance(child, (tk.Entry, ttk.Entry))]
        # Clear and insert new album details.
        entry_widgets[0].delete(0, tk.END)
        entry_widgets[0].insert(0, "Artist1")
        entry_widgets[1].delete(0, tk.END)
        entry_widgets[1].insert(0, "Album1")
        entry_widgets[2].delete(0, tk.END)
        entry_widgets[2].insert(0, "2023-03-03")
        entry_widgets[3].delete(0, tk.END)
        entry_widgets[3].insert(0, "Jazz")
        # Patch file dialog again to simulate no file selection.
        with patch("main.filedialog.askopenfilename", return_value=""):
            buttons = [child for child in add_win.winfo_children() if isinstance(child, ttk.Button)]
            for btn in buttons:
                if "Save Album" in btn.cget("text"):
                    btn.invoke()
                    break
        # Verify the new album is added.
        self.assertTrue(any(album["Album"] == "Album1" for album in self.app.albums),
                        "The album 'Album1' should be added.")
        
        # Simulate searching for the album.
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "Album1")
        self.app.search()
        self.assertTrue(len(self.app.search_results) > 0,
                        "Search should return results for 'Album1'.")
        
        # Simulate logging out.
        catalog_frame.logout()
        self.assertIsNone(self.app.current_user, "Logout should reset current_user to None.")

    def test_guest_user_workflow(self):
        """
        OB Test 8: Simulate a guest user workflow: continue as guest and perform a search.
        """
        # Use the LoginFrame to simulate continuing as a guest.
        login_frame = self.app.frames["LoginFrame"]
        login_frame.continue_as_guest()
        # Verify that current_user is set to 'Guest'.
        self.assertEqual(self.app.current_user, "Guest", "Guest login should set current_user to 'Guest'.")
        # Simulate a search action by the guest user.
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "Test Album")
        self.app.search()
        # Verify search results are returned.
        self.assertTrue(len(self.app.search_results) > 0,
                        "Search should return results for 'Test Album' for a guest user.")
        # Verify that the global is_logged_in flag remains False for guests.
        self.assertFalse(main.is_logged_in, "is_logged_in should be False for guest users.")

    def test_search_functionality(self):
        """
        OB Test 9: Verify search functionality with different filters.
        """
        # Manually set the albums list to a known value.
        self.app.albums = [{
            "Ranking": "1",
            "Album": "Test Album",
            "Artist Name": "Test Artist",
            "Release Date": "2021-01-01",
            "Genres": "Pop",
            "Average Rating": "5",
            "Number of Ratings": "100",
            "Number of Reviews": "50",
            "Cover URL": "",
            "Tracklist": "",
            "Deezer_ID": ""
        }]
        # Test searching by "Album Name".
        self.app.search_filter.set("Album Name")
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "test album")
        self.app.search()
        self.assertEqual(len(self.app.search_results), 1, "Search should find the album by name.")
        
        # Test searching by "Artist Name".
        self.app.search_filter.set("Artist Name")
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "test artist")
        self.app.search()
        self.assertEqual(len(self.app.search_results), 1, "Search should find the album by artist.")

    def test_edit_account(self):
        """
        OB Test 10: Simulate editing a user account.
        """
        # Set up a user with an existing password.
        self.app.users = {"edituser": {"password": "oldpass", "email": "edit@example.com"}}
        self.app.current_user = "edituser"
        main.current_user = "edituser"
        main.is_logged_in = True
        # Clear any previously created Toplevel windows.
        self.created_toplevels.clear()
        # Invoke edit_account from the CatalogFrame.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.edit_account()
        # Verify that a Toplevel window for account editing was created.
        self.assertTrue(len(self.created_toplevels) > 0, "Edit Account should open a Toplevel window")
        # Get the most recent Toplevel window.
        edit_win = self.created_toplevels[-1]
        # Retrieve entry widgets from the Toplevel window.
        entries = [child for child in edit_win.winfo_children() 
                   if isinstance(child, (tk.Entry, ttk.Entry))]
        # Map the entries: current password, new username, new password, confirm new password.
        current_pass_entry = entries[0]
        new_username_entry = entries[1]
        new_pass_entry = entries[2]
        confirm_new_pass_entry = entries[3]
        # Insert test values to simulate account edit.
        current_pass_entry.delete(0, tk.END)
        current_pass_entry.insert(0, "oldpass")
        new_username_entry.delete(0, tk.END)
        new_username_entry.insert(0, "editeduser")
        new_pass_entry.delete(0, tk.END)
        new_pass_entry.insert(0, "newpass")
        confirm_new_pass_entry.delete(0, tk.END)
        confirm_new_pass_entry.insert(0, "newpass")
        # Retrieve and click the "Update Account" button.
        buttons = [child for child in edit_win.winfo_children() if isinstance(child, ttk.Button)]
        for btn in buttons:
            if "Update Account" in btn.cget("text"):
                btn.invoke()
                break
        # Verify that the username has been updated and the new password is set.
        self.assertIn("editeduser", self.app.users, "Username should be updated to 'editeduser'.")
        self.assertEqual(self.app.users["editeduser"]["password"], "newpass", "Password should be updated to 'newpass'.")

    def test_logout_functionality(self):
        """
        OB Test 11: Verify that logout resets user state and hides UI elements.
        """
        # Set a logged-in user state.
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True
        # Access the CatalogFrame.
        catalog_frame = self.app.frames["CatalogFrame"]
        # Invoke the logout method.
        catalog_frame.logout()
        # Check that current_user is reset.
        self.assertIsNone(self.app.current_user, "Logout should set current_user to None")
        # Check that the global is_logged_in flag is set to False.
        self.assertFalse(main.is_logged_in, "Logout should set is_logged_in to False")
        # Verify that the search bar is no longer visible.
        self.assertFalse(self.app.search_bar.winfo_ismapped(), "Search bar should be hidden after logout")

    def test_edit_album_functionality(self):
        """
        OB Test 12: Simulate editing an existing album's details.
        """
        # Ensure that the user is logged in.
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True

        # Set up a sample album in the application's album list.
        self.app.albums = [{
            "Ranking": "1",
            "Album": "Old Album",
            "Artist Name": "Old Artist",
            "Release Date": "2020-01-01",
            "Genres": "Rock",
            "Average Rating": "4",
            "Number of Ratings": "80",
            "Number of Reviews": "40",
            "Cover URL": "",
            "Tracklist": "",
            "Deezer_ID": ""
        }]
        # Refresh the album list in the CatalogFrame.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        # Simulate selecting the first (and only) album.
        if catalog_frame.album_items:
            catalog_frame.selected_album = catalog_frame.album_items[0]
        # Clear any previous Toplevel windows.
        self.created_toplevels.clear()
        # Invoke edit_album with force=True to bypass login and selection checks.
        catalog_frame.edit_album(True)
        # Verify that a Toplevel window was opened for editing the album.
        self.assertTrue(len(self.created_toplevels) > 0, "Edit Album should open a Toplevel window")
        edit_win = self.created_toplevels[-1]
        # Retrieve entry widgets; expected order: Artist, Album, Release Date, Genres.
        entry_widgets = [child for child in edit_win.winfo_children() if isinstance(child, (tk.Entry, ttk.Entry))]
        # Update the album details with new test data.
        entry_widgets[0].delete(0, tk.END)
        entry_widgets[0].insert(0, "New Artist")
        entry_widgets[1].delete(0, tk.END)
        entry_widgets[1].insert(0, "New Album")
        entry_widgets[2].delete(0, tk.END)
        entry_widgets[2].insert(0, "2021-12-12")
        entry_widgets[3].delete(0, tk.END)
        entry_widgets[3].insert(0, "Jazz")
        # Patch the file dialog to simulate no file selection.
        with patch("main.filedialog.askopenfilename", return_value=""):
            buttons = [child for child in edit_win.winfo_children() if isinstance(child, ttk.Button)]
            for btn in buttons:
                if "Update Album" in btn.cget("text"):
                    btn.invoke()
                    break
        # Verify that the album details in the application's album list have been updated.
        updated_album = self.app.albums[0]
        self.assertEqual(updated_album["Artist Name"], "New Artist", "Artist Name should be updated")
        self.assertEqual(updated_album["Album"], "New Album", "Album name should be updated")
        self.assertEqual(updated_album["Release Date"], "2021-12-12", "Release Date should be updated")
        self.assertEqual(updated_album["Genres"], "Jazz", "Genres should be updated")

    def test_delete_album_functionality(self):
        """
        OB Test 13: Simulate deleting an album from the catalog.
        """
        # Ensure the user is logged in.
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True

        # Set up an album that will be deleted.
        self.app.albums = [{
            "Ranking": "1",
            "Album": "Delete Album",
            "Artist Name": "Artist",
            "Release Date": "2020-01-01",
            "Genres": "Rock",
            "Average Rating": "4",
            "Number of Ratings": "80",
            "Number of Reviews": "40",
            "Cover URL": "",
            "Tracklist": "",
            "Deezer_ID": ""
        }]
        # Refresh the CatalogFrame album list.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        # Simulate selecting the album to delete.
        catalog_frame.selected_album = catalog_frame.album_items[0]
        # Call delete_album with force=True to bypass confirmation in tests.
        catalog_frame.delete_album(True)
        # Verify that the album is no longer in the application's album list.
        self.assertFalse(any(album["Album"] == "Delete Album" for album in self.app.albums),
                         "The album 'Delete Album' should be deleted.")

    def test_tracks_album_functionality(self):
        """
        OB Test 14: Simulate viewing the tracklist of an album.
        """
        # Set up an album with a tracklist.
        self.app.albums = [{
            "Ranking": "1",
            "Album": "Tracks Album",
            "Artist Name": "Artist",
            "Release Date": "2020-01-01",
            "Genres": "Pop",
            "Average Rating": "5",
            "Number of Ratings": "100",
            "Number of Reviews": "50",
            "Cover URL": "",
            "Tracklist": "Song1; Song2; Song3",
            "Deezer_ID": ""
        }]
        # Refresh the album list.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        # Simulate selecting the album.
        if catalog_frame.album_items:
            catalog_frame.selected_album = catalog_frame.album_items[0]
        # Record the number of Toplevel windows before invoking tracks_album.
        initial_toplevel_count = len(self.created_toplevels)
        # Invoke tracks_album to open the tracklist window.
        catalog_frame.tracks_album()
        # Verify that a new Toplevel window was created.
        self.assertTrue(len(self.created_toplevels) > initial_toplevel_count,
                        "Tracks Album should open a new Toplevel window.")

    def test_search_filter_release_date(self):
        """
        OB Test 15: Verify that search functionality works correctly when filtering by Release Date.
        """
        # Set up an album with a specific release date.
        self.app.albums = [{
            "Ranking": "1",
            "Album": "Release Date Album",
            "Artist Name": "Artist",
            "Release Date": "2021-05-05",
            "Genres": "Pop",
            "Average Rating": "5",
            "Number of Ratings": "100",
            "Number of Reviews": "50",
            "Cover URL": "",
            "Tracklist": "",
            "Deezer_ID": ""
        }]
        # Set the search filter to "Release Date".
        self.app.search_filter.set("Release Date")
        # Insert a search query that should match the album's release year.
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "2021")
        self.app.search()
        # Verify that one album is returned by the search.
        self.assertEqual(len(self.app.search_results), 1, "Search should return album when filtering by Release Date.")

    def test_refresh_catalog(self):
        """
        OB Test 16: Verify that refresh_catalog clears the search bar and updates the catalog display.
        """
        # Insert text into the search bar.
        self.app.search_bar.insert("1.0", "Some text")
        # Call refresh_catalog to clear search inputs and refresh display.
        self.app.refresh_catalog()
        # Get the content of the search bar after refresh.
        content = self.app.search_bar.get("1.0", tk.END).strip()
        # Verify that the search bar is empty.
        self.assertEqual(content, "", "Refresh catalog should clear the search bar.")

    def test_search_bar_enter_key_binding(self):
        """
        OB Test 17: Verify that pressing Enter in the search bar triggers the search function.
        """
        # Clear the search bar and insert test text.
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "Test")
        # Create a fake event to simulate the Enter key press.
        event = tk.Event()
        event.widget = self.app.search_bar
        # Call the on_enter_pressed method.
        self.app.on_enter_pressed(event)
        # Verify that the search_results attribute has been updated.
        self.assertTrue(hasattr(self.app, "search_results"), "Search results should be updated when Enter is pressed.")

    def test_threadpool_executor_usage(self):
        """
        OB Test 18: Confirm that the thread pool executor submits one task per album when refreshing the album list.
        """
        # Set up a single album for testing.
        self.app.albums = [{
            "Ranking": "1",
            "Album": "Threaded Album",
            "Artist Name": "Artist",
            "Release Date": "2021-01-01",
            "Genres": "Rock",
            "Average Rating": "4",
            "Number of Ratings": "80",
            "Number of Reviews": "40",
            "Cover URL": "",
            "Tracklist": "",
            "Deezer_ID": ""
        }]
        # Access the CatalogFrame and refresh the album list.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        # Verify that the number of thread tasks matches the number of albums.
        self.assertEqual(len(catalog_frame.refresh_album_threads), len(self.app.albums),
                         "Each album should have a corresponding thread task submitted.")

    def test_edit_account_invalid_password(self):
        """
        OB Test 19: Verify that editing an account fails when the current password is incorrect.
        """
        # Set up a user with a known correct password.
        self.app.users = {"invaliduser": {"password": "correctpass", "email": "inv@example.com"}}
        self.app.current_user = "invaliduser"
        main.current_user = "invaliduser"
        main.is_logged_in = True
        # Clear previous Toplevel windows.
        self.created_toplevels.clear()
        # Invoke edit_account.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.edit_account()
        # Get the Toplevel window for editing.
        edit_win = self.created_toplevels[-1]
        # Retrieve entry widgets.
        entries = [child for child in edit_win.winfo_children() if isinstance(child, (tk.Entry, ttk.Entry))]
        # Set the current password to an incorrect value.
        entries[0].delete(0, tk.END)
        entries[0].insert(0, "wrongpass")
        # Fill in the new username and password.
        entries[1].delete(0, tk.END)
        entries[1].insert(0, "newuser")
        entries[2].delete(0, tk.END)
        entries[2].insert(0, "newpass")
        entries[3].delete(0, tk.END)
        entries[3].insert(0, "newpass")
        # Patch messagebox.showerror to intercept error messages.
        with patch("main.messagebox.showerror") as mock_showerror:
            buttons = [child for child in edit_win.winfo_children() if isinstance(child, ttk.Button)]
            # Invoke the "Update Account" button.
            for btn in buttons:
                if "Update Account" in btn.cget("text"):
                    btn.invoke()
                    break
            # Verify that an error was shown.
            mock_showerror.assert_called_once()
        # Verify that the password remains unchanged.
        self.assertEqual(self.app.users["invaliduser"]["password"], "correctpass",
                         "Password should remain unchanged if current password is incorrect.")

    def test_signup_invalid_email(self):
        """
        OB Test 20: Verify that sign up fails when an invalid email format is provided.
        """
        # Access the SignupFrame and input invalid email data.
        signup_frame = self.app.frames["SignupFrame"]
        signup_frame.username_entry.delete(0, tk.END)
        signup_frame.username_entry.insert(0, "bademailuser")
        signup_frame.email_entry.delete(0, tk.END)
        signup_frame.email_entry.insert(0, "notanemail")
        signup_frame.password_entry.delete(0, tk.END)
        signup_frame.password_entry.insert(0, "password")
        signup_frame.confirm_password_entry.delete(0, tk.END)
        signup_frame.confirm_password_entry.insert(0, "password")
        # Patch messagebox.showerror to capture error output.
        with patch("main.messagebox.showerror") as mock_showerror:
            signup_frame.signup()
            mock_showerror.assert_called_once()
        # Verify that the user was not added.
        self.assertNotIn("bademailuser", self.app.users, "User should not be created with an invalid email.")

    def test_signup_password_mismatch(self):
        """
        OB Test 21: Verify that sign up fails when the provided passwords do not match.
        """
        # Access the SignupFrame and input mismatching passwords.
        signup_frame = self.app.frames["SignupFrame"]
        signup_frame.username_entry.delete(0, tk.END)
        signup_frame.username_entry.insert(0, "mismatchuser")
        signup_frame.email_entry.delete(0, tk.END)
        signup_frame.email_entry.insert(0, "mismatch@example.com")
        signup_frame.password_entry.delete(0, tk.END)
        signup_frame.password_entry.insert(0, "password1")
        signup_frame.confirm_password_entry.delete(0, tk.END)
        signup_frame.confirm_password_entry.insert(0, "password2")
        # Patch messagebox.showerror to capture error output.
        with patch("main.messagebox.showerror") as mock_showerror:
            signup_frame.signup()
            mock_showerror.assert_called_once()
        # Verify that the user was not added.
        self.assertNotIn("mismatchuser", self.app.users, "User should not be created when passwords do not match.")

    def test_login_failure(self):
        """
        OB Test 22: Verify that login fails with incorrect credentials.
        """
        # Set up a user with the correct password.
        self.app.users = {"userfail": {"password": "rightpass", "email": "fail@example.com"}}
        # Access the LoginFrame and input incorrect credentials.
        login_frame = self.app.frames["LoginFrame"]
        login_frame.username_entry.delete(0, tk.END)
        login_frame.username_entry.insert(0, "userfail")
        login_frame.password_entry.delete(0, tk.END)
        login_frame.password_entry.insert(0, "wrongpass")
        # Patch messagebox.showerror to intercept error messages.
        with patch("main.messagebox.showerror") as mock_showerror:
            login_frame.login()
            mock_showerror.assert_called_once()
        # Verify that current_user is not set to the incorrect user.
        self.assertNotEqual(self.app.current_user, "userfail", "Login should fail with incorrect password.")

    def test_continue_as_guest(self):
        """
        OB Test 23: Verify that continuing as guest sets current_user to 'Guest' and disables editing.
        """
        # Use the LoginFrame to simulate a guest login.
        login_frame = self.app.frames["LoginFrame"]
        login_frame.continue_as_guest()
        # Verify that current_user is set to "Guest".
        self.assertEqual(self.app.current_user, "Guest", "Current user should be 'Guest'")
        # Verify that the global is_logged_in flag is False for guests.
        self.assertFalse(main.is_logged_in, "is_logged_in should be False for guest users.")

    def test_favourites_no_favourites(self):
        """
        OB Test 24: Verify that invoking favourites on a user with no favourites shows an error message
        and leaves search_results empty.
        """
        # Set the current user and global login state.
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        # Create a user record without the 'favourites' key.
        self.app.users["faveuser"] = {}
        # Patch messagebox.showerror to capture the error message.
        with patch("main.messagebox.showerror") as mock_showerror:
            self.app.favourites()
            mock_showerror.assert_called_once_with("No Results", "No favourites yet.")
        # Verify that the search_results list remains empty.
        self.assertEqual(self.app.search_results, [], "Search results should be empty when no favourites are set.")

    def test_favourites_with_favourites(self):
        """
        OB Test 25: Verify that the favourites functionality correctly filters and displays the user's favourite album(s).
        """
        # Set up a user with a favourite album.
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        # Set up two albums: one favourite and one regular.
        self.app.albums = [
            {"Ranking": "1", "Album": "Favourite Album", "Artist Name": "Fav Artist", "Release Date": "2020-01-01",
             "Genres": "Rock", "Average Rating": "4", "Number of Ratings": "50", "Number of Reviews": "20",
             "Cover URL": "", "Tracklist": "", "Deezer_ID": "fav123"},
            {"Ranking": "2", "Album": "Regular Album", "Artist Name": "Artist", "Release Date": "2019-01-01",
             "Genres": "Pop", "Average Rating": "3", "Number of Ratings": "30", "Number of Reviews": "10",
             "Cover URL": "", "Tracklist": "", "Deezer_ID": "reg456"}
        ]
        # Assign a favourites list to the user.
        self.app.users["faveuser"] = {"favourites": ["fav123"]}
        # Invoke the favourites function.
        self.app.favourites()
        # Verify that only the favourite album is returned in search_results.
        self.assertEqual(len(self.app.search_results), 1, "Search results should contain one favourite album")
        self.assertEqual(self.app.search_results[0]["Deezer_ID"], "fav123", "The favourite album's Deezer_ID should match")

    def test_unfavourite_album_success(self):
        """
        OB Test 26: Verify that unfavourite_album successfully removes a favourite album.
        """
        # Set up the current user and login state.
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        favourite_id = "fav123"
        # Set up a user with a favourite album.
        self.app.users["faveuser"] = {"favourites": [favourite_id]}
        # Create an album that matches the favourite album.
        album = {
            "Ranking": "1",
            "Album": "Fav Album",
            "Artist Name": "Fav Artist",
            "Release Date": "2021-01-01",
            "Genres": "Pop",
            "Average Rating": "5",
            "Number of Ratings": "100",
            "Number of Reviews": "50",
            "Cover URL": "",
            "Tracklist": "",
            "Deezer_ID": favourite_id
        }
        self.app.albums = [album]
        # Access the CatalogFrame and refresh the album list without threading.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list(True)
        # Simulate selecting the album.
        catalog_frame.selected_album = catalog_frame.album_items[0]
        # Patch messagebox.showinfo to capture success messages.
        with patch("main.messagebox.showinfo") as mock_showinfo:
            catalog_frame.unfavourite_album()
            mock_showinfo.assert_called_once_with("Success", f"Album '{album['Album']}' has been removed from your favourites.")
        # Verify that the favourite album has been removed from the user's favourites list.
        self.assertNotIn(favourite_id, self.app.users["faveuser"].get("favourites", []))

    def test_unfavourite_album_not_in_favourites(self):
        """
        OB Test 27: Verify that unfavourite_album shows an error when the album is not in favourites.
        """
        # Set up the current user and login state.
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        # Create a user record with an empty favourites list.
        self.app.users["faveuser"] = {"favourites": []}
        album = {
            "Ranking": "1",
            "Album": "Non-Fav Album",
            "Artist Name": "Artist",
            "Release Date": "2021-01-01",
            "Genres": "Pop",
            "Average Rating": "5",
            "Number of Ratings": "100",
            "Number of Reviews": "50",
            "Cover URL": "",
            "Tracklist": "",
            "Deezer_ID": "nonfav123"
        }
        self.app.albums = [album]
        # Access the CatalogFrame and refresh the album list without threading.
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list(True)
        # Simulate selecting the album.
        catalog_frame.selected_album = catalog_frame.album_items[0]
        # Patch messagebox.showerror to capture error messages.
        with patch("main.messagebox.showerror") as mock_showerror:
            catalog_frame.unfavourite_album()
            mock_showerror.assert_called_once_with("Error", f"Album '{album['Album']}' is not in your favourites.")

if __name__ == '__main__':
    unittest.main()
