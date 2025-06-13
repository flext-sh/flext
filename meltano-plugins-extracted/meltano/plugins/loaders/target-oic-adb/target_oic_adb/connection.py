"""Oracle database connection for target-oic-adb."""

import logging
import os
from typing import Any

try:
    import cx_Oracle

    DRIVER_AVAILABLE = True
except ImportError:
    DRIVER_AVAILABLE = False

try:
    import oracledb

    ODB_DRIVER_AVAILABLE = True
except ImportError:
    ODB_DRIVER_AVAILABLE = False


class OracleConnection:
    """Oracle database connection manager."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the connection manager."""
        self.config = config
        self.connection = None
        self.is_autonomous = config.get("connection_type") == "autonomous"
        self.driver_type = config.get("driver_type", "thin")

        # Check if required drivers are available
        if not DRIVER_AVAILABLE and not ODB_DRIVER_AVAILABLE:
            msg = (
                "Neither cx_Oracle nor python-oracledb library found. "
                "Please install one of them: pip install cx_Oracle or pip install oracledb"
            )
            raise ImportError(
                msg,
            )

        # Decide which driver to use
        self.use_oracledb = ODB_DRIVER_AVAILABLE
        if DRIVER_AVAILABLE and not ODB_DRIVER_AVAILABLE:
            self.use_oracledb = False

        self.logger = logging.getLogger("target-oic-adb")

    def get_connection(self) -> Any:
        """Return an open connection to the database."""
        if self.connection is not None and self._is_connection_alive():
            return self.connection

        # Close existing connection if it exists
        self._close_connection()

        # Create new connection
        if self.is_autonomous:
            self.connection = self._connect_autonomous()
        else:
            self.connection = self._connect_normal()

        return self.connection

    def _connect_normal(self) -> Any:
        """Connect to a normal Oracle database."""
        host = self.config["host"]
        port = self.config.get("port", 1521)
        user = self.config["user"]
        password = self.config["password"]
        service_name = self.config.get("service_name")
        sid = self.config.get("sid")

        if not service_name and not sid:
            msg = "Either service_name or sid must be provided"
            raise ValueError(msg)

        if self.use_oracledb:
            if service_name:
                dsn = oracledb.makedsn(host, port, service_name=service_name)
            else:
                dsn = oracledb.makedsn(host, port, sid=sid)

            if self.driver_type == "thick":
                oracledb.init_oracle_client()

            return oracledb.connect(user=user, password=password, dsn=dsn)
        if service_name:
            dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        else:
            dsn = cx_Oracle.makedsn(host, port, sid=sid)

        return cx_Oracle.connect(user=user, password=password, dsn=dsn)

    def _connect_autonomous(self) -> Any:
        """Connect to an Oracle Autonomous Database."""
        user = self.config["user"]
        password = self.config["password"]
        wallet_location = self.config.get("wallet_location")
        wallet_password = self.config.get("wallet_password")
        service_name = self.config.get("service_name")

        if not wallet_location:
            msg = "wallet_location is required for autonomous connection"
            raise ValueError(msg)

        if not os.path.exists(wallet_location):
            msg = f"Wallet file not found at {wallet_location}"
            raise FileNotFoundError(msg)

        if not service_name:
            msg = "service_name is required for autonomous connection"
            raise ValueError(msg)

        if self.use_oracledb:
            oracledb.init_oracle_client(
                config_dir=wallet_location,
                wallet_location=wallet_location,
                wallet_password=wallet_password,
            )
            connection = oracledb.connect(
                user=user,
                password=password,
                dsn=service_name,
            )
        else:
            os.environ["TNS_ADMIN"] = wallet_location
            connection = cx_Oracle.connect(
                user=user,
                password=password,
                dsn=service_name,
            )

        return connection

    def _is_connection_alive(self) -> bool:
        """Check if the connection is still alive."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.close()
            return True
        except Exception:
            return False

    def _close_connection(self) -> None:
        """Close the current connection if it exists."""
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception as e:
                self.logger.warning(f"Error closing connection: {e!s}")
            finally:
                self.connection = None

    def close(self) -> None:
        """Close the connection."""
        self._close_connection()

    def __del__(self) -> None:
        """Destructor to ensure connection is closed."""
        self._close_connection()
