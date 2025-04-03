"""
Test Suite for BrightByte Music Cataloging Software
======================================================

This suite has been updated to simulate proper login state, correctly reference global variables,
and now includes tests for the favourites functionality.
"""

import unittest
import tempfile
import os
import json
import csv
import tkinter as tk
from tkinter import ttk
from unittest.mock import patch
from PIL import Image
import main  # The application module from main.py

class TestAlbumCatalogApp(unittest.TestCase):
    def setUp(self):
        """
        Setup temporary files and override global constants for testing.
        Also, patch out image loading and track Toplevel window creation.
        """
        self.test_dir = tempfile.TemporaryDirectory()
        self.users_file = os.path.join(self.test_dir.name, "users.json")
        self.albums_file = os.path.join(self.test_dir.name, "cleaned_music_data.csv")
        
        # Override file paths in the main module to use our temporary files.
        main.USERS_JSON = self.users_file
        main.ALBUMS_CSV = self.albums_file

        # Write a sample album CSV file with one entry.
        with open(self.albums_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Ranking", "Album", "Artist Name", "Release Date",
                                                     "Genres", "Average Rating", "Number of Ratings",
                                                     "Number of Reviews", "Cover URL"])
            writer.writeheader()
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
        
        # Write an empty users file.
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump({}, f)
        
        # Patch image loading to avoid errors due to missing image files.
        self.patcher_image_open = patch("main.Image.open", return_value=Image.new("RGB", (125, 75)))
        self.mock_image_open = self.patcher_image_open.start()

        # --- Patch Toplevel creation to track instances ---
        self.created_toplevels = []
        self.original_Toplevel = main.tk.Toplevel
        def fake_Toplevel(*args, **kwargs):
            instance = self.original_Toplevel(*args, **kwargs)
            self.created_toplevels.append(instance)
            return instance
        self.patcher_toplevel = patch("main.tk.Toplevel", side_effect=fake_Toplevel)
        self.mock_toplevel = self.patcher_toplevel.start()
        # ---------------------------------------------------------------

        # Instantiate the application (but do not call mainloop); withdraw window to keep tests headless.
        self.app = main.AlbumCatalogApp()
        self.app.withdraw()

    def tearDown(self):
        """
        Stop patches, destroy the app instance, and clean up temporary files.
        """
        self.patcher_image_open.stop()
        self.patcher_toplevel.stop()
        self.app.destroy()
        self.test_dir.cleanup()

    # =======================
    # Clear Box Tests (CB)
    # =======================

    def test_load_users_no_file(self):
        """
        CB Test 1: Verify that load_users() returns an empty dict when users.json does not exist.
        """
        if os.path.exists(self.users_file):
            os.remove(self.users_file)
        users = self.app.load_users()
        self.assertEqual(users, {}, "Expected empty dict when users.json does not exist")

    def test_load_users_invalid_json(self):
        """
        CB Test 2: Verify that load_users() handles invalid JSON by returning an empty dict.
        """
        with open(self.users_file, "w", encoding="utf-8") as f:
            f.write("invalid json")
        users = self.app.load_users()
        self.assertEqual(users, {}, "Expected empty dict when users.json contains invalid JSON")

    def test_load_albums_from_csv_valid(self):
        """
        CB Test 3: Verify that load_albums_from_csv() correctly parses a valid CSV file.
        """
        albums = self.app.load_albums_from_csv()
        self.assertEqual(len(albums), 1, "Expected one album in CSV")
        self.assertEqual(albums[0]["Album"], "Test Album", "Album name should match sample CSV data")

    # ============================
    # Translucent Box Tests (TB)
    # ============================

    def test_login_success(self):
        """
        TB Test 4: Simulate a successful login by inserting valid credentials.
        """
        self.app.users = {"testuser": {"password": "pass123", "email": "test@example.com"}}
        login_frame = self.app.frames["LoginFrame"]
        login_frame.username_entry.delete(0, tk.END)
        login_frame.username_entry.insert(0, "testuser")
        login_frame.password_entry.delete(0, tk.END)
        login_frame.password_entry.insert(0, "pass123")
        login_frame.login()
        self.assertEqual(self.app.current_user, "testuser", "Login should set current_user to 'testuser'")

    def test_signup_creates_account(self):
        """
        TB Test 5: Simulate the sign-up process using valid user information.
        """
        signup_frame = self.app.frames["SignupFrame"]
        signup_frame.username_entry.delete(0, tk.END)
        signup_frame.username_entry.insert(0, "newuser")
        signup_frame.email_entry.delete(0, tk.END)
        signup_frame.email_entry.insert(0, "new@example.com")
        signup_frame.password_entry.delete(0, tk.END)
        signup_frame.password_entry.insert(0, "newpass")
        signup_frame.confirm_password_entry.delete(0, tk.END)
        signup_frame.confirm_password_entry.insert(0, "newpass")
        signup_frame.signup()
        self.assertIn("newuser", self.app.users, "Signup should add 'newuser' to the users dictionary")

    def test_add_album_integration(self):
        """
        TB Test 6: Simulate adding an album through the CatalogFrame.
        """
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True

        catalog_frame = self.app.frames["CatalogFrame"]
        self.created_toplevels.clear()
        catalog_frame.add_album()
        self.assertTrue(len(self.created_toplevels) > 0, "Add Album should open a Toplevel window")
        add_win = self.created_toplevels[-1]
        entry_widgets = [child for child in add_win.winfo_children() 
                         if isinstance(child, (tk.Entry, ttk.Entry))]
        for widget in entry_widgets:
            widget.delete(0, tk.END)
        entry_widgets[0].insert(0, "Artist Test")
        entry_widgets[1].insert(0, "Album Test")
        entry_widgets[2].insert(0, "2022-02-02")
        entry_widgets[3].insert(0, "Rock")
        with patch("main.filedialog.askopenfilename", return_value=""):
            buttons = [child for child in add_win.winfo_children() if isinstance(child, ttk.Button)]
            for btn in buttons:
                if "Save Album" in btn.cget("text"):
                    btn.invoke()
                    break
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
        
        self.app.show_frame("LoginFrame")
        login_frame = self.app.frames["LoginFrame"]
        login_frame.username_entry.delete(0, tk.END)
        login_frame.username_entry.insert(0, "user1")
        login_frame.password_entry.delete(0, tk.END)
        login_frame.password_entry.insert(0, "password1")
        login_frame.login()
        self.assertEqual(self.app.current_user, "user1", "Login should set current_user to 'user1'.")
        
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
        entry_widgets[0].delete(0, tk.END)
        entry_widgets[0].insert(0, "Artist1")
        entry_widgets[1].delete(0, tk.END)
        entry_widgets[1].insert(0, "Album1")
        entry_widgets[2].delete(0, tk.END)
        entry_widgets[2].insert(0, "2023-03-03")
        entry_widgets[3].delete(0, tk.END)
        entry_widgets[3].insert(0, "Jazz")
        with patch("main.filedialog.askopenfilename", return_value=""):
            buttons = [child for child in add_win.winfo_children() if isinstance(child, ttk.Button)]
            for btn in buttons:
                if "Save Album" in btn.cget("text"):
                    btn.invoke()
                    break
        self.assertTrue(any(album["Album"] == "Album1" for album in self.app.albums),
                        "The album 'Album1' should be added.")
        
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "Album1")
        self.app.search()
        self.assertTrue(len(self.app.search_results) > 0,
                        "Search should return results for 'Album1'.")
        
        catalog_frame.logout()
        self.assertIsNone(self.app.current_user, "Logout should reset current_user to None.")

    def test_guest_user_workflow(self):
        """
        OB Test 8: Simulate a guest user workflow: continue as guest and perform a search.
        """
        login_frame = self.app.frames["LoginFrame"]
        login_frame.continue_as_guest()
        self.assertEqual(self.app.current_user, "Guest", "Guest login should set current_user to 'Guest'.")
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "Test Album")
        self.app.search()
        self.assertTrue(len(self.app.search_results) > 0,
                        "Search should return results for 'Test Album' for a guest user.")
        self.assertFalse(main.is_logged_in, "is_logged_in should be False for guest users.")

    def test_search_functionality(self):
        """
        OB Test 9: Verify search functionality with different filters.
        """
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
        self.app.search_filter.set("Album Name")
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "test album")
        self.app.search()
        self.assertEqual(len(self.app.search_results), 1, "Search should find the album by name.")
        
        self.app.search_filter.set("Artist Name")
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "test artist")
        self.app.search()
        self.assertEqual(len(self.app.search_results), 1, "Search should find the album by artist.")

    def test_edit_account(self):
        """
        OB Test 10: Simulate editing a user account.
        """
        self.app.users = {"edituser": {"password": "oldpass", "email": "edit@example.com"}}
        self.app.current_user = "edituser"
        main.current_user = "edituser"
        main.is_logged_in = True
        self.created_toplevels.clear()
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.edit_account()
        self.assertTrue(len(self.created_toplevels) > 0, "Edit Account should open a Toplevel window")
        edit_win = self.created_toplevels[-1]
        entries = [child for child in edit_win.winfo_children() 
                   if isinstance(child, (tk.Entry, ttk.Entry))]
        current_pass_entry = entries[0]
        new_username_entry = entries[1]
        new_pass_entry = entries[2]
        confirm_new_pass_entry = entries[3]
        current_pass_entry.delete(0, tk.END)
        current_pass_entry.insert(0, "oldpass")
        new_username_entry.delete(0, tk.END)
        new_username_entry.insert(0, "editeduser")
        new_pass_entry.delete(0, tk.END)
        new_pass_entry.insert(0, "newpass")
        confirm_new_pass_entry.delete(0, tk.END)
        confirm_new_pass_entry.insert(0, "newpass")
        buttons = [child for child in edit_win.winfo_children() if isinstance(child, ttk.Button)]
        for btn in buttons:
            if "Update Account" in btn.cget("text"):
                btn.invoke()
                break
        self.assertIn("editeduser", self.app.users, "Username should be updated to 'editeduser'.")
        self.assertEqual(self.app.users["editeduser"]["password"], "newpass", "Password should be updated to 'newpass'.")

    def test_logout_functionality(self):
        """
        OB Test 11: Verify that logout resets user state and hides UI elements.
        """
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.logout()
        self.assertIsNone(self.app.current_user, "Logout should set current_user to None")
        self.assertFalse(main.is_logged_in, "Logout should set is_logged_in to False")
        self.assertFalse(self.app.search_bar.winfo_ismapped(), "Search bar should be hidden after logout")

    def test_edit_album_functionality(self):
        """
        OB Test 12: Simulate editing an existing album's details.
        """
        # Ensure login state.
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True

        # Set up an album in the catalog.
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
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        # Simulate selecting the album.
        if catalog_frame.album_items:
            catalog_frame.selected_album = catalog_frame.album_items[0]
        # Invoke the edit album function.
        self.created_toplevels.clear()
        catalog_frame.edit_album(True)
        self.assertTrue(len(self.created_toplevels) > 0, "Edit Album should open a Toplevel window")
        edit_win = self.created_toplevels[-1]
        entry_widgets = [child for child in edit_win.winfo_children() if isinstance(child, (tk.Entry, ttk.Entry))]
        # Assume order: Artist, Album, Release Date, Genres, (and Album Cover entry).
        entry_widgets[0].delete(0, tk.END)
        entry_widgets[0].insert(0, "New Artist")
        entry_widgets[1].delete(0, tk.END)
        entry_widgets[1].insert(0, "New Album")
        entry_widgets[2].delete(0, tk.END)
        entry_widgets[2].insert(0, "2021-12-12")
        entry_widgets[3].delete(0, tk.END)
        entry_widgets[3].insert(0, "Jazz")
        with patch("main.filedialog.askopenfilename", return_value=""):
            buttons = [child for child in edit_win.winfo_children() if isinstance(child, ttk.Button)]
            for btn in buttons:
                if "Update Album" in btn.cget("text"):
                    btn.invoke()
                    break
        # Verify that the album details have been updated.
        updated_album = self.app.albums[0]
        self.assertEqual(updated_album["Artist Name"], "New Artist", "Artist Name should be updated")
        self.assertEqual(updated_album["Album"], "New Album", "Album name should be updated")
        self.assertEqual(updated_album["Release Date"], "2021-12-12", "Release Date should be updated")
        self.assertEqual(updated_album["Genres"], "Jazz", "Genres should be updated")

    def test_delete_album_functionality(self):
        """
        OB Test 13: Simulate deleting an album from the catalog.
        """
        # Ensure login state.
        self.app.current_user = "testuser"
        main.current_user = "testuser"
        main.is_logged_in = True

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
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        catalog_frame.selected_album = catalog_frame.album_items[0]
        # Patch confirmation to always return True.
        catalog_frame.delete_album(True)
        self.assertFalse(any(album["Album"] == "Delete Album" for album in self.app.albums),
                         "The album 'Delete Album' should be deleted.")

    def test_tracks_album_functionality(self):
        """
        OB Test 14: Simulate viewing the tracklist of an album.
        """
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
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        if catalog_frame.album_items:
            catalog_frame.selected_album = catalog_frame.album_items[0]
        initial_toplevel_count = len(self.created_toplevels)
        catalog_frame.tracks_album()
        self.assertTrue(len(self.created_toplevels) > initial_toplevel_count,
                        "Tracks Album should open a new Toplevel window.")

    def test_search_filter_release_date(self):
        """
        OB Test 15: Verify that search functionality works correctly when filtering by Release Date.
        """
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
        self.app.search_filter.set("Release Date")
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "2021")
        self.app.search()
        self.assertEqual(len(self.app.search_results), 1, "Search should return album when filtering by Release Date.")

    def test_refresh_catalog(self):
        """
        OB Test 16: Verify that refresh_catalog clears the search bar and updates the catalog display.
        """
        self.app.search_bar.insert("1.0", "Some text")
        self.app.refresh_catalog()
        content = self.app.search_bar.get("1.0", tk.END).strip()
        self.assertEqual(content, "", "Refresh catalog should clear the search bar.")

    def test_search_bar_enter_key_binding(self):
        """
        OB Test 17: Verify that pressing Enter in the search bar triggers the search function.
        """
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "Test")
        event = tk.Event()
        event.widget = self.app.search_bar
        self.app.on_enter_pressed(event)
        self.assertTrue(hasattr(self.app, "search_results"), "Search results should be updated when Enter is pressed.")

    def test_threadpool_executor_usage(self):
        """
        OB Test 18: Confirm that the thread pool executor submits one task per album when refreshing the album list.
        """
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
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        self.assertEqual(len(catalog_frame.refresh_album_threads), len(self.app.albums),
                         "Each album should have a corresponding thread task submitted.")

    def test_edit_account_invalid_password(self):
        """
        OB Test 19: Verify that editing an account fails when the current password is incorrect.
        """
        self.app.users = {"invaliduser": {"password": "correctpass", "email": "inv@example.com"}}
        self.app.current_user = "invaliduser"
        main.current_user = "invaliduser"
        main.is_logged_in = True
        self.created_toplevels.clear()
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.edit_account()
        edit_win = self.created_toplevels[-1]
        entries = [child for child in edit_win.winfo_children() if isinstance(child, (tk.Entry, ttk.Entry))]
        entries[0].delete(0, tk.END)
        entries[0].insert(0, "wrongpass")
        entries[1].delete(0, tk.END)
        entries[1].insert(0, "newuser")
        entries[2].delete(0, tk.END)
        entries[2].insert(0, "newpass")
        entries[3].delete(0, tk.END)
        entries[3].insert(0, "newpass")
        with patch("main.messagebox.showerror") as mock_showerror:
            buttons = [child for child in edit_win.winfo_children() if isinstance(child, ttk.Button)]
            for btn in buttons:
                if "Update Account" in btn.cget("text"):
                    btn.invoke()
                    break
            mock_showerror.assert_called_once()
        self.assertEqual(self.app.users["invaliduser"]["password"], "correctpass",
                         "Password should remain unchanged if current password is incorrect.")

    def test_signup_invalid_email(self):
        """
        OB Test 20: Verify that sign up fails when an invalid email format is provided.
        """
        signup_frame = self.app.frames["SignupFrame"]
        signup_frame.username_entry.delete(0, tk.END)
        signup_frame.username_entry.insert(0, "bademailuser")
        signup_frame.email_entry.delete(0, tk.END)
        signup_frame.email_entry.insert(0, "notanemail")
        signup_frame.password_entry.delete(0, tk.END)
        signup_frame.password_entry.insert(0, "password")
        signup_frame.confirm_password_entry.delete(0, tk.END)
        signup_frame.confirm_password_entry.insert(0, "password")
        with patch("main.messagebox.showerror") as mock_showerror:
            signup_frame.signup()
            mock_showerror.assert_called_once()
        self.assertNotIn("bademailuser", self.app.users, "User should not be created with an invalid email.")

    def test_signup_password_mismatch(self):
        """
        OB Test 21: Verify that sign up fails when the provided passwords do not match.
        """
        signup_frame = self.app.frames["SignupFrame"]
        signup_frame.username_entry.delete(0, tk.END)
        signup_frame.username_entry.insert(0, "mismatchuser")
        signup_frame.email_entry.delete(0, tk.END)
        signup_frame.email_entry.insert(0, "mismatch@example.com")
        signup_frame.password_entry.delete(0, tk.END)
        signup_frame.password_entry.insert(0, "password1")
        signup_frame.confirm_password_entry.delete(0, tk.END)
        signup_frame.confirm_password_entry.insert(0, "password2")
        with patch("main.messagebox.showerror") as mock_showerror:
            signup_frame.signup()
            mock_showerror.assert_called_once()
        self.assertNotIn("mismatchuser", self.app.users, "User should not be created when passwords do not match.")

    def test_login_failure(self):
        """
        OB Test 22: Verify that login fails with incorrect credentials.
        """
        self.app.users = {"userfail": {"password": "rightpass", "email": "fail@example.com"}}
        login_frame = self.app.frames["LoginFrame"]
        login_frame.username_entry.delete(0, tk.END)
        login_frame.username_entry.insert(0, "userfail")
        login_frame.password_entry.delete(0, tk.END)
        login_frame.password_entry.insert(0, "wrongpass")
        with patch("main.messagebox.showerror") as mock_showerror:
            login_frame.login()
            mock_showerror.assert_called_once()
        self.assertNotEqual(self.app.current_user, "userfail", "Login should fail with incorrect password.")

    def test_continue_as_guest(self):
        """
        OB Test 23: Verify that continuing as guest sets current_user to 'Guest' and disables editing.
        """
        login_frame = self.app.frames["LoginFrame"]
        login_frame.continue_as_guest()
        self.assertEqual(self.app.current_user, "Guest", "Current user should be 'Guest'")
        self.assertFalse(main.is_logged_in, "is_logged_in should be False for guest users.")

    def test_favourites_no_favourites(self):
        """
        OB Test 24: Verify that invoking favourites on a user with no favourites shows an error message
        and leaves search_results empty.
        """
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        self.app.users["faveuser"] = {}  # No favourites key
        with patch("main.messagebox.showerror") as mock_showerror:
            self.app.favourites()
            mock_showerror.assert_called_once_with("No Results", "No favourites yet.")
        self.assertEqual(self.app.search_results, [], "Search results should be empty when no favourites are set.")

    def test_favourites_with_favourites(self):
        """
        OB Test 25: Verify that the favourites functionality correctly filters and displays the user's favourite album(s).
        """
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        self.app.albums = [
            {"Ranking": "1", "Album": "Favourite Album", "Artist Name": "Fav Artist", "Release Date": "2020-01-01",
             "Genres": "Rock", "Average Rating": "4", "Number of Ratings": "50", "Number of Reviews": "20",
             "Cover URL": "", "Tracklist": "", "Deezer_ID": "fav123"},
            {"Ranking": "2", "Album": "Regular Album", "Artist Name": "Artist", "Release Date": "2019-01-01",
             "Genres": "Pop", "Average Rating": "3", "Number of Ratings": "30", "Number of Reviews": "10",
             "Cover URL": "", "Tracklist": "", "Deezer_ID": "reg456"}
        ]
        self.app.users["faveuser"] = {"favourites": ["fav123"]}
        self.app.favourites()
        self.assertEqual(len(self.app.search_results), 1, "Search results should contain one favourite album")
        self.assertEqual(self.app.search_results[0]["Deezer_ID"], "fav123", "The favourite album's Deezer_ID should match")
    def test_unfavourite_album_success(self):
        """
        OB Test 26: Verify that unfavourite_album successfully removes a favourite album.
        """
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        favourite_id = "fav123"
        # Set up the user with a favourite album.
        self.app.users["faveuser"] = {"favourites": [favourite_id]}
        # Create an album with the given Deezer_ID.
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
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        # Simulate selecting the album.
        catalog_frame.selected_album = catalog_frame.album_items[0]
        with patch("main.messagebox.showinfo") as mock_showinfo:
            catalog_frame.unfavourite_album()
            mock_showinfo.assert_called_once_with("Success", f"Album '{album['Album']}' has been removed from your favourites.")
        self.assertNotIn(favourite_id, self.app.users["faveuser"].get("favourites", []))

    def test_unfavourite_album_not_in_favourites(self):
        """
        OB Test 27: Verify that unfavourite_album shows an error when the album is not in favourites.
        """
        self.app.current_user = "faveuser"
        main.current_user = "faveuser"
        main.is_logged_in = True
        # Set up the user with no favourites.
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
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.refresh_album_list()
        # Simulate selecting the album.
        catalog_frame.selected_album = catalog_frame.album_items[0]
        with patch("main.messagebox.showerror") as mock_showerror:
            catalog_frame.unfavourite_album()
            mock_showerror.assert_called_once_with("Error", f"Album '{album['Album']}' is not in your favourites.")


if __name__ == '__main__':
    unittest.main()
