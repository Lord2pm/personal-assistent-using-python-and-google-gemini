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


def add_task(
    summary,
    description,
    horas_por_dia,
    dias_por_semana,
    numero_pessoas,
    start_date,
    end_date,
):
    cursor.execute(
        "INSERT INTO projetos (titulo, descricao, horas_trabalho_por_dia, dias_por_semana, numero_pessoas, data_inicio, data_fim) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        [
            summary,
            description,
            horas_por_dia,
            dias_por_semana,
            numero_pessoas,
            start_date,
            end_date,
        ],
    )
    connection.commit()


def get_all_tasks() -> tuple:
    cursor.execute("select * from projetos")
    data = cursor.fetchall()
    return data


def check_task(start_date, end_date):
    query = """
        SELECT COUNT(*) 
        FROM projetos 
        WHERE (data_inicio <= %s AND data_fim >= %s)
        OR (data_inicio <= %s AND data_fim >= %s)
        OR (%s <= data_inicio AND %s >= data_inicio)
        OR (%s <= data_fim AND %s >= data_fim)
    """
    cursor.execute(
        query,
        [
            end_date,
            end_date,
            start_date,
            start_date,
            start_date,
            end_date,
            start_date,
            end_date,
        ],
    )
    (count,) = cursor.fetchone()

    return False if count > 0 else True
