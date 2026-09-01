import os
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.test import SimpleTestCase

# تسمح باستيراد حزمة التخزين في بيئة الاختبار دون أسرار حقيقية.
os.environ.setdefault(
    "CLOUDINARY_URL",
    "cloudinary://test_key:test_secret@test_cloud",
)

from scince.storage import MixedMediaCloudinaryStorage


class MixedMediaCloudinaryStorageTests(SimpleTestCase):
    def setUp(self):
        self.storage = MixedMediaCloudinaryStorage()

    def test_resource_type_is_detected_from_extension(self):
        cases = {
            "work.jpg": "image",
            "experiment.mov": "video",
            "recording.m4a": "video",
            "report.pdf": "raw",
        }

        for filename, expected_type in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(
                    self.storage._get_resource_type(filename),
                    expected_type,
                )

    def test_saved_type_folder_preserves_video_resource_type(self):
        self.assertEqual(
            self.storage._get_resource_type(
                "student_videos/portfolios/submissions/experiment"
            ),
            "video",
        )

    def test_video_delivery_url_is_https(self):
        url = self.storage.url(
            "student_videos/portfolios/submissions/experiment"
        )

        self.assertTrue(url.startswith("https://"))
        self.assertIn("/video/upload/", url)

    @patch("scince.storage.cloudinary.uploader.upload")
    def test_video_upload_uses_video_resource_type(self, upload_mock):
        upload_mock.return_value = {
            "public_id": "student_videos/portfolios/clip"
        }

        self.storage._upload(
            "portfolios/submissions/clip.mp4",
            ContentFile(b"video", name="clip.mp4"),
        )

        upload_options = upload_mock.call_args.kwargs
        self.assertEqual(upload_options["resource_type"], "video")
        self.assertEqual(
            upload_options["folder"],
            "student_videos/portfolios/submissions",
        )
