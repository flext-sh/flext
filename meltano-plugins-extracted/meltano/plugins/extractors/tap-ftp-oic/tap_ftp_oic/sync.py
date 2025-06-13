"""FTP to OIC Synchronization.

This module handles data synchronization from FTP to OIC.
"""

import logging
import os
from datetime import datetime

from tap_ftp_oic.client import FTPClient

logger = logging.getLogger(__name__)


class FTPOICSyncer:
    """Handles data synchronization from FTP to OIC."""

    def __init__(
        self,
        ftp_client: FTPClient,
        source_dir: str,
        target_dir: str,
        file_pattern: str = r".*\.json",
        processed_marker: str = "_processed",
    ) -> None:
        """Initialize FTP to OIC syncer.

        Args:
            ftp_client: FTP client
            source_dir: Source directory on FTP server
            target_dir: Target directory for processed files
            file_pattern: Pattern to match source files
            processed_marker: Marker to add to processed files

        """
        self.ftp_client = ftp_client
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.file_pattern = file_pattern
        self.processed_marker = processed_marker
        self.stats = {"processed": 0, "errors": 0, "skipped": 0}

    def list_source_files(self) -> list[str]:
        """List files in source directory matching pattern.

        Returns:
            list of file paths

        """
        return self.ftp_client.find_files_by_pattern(self.source_dir, self.file_pattern)

    def mark_as_processed(self, file_path: str) -> str:
        """Mark a file as processed by moving it to target directory.

        Args:
            file_path: Path to file

        Returns:
            New file path

        """
        filename = os.path.basename(file_path)
        base, ext = os.path.splitext(filename)
        new_filename = f"{base}{self.processed_marker}{ext}"
        new_path = os.path.join(self.target_dir, new_filename)

        # Download file
        content = self.ftp_client.read_file(file_path)

        # Upload to target location
        self.ftp_client.upload_data(content, new_path)

        # Delete original
        self.ftp_client.connection.delete(file_path)

        logger.info(f"Marked {file_path} as processed, moved to {new_path}")
        return new_path

    def process_file(self, file_path: str) -> dict:
        """Process a single file.

        Args:
            file_path: Path to file

        Returns:
            Processed data

        """
        try:
            data = self.ftp_client.read_json(file_path)

            # Add metadata
            data["_processed_at"] = datetime.now().isoformat()
            data["_source_file"] = file_path

            # Mark as processed
            self.mark_as_processed(file_path)

            self.stats["processed"] += 1
            return data
        except Exception as e:
            logger.exception(f"Error processing {file_path}: {e!s}")
            self.stats["errors"] += 1
            return {"error": str(e), "file": file_path}

    def sync(self, max_files: int | None = None) -> dict:
        """Synchronize data from FTP to OIC.

        Args:
            max_files: Maximum number of files to process

        Returns:
            Sync statistics

        """
        logger.info(f"Starting FTP to OIC sync from {self.source_dir}")

        # Reset stats
        self.stats = {
            "processed": 0,
            "errors": 0,
            "skipped": 0,
            "start_time": datetime.now().isoformat(),
        }

        # Get files to process
        files = self.list_source_files()
        logger.info(f"Found {len(files)} files to process")

        # Apply max_files limit
        if max_files and len(files) > max_files:
            logger.info(f"Limiting to {max_files} files")
            files = files[:max_files]
            self.stats["skipped"] = len(files) - max_files

        # Process files
        processed_data = []
        for file_path in files:
            data = self.process_file(file_path)
            processed_data.append(data)

        # Update stats
        self.stats["end_time"] = datetime.now().isoformat()
        self.stats["total_files"] = len(files)
        self.stats["data"] = processed_data

        logger.info(
            f"Completed FTP to OIC sync: {self.stats['processed']} processed, {self.stats['errors']} errors",
        )
        return self.stats
