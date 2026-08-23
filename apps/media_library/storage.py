"""Django storage backend for a public Vercel Blob store."""

from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


class VercelBlobStorage(Storage):
    """Store uploaded media in Vercel Blob and expose public URLs."""

    def __init__(self, *args, **kwargs):
        try:
            from vercel.blob import BlobClient
        except ImportError as exc:
            raise ImproperlyConfigured(
                'Install the vercel package to use Vercel Blob storage.'
            ) from exc
        self.client = BlobClient()
        self.access = getattr(settings, 'VERCEL_BLOB_ACCESS', 'public')
        if self.access != 'public':
            raise ImproperlyConfigured(
                'This CMS requires a public Vercel Blob store for direct image URLs.'
            )

    def _save(self, name, content):
        blob = self.client.put(
            name,
            b''.join(content.chunks()),
            access='public',
            content_type=getattr(content, 'content_type', None),
            add_random_suffix=True,
        )
        return blob.url

    def _open(self, name, mode='rb'):
        if 'r' not in mode:
            raise ValueError('Vercel Blob storage only supports read access through open().')
        result = self.client.get(name, access='public')
        if result is None or result.status_code != 200:
            raise FileNotFoundError(name)
        return ContentFile(b''.join(result.stream), name=name)

    def delete(self, name):
        if name:
            self.client.delete(name)

    def exists(self, name):
        return False

    def url(self, name):
        if name.startswith(('http://', 'https://')):
            return name
        raise ImproperlyConfigured('Vercel Blob returned an invalid media URL.')

    def size(self, name):
        return self.client.head(name).size
