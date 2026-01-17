import os
import asyncio
from collections import defaultdict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🧭 ID الجروب الثاني (الذي سيتم النقل إليه)
TARGET_GROUP = -1003354274844

# 👍 سطر الإيموجي الذي يُرسل بعد كل نقل
EMOJI_LINE = "👍👍👍👍👍👍👍👍👍👍👍👍👍👍👍👍👍👍"

albums = defaultdict(list)

async def collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.media_group_id:
        albums[update.message.media_group_id].append(update.message)

async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.reply_to_message:
        return

    cmd = update.message
    original = update.message.reply_to_message

    # 🔹 حالة رسالة واحدة
    if not original.media_group_id:
        await context.bot.copy_message(
            chat_id=TARGET_GROUP,
            from_chat_id=original.chat_id,
            message_id=original.message_id
        )

        # ✅ إرسال سطر الإيموجي بعد النقل
        await context.bot.send_message(TARGET_GROUP, EMOJI_LINE)

        # حذف الرسالة الأصلية
        try:
            await context.bot.delete_message(original.chat_id, original.message_id)
        except:
            pass

        # حذف أمر /tm
        await context.bot.delete_message(cmd.chat_id, cmd.message_id)
        return

    # 🔹 حالة ألبوم صور
    gid = original.media_group_id
    await asyncio.sleep(2)

    messages = albums.get(gid, [original])

    # نقل الألبوم كاملًا
    for m in messages:
        await context.bot.copy_message(
            chat_id=TARGET_GROUP,
            from_chat_id=m.chat_id,
            message_id=m.message_id
        )

    # ✅ إرسال سطر الإيموجي بعد نقل الألبوم
    await context.bot.send_message(TARGET_GROUP, EMOJI_LINE)

    # حذف الألبوم من الجروب الأول
    for m in messages:
        try:
            await context.bot.delete_message(m.chat_id, m.message_id)
        except:
            pass

    # حذف أمر /tm
    await context.bot.delete_message(cmd.chat_id, cmd.message_id)

    albums.pop(gid, None)

# 🔐 التوكن من متغيرات البيئة (Railway)
app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
app.add_handler(CommandHandler("tm", move))
app.add_handler(MessageHandler(filters.ALL, collect))
app.run_polling()
