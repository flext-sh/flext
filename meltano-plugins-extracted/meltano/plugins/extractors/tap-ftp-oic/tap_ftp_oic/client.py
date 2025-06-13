"""FTP Client for OIC integration.

This module provides FTP client functionality for extracting data to be loaded into OIC.
"""

import ftplib
import io
import json
import logging
import os
import re

logger = logging.getLogger(__name__)


class FTPClient:
    """FTP client for extracting data for OIC integration."""

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int = 21,
        passive: bool = True,
    ) -> None:
        """Initialize FTP client.

        Args:
            hostname: FTP server hostname
            username: FTP username
            password: FTP password
            port: FTP server port
            passive: Whether to use passive mode

        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.passive = passive
        self.connection = None

    def connect(self) -> None:
        """Connect to FTP server."""
        try:
            self.connection = ftplib.FTP()
            self.connection.connect(self.hostname, self.port)
            self.connection.login(self.username, self.password)
            if self.passive:
                self.connection.set_pasv(True)
            logger.info(f"Connected to FTP server {self.hostname}")
        except Exception as e:
            logger.exception(f"Failed to connect to FTP server: {e!s}")
            raise

    def disconnect(self) -> None:
        """Disconnect from FTP server."""
        if self.connection:
            try:
                self.connection.quit()
            except Exception:
                self.connection.close()
            self.connection = None
            logger.info("Disconnected from FTP server")

    def __enter__(self):
        """Enter context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.disconnect()

    def list_files(self, path: str = "/") -> list[str]:
        """List files in a directory.

        Args:
            path: Directory path

        Returns:
            list of file names

        """
        if not self.connection:
            self.connect()

        file_list = []
        self.connection.cwd(path)
        self.connection.retrlines("LIST", lambda x: file_list.append(x.split()[-1]))
        return file_list

    def download_file(self, remote_path: str, local_path: str | None = None) -> str:
        """Download a file from FTP.

        Args:
            remote_path: Remote file path
            local_path: Local file path

        Returns:
            Path to downloaded file

        """
        if not self.connection:
            self.connect()

        if not local_path:
            local_path = os.path.basename(remote_path)

        with open(local_path, "wb") as f:
            self.connection.retrbinary(f"RETR {remote_path}", f.write)

        logger.info(f"Downloaded {remote_path} to {local_path}")
        return local_path

    def read_file(self, remote_path: str) -> bytes:
        """Read a file from FTP without saving to disk.

        Args:
            remote_path: Remote file path

        Returns:
            File contents as bytes

        """
        if not self.connection:
            self.connect()

        buffer = io.BytesIO()
        self.connection.retrbinary(f"RETR {remote_path}", buffer.write)
        buffer.seek(0)
        return buffer.getvalue()

    def read_json(self, remote_path: str) -> dict:
        """Read a JSON file from FTP.

        Args:
            remote_path: Remote file path

        Returns:
            Parsed JSON data

        """
        content = self.read_file(remote_path)
        return json.loads(content.decode("utf-8"))

    def read_csv(self, remote_path: str, delimiter: str = ",") -> list[list[str]]:
        """Read a CSV file from FTP.

        Args:
            remote_path: Remote file path
            delimiter: CSV delimiter

        Returns:
            list of rows

        """
        content = self.read_file(remote_path).decode("utf-8")
        return [line.split(delimiter) for line in content.splitlines()]

    def upload_file(self, local_path: str, remote_path: str | None = None) -> str:
        """Upload a file to FTP.

        Args:
            local_path: Local file path
            remote_path: Remote file path

        Returns:
            Remote file path

        """
        if not self.connection:
            self.connect()

        if not remote_path:
            remote_path = os.path.basename(local_path)

        with open(local_path, "rb") as f:
            self.connection.storbinary(f"STOR {remote_path}", f)

        logger.info(f"Uploaded {local_path} to {remote_path}")
        return remote_path

    def upload_data(self, data: str | bytes, remote_path: str) -> str:
        """Upload data to FTP.

        Args:
            data: Data to upload
            remote_path: Remote file path

        Returns:
            Remote file path

        """
        if not self.connection:
            self.connect()

        if isinstance(data, str):
            data = data.encode("utf-8")

        buffer = io.BytesIO(data)
        self.connection.storbinary(f"STOR {remote_path}", buffer)

        logger.info(f"Uploaded data to {remote_path}")
        return remote_path

    def find_files_by_pattern(self, directory: str, pattern: str) -> list[str]:
        """Find files matching a pattern.

        Args:
            directory: Directory to search in
            pattern: Regex pattern to match against filenames

        Returns:
            list of matching file paths

        """
        if not self.connection:
            self.connect()

        all_files = self.list_files(directory)
        return [os.path.join(directory, f) for f in all_files if re.match(pattern, f)]

    def find_files_by_date(
        self,
        directory: str,
        date_format: str = r"\d{4}-\d{2}-\d{2}",
        after_date: str | None = None,
    ) -> list[str]:
        """Find files by date pattern in filename.

        Args:
            directory: Directory to search in
            date_format: Regex pattern to extract date from filename
            after_date: Only include files after this date (YYYY-MM-DD)

        Returns:
            list of matching file paths

        """
        if not self.connection:
            self.connect()

        all_files = self.list_files(directory)
        matching_files = []

        for filename in all_files:
            match = re.search(date_format, filename)
            if match:
                if after_date:
                    file_date = match.group(0)
                    if file_date >= after_date:
                        matching_files.append(os.path.join(directory, filename))
                else:
                    matching_files.append(os.path.join(directory, filename))

        return matching_files
