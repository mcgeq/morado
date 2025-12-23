"""Session manager implementation.

This module provides HTTP session management with connection pooling,
lifecycle management, and context manager support.
"""

from collections.abc import Generator
from contextlib import contextmanager

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as Urllib3Retry


class SessionManager:
    """HTTP session manager.

    Manages the creation, configuration, and cleanup of HTTP sessions.
    Provides connection pooling and context manager support for automatic
    resource management.

    Attributes:
        pool_connections: Number of connection pools to cache
        pool_maxsize: Maximum number of connections to save in the pool
        max_retries: Maximum number of retries (handled by retry module, set to 0)
    """

    def __init__(
        self,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: int = 0
    ):
        """Initialize session manager.

        Args:
            pool_connections: Number of connection pools to cache (default: 10)
            pool_maxsize: Maximum number of connections in the pool (default: 10)
            max_retries: Maximum retries at urllib3 level (default: 0, handled by retry module)
        """
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.max_retries = max_retries
        self._active_sessions: list[Session] = []

    def create_session(self) -> Session:
        """Create a new HTTP session with configured connection pooling.

        Creates a requests.Session object with HTTPAdapter configured for
        connection pooling. The session is tracked for cleanup.

        Returns:
            Configured requests.Session object
        """
        session = Session()

        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            max_retries=Urllib3Retry(
                total=self.max_retries,
                read=self.max_retries,
                connect=self.max_retries,
                backoff_factor=0
            )
        )

        # Mount adapter for both HTTP and HTTPS
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Track active session for cleanup
        self._active_sessions.append(session)

        return session

    @contextmanager
    def session_scope(self) -> Generator[Session]:
        """Context manager for automatic session lifecycle management.

        Creates a session and ensures it's properly closed when the context
        exits, even if an exception occurs.

        Yields:
            Configured requests.Session object

        Example:
            >>> manager = SessionManager()
            >>> with manager.session_scope() as session:
            ...     response = session.get('https://example.com')
        """
        session = self.create_session()
        try:
            yield session
        finally:
            self.close_session(session)

    def close_session(self, session: Session) -> None:
        """Close a session and release its resources.

        Closes the session and removes it from the active sessions list.
        This ensures connection pools are properly cleaned up.

        Args:
            session: The session to close
        """
        if session in self._active_sessions:
            self._active_sessions.remove(session)

        session.close()

    def close_all_sessions(self) -> None:
        """Close all active sessions.

        Closes all sessions that were created by this manager and haven't
        been explicitly closed. Useful for cleanup during shutdown.
        """
        for session in list(self._active_sessions):
            self.close_session(session)

    def __del__(self):
        """Cleanup on garbage collection.

        Ensures all sessions are closed when the manager is destroyed.
        """
        self.close_all_sessions()
