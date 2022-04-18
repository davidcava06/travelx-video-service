import firebase_admin
import structlog
from firebase_admin import credentials, firestore
from google.cloud import storage

logger = structlog.get_logger(__name__)


class GoogleStorageProcessor:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._client = None
        self._db = None
        self.project = app.config.get("GCP_PROJECT")
        self.location = app.config.get("GCP_REGION")
        self.bucket = app.config.get("GCP_BUCKET")

    @property
    def client(self):
        if self._client is None:
            logger.info("Initializing Cloud Storage Client")
            self._client = storage.Client()
        return self._client

    @property
    def db(self):
        if self._db is None:
            logger.info("Initializing Firestore Client")
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(
                cred,
                {
                    "projectId": self.project,
                },
            )
            self._db = firestore.client()
        return self._db

    def _upload_sync(self, filename, key):
        bucket = self.client.get_bucket(self.bucket)
        if not bucket.exists():
            logger.error("Failed upload: Bucket does not exist.")
        blob = bucket.blob(key)
        blob.upload_from_filename(filename)
        logger.info("Blob {} uploaded.".format(filename))
        return True

    def _list_blobs_sync(self, prefix):
        bucket = self.client.get_bucket(self.bucket)
        if not bucket.exists():
            logger.error("Failed read: Bucket does not exist.")
        blob_list = self.client.list_blobs(self.bucket, prefix=prefix)
        return [blob for blob in blob_list]

    def _delete_blob(self, blob_name):
        """Deletes a blob from the bucket."""
        bucket = self.client.get_bucket(self.bucket)
        if not bucket.exists():
            logger.error("Failed read: Bucket does not exist.")
        blob = bucket.blob(blob_name)
        blob.delete()

        logger.info("Blob {} deleted.".format(blob_name))

    def _upload_document_to_firestore(
        self, object: dict, id: str, collection: str = "tiktok"
    ):
        doc_ref = self.db.collection(collection).document(id)
        doc_ref.set(object)
