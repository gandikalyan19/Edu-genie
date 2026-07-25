"""Create the EduGenie database tables.

Usage: python -m scripts.init_db
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.core.config import get_settings  # noqa: E402
from backend.app.database.session import init_db  # noqa: E402


def main() -> None:
    settings = get_settings()
    init_db()
    print(f"Database ready at {settings.database_url}")


if __name__ == "__main__":
    main()
