import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ضع ID الجروب الثاني هنا
TARGET_GROUP = -1003354274844

async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.reply_to_message:
        return

    msg = update.message.reply_to_message

    await context.bot.copy_message(
        chat_id=TARGET_GROUP,
        from_chat_id=msg.chat_id,
        message_id=msg.message_id
    )

    # حذف أمر التنفيذ نفسه فقط (الحذف الكامل يعتمد على صلاحيات تيليجرام)
    await context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("tm", move))
app.run_polling()
