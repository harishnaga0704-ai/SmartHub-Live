import io
import zipfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from shop.models import Product


class BackupRestoreViewTests(TestCase):
    def test_download_backup_creates_zip_and_restore_accepts_it(self):
        User = get_user_model()
        admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="StrongPass123!")
        self.client.force_login(admin)

        Product.objects.create(
            name="Existing Product",
            category="Mobile",
            brand="TestBrand",
            price=1999,
            stock=5,
            description="Old product",
        )

        download_response = self.client.get("/backup-restore/download/")
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response["Content-Type"], "application/zip")
        self.assertIn("smarthub-complete-backup.zip", download_response["Content-Disposition"])

        zip_buffer = io.BytesIO(download_response.content)
        with zipfile.ZipFile(zip_buffer, "r") as archive:
            self.assertIn("manage.py", archive.namelist())

        backup = SimpleUploadedFile(
            "smarthub-complete-backup.zip",
            download_response.content,
            content_type="application/zip",
        )

        response = self.client.post("/backup-restore/", {"backup_file": backup}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Full project backup restored successfully.")
