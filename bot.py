from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests, re

# Token bot dari BotFather
BOT_TOKEN = "8332677116:AAFI92708Ijc7tilnJQJPs51RP5o455KZVQ"

# ========= FUNGSI OSINT =========

# 1. Cek info IP
def get_ip_info(ip: str):
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url).json()
        if response["status"] == "fail":
            return "⚠️ IP tidak valid atau tidak ditemukan."
        return (
            f"🌍 IP: {response['query']}\n"
            f"📍 Negara: {response['country']}\n"
            f"🏙 Kota: {response['city']}\n"
            f"📡 ISP: {response['isp']}\n"
            f"⏱ Zona Waktu: {response['timezone']}"
        )
    except Exception as e:
        return f"Error: {e}"

# 2. Cek info domain
def get_domain_info(domain: str):
    try:
        url = f"https://api.hackertarget.com/whois/?q={domain}"
        response = requests.get(url).text
        if "Error" in response:
            return "⚠️ Domain tidak valid atau tidak ditemukan."
        return f"📡 WHOIS info untuk {domain}:\n\n{response}"
    except Exception as e:
        return f"Error: {e}"

# 3. Cek username di platform populer
def check_username(username: str):
    sites = {
        "GitHub": f"https://github.com/{username}",
        "Twitter": f"https://x.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "Reddit": f"https://reddit.com/user/{username}"
    }
    result = f"🔎 Hasil pengecekan username: {username}\n\n"
    for site, url in sites.items():
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                result += f"✅ {site}: ditemukan → {url}\n"
            else:
                result += f"❌ {site}: tidak ditemukan\n"
        except:
            result += f"⚠️ {site}: gagal cek\n"
    return result

# 4. Lookup nomor HP (gunakan API numverify, di sini masih demo)
def phone_lookup(number: str):
    try:
        url = f"http://apilayer.net/api/validate?access_key=DEMO_KEY&number={number}"
        response = requests.get(url).json()
        if not response.get("valid", False):
            return "⚠️ Nomor tidak valid atau tidak bisa dicek."
        return (
            f"📱 Nomor: {response['international_format']}\n"
            f"🌍 Negara: {response['country_name']}\n"
            f"📡 Operator: {response['carrier']}"
        )
    except Exception as e:
        return f"Error: {e}"

# ========= DETEKSI OTOMATIS =========
def detect_and_lookup(text: str):
    text = text.strip()

    # Regex sederhana
    ip_regex = r"^\d{1,3}(\.\d{1,3}){3}$"
    domain_regex = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    phone_regex = r"^\+?\d{8,15}$"

    if re.match(ip_regex, text):
        return get_ip_info(text)
    elif re.match(domain_regex, text):
        return get_domain_info(text)
    elif re.match(phone_regex, text):
        return phone_lookup(text)
    else:
        # kalau tidak cocok apa-apa → coba cek username
        return check_username(text)

# ========= HANDLER =========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 Bot OSINT siap digunakan!\n\n"
        "📌 Perintah tersedia:\n"
        "/ip <alamat_ip>\n"
        "/domain <domain.com>\n"
        "/user <username>\n"
        "/phone <nomor>\n\n"
        "👉 Atau cukup kirim teks (IP/domain/username/nomor HP), bot akan otomatis deteksi."
    )
    await update.message.reply_text(text)

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Gunakan: /ip <alamat_ip>")
        return
    await update.message.reply_text(get_ip_info(context.args[0]))

async def domain_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Gunakan: /domain <domain.com>")
        return
    await update.message.reply_text(get_domain_info(context.args[0]))

async def user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Gunakan: /user <username>")
        return
    await update.message.reply_text(check_username(context.args[0]))

async def phone_lookup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Gunakan: /phone <nomor>")
        return
    await update.message.reply_text(phone_lookup(context.args[0]))

async def auto_detect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    result = detect_and_lookup(user_text)
    await update.message.reply_text(result)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CommandHandler("domain", domain_lookup))
    app.add_handler(CommandHandler("user", user_lookup))
    app.add_handler(CommandHandler("phone", phone_lookup_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_detect))

    print("Bot OSINT berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()