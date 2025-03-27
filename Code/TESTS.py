"""
Test Suite for BrightByte Music Cataloging Software
======================================================

[... Header and documentation remain unchanged ...]
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
        # Create a temporary directory for test files.
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

        # --- NEW CODE: Patch Toplevel creation to track instances ---
        self.created_toplevels = []
        self.original_Toplevel = main.tk.Toplevel  # Get the original Toplevel class from main's tk.
        def fake_Toplevel(*args, **kwargs):
            # Call the original Toplevel to create an instance.
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
        self.patcher_toplevel.stop()  # Stop the Toplevel patch.
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
        catalog_frame = self.app.frames["CatalogFrame"]
        # Clear previously tracked Toplevels.
        self.created_toplevels.clear()
        catalog_frame.add_album()
        # Now, instead of checking self.app.winfo_children(), we check our tracked list.
        self.assertTrue(len(self.created_toplevels) > 0, "Add Album should open a Toplevel window")
        # Simulate entering album details.
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
        # --- Sign Up ---
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
        
        # --- Log In ---
        self.app.show_frame("LoginFrame")
        login_frame = self.app.frames["LoginFrame"]
        login_frame.username_entry.delete(0, tk.END)
        login_frame.username_entry.insert(0, "user1")
        login_frame.password_entry.delete(0, tk.END)
        login_frame.password_entry.insert(0, "password1")
        login_frame.login()
        self.assertEqual(self.app.current_user, "user1", "Login should set current_user to 'user1'.")
        
        # --- Add Album ---
        catalog_frame = self.app.frames["CatalogFrame"]
        self.created_toplevels.clear()  # Clear before triggering add_album.
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
        
        # --- Search ---
        self.app.search_bar.delete("1.0", tk.END)
        self.app.search_bar.insert("1.0", "Album1")
        self.app.search()
        self.assertTrue(len(self.app.search_results) > 0,
                        "Search should return results for 'Album1'.")
        
        # --- Logout ---
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
            "Cover URL": ""
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
        self.created_toplevels.clear()
        catalog_frame = self.app.frames["CatalogFrame"]
        catalog_frame.edit_account()
        self.assertTrue(len(self.created_toplevels) > 0, "Edit Account should open a Toplevel window")
        edit_win = self.created_toplevels[-1]
        entries = [child for child in edit_win.winfo_children() 
                   if isinstance(child, (tk.Entry, ttk.Entry))]
        # Expected order: current_pass, new_username, new_pass, confirm_new_pass.
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


if __name__ == "__main__":
    unittest.main()
