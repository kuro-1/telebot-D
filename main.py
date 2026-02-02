import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# --- الإعدادات ---
TOKEN = '8549941066:AAFzZwFVYqx2gZ9Cl0A1yxA64DrCmRXqm6s'
ADMIN_ID = 6271177587 # استبدل هذا الرقم بـ ID حسابك في تلغرام
USERS_FILE = 'users_data.json'

# --- وظائف إدارة المستخدمين ---
def save_user(user):
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    
    # حفظ المستخدم بالـ ID الخاص به لمنع التكرار
    user_id = str(user.id)
    users[user_id] = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- المهام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user) # حفظ بيانات المستخدم عند أول تفاعل
    await update.message.reply_text(f"أهلاً بك {user.first_name}!\nأرسل رابط الفيديو للتحميل.")

async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التأكد أن الشخص هو الإدمن
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("عذراً، هذا الأمر للمدير فقط.")
        return

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        count = len(users)
        await update.message.reply_text(f"📊 إحصائيات البوت:\nعدد المستخدمين الكلي: {count}")
        # إرسال ملف البيانات للمدير
        await update.message.reply_document(document=open(USERS_FILE, 'rb'), caption="قائمة بيانات المستخدمين")
    else:
        await update.message.reply_text("لا يوجد مستخدمين بعد.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return # تجاهل الرسائل التي ليست روابط

    status_msg = await update.message.reply_text("جاري التحميل... ⏳")
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'downloads/%(title)s_{update.effective_user.id}.%(ext)s',
        'max_filesize': 45 * 1024 * 1024,
    }

    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(filename, 'rb'), caption=info.get('title', 'تم!'))
        os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"خطأ: {str(e)}")

# --- التشغيل ---
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", get_stats)) # أمر الإحصائيات للإدمن
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("البوت يعمل مع نظام الإدارة...")
    app.run_polling()




