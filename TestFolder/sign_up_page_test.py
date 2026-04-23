#############################################################################
# sign_up_page_test.py
#
# Unit tests for view/sign_up_page.py
# All Streamlit and backend calls are mocked to run without dependencies.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock

from view.sign_up_page import sign_up_page


class TestSignUpPageDisplay(unittest.TestCase):
    """Tests for the sign_up_page function."""

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_displays_title(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that the sign up page displays the correct title."""
        mock_display_form.return_value = (
            'John Doe', 'johndoe', 'password123', '1990-01-01', 'image.png', False
        )
        
        sign_up_page()
        
        mock_title.assert_called_once_with("Join WebFit 💪")

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_calls_display_signup_form(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that the sign up form is displayed."""
        mock_display_form.return_value = (
            'Jane Doe', 'janedoe', 'password456', '1995-05-15', 'image2.png', False
        )
        
        sign_up_page()
        
        mock_display_form.assert_called_once()

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_does_not_create_user_when_not_submitted(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that user is not created when form is not submitted."""
        mock_display_form.return_value = (
            'John Doe', 'johndoe', 'password123', '1990-01-01', 'image.png', False
        )
        
        sign_up_page()
        
        mock_create_user.assert_not_called()
        mock_success.assert_not_called()

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_creates_user_when_submitted(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that user is created when form is submitted."""
        name = 'John Doe'
        username = 'johndoe'
        password = 'password123'
        dob = '1990-01-01'
        image = 'image.png'
        
        mock_display_form.return_value = (name, username, password, dob, image, True)
        
        sign_up_page()
        
        mock_create_user.assert_called_once_with(name, username, password, dob, image)

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_shows_success_message_on_submit(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that success message is displayed after form submission."""
        mock_display_form.return_value = (
            'John Doe', 'johndoe', 'password123', '1990-01-01', 'image.png', True
        )
        
        sign_up_page()
        
        mock_success.assert_called_once_with(
            "Account successfully created! You can now log in."
        )

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_passes_correct_parameters_to_create_user(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that all form parameters are correctly passed to create_user."""
        test_data = {
            'name': 'Jane Smith',
            'username': 'janesmith',
            'password': 'securepass789',
            'dob': '1992-07-20',
            'image': 'jane_profile.png'
        }
        
        mock_display_form.return_value = (
            test_data['name'],
            test_data['username'],
            test_data['password'],
            test_data['dob'],
            test_data['image'],
            True
        )
        
        sign_up_page()
        
        # Verify create_user was called with exact parameters
        mock_create_user.assert_called_once()
        call_args = mock_create_user.call_args[0]
        
        self.assertEqual(call_args[0], test_data['name'])
        self.assertEqual(call_args[1], test_data['username'])
        self.assertEqual(call_args[2], test_data['password'])
        self.assertEqual(call_args[3], test_data['dob'])
        self.assertEqual(call_args[4], test_data['image'])

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_handles_empty_image(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that the form handles cases with no image provided."""
        mock_display_form.return_value = (
            'John Doe', 'johndoe', 'password123', '1990-01-01', None, True
        )
        
        sign_up_page()
        
        mock_create_user.assert_called_once_with(
            'John Doe', 'johndoe', 'password123', '1990-01-01', None
        )
        mock_success.assert_called_once()

    @patch('streamlit.success')
    @patch('view.sign_up_page.create_user')
    @patch('view.sign_up_page.display_signup_form')
    @patch('streamlit.title')
    def test_sign_up_page_multiple_submissions(
        self, mock_title, mock_display_form, mock_create_user, mock_success
    ):
        """Test that form can handle multiple sequential calls."""
        first_submission = ('Alice', 'alice', 'pass1', '1988-03-10', 'alice.png', True)
        second_submission = ('Bob', 'bob', 'pass2', '1991-08-25', 'bob.png', False)
        
        # First call with submission
        mock_display_form.return_value = first_submission
        sign_up_page()
        
        self.assertEqual(mock_create_user.call_count, 1)
        
        # Second call without submission
        mock_display_form.return_value = second_submission
        sign_up_page()
        
        # Should still be 1 call (not incremented)
        self.assertEqual(mock_create_user.call_count, 1)


if __name__ == '__main__':
    unittest.main()
