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

# def load_faq_from_csv(file_path="faq.csv"):
#     faq_entries = []
#     with open(file_path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.reader(csvfile)
#         for row in reader:
#             if len(row) >= 2:
#                 q, a = row[0].strip(), row[1].strip()
#                 faq_entries.append(f"Q: {q}\nA: {a}")
#     return "\n\n".join(faq_entries)

def load_faq_from_txt(file_path="faq.txt"):
    faq_entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split blocks on double newlines → each block = one Q/A pair
    blocks = content.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        if not lines or not lines[0].startswith("Q:"):
            continue

        question = lines[0].replace("Q:", "").strip()
        # Everything after first line = answer (keeps paragraphs & bullets)
        answer = "\n".join(lines[1:]).replace("A:", "").strip()

        if question and answer:
            faq_entries.append(f"Q: {question}\nA: {answer}")

    return "\n\n".join(faq_entries)


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
async def chat(q: Query):
    faq = load_faq_from_txt()
    prompt = f"You are a helpful AI chatbot for KweHealth LLC, which produces an exosome product called HydroKarma. Use the following faq to answer the user's question with the references provided. {faq}\n\nUser: {q.message}\nAssistant:"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response.choices[0].message.content}
