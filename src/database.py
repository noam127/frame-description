from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError
from .exceptions import (
    DatabaseConnectionFailureError,
    DatabaseDuplicateEntryError,
    DatabaseWriteError
)


class FrameDescriptionRepository:
    """Repository for managing frame descriptions in MongoDB."""

    def __init__(self, mongodb_uri: str, database_name: str, collection_name: str):
        """Initialize the repository and create indexes.

        Raises:
            DatabaseConnectionFailureError: If connection to MongoDB fails.
        """
        try:
            self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')

            self.db = self.client[database_name]
            self.collection = self.db[collection_name]

            # Create indexes
            self._create_indexes()

        except ConnectionFailure as e:
            raise DatabaseConnectionFailureError(
                f"Cannot connect to MongoDB at {mongodb_uri}: {str(e)}. "
                "Ensure MongoDB is running."
            )
        except PyMongoError as e:
            raise DatabaseConnectionFailureError(
                f"MongoDB error during initialization: {str(e)}"
            )

    def _create_indexes(self):
        """Create necessary indexes for the collection."""
        # Unique compound index on video_path and timestamp
        self.collection.create_index(
            [("video_path", ASCENDING), ("timestamp", ASCENDING)],
            unique=True,
            name="video_timestamp_unique"
        )

        # Index for temporal queries
        self.collection.create_index(
            [("created_at", DESCENDING)],
            name="created_at_desc"
        )

    def insert_description(self, document: dict) -> str:
        """Insert a frame description document.

        Args:
            document: Dictionary containing frame description data.

        Returns:
            String representation of the inserted document's ObjectId.
        """
        try:
            # Add timestamp for when this was created
            document["created_at"] = datetime.utcnow()

            # Insert the document
            result = self.collection.insert_one(document)

            return str(result.inserted_id)

        except DuplicateKeyError:
            raise DatabaseDuplicateEntryError(
                f"Frame description already exists for video '{document.get('video_path')}' "
                f"at timestamp {document.get('timestamp')}s"
            )
        except PyMongoError as e:
            raise DatabaseWriteError(
                f"Failed to insert document into MongoDB: {str(e)}"
            )

    def close(self):
        self.client.close()
