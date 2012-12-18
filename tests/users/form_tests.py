"""Tests for form creation and editing."""

from tests import ACMFormTest
from acm_phoenix.users.forms import RegisterForm, EditForm

class UserFormsTest(ACMFormTest):
    """Unit tests for User Forms."""
    forms = [RegisterForm, EditForm]
