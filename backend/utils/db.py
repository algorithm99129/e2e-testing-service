import sqlite3
from contextlib import closing
from typing import List, Dict
import os
import shutil

DB_NAME = "test_results.db"


def init_db(db_name=DB_NAME):
    """Initialize the database and create necessary tables."""
    if not os.path.exists(db_name):
        with open(db_name, "w"):
            pass

    with sqlite3.connect(db_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT,
                    message TEXT,
                    type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY,
                    description TEXT,
                    status TEXT,
                    no_of_steps INTEGER
                )
            """
            )
            conn.commit()

            # Insert initial test cases
            cursor.execute(
                """
                INSERT OR IGNORE INTO test_cases (id, description, status, no_of_steps)
                VALUES
                (0, 'Success upload use case: agent is able to select an mp4 less than 4GB to be converted to avi with rule to choose the lowest HD', 'todo', 4),
                (1, 'Unsuccessful upload use case: upload a video from youtube: https://www.youtube.com/watch?v=aWk2XZ_8lhA', 'todo', 4),
                (2, 'Unsuccessful upload use case: upload video file above 4GB', 'todo', 4)
            """
            )
            conn.commit()


def log_test_message(test_id, log_message, message_type, db_name=DB_NAME):
    """Log a message for a specific test case."""
    with sqlite3.connect(db_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                INSERT INTO test_logs (test_id, message, type)
                VALUES (?, ?, ?)
            """,
                (test_id, log_message, message_type),
            )
            conn.commit()


def fetch_test_logs(test_id, db_name=DB_NAME):
    """Fetch all log messages for a specific test case, sorted by creation time."""
    with sqlite3.connect(db_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "SELECT message, type, created_at FROM test_logs WHERE test_id = ? ORDER BY created_at",
                (test_id,),
            )
            logs = cursor.fetchall()
            logs_json = [
                {"message": log[0], "type": log[1], "created_at": log[2]}
                for log in logs
            ]
    return logs_json


def delete_test_logs(test_id, db_name=DB_NAME):
    """Delete all log messages for a specific test case."""
    with sqlite3.connect(db_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("DELETE FROM test_logs WHERE test_id = ?", (test_id,))
            conn.commit()


def fetch_test_cases(db_name: str = DB_NAME) -> List[Dict[str, str]]:
    """Fetch all test cases."""
    with sqlite3.connect(db_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "SELECT id, description, status, no_of_steps FROM test_cases"
            )
            cases = cursor.fetchall()
            cases_json = [
                {
                    "id": case[0],
                    "description": case[1],
                    "status": case[2],
                    "no_of_steps": case[3],
                }
                for case in cases
            ]
    return cases_json


def update_test_case_status(test_id, status, db_name=DB_NAME):
    """Update the status of a specific test case."""
    with sqlite3.connect(db_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                UPDATE test_cases
                SET status = ?
                WHERE id = ?
            """,
                (status, test_id),
            )
            conn.commit()


def reset_all_test_cases(db_name=DB_NAME):
    """Reset all test cases and delete all log messages."""
    with sqlite3.connect(db_name) as conn:
        with closing(conn.cursor()) as cursor:
            # Delete all log messages
            cursor.execute("DELETE FROM test_logs")
            conn.commit()

            # Reset the status of all test cases to 'todo'
            cursor.execute("UPDATE test_cases SET status = 'todo'")
            conn.commit()

    tmp_folder = "tmp"
    # Check if the folder exists
    if os.path.exists(tmp_folder):
        # Delete all files and subdirectories in the tmp folder
        for filename in os.listdir(tmp_folder):
            file_path = os.path.join(tmp_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
