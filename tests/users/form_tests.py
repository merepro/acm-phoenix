"""Tests for form creation and editing."""

from tests import ACMFormTest
from acm_phoenix.users.forms import RegisterForm, EditForm

import abc

class UserFormsTest(ACMFormTest):
    """Unit tests for User Forms."""
    forms = [RegisterForm, EditForm]

    def test_necessary_fields_in_form(self):
        reg_and_edit_fields = ['name', 'netid', 'email', 'standing', 'major',
                               'shirt_size', 'description']

        form = RegisterForm()
        assert self.fields_in_form_data(form.data, reg_and_edit_fields)

        form = EditForm()
        assert self.fields_in_form_data(form.data, reg_and_edit_fields)
        
        
