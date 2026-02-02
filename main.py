import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# --- الإعدادات (تم وضع بياناتك هنا) ---
TOKEN = '8549941066:AAFzZwFVYqx2gZ9Cl0A1yxA64DrCmRXqm6s'
ADMIN_ID = 6271177587 
USERS_FILE = 'users_data.json'

# --- وظيفة حفظ البيانات ---
def save_user(user):
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except: users = {}
    
    users[str(user.id)] = {"username": user.username, "name": user.first_name}
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- الأوامر ---

# 1. الترحيب بالاسم مع أزرار شفافة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    
    # إنشاء الأزرار
    keyboard = [
        [
            InlineKeyboardButton("📢 قناة المطور", url="https://t.me/GOTHIKAN"), # يمكنك تغيير الرابط لاحقاً
            InlineKeyboardButton("🛠️ الدعم الفني", url=f"tg://user?id={ADMIN_ID}")
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"يا هلا بك يا **{user.first_name}**! ❤️\n\n"
        f"أنا بوت تحميل الفيديوهات السريع. 🚀\n"
        f"كل ما عليك هو إرسال رابط الفيديو من:\n"
        f"*TikTok - Instagram - YouTube*\n\n"
        f"استخدم الأزرار أدناه للمزيد من المعلومات 👇"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# 2. الإحصائيات (للمدير فقط)
async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(f"❌ أنت لست المدير.")
        return
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        await update.message.reply_text(f"📊 عدد المشتركين الحالي: {len(users)}")
        await update.message.reply_document(document=open(USERS_FILE, 'rb'), caption="قائمة المستخدمين")
    else:
        await update.message.reply_text("📁 لا توجد بيانات مسجلة حالياً.")

# 3. الإذاعة
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("⚠️ اكتب الرسالة هكذا:\n`/broadcast نص الرسالة`", parse_mode='Markdown')
        return

    msg_text = " ".join(context.args)
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        sent = 0
        for uid in users.keys():
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 **رسالة إدارية:**\n\n{msg_text}", parse_mode='Markdown')
                sent += 1
                await asyncio.sleep(0.05)
            except: continue
        await update.message.reply_text(f"✅ تم الإرسال إلى {sent} مستخدم.")

# 4. وظيفة التحميل
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    status = await update.message.reply_text("جاري التحميل... ⏳")
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': f'downloads/%(title)s_{update.effective_user.id}.%(ext)s',
            'max_filesize': 48*1024*1024
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(path, 'rb'), caption=f"✅ {info.get('title', 'تم التحميل')}")
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ فشل التحميل. قد يكون الرابط غير مدعوم أو الحجم كبيراً.")

# --- التشغيل ---
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", get_stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("البوت يعمل الآن بالبيانات الجديدة...")
    app.run_polling()


