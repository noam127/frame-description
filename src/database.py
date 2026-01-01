"""MongoDB operations for storing frame descriptions."""

from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError
from .exceptions import (
    ConnectionFailureError,
    DuplicateFrameError,
    DatabaseWriteError
)


class FrameDescriptionRepository:
    """Repository for managing frame descriptions in MongoDB."""

    def __init__(self, mongodb_uri: str, database_name: str, collection_name: str):
        """Initialize the repository and create indexes.

        Args:
            mongodb_uri: MongoDB connection URI.
            database_name: Name of the database.
            collection_name: Name of the collection.

        Raises:
            ConnectionFailureError: If connection to MongoDB fails.
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
            raise ConnectionFailureError(
                f"Cannot connect to MongoDB at {mongodb_uri}: {str(e)}. "
                "Ensure MongoDB is running."
            )
        except PyMongoError as e:
            raise ConnectionFailureError(
                f"MongoDB error during initialization: {str(e)}"
            )

    def _create_indexes(self):
        """Create necessary indexes for the collection."""
        try:
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

        except PyMongoError as e:
            # Don't fail initialization if index creation fails
            # (indexes might already exist)
            pass

    def insert_description(self, document: dict) -> str:
        """Insert a frame description document.

        Args:
            document: Dictionary containing frame description data.

        Returns:
            String representation of the inserted document's ObjectId.

        Raises:
            DuplicateFrameError: If a description for this video+timestamp already exists.
            DatabaseWriteError: If the insert operation fails.
        """
        try:
            # Add timestamp for when this was created
            document["created_at"] = datetime.utcnow()

            # Insert the document
            result = self.collection.insert_one(document)

            return str(result.inserted_id)

        except DuplicateKeyError:
            raise DuplicateFrameError(
                f"Frame description already exists for video '{document.get('video_path')}' "
                f"at timestamp {document.get('timestamp')}s"
            )
        except PyMongoError as e:
            raise DatabaseWriteError(
                f"Failed to insert document into MongoDB: {str(e)}"
            )

    def find_by_video(self, video_path: str) -> list:
        """Find all frame descriptions for a given video.

        Args:
            video_path: Path to the video file.

        Returns:
            List of frame description documents.
        """
        try:
            return list(self.collection.find({"video_path": video_path}))
        except PyMongoError as e:
            raise DatabaseWriteError(
                f"Failed to query MongoDB: {str(e)}"
            )

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
