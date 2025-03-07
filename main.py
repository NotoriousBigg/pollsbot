import asyncio

from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv

import os
import httpx
import sqlite3

load_dotenv()

# tg bot token
TOKEN = os.getenv('BOT_TOKEN') # get token from bot father
QUIZ_API_KEY = os.getenv('QUIZ_API_KEY') # get your api key from https://quizapi.io
BASE_URL = "https://quizapi.io/api/v1/questions"

# start async telebot
Prime = AsyncTeleBot(TOKEN)

DB_FILE = 'prime.db'

# Create database
def init_db():
    """Initialize the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

# database functions

async def add_chat(chat_id):
    """Add a chat to the database if not already added."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()

async def remove_chat(chat_id):
    """Remove a chat from the database when bot is removed."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

async def get_chats():
    """Get all chat IDs from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM chats")
    chats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return chats

# Function for http requests
async def get_http_data(url):
    async with httpx.AsyncClient(timeout=20) as cl:
        data = {
            'X-Api-Key': QUIZ_API_KEY
        }
        r = await cl.get(url, headers=data)
        if r.status_code != 200:
            print(r.status_code)
            return None
        return r.json()[0] # return the first question


#for fetching poll data
async def get_poll_data(data: {}):
    if data is None:
        return None, None, None, None
    quiz = data['question']

    explanation = data.get("explanation", "No explanation provided.")
    if len(explanation) > 200:
        explanation = explanation[:197] + "..."

    answers_dict = data["answers"]
    options = [ans for ans in answers_dict.values() if ans]

    correct_answers_dict = data["correct_answers"]
    correct_index = next(
        (i for i, key in enumerate(answers_dict.keys()) if correct_answers_dict[f"{key}_correct"] == "true"), None
    )

    return quiz, options, correct_index, explanation


async def auto_poll():
    while True:
        chats = await get_chats()  # Get all stored chats
        if not chats:
            print("⚠️ No groups/channels found. Waiting...")
            continue

        data = await get_http_data(BASE_URL)
        if data is None:
            print("⚠️ API Error. Retrying in 30 minutes...")
            await asyncio.sleep(1800)
            continue

        poll_data = await get_poll_data(data)
        if None in poll_data:
            print("⚠️ Failed to fetch poll data. Retrying in 30 minutes...")
            await asyncio.sleep(1800)
            continue

        quiz, options, correct_index, explanation = poll_data
        for chat_id in chats:
            try:
                msg = await Prime.send_poll(
                    chat_id=chat_id,
                    question=quiz,
                    options=options,
                    type='quiz',
                    correct_option_id=correct_index,
                    explanation=explanation,
                    is_anonymous=False
                )

                await asyncio.sleep(1800)
                await Prime.delete_message(chat_id, message_id=msg.message_id)
            except Exception as e:
                print(f"⚠️ Failed to send poll to {chat_id}: {e}")
                await remove_chat(chat_id)


# define start command
@Prime.message_handler(commands=['start'])
async def start_handler(message):
    first_name = message.from_user.first_name
    await Prime.send_message(
        message.chat.id,
        f"Hello {first_name}, Welcome to QUIZ BOT"
    )

# poll command handler
@Prime.message_handler(commands=['poll'])
async def poll_handler(message):
    try:
        while True:
            data = await get_http_data(BASE_URL)
            if data is None:
                await Prime.send_message(
                    message.chat.id,
                    "An error occurred communicating with API. Try again later"
                )
                return
            poll_data = await get_poll_data(data)
            if not poll_data:
                await Prime.send_message(
                    message.chat.id,
                    'Failed to fetch poll data.'
                )
                return
            quiz, options, correct_index, explanation = poll_data
            msg = await Prime.send_poll(
                chat_id=message.chat.id,
                question=quiz,
                options=options,
                type='quiz',
                correct_option_id=correct_index,
                explanation=explanation,
                is_anonymous=False
            )

            await asyncio.sleep(1800)
            await Prime.delete_message(
                message.chat.id,
                message_id=msg.message_id
            )

    except Exception as k:
        await Prime.send_message(
            message.chat.id,
            f"error: {k}"
        )

@Prime.message_handler(content_types=['new_chat_members'])
async def new_chat_handler(message):
    chat_id = message.chat.id
    await add_chat(chat_id)
    await Prime.send_message(chat_id, "✅ Thanks for adding me to your group. I will be sending polls after 30 minutes.")
    await auto_poll()

# Remove chat from DB when bot is removed
@Prime.message_handler(content_types=['left_chat_member'])
async def left_chat_handler(message):
    chat_id = message.chat.id
    await remove_chat(chat_id)

async def main():
    print("🚀 Bot started. Sending auto-polls...")
    init_db()
    asyncio.create_task(auto_poll())
    await Prime.infinity_polling()

if __name__ == '__main__':
    print("Bot started")
    asyncio.run(main())