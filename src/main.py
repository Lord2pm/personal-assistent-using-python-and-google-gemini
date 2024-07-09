import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from models.db import add_task, check_task, get_all_tasks, connection
from utils.assistente_audio import text_to_audio
from utils.gemini import create_prompt


st.set_page_config(page_title="Agendador de tarefas", layout="wide")
st.title("Agendador de Tarefas")
st.text(
    "Optimize o seu tempo! Agende suas tarefas de forma fácil e rápida utilizando o poder do Google Gemini"
)

tabs = st.tabs(["Agendar tarefas", "Ver tarefas agendadas"])

with tabs[0]:
    st.header("Cadastrar tarefa")
    with st.form(key="event_form"):
        summary = st.text_input("Título da tarefa")
        description = st.text_area("Descrição da tarefa")
        start_date = st.date_input("Data de Início", datetime.now().date())
        start_time = st.time_input("Hora de Início", datetime.now().time())
        end_date = st.date_input("Data de Fim", datetime.now().date())
        end_time = st.time_input(
            "Hora de Fim", (datetime.now() + timedelta(hours=1)).time()
        )

        submit_button = st.form_submit_button(label="Agendar Tarefa")

        if submit_button:
            if summary and description:
                start_datetime = datetime.combine(start_date, start_time).isoformat()
                end_datetime = datetime.combine(end_date, end_time).isoformat()

                if check_task(start_datetime, end_datetime):
                    add_task(summary, description, start_datetime, end_datetime)
                    st.success("Tarefa agendada com sucesso")
                else:
                    st.toast(
                        "Conflito: Já existe uma tarefa agendada para esse período."
                    )
            else:
                st.toast("Preencha todos os campos devidamente")

with tabs[1]:
    st.header("Lista de tarefas")
    df = pd.read_sql(
        "select summary as Título, description as Descrição, start_datetime as Ínicio, end_datetime as Término from tasks",
        connection,
    )
    st.write(df)
    bt_alexa = st.button("Ouvir o resumo do Assistente virtual")

    if bt_alexa:
        tasks = get_all_tasks()
        text = create_prompt(
            "Me diga de forma resumida quais as tarefas que eu devo priorizar com base no tempo de ińicio e fim. O formato da resposta deverá ser o seguinte: Primeiro fale tens algumas tarefas para priorizar, depois diga o id da tarefa, título da tarefa e as datas de início e de fim, não coloque ou fale asterisco. E, antes de dizer uma informação diga se se trata do id ou da data. E não inclua as tarefas cujo o tempo de término já foi ultrapassado",
            tasks,
        )
        text_to_audio(text.replace("*", ""))
        st.audio("audio.mp3", autoplay=True)
