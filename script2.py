import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ضع توكن بوتك هنا
TOKEN = '8549941066:AAFzZwFVYqx2gZ9Cl0A1yxA64DrCmRXqm6s'

# إعدادات تحميل الفيديو
YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best',  # تحميل أفضل جودة بصيغة mp4
    'outtmpl': 'downloads/%(title)s.%(ext)s',  # مكان حفظ الفيديو
    'max_filesize': 50 * 1024 * 1024,  # حد 50 ميجابايت (حد التلغرام للبوتات العادية)
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! أرسل لي رابط فيديو من أي موقع (تيك توك، يوتيوب، إنستقرام) وسأقوم بتحميله لك.")


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status_msg = await update.message.reply_text("جاري معالجة الرابط والتحميل... انتظر قليلاً ⏳")

    try:
        # إنشاء مجلد التحميل إذا لم يكن موجوداً
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو للمستخدم
        await update.message.reply_video(video=open(filename, 'rb'), caption=info.get('title', 'تم التحميل بنجاح!'))

        # حذف الملف بعد الإرسال لتوفير المساحة
        os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"عذراً، حدث خطأ: {str(e)}")


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("بوت التحميل يعمل...")
    app.run_polling()