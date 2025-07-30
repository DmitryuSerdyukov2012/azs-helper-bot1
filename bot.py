import telebot
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("knowledge_base.json", "r", encoding="utf-8") as f:
    kb = json.load(f)

def find_algorithm(query):
    for algo in kb.get("алгоритмы", []):
        if any(k.lower() in query.lower() for k in algo["ключевые_темы"]):
            return algo
    return None

def ask_gpt(prompt):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты помощник оператора АЗС. Отвечай по существу, кратко, ссылаясь на ГОСТы и инструкции."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "🔧 Я бот-помощник для операторов АЗС. Задай вопрос или напиши ключевое слово (например: 'прием СУГ').")

@bot.message_handler(func=lambda message: True)
def handle_query(message):
    algo = find_algorithm(message.text)
    if algo:
        reply = f"📘 *{algo['название']}*\n"
        for step in algo["этапы"]:
            reply += f"🔹 *{step['этап']}*: {step['описание']}\n"
        bot.send_message(message.chat.id, reply, parse_mode="Markdown")
    else:
        answer = ask_gpt(message.text)
        bot.send_message(message.chat.id, answer)

bot.infinity_polling()
