# File path: backend/api/storage.py
from django.core.files.storage import FileSystemStorage
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.storage import Storage

class MixedStorage(Storage):
    """
    Custom storage to route PDFs to local filesystem and images to Cloudinary.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloudinary_storage = MediaCloudinaryStorage()
        self.local_storage = FileSystemStorage()

    def _save(self, name, content):
        # Agar file PDF hai, toh local storage me save karo
        if name.lower().endswith('.pdf'):
            return self.local_storage._save(name, content)
        # Baaki files (images) Cloudinary par jayengi
        return self.cloudinary_storage._save(name, content)

    def url(self, name):
        if name.lower().endswith('.pdf'):
            return self.local_storage.url(name)
        return self.cloudinary_storage.url(name)

    def exists(self, name):
        if name.lower().endswith('.pdf'):
            return self.local_storage.exists(name)
        return self.cloudinary_storage.exists(name)

    def delete(self, name):
        if name.lower().endswith('.pdf'):
            return self.local_storage.delete(name)
        return self.cloudinary_storage.delete(name)