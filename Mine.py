import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")

TEXT, COLOR, GIF = range(3)

COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0)
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! متن رو بفرست تا روی گیف قرار بدم.")
    return TEXT

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text
    color_list = "\n".join([f"- {c}" for c in COLORS.keys()])
    await update.message.reply_text(f"رنگ متن رو انتخاب کن:\n{color_list}")
    return COLOR

async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    color = update.message.text.lower()
    if color not in COLORS:
        await update.message.reply_text("این رنگ موجود نیست، یکی از لیست انتخاب کن.")
        return COLOR
    context.user_data["color"] = COLORS[color]
    await update.message.reply_text("حالا گیف رو بفرست.")
    return GIF

async def process_gif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.animation.get_file()
    gif_path = "input.gif"
    await file.download_to_drive(gif_path)

    img = Image.open(gif_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 10), context.user_data["text"], font=font, fill=context.user_data["color"])
    output_path = "output.gif"
    img.save(output_path)

    await update.message.reply_document(InputFile(output_path))
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)],
        COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_color)],
        GIF: [MessageHandler(filters.ANIMATION, process_gif)],
    },
    fallbacks=[],
)

app.add_handler(conv_handler)

if __name__ == "__main__":
    app.run_polling()
