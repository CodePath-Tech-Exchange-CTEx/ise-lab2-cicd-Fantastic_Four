#############################################################################
# loggin_page_test.py
#
# Unit tests for view/loggin_page.py
# All Streamlit and backend calls are mocked to run without dependencies.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock

from view.loggin_page import login_page


class TestLoginPage(unittest.TestCase):
    """Tests for the login_page function."""

    @patch('view.loggin_page.display_login_form')
    @patch('streamlit.title')
    def test_login_page_calls_display_login_form(
        self, mock_title, mock_display_form
    ):
        """Test that the login form is displayed."""
        mock_display_form.return_value = ('testuser', 'password123', False)
        
        login_page()
        
        mock_display_form.assert_called_once()

    @patch('streamlit.rerun')
    @patch('streamlit.success')
    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_successful_login(
        self, mock_display_form, mock_verify_login, mock_success, mock_rerun
    ):
        """Test successful login when credentials are correct."""
        mock_display_form.return_value = ('testuser', 'password123', True)
        mock_verify_login.return_value = 'user123'
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            login_page()
        
        mock_verify_login.assert_called_once_with('testuser', 'password123')
        mock_success.assert_called_once_with("Login successful! Welcome!")

    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_no_action_when_not_submitted(
        self, mock_display_form, mock_verify_login
    ):
        """Test that no verification happens when form is not submitted."""
        mock_display_form.return_value = ('testuser', 'password123', False)
        
        login_page()
        
        mock_verify_login.assert_not_called()

    @patch('streamlit.error')
    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_failed_login_incorrect_credentials(
        self, mock_display_form, mock_verify_login, mock_error
    ):
        """Test failed login when credentials are incorrect."""
        mock_display_form.return_value = ('testuser', 'wrongpassword', True)
        mock_verify_login.return_value = None
        
        login_page()
        
        mock_verify_login.assert_called_once_with('testuser', 'wrongpassword')
        mock_error.assert_called_once_with("Incorrect username or password.")

    @patch('streamlit.error')
    @patch('streamlit.success')
    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_no_success_message_on_failure(
        self, mock_display_form, mock_verify_login, mock_success, mock_error
    ):
        """Test that success message is not shown on failed login."""
        mock_display_form.return_value = ('testuser', 'wrongpass', True)
        mock_verify_login.return_value = None
        
        login_page()
        
        mock_success.assert_not_called()
        mock_error.assert_called_once()

    @patch('streamlit.rerun')
    @patch('streamlit.success')
    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_sets_session_state_on_success(
        self, mock_display_form, mock_verify_login, mock_success, mock_rerun
    ):
        """Test that session state is set correctly on successful login."""
        mock_display_form.return_value = ('testuser', 'password123', True)
        mock_verify_login.return_value = 'user456'
        
        with patch.dict('streamlit.session_state', {}, clear=True) as session_state:
            login_page()
            self.assertEqual(session_state['logged_in_user'], 'user456')

    @patch('streamlit.rerun')
    @patch('streamlit.success')
    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_calls_rerun_on_success(
        self, mock_display_form, mock_verify_login, mock_success, mock_rerun
    ):
        """Test that streamlit rerun is called on successful login."""
        mock_display_form.return_value = ('testuser', 'password123', True)
        mock_verify_login.return_value = 'user789'
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            login_page()
        
        mock_rerun.assert_called_once()

    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_with_empty_credentials(
        self, mock_display_form, mock_verify_login
    ):
        """Test login attempt with empty username and password."""
        mock_display_form.return_value = ('', '', True)
        mock_verify_login.return_value = None
        
        login_page()
        
        mock_verify_login.assert_called_once_with('', '')

    @patch('streamlit.rerun')
    @patch('streamlit.success')
    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_with_special_characters_in_username(
        self, mock_display_form, mock_verify_login, mock_success, mock_rerun
    ):
        """Test login with special characters in username."""
        username_special = 'user@example.com'
        mock_display_form.return_value = (username_special, 'password123', True)
        mock_verify_login.return_value = 'user_special_id'
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            login_page()
        
        mock_verify_login.assert_called_once_with(username_special, 'password123')
        mock_success.assert_called_once()

    @patch('streamlit.error')
    @patch('view.loggin_page.verify_login')
    @patch('view.loggin_page.display_login_form')
    def test_login_page_case_sensitivity(
        self, mock_display_form, mock_verify_login, mock_error
    ):
        """Test that login handles case-sensitive usernames."""
        mock_display_form.return_value = ('TestUser', 'password123', True)
        mock_verify_login.return_value = None
        
        login_page()
        
        mock_verify_login.assert_called_once_with('TestUser', 'password123')


if __name__ == '__main__':
    unittest.main()
