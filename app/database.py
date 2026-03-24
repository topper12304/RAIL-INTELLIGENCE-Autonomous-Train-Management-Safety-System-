"""
Task 9: SQLite persistence layer for RAIL-INTELLIGENCE event logging.
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rail_intelligence.db")


def _ensure_data_dir() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


# ---------------------------------------------------------------------------
# Task 9.1 — Schema initialization
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS route_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id    TEXT    NOT NULL,
    source      TEXT    NOT NULL,
    target      TEXT    NOT NULL,
    distance    REAL,
    path        TEXT,
    priority    INTEGER,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fault_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id    TEXT,
    coach_id    TEXT    NOT NULL,
    position    INTEGER NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS platform_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_id     INTEGER NOT NULL,
    train_id        TEXT,
    arrival_time    INTEGER NOT NULL,
    departure_time  INTEGER NOT NULL,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS safety_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id        TEXT,
    position        INTEGER NOT NULL,
    final_position  INTEGER NOT NULL,
    final_state     TEXT    NOT NULL,
    action          TEXT,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def init_database(db_path: str = DB_PATH) -> None:
    """Create all tables if they don't exist."""
    _ensure_data_dir()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


# ---------------------------------------------------------------------------
# Task 9.2 — DatabaseManager with context manager
# ---------------------------------------------------------------------------

class DatabaseManager:
    """Manages SQLite connections with transaction context manager support."""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        init_database(db_path)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    #  Task 3.9 — Route event logging                                     #
    # ------------------------------------------------------------------ #

    def log_route_event(
        self,
        train_id: str,
        source: str,
        target: str,
        distance: float,
        path: list,
        priority: int = 2,
    ) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO route_events (train_id, source, target, distance, path, priority)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (train_id, source, target, distance, "->".join(path), priority),
            )

    # ------------------------------------------------------------------ #
    #  Task 4.8 — Fault event logging                                     #
    # ------------------------------------------------------------------ #

    def log_fault_event(
        self,
        coach_id: str,
        position: int,
        train_id: str = "",
    ) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO fault_events (train_id, coach_id, position)
                   VALUES (?, ?, ?)""",
                (train_id, coach_id, position),
            )

    # ------------------------------------------------------------------ #
    #  Task 6.7 — Platform event logging                                  #
    # ------------------------------------------------------------------ #

    def log_platform_event(
        self,
        platform_id: int,
        arrival_time: int,
        departure_time: int,
        train_id: str = "",
    ) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO platform_events (platform_id, train_id, arrival_time, departure_time)
                   VALUES (?, ?, ?, ?)""",
                (platform_id, train_id, arrival_time, departure_time),
            )

    # ------------------------------------------------------------------ #
    #  Task 7.10 — Safety event logging                                   #
    # ------------------------------------------------------------------ #

    def log_safety_event(
        self,
        position: int,
        final_position: int,
        final_state: str,
        action: str = "",
        train_id: str = "",
    ) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO safety_events (train_id, position, final_position, final_state, action)
                   VALUES (?, ?, ?, ?, ?)""",
                (train_id, position, final_position, final_state, action),
            )


# ---------------------------------------------------------------------------
# Convenience shim used by coach router (log_fault)
# ---------------------------------------------------------------------------

_default_db: DatabaseManager | None = None


def _get_db() -> DatabaseManager:
    global _default_db
    if _default_db is None:
        _default_db = DatabaseManager()
    return _default_db


def log_fault(coach_id: str, position: int, train_id: str = "") -> None:
    _get_db().log_fault_event(coach_id, position, train_id)
