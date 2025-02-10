import os
import platform
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
from ..config.config import Config
from ..config.database import db

# Aktif oturum açma işlemleri
active_sessions = {}

# Sistem bilgilerini al
SYSTEM_INFO = {
    "os": platform.system(),
    "version": platform.version(),
    "machine": platform.machine(),
    "start_time": datetime.now()
}

@Client.on_message(filters.command("login", prefixes=Config.CMD_PREFIX) & filters.private)
async def start_login(client: Client, message: Message):
    """Telegram hesabına giriş başlat"""
    try:
        # Zaten giriş yapmış mı kontrol et
        if message.from_user.id == client.me.id:
            await message.reply("✅ Zaten giriş yapmış durumdasınız!")
            return
            
        # Yeni bir Pyrogram client oluştur
        temp_client = Client(
            f"temp_session_{message.from_user.id}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            in_memory=True
        )
        
        active_sessions[message.from_user.id] = {
            "client": temp_client,
            "step": "phone"
        }
        
        await message.reply(
            "📱 Telegram hesabınıza giriş yapalım!\n"
            "Lütfen telefon numaranızı uluslararası formatta girin.\n"
            "Örnek: +905551234567"
        )
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")

@Client.on_message(filters.regex(r'^\+\d+$') & filters.private)
async def handle_phone(client: Client, message: Message):
    """Telefon numarasını işle"""
    user_id = message.from_user.id
    if user_id not in active_sessions or active_sessions[user_id]["step"] != "phone":
        return
        
    try:
        temp_client = active_sessions[user_id]["client"]
        phone = message.text
        
        # Oturumu başlat ve kod gönder
        await temp_client.connect()
        code = await temp_client.send_code(phone)
        
        active_sessions[user_id].update({
            "phone": phone,
            "phone_code_hash": code.phone_code_hash,
            "step": "code"
        })
        
        await message.reply(
            "📬 Telegram'dan gelen 5 haneli kodu gönderin.\n"
            "Not: Kod genelde XXXXX formatında gelir."
        )
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")
        del active_sessions[user_id]

@Client.on_message(filters.regex(r'^\d{5}$') & filters.private)
async def handle_code(client: Client, message: Message):
    """Doğrulama kodunu işle"""
    user_id = message.from_user.id
    if user_id not in active_sessions or active_sessions[user_id]["step"] != "code":
        return
        
    try:
        session = active_sessions[user_id]
        temp_client = session["client"]
        
        try:
            # Kodu doğrula
            await temp_client.sign_in(
                session["phone"],
                session["phone_code_hash"],
                message.text
            )
            
            # Oturum dizinini oluştur
            if not os.path.exists("sessions"):
                os.makedirs("sessions")
            
            # Oturum dosyasını kaydet
            session_file = f"sessions/user_{user_id}.session"
            await temp_client.export_session_string()
            
            # Veritabanına kaydet
            await db.save_user({
                "user_id": user_id,
                "phone": session["phone"],
                "session_file": session_file,
                "is_active": True
            })
            
            await message.reply(
                "✅ Başarıyla giriş yaptınız!\n"
                "Artık UserBot'u kullanmaya başlayabilirsiniz.\n\n"
                "Temel komutlar için !help yazabilirsiniz."
            )
            
        except SessionPasswordNeeded:
            active_sessions[user_id]["step"] = "2fa"
            await message.reply(
                "🔐 İki Adımlı Doğrulama aktif.\n"
                "Lütfen Telegram hesabınızın şifresini girin."
            )
            
        except (PhoneCodeInvalid, PhoneCodeExpired):
            await message.reply("❌ Geçersiz veya süresi dolmuş kod. Lütfen tekrar deneyin.")
            del active_sessions[user_id]
            
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")
        del active_sessions[user_id]

@Client.on_message(filters.regex(r'^.+$') & filters.private)
async def handle_2fa(client: Client, message: Message):
    """2FA şifresini işle"""
    user_id = message.from_user.id
    if user_id not in active_sessions or active_sessions[user_id]["step"] != "2fa":
        return
        
    try:
        session = active_sessions[user_id]
        temp_client = session["client"]
        
        # 2FA şifresi ile giriş yap
        await temp_client.check_password(message.text)
        
        # Oturum dizinini oluştur
        if not os.path.exists("sessions"):
            os.makedirs("sessions")
        
        # Oturum dosyasını kaydet
        session_file = f"sessions/user_{user_id}.session"
        await temp_client.export_session_string()
        
        # Veritabanına kaydet
        await db.save_user({
            "user_id": user_id,
            "phone": session["phone"],
            "session_file": session_file,
            "is_active": True
        })
        
        await message.reply(
            "✅ Başarıyla giriş yaptınız!\n"
            "Artık UserBot'u kullanmaya başlayabilirsiniz.\n\n"
            "Temel komutlar için !help yazabilirsiniz."
        )
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")
    finally:
        del active_sessions[user_id]

@Client.on_message(filters.command("logout", prefixes=Config.CMD_PREFIX) & filters.me)
async def handle_logout(client: Client, message: Message):
    """Oturumu kapat"""
    try:
        user_id = message.from_user.id
        
        # Oturum dosyasını sil
        session_file = f"sessions/user_{user_id}.session"
        if os.path.exists(session_file):
            os.remove(session_file)
        
        # Veritabanından kullanıcıyı güncelle
        await db.save_user({
            "user_id": user_id,
            "is_active": False
        })
        
        await message.reply("👋 Oturumunuz başarıyla kapatıldı!")
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")

# Test komutu
@Client.on_message(filters.command("test", prefixes=Config.CMD_PREFIX) & filters.me)
async def test_command(client: Client, message: Message):
    """Test mesajı gönder"""
    try:
        test_message = (
            "🤖 UserBot Test Mesajı\n\n"
            f"👤 Kullanıcı: {client.me.first_name}\n"
            f"🆔 ID: {client.me.id}\n"
            f"📱 Telefon: {getattr(client.me, 'phone_number', 'Gizli')}\n"
            "✅ Bot çalışıyor!"
        )
        await message.edit(test_message)
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command("sysinfo", prefixes=Config.CMD_PREFIX) & filters.me)
async def system_info(client: Client, message: Message):
    """Sistem bilgilerini göster"""
    try:
        uptime = datetime.now() - SYSTEM_INFO["start_time"]
        uptime_str = str(uptime).split('.')[0]  # Mikrosaniyeleri kaldır
        
        info_text = (
            "🖥️ **Sistem Bilgileri**\n\n"
            f"**İşletim Sistemi:** {SYSTEM_INFO['os']}\n"
            f"**Sürüm:** {SYSTEM_INFO['version']}\n"
            f"**Mimari:** {SYSTEM_INFO['machine']}\n"
            f"**Çalışma Süresi:** {uptime_str}\n"
            f"**Python Sürümü:** {platform.python_version()}\n"
        )
        
        await message.edit(info_text)
    except Exception as e:
        await message.edit(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command("uptime", prefixes=Config.CMD_PREFIX) & filters.me)
async def show_uptime(client: Client, message: Message):
    """Bot çalışma süresini göster"""
    try:
        uptime = datetime.now() - SYSTEM_INFO["start_time"]
        uptime_str = str(uptime).split('.')[0]
        
        await message.edit(
            f"⏱️ **Bot Çalışma Süresi**\n"
            f"▶️ {uptime_str}"
        )
    except Exception as e:
        await message.edit(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command("ping", prefixes=Config.CMD_PREFIX) & filters.me)
async def ping_pong(client: Client, message: Message):
    """Ping komutu"""
    try:
        start = datetime.now()
        ping_msg = await message.edit("🏓 Ping...")
        end = datetime.now()
        
        ping_time = (end - start).microseconds / 1000
        
        await ping_msg.edit(
            f"🏓 **Pong!**\n"
            f"⚡ `{ping_time:.2f}ms`"
        )
    except Exception as e:
        await message.edit(f"❌ Hata: {str(e)}") 