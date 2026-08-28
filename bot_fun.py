import random
import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8614501569:AAHuGxvxoNi4iClVgpOdtPQJFYNsSuQPBHI"
SUBSCRIBERS_FILE = "subscribers.txt"

# Helper function to load a random joke
def get_arabic_joke() -> str:
    try:
        df = pd.read_csv("clean_jokes.csv", encoding="utf-8")
        column_name = "joke" if "joke" in df.columns else "النص"
        jokes_list = df[column_name].dropna().tolist()
        if jokes_list:
            return random.choice(jokes_list)
        return "الملف فارغ حالياً."
    except Exception as e:
        return f"خطأ في قراءة البيانات: {e}"

# Helper function to save subscriber IDs
def add_subscriber(chat_id: int):
    chat_id_str = str(chat_id)
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            subscribers = set(line.strip() for line in f if line.strip())
    else:
        subscribers = set()
    
    if chat_id_str not in subscribers:
        with open(SUBSCRIBERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{chat_id_str}\n")

# Scheduled job: Runs every 12 hours (43200 seconds)
async def scheduled_joke_job(context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(SUBSCRIBERS_FILE):
        return

    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        subscribers = [line.strip() for line in f if line.strip()]

    if not subscribers:
        return

    joke_text = get_arabic_joke()
    message = f"⏰ طريفة التوقيت التلقائي:\n\n{joke_text}"

    for chat_id in subscribers:
        try:
            await context.bot.send_message(chat_id=int(chat_id), text=message)
        except Exception:
            pass

# Handler for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_subscriber(chat_id)
    welcome_text = (
        "أهلاً بك في بوت الابتسامة! 😄\n\n"
        "✨ تم تفعيل الاشتراك التلقائي: ستصلك نكتتان يومياً بمعدل كل 12 ساعة.\n"
        "👉 للحصول على نكتة فورية في أي وقت، أرسل: /joke"
    )
    await update.message.reply_text(welcome_text)

# Handler for /joke command
async def send_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_text = get_arabic_joke()
    await update.message.reply_text(f"😂 طريفة اليوم:\n\n{joke_text}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joke", send_joke))

    # Schedule recurring job every 12 hours (43200s), first run after 10s for verification
    if app.job_queue:
        app.job_queue.run_repeating(scheduled_joke_job, interval=43200, first=10)

    print("Bot is running with automated scheduler...")
    app.run_polling()