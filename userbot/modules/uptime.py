import os
import json
import asyncio
import aiohttp
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from ..config.config import Config
from ..config.database import db

# Uptime sistemi için sabitler
UPTIMEROBOT_API_KEY = os.getenv("UPTIMEROBOT_API_KEY")
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
RAILWAY_API_KEY = os.getenv("RAILWAY_API_KEY")

class UptimeManager:
    def __init__(self):
        self.start_time = datetime.now()
        self.uptime_service = None
        self.service_url = None
        self.is_active = False
        self._load_config()
    
    def _load_config(self):
        """Uptime ayarlarını yükle"""
        try:
            if os.path.exists("uptime_config.json"):
                with open("uptime_config.json", "r") as f:
                    config = json.load(f)
                    self.uptime_service = config.get("service")
                    self.service_url = config.get("url")
                    self.is_active = config.get("is_active", False)
        except:
            pass
    
    def _save_config(self):
        """Uptime ayarlarını kaydet"""
        try:
            config = {
                "service": self.uptime_service,
                "url": self.service_url,
                "is_active": self.is_active
            }
            with open("uptime_config.json", "w") as f:
                json.dump(config, f, indent=4)
        except:
            pass

    async def setup_uptimerobot(self, url: str) -> str:
        """UptimeRobot servisini ayarla"""
        if not UPTIMEROBOT_API_KEY:
            return "❌ UptimeRobot API anahtarı bulunamadı!"
            
        try:
            async with aiohttp.ClientSession() as session:
                # Yeni monitor oluştur
                api_url = "https://api.uptimerobot.com/v2/newMonitor"
                data = {
                    "api_key": UPTIMEROBOT_API_KEY,
                    "format": "json",
                    "type": 1,  # HTTP(s)
                    "url": url,
                    "friendly_name": "UserBot Uptime"
                }
                
                async with session.post(api_url, data=data) as resp:
                    result = await resp.json()
                    
                    if result.get("stat") == "ok":
                        self.uptime_service = "uptimerobot"
                        self.service_url = url
                        self.is_active = True
                        self._save_config()
                        return "✅ UptimeRobot başarıyla ayarlandı!"
                    else:
                        return f"❌ UptimeRobot hatası: {result.get('error', 'Bilinmeyen hata')}"
                        
        except Exception as e:
            return f"❌ Hata: {str(e)}"

    async def setup_render(self, url: str) -> str:
        """Render.com servisini ayarla"""
        if not RENDER_API_KEY:
            return "❌ Render API anahtarı bulunamadı!"
            
        # Render.com API entegrasyonu buraya gelecek
        self.uptime_service = "render"
        self.service_url = url
        self.is_active = True
        self._save_config()
        return "✅ Render.com başarıyla ayarlandı!"

    async def setup_railway(self, url: str) -> str:
        """Railway servisini ayarla"""
        if not RAILWAY_API_KEY:
            return "❌ Railway API anahtarı bulunamadı!"
            
        # Railway API entegrasyonu buraya gelecek
        self.uptime_service = "railway"
        self.service_url = url
        self.is_active = True
        self._save_config()
        return "✅ Railway başarıyla ayarlandı!"

# Global uptime yöneticisi
uptime_manager = UptimeManager()

@Client.on_message(filters.command("uptime_setup", prefixes=Config.CMD_PREFIX) & filters.me)
async def setup_uptime(client: Client, message: Message):
    """Uptime servisini ayarla"""
    try:
        args = message.text.split()
        if len(args) < 3:
            await message.edit(
                "❌ Kullanım: !uptime_setup <servis> <url>\n\n"
                "📌 Desteklenen servisler:\n"
                "• uptimerobot\n"
                "• render\n"
                "• railway"
            )
            return
            
        service = args[1].lower()
        url = args[2]
        
        if service == "uptimerobot":
            result = await uptime_manager.setup_uptimerobot(url)
        elif service == "render":
            result = await uptime_manager.setup_render(url)
        elif service == "railway":
            result = await uptime_manager.setup_railway(url)
        else:
            result = "❌ Geçersiz servis! Desteklenen servisler: uptimerobot, render, railway"
            
        await message.edit(result)
        
    except Exception as e:
        await message.edit(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command("uptime_status", prefixes=Config.CMD_PREFIX) & filters.me)
async def uptime_status(client: Client, message: Message):
    """Uptime durumunu göster"""
    try:
        if not uptime_manager.is_active:
            await message.edit("❌ Uptime servisi aktif değil!")
            return
            
        status_text = (
            "📊 **Uptime Durumu**\n\n"
            f"**Servis:** {uptime_manager.uptime_service}\n"
            f"**URL:** {uptime_manager.service_url}\n"
            f"**Durum:** {'✅ Aktif' if uptime_manager.is_active else '❌ Pasif'}"
        )
        
        await message.edit(status_text)
        
    except Exception as e:
        await message.edit(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command("uptime_disable", prefixes=Config.CMD_PREFIX) & filters.me)
async def disable_uptime(client: Client, message: Message):
    """Uptime servisini devre dışı bırak"""
    try:
        uptime_manager.is_active = False
        uptime_manager._save_config()
        
        await message.edit("✅ Uptime servisi devre dışı bırakıldı!")
        
    except Exception as e:
        await message.edit(f"❌ Hata: {str(e)}")

# Yeni komutlar için yardım metni
UPTIME_HELP = """
📌 **Uptime Komutları**

• `!uptime_setup <servis> <url>` - Uptime servisini ayarla
• `!uptime_status` - Uptime durumunu göster
• `!uptime_disable` - Uptime servisini devre dışı bırak

📋 **Desteklenen Servisler:**
• UptimeRobot
• Render.com
• Railway

⚙️ **Kurulum:**
1. Tercih ettiğiniz servisten API anahtarı alın
2. `.env` dosyasına API anahtarını ekleyin
3. `!uptime_setup` komutu ile servisi ayarlayın
"""

RAILWAY_HELP = """
🚂 **Railway.app Kurulum Rehberi**

1️⃣ **Railway.app Hesabı Oluşturma:**
• https://railway.app adresine gidin
• GitHub hesabınızla giriş yapın

2️⃣ **Projeyi Deploy Etme:**
• Bu bağlantıya tıklayın: [UserBot'u Railway'e Kur](https://railway.app/template/...)
• "Deploy Now" butonuna tıklayın
• GitHub hesabınızı bağlayın

3️⃣ **Değişkenleri Ayarlama:**
• Variables bölümüne girin
• Aşağıdaki değişkenleri ekleyin:
  - `API_ID` (Telegram API ID'niz)
  - `API_HASH` (Telegram API Hash'iniz)

4️⃣ **Bot'u Başlatma:**
• Deploy işlemi otomatik başlayacak
• Logları kontrol edin
• Bot çalışmaya başladığında size mesaj atacak

❗ **Önemli Notlar:**
• Railway her ay 500 saat ücretsiz kredi veriyor
• Kredi bitmeden yeni hesap oluşturabilirsiniz
• Bot 7/24 açık kalacak
• Herhangi bir teknik bilgi gerektirmez

🔄 **Yeni Hesap Oluşturma:**
1. Railway.app'den çıkış yapın
2. Yeni bir GitHub hesabı oluşturun
3. Yeni GitHub hesabıyla Railway'e giriş yapın
4. Yukarıdaki adımları tekrarlayın

⚠️ Her hesapta farklı e-posta ve GitHub hesabı kullanın!
"""

@Client.on_message(filters.command(["uptime", "railway"], prefixes=Config.CMD_PREFIX) & filters.me)
async def railway_help(client: Client, message: Message):
    """Railway.app kurulum rehberini göster"""
    try:
        await message.edit(RAILWAY_HELP)
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