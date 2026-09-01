"""Cloudinary storage that supports mixed student portfolio media."""

import os
from pathlib import PurePosixPath

import cloudinary.uploader
from cloudinary_storage.storage import MediaCloudinaryStorage


class MixedMediaCloudinaryStorage(MediaCloudinaryStorage):
    """Store images, videos/audio, and documents using the right resource type.

    ``MediaCloudinaryStorage`` treats every upload as an image.  Portfolio
    attachments are mixed media, so each saved public ID is placed below a
    type-specific folder.  That marker also lets URL generation and deletion
    use the correct Cloudinary resource type later, after the extension has
    been removed from an image or video public ID.
    """

    IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
    VIDEO_EXTENSIONS = {"mp4", "mov", "webm", "mp3", "wav", "m4a"}

    TYPE_FOLDERS = {
        "image": "student_images",
        "video": "student_videos",
        "raw": "student_files",
    }

    def _get_resource_type(self, name):
        normalized_name = str(name).replace("\\", "/").lower().lstrip("/")

        for resource_type, folder in self.TYPE_FOLDERS.items():
            if normalized_name.startswith(f"{folder}/"):
                return resource_type

        extension = PurePosixPath(normalized_name).suffix.lower().lstrip(".")

        if extension in self.VIDEO_EXTENSIONS:
            return "video"

        if extension in self.IMAGE_EXTENSIONS:
            return "image"

        if extension:
            return "raw"

        # ملفات الصور القديمة حُفظت قبل إضافة مجلدات النوع.
        return "image"

    def _upload(self, name, content):
        resource_type = self._get_resource_type(name)
        normalized_name = self._normalise_name(name).lstrip("/")
        type_folder = self.TYPE_FOLDERS[resource_type]

        if not normalized_name.startswith(f"{type_folder}/"):
            normalized_name = f"{type_folder}/{normalized_name}"

        options = {
            "use_filename": True,
            "resource_type": resource_type,
            "tags": self.TAG,
        }
        folder = os.path.dirname(normalized_name)

        if folder:
            options["folder"] = folder

        return cloudinary.uploader.upload(content, **options)
