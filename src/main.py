import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu

from models.db import (
    add_task,
    check_task,
    get_all_tasks,
    suggest_new_start_date,
    connection,
)
from utils.assistente_audio import text_to_audio
from utils.gemini import create_prompt


st.set_page_config(page_title="Agendador de tarefas", layout="wide")
st.title("Agendador de Tarefas")
st.text(
    "Optimize o seu tempo! Agende suas tarefas de forma fácil e rápida utilizando o poder do Google Gemini"
)

with st.sidebar:
    selected = option_menu(
        menu_title="Menu Principal",
        options=["Home", "Cadastrar Projecto", "Ver Agenda"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

if selected == "Home":
    st.image(
        "img/639fb8517670a17d0e466903_Gerenciador-de-tarefas.png",
        caption="Optimize seu tempo, poupe seus recursos e ganhe muito mais!",
        width=700,
    )
    with st.expander("Nossas Vantagens"):
        st.write(
            """
            - **Integração com IA**: Uso de IA para gerenciar a sobreposição e conflito de horários.
            - **Assistente Virtual integrado**: Um assistente virtual integrado para optmizar a interação com pessoas por meio de comandos de voz.
            - **Usabilidade**: Fácil de usar.
            """
        )
elif selected == "Cadastrar Projecto":
    st.header("Cadastrar Projecto")
    with st.form(key="event_form"):
        summary = st.text_input("Título do Projecto")
        description = st.text_area("Descrição do Projecto")
        work_hours = st.number_input("Horas de trabalho por dia")
        number_week_days = st.number_input("Quantidade de dias por semana")
        number_people = st.number_input("Número de pessoas")
        start_date = st.date_input("Data de Início", datetime.now().date())
        end_date = st.date_input("Data de Fim", datetime.now().date())
        submit_button = st.form_submit_button(label="Agendar Tarefa")

        if submit_button:
            if summary and description:
                if start_date < datetime.now().date():
                    start_date = suggest_new_start_date(start_date, end_date)
                    st.warning(
                        f"Sugestão: Transfira a data de início desta tarefa para o dia {start_date} e o fim para."
                    )
                    st.toast(
                        "Conflito: A data de início é no passado. Sugerindo uma nova data..."
                    )
                elif check_task(start_date, end_date):
                    add_task(
                        summary,
                        description,
                        int(work_hours),
                        int(number_week_days),
                        int(number_people),
                        start_date,
                        end_date,
                    )
                    text = create_prompt(
                        f"Tendo em conta as características de um projecto contidas nesta, deia dicas para orientar a equipa de trabalho e ajudar a nivelar recursos de modos a concluir no tempo previsto",
                        [
                            summary,
                            description,
                            int(work_hours),
                            int(number_week_days),
                            int(number_people),
                            start_date,
                            end_date,
                        ],
                    )

                    st.success("Tarefa agendada com sucesso")
                    st.warning(text)
                else:
                    td = end_date - start_date
                    start_date = suggest_new_start_date(start_date, end_date)
                    st.warning(
                        f"Sugestão: Transfira a data de início deste projecto para o dia {start_date} e a data de término para {start_date + timedelta(days=td.days)}."
                    )
                    st.toast(
                        "Conflito: Já existe uma tarefa agendada para esse período."
                    )
            else:
                st.toast("Preencha todos os campos devidamente")
elif selected == "Ver Agenda":
    tabs = st.tabs(["Agenda", "Lista de tarefas"])

    with tabs[1]:
        st.header("Lista de tarefas")
        df = pd.read_sql(
            "select * from projetos",
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
    with tabs[0]:
        projects = get_all_tasks()
        events = []

        for project in projects:

            dt_inicio = datetime.combine(project[6], time(8, 30))
            dt_fim = datetime.combine(project[7], time.min)

            events.append(
                {
                    "title": project[1],
                    "start": dt_inicio.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": dt_fim.strftime("%Y-%m-%dT%H:%M:%S"),
                }
            )

        calendar(events)
