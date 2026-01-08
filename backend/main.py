"""Main entry point for the Morado backend application.

This module serves as the entry point for running the Morado backend
application with Uvicorn ASGI server.

Usage:
    Development mode (with auto-reload):
        $ uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

    Production mode:
        $ uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

    Using the module directly:
        $ python -m backend.main
"""

from morado.app import app

if __name__ == "__main__":
    import uvicorn

    from morado.core.config import get_settings

    settings = get_settings()

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload or settings.is_development,
        workers=1 if settings.is_development else settings.workers,
        log_level=settings.log_level.lower(),
    )
