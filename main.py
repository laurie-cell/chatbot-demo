from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import csv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class Query(BaseModel):
    message: str

# testing
# @app.get("/")
# def read_root():
#     return {"message": "Chatbot is running"}

def load_faq_from_csv(file_path="faq.csv"):
    faq_entries = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:
                q, a = row[0].strip(), row[1].strip()
                faq_entries.append(f"Q: {q}\nA: {a}")
    return "\n\n".join(faq_entries)


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
async def chat(q: Query):
    faq = load_faq_from_csv()
    prompt = f"{faq}\n\nUser: {q.message}\nAssistant:"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response.choices[0].message.content}
