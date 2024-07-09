import pymysql as mysql
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

connection = mysql.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    port=int(os.getenv("PORT")),
)
cursor = connection.cursor()


def add_task(summary, description, start_datetime, end_datetime):
    cursor.execute(
        "INSERT INTO tasks (summary, description, start_datetime, end_datetime) VALUES (%s, %s, %s, %s)",
        [summary, description, start_datetime, end_datetime],
    )
    connection.commit()


def get_all_tasks() -> tuple:
    cursor.execute("select * from tasks")
    data = cursor.fetchall()
    return data


def check_task(start_datetime, end_datetime) -> bool:
    query = """
    SELECT COUNT(*) FROM tasks
    WHERE (start_datetime <= %s AND end_datetime >= %s)
       OR (start_datetime <= %s AND end_datetime >= %s)
       OR (start_datetime >= %s AND end_datetime <= %s)
    """
    cursor.execute(
        query,
        [
            start_datetime,
            start_datetime,
            end_datetime,
            end_datetime,
            start_datetime,
            end_datetime,
        ],
    )
    conflict_count = cursor.fetchone()[0]

    if conflict_count > 0:
        return False

    return True
