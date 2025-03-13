import unittest
from unittest.mock import patch
import tkinter as tk
from tkinter import messagebox
from main import LoginFrame, SignupFrame


# Dummy controller to simulate the minimal attributes and methods required by the frames.

# This helper class simulates the minimal behavior of the main application (the controller) that the frames depend on. It provides:

#     A users dictionary to store user data.
#     A current_user attribute.
#     A show_frame method that records which frame is being shown (instead of actually changing GUI frames).
#     A save_users method that simply marks that a save was triggered.
class DummyController:
    def __init__(self, users=None):
        self.users = users if users is not None else {}
        self.current_user = None
        self.frame_shown = None
        self.saved = False

    def show_frame(self, frame_name):
        self.frame_shown = frame_name

    def save_users(self):
        self.saved = True

# ----------------- Tests for LoginFrame -----------------
class TestLoginFrame(unittest.TestCase):
    # What It Does:

    # A Tkinter root window is created (and hidden) so that the GUI components can be instantiated.
    # A dummy controller is initialized with one known user (user1 with password pass1).
    # An instance of LoginFrame is created using the root window and the dummy controller.
    def setUp(self):
        # Create a hidden Tk root so that widget creation works.
        self.root = tk.Tk()
        self.root.withdraw()
        # Pre-load the dummy controller with a known user.
        users = {"user1": {"password": "pass1", "email": "user1@example.com"}}
        self.controller = DummyController(users)
        # Create the LoginFrame instance.
        self.login_frame = LoginFrame(self.root, self.controller)

    def tearDown(self):
        self.root.destroy()


    # Step-by-Step Explanation:

    # Mocking:
    # The @patch decorators replace messagebox.showinfo and messagebox.showerror with mocks so that we can verify which ones are called.
    # Simulating User Input:
    # The test inserts the correct username and password into the entry fields.
    # Calling the Login Method:
    # The login() method is called. The method checks the input against the dummy controller’s user database.
    # Verifications:
    #     The test asserts that messagebox.showinfo was called with a success message.
    #     It checks that the dummy controller's current_user is set to "user1".
    #     It verifies that the frame has been switched (recorded by frame_shown being "CatalogFrame").
    #     It confirms that the entry fields have been cleared.

    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    def test_successful_login(self, mock_showerror, mock_showinfo):
        # Set up the entry fields with valid credentials.
        self.login_frame.username_entry.insert(0, "user1")
        self.login_frame.password_entry.insert(0, "pass1")
        # Call the login method.
        self.login_frame.login()
        # Assert that a success info message was shown.
        mock_showinfo.assert_called_with("Login", "Login successful!")
        # The dummy controller should have its current_user updated and frame switched.
        self.assertEqual(self.controller.current_user, "user1")
        self.assertEqual(self.controller.frame_shown, "CatalogFrame")
        # After login, entry fields should be cleared.
        self.assertEqual(self.login_frame.username_entry.get(), "")
        self.assertEqual(self.login_frame.password_entry.get(), "")


# Step-by-Step Explanation:

#     Simulated Incorrect Input:
#     The test inputs an incorrect password.
#     Calling the Login Method:
#     When login() is called, it detects the mismatch.
#     Verifications:
#         The test checks that messagebox.showerror was called with an error message.
#         It verifies that no user was set (i.e., current_user remains None).
#         It confirms that no frame switch occurred (frame_shown remains None).
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    def test_failed_login(self, mock_showerror, mock_showinfo):
        # Set up the entry fields with an invalid password.
        self.login_frame.username_entry.insert(0, "user1")
        self.login_frame.password_entry.insert(0, "wrongpass")
        # Call the login method.
        self.login_frame.login()
        # Assert that an error message was shown.
        mock_showerror.assert_called_with("Error", "Invalid username or password.")
        # current_user should remain None and no frame change should occur.
        self.assertIsNone(self.controller.current_user)
        self.assertIsNone(self.controller.frame_shown)

# ----------------- Tests for SignupFrame -----------------
class TestSignupFrame(unittest.TestCase):
    # What It Does:

    # Creates a hidden Tkinter root.
    # Instantiates a dummy controller with an empty user database.
    # Creates an instance of SignupFrame.
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyController()
        self.signup_frame = SignupFrame(self.root, self.controller)

    def tearDown(self):
        self.root.destroy()

# Step-by-Step Explanation:

#     Simulating Valid Input:
#     The test inserts a new username (user2), a valid email, and matching passwords into the signup fields.
#     Calling the Signup Method:
#     The signup() method processes the data:
#         It checks for an existing username.
#         It checks that the passwords match.
#         It validates the email format.
#         It checks for non-empty fields.
#     Verifications:
#         The test confirms that the new user is added to the dummy controller's users dictionary.
#         It checks that save_users() was called (flagged by self.controller.saved being True).
#         It asserts that a success message is shown and the frame changes back to the login screen.
#         Finally, it verifies that the entry fields are cleared after signup.
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    def test_successful_signup(self, mock_showerror, mock_showinfo):
        # Provide valid input data.
        self.signup_frame.username_entry.insert(0, "user2")
        self.signup_frame.email_entry.insert(0, "user2@example.com")
        self.signup_frame.password_entry.insert(0, "pass2")
        self.signup_frame.confirm_password_entry.insert(0, "pass2")
        # Call the signup method.
        self.signup_frame.signup()
        # Assert that the user is added to the controller's user dictionary.
        self.assertIn("user2", self.controller.users)
        self.assertEqual(self.controller.users["user2"]["password"], "pass2")
        self.assertEqual(self.controller.users["user2"]["email"], "user2@example.com")
        # Confirm that the save_users method was triggered.
        self.assertTrue(self.controller.saved)
        # Assert that a success message was shown and that the frame switched back to login.
        mock_showinfo.assert_called_with("Sign Up", "Account created successfully!")
        self.assertEqual(self.controller.frame_shown, "LoginFrame")
        # The input fields should be cleared.
        self.assertEqual(self.signup_frame.username_entry.get(), "")
        self.assertEqual(self.signup_frame.password_entry.get(), "")
        self.assertEqual(self.signup_frame.confirm_password_entry.get(), "")

# Step-by-Step Explanation:

#     Precondition Setup:
#     A user with username "user2" is pre-added to the dummy controller.
#     Simulated Input:
#     The test attempts to sign up with the same username.
#     Verification:
#     It asserts that an error message is shown, indicating the username already exists.
    @patch('tkinter.messagebox.showerror')
    def test_existing_username(self, mock_showerror):
        # Pre-add a user with username "user2".
        self.controller.users["user2"] = {"email": "user2@example.com", "password": "pass2"}
        self.signup_frame.username_entry.insert(0, "user2")
        self.signup_frame.email_entry.insert(0, "user2@example.com")
        self.signup_frame.password_entry.insert(0, "pass2")
        self.signup_frame.confirm_password_entry.insert(0, "pass2")
        # Call the signup method.
        self.signup_frame.signup()
        # Expect an error message about the username already existing.
        mock_showerror.assert_called_with("Error", "Username already exists.")

# Step-by-Step Explanation:

#     Simulated Input:
#     The test inputs a username, a valid email, and two different passwords.
#     Verification:
#     The method should detect that the passwords do not match and call showerror with the appropriate message.
    @patch('tkinter.messagebox.showerror')
    def test_mismatched_passwords(self, mock_showerror):
        self.signup_frame.username_entry.insert(0, "user3")
        self.signup_frame.email_entry.insert(0, "user3@example.com")
        self.signup_frame.password_entry.insert(0, "pass3")
        self.signup_frame.confirm_password_entry.insert(0, "different")
        self.signup_frame.signup()
        mock_showerror.assert_called_with("Error", "Passwords do not match.")
        

# Step-by-Step Explanation:

#     Simulated Input:
#     A username and matching passwords are provided, but the email format is invalid.
#     Verification:
#     The test confirms that the email validation kicks in and an error message is shown.
    @patch('tkinter.messagebox.showerror')
    def test_invalid_email(self, mock_showerror):
        self.signup_frame.username_entry.insert(0, "user4")
        self.signup_frame.email_entry.insert(0, "invalid-email")
        self.signup_frame.password_entry.insert(0, "pass4")
        self.signup_frame.confirm_password_entry.insert(0, "pass4")
        self.signup_frame.signup()
        mock_showerror.assert_called_with("Error", "Email is invalid.")

# Step-by-Step Explanation:

#     Simulated Input:
#     The test leaves all fields empty.
#     Verification:
#     The expectation is that the signup logic detects missing data and calls showerror with a message that required fields are empty.
#     Important Note:
#     In the actual code, the email validation may be checked before the empty fields check, so the message might differ (for example, it might report "Email is invalid.").
#         You have two options: adjust the test expectation or change the order of validations in the code so that the empty fields check happens first.

    @patch('tkinter.messagebox.showerror')
    def test_empty_fields(self, mock_showerror):
        # Insert empty values for username, email, and password fields.
        self.signup_frame.username_entry.insert(0, "")
        self.signup_frame.email_entry.insert(0, "")
        self.signup_frame.password_entry.insert(0, "")
        self.signup_frame.confirm_password_entry.insert(0, "")
        self.signup_frame.signup()
        mock_showerror.assert_called_with("Error", "Username and password cannot be empty.")

if __name__ == "__main__":
    unittest.main()


# Overall Structure:
# The unit test suite sets up a controlled environment using a hidden Tkinter root and a dummy controller. 
# It creates instances of the GUI frames and simulates user interactions by inserting text into entry fields.

# Use of Mocks:
# By patching messagebox.showinfo and messagebox.showerror, the tests verify that the methods under test behave as expected without showing actual pop-up dialogs. 
# This is essential for unit testing GUI logic.

# Coverage:
# The tests cover both success and failure scenarios:

#     For LoginFrame, both a valid login and an invalid login.
#     For SignupFrame, scenarios include successful signup, duplicate usernames, mismatched passwords, invalid email, and empty input fields.

# Meeting the Requirements:
# The provided test suite fulfills the initial instructions by isolating and testing methods of two classes at the unit level,
#  using simple tests with mock objects. This ensures that the critical logic (input validation, user creation, navigation between frames) is working as intended.