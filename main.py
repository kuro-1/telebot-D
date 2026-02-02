import os
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# --- الإعدادات (تأكد من استبدالها بدقة) ---
TOKEN = '8549941066:AAFzZwFVYqx2gZ9Cl0A1yxA64DrCmRXqm6s'
ADMIN_ID =  '6271177587'
USERS_FILE = 'users_data.json'

# --- وظائف إدارة البيانات ---
def save_user(user):
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except: users = {}
    
    users[str(user.id)] = {
        "username": user.username,
        "first_name": user.first_name
    }
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- أوامر البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user)
    await update.message.reply_text("أهلاً بك! أرسل رابط الفيديو وسأقوم بتحميله لك فوراً.")

# أمر الإحصائيات المطور
async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text(f"❌ أنت لست المدير.\nرقمك الحقيقي هو: `{user_id}`\nانسخه وضعه في الكود.", parse_mode='Markdown')
        return

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        await update.message.reply_document(document=open(USERS_FILE, 'rb'), caption=f"📊 عدد المشتركين: {len(users)}")
    else:
        await update.message.reply_text("📁 لا يوجد بيانات بعد.")

# أمر الإذاعة (إرسال رسالة للكل)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    if not context.args:
        await update.message.reply_text("استخدم الأمر هكذا: /broadcast نص الرسالة")
        return

    msg = " ".join(context.args)
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        count = 0
        for uid in users.keys():
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 رسالة من الإدارة:\n\n{msg}")
                count += 1
                await asyncio.sleep(0.1) # لتجنب الحظر من تلغرام
            except: continue
        await update.message.reply_text(f"✅ تم إرسال الرسالة إلى {count} مستخدم.")

# وظيفة التحميل
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    
    status_msg = await update.message.reply_text("جاري التحميل... ⏳")
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'downloads/%(title)s_{update.effective_user.id}.%(ext)s',
        'max_filesize': 48 * 1024 * 1024,
    }

    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(filename, 'rb'), caption=info.get('title', 'تم التحميل!'))
        os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"حدث خطأ: {str(e)}")

# --- التشغيل ---
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", get_stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("البوت المحدث يعمل الآن...")
    app.run_polling()
