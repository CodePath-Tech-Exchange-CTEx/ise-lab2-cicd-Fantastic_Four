import unittest
from unittest.mock import patch, MagicMock
import datetime
from view.sign_up_page import sign_up_page

class TestSignUpPage(unittest.TestCase):

    def setUp(self):
        """Set up mocks for Streamlit and backend functions."""
        self.patchers = [
            patch('view.sign_up_page.st'),
            patch('view.sign_up_page.create_user')
        ]
        
        # Start patchers
        self.mock_st, self.mock_create_user = [p.start() for p in self.patchers]
        
        # Configure the mock form context manager
        # This allows 'with st.form("signup_form"):' to work in tests
        self.mock_st.form.return_value.__enter__ = MagicMock()
        self.mock_st.form.return_value.__exit__ = MagicMock()

    def tearDown(self):
        """Stop all patchers."""
        for p in self.patchers:
            p.stop()

    def test_signup_form_renders_properly(self):
        """Check if all necessary input fields are present in the UI."""
        # Simulate button NOT clicked
        self.mock_st.form_submit_button.return_value = False
        
        sign_up_page()
        
        # Verify UI components are called
        self.mock_st.form.assert_called_once_with("signup_form")
        self.mock_st.text_input.assert_any_call("Enter your name")
        self.mock_st.text_input.assert_any_call("Enter your unique username")
        self.mock_st.text_input.assert_any_call("Create a unique password", type="password")
        self.mock_st.date_input.assert_called_once_with("Insert your DOB")

    def test_successful_signup_flow(self):
        """Verify that create_user is called with correct data when button is clicked."""
        # Setup mock inputs
        test_data = {
            "name": "John Doe",
            "username": "johnd",
            "password": "securepassword123",
            "dob": datetime.date(1995, 5, 20),
            "image": "http://example.com/photo.jpg"
        }
        
        # Mock the return values of the inputs in order
        self.mock_st.text_input.side_effect = [test_data["name"], test_data["username"], test_data["password"], test_data["image"]]
        self.mock_st.date_input.return_value = test_data["dob"]
        
        # Simulate the user clicking the Submit button
        self.mock_st.form_submit_button.return_value = True
        
        sign_up_page()
        
        # Verify backend call
        self.mock_create_user.assert_called_once_with(
            test_data["name"],
            test_data["username"],
            test_data["password"],
            test_data["dob"],
            test_data["image"]
        )
        
        # Verify success message
        self.mock_st.success.assert_called_once_with("Account successfully created! You can now log in.")

    def test_no_action_when_button_not_clicked(self):
        """Ensure backend is NOT called if the submit button isn't pressed."""
        self.mock_st.form_submit_button.return_value = False
        
        sign_up_page()
        
        self.mock_create_user.assert_not_called()
        self.mock_st.success.assert_not_called()

if __name__ == '__main__':
    unittest.main()