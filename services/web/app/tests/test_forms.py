# app/tests/test_project_forms.py

from django.test import SimpleTestCase

from app.forms import (
    ProjectCreateForm,
    ProjectDeleteForm,
    ProjectSelectForm,
    ProjectUpdateForm,
)


class ProjectSelectFormTests(SimpleTestCase):
    def test_valid_form(self):
        form = ProjectSelectForm(data={"project_id": 1})

        self.assertTrue(form.is_valid())

    def test_project_id_required(self):
        form = ProjectSelectForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("project_id", form.errors)


class ProjectCreateFormTests(SimpleTestCase):
    def test_valid_form(self):
        form = ProjectCreateForm(data={"name": "Test Project"})

        self.assertTrue(form.is_valid())

    def test_name_required(self):
        form = ProjectCreateForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_name_max_length(self):
        form = ProjectCreateForm(data={"name": "a" * 256})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class ProjectUpdateFormTests(SimpleTestCase):
    def test_valid_form(self):
        form = ProjectUpdateForm(
            data={
                "project_id": 1,
                "name": "Updated Project",
            }
        )

        self.assertTrue(form.is_valid())

    def test_project_id_required(self):
        form = ProjectUpdateForm(data={"name": "Updated Project"})

        self.assertFalse(form.is_valid())
        self.assertIn("project_id", form.errors)

    def test_name_required(self):
        form = ProjectUpdateForm(data={"project_id": 1})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class ProjectDeleteFormTests(SimpleTestCase):
    def test_valid_form(self):
        form = ProjectDeleteForm(data={"project_id": 1})

        self.assertTrue(form.is_valid())

    def test_project_id_required(self):
        form = ProjectDeleteForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("project_id", form.errors)
