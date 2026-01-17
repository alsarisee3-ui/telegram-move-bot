from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from collections import defaultdict
import asyncio
import os

# 🧭 ضع هنا ID الجروب الثاني (الذي تريد النقل إليه)
TARGET_GROUP = -1003354274844

albums = defaultdict(list)

async def collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.media_group_id:
        albums[update.message.media_group_id].append(update.message)

async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.reply_to_message:
        return

    cmd = update.message
    original = update.message.reply_to_message

    # حالة صورة واحدة (حتى لو كانت Forwarded)
    if not original.media_group_id:
        await context.bot.copy_message(TARGET_GROUP, original.chat_id, original.message_id)
        try:
            await context.bot.delete_message(original.chat_id, original.message_id)
        except:
            pass
        await context.bot.delete_message(cmd.chat_id, cmd.message_id)
        return

    # حالة ألبوم صور
    gid = original.media_group_id
    await asyncio.sleep(2)

    messages = albums.get(gid, [original])

    # نقل الألبوم كاملًا
    for m in messages:
        await context.bot.copy_message(TARGET_GROUP, m.chat_id, m.message_id)

    # حذف الألبوم كاملًا
    for m in messages:
        try:
            await context.bot.delete_message(m.chat_id, m.message_id)
        except:
            pass

    # حذف أمر التنفيذ
    await context.bot.delete_message(cmd.chat_id, cmd.message_id)

    albums.pop(gid, None)

# ✅ Railway-friendly token
import os

app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
app.add_handler(CommandHandler("tm", move))
app.add_handler(MessageHandler(filters.ALL, collect))
app.run_polling()
