import google.generativeai as genai
from dotenv import load_dotenv
import os


load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


def create_prompt(context: str, data: tuple):
    response = model.generate_content(f"{data}\n{context}")
    return response.text
