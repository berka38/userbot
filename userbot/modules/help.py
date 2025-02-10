from pyrogram import Client, filters
from pyrogram.types import Message
from ..config.config import Config

HELP_TEXT = """
📚 **UserBot Komutları**

**🔐 Hesap Yönetimi:**
• `!login` - Telegram hesabına giriş yap
• `!logout` - Oturumu kapat
• `!test` - Bot'un çalışıp çalışmadığını kontrol et

**⏰ Zamanlayıcı:**
• `!zamanla <süre> <tekrar> <mesaj>` - Mesaj zamanla
• `!iptal` - Zamanlanmış mesajları iptal et

**📦 Modül Yönetimi:**
• `!botinstall <modül_adı>` - Yeni modül yükle
• `!botmodules` - Yüklü modülleri listele
• `!bottoggle <modül_adı>` - Modülü aç/kapat
• `!botuninstall <modül_adı>` - Modülü kaldır

**🛠️ Sistem:**
• `!terminal <komut>` - Terminal komutu çalıştır

**📝 Örnekler:**
1. Zamanlanmış mesaj:
   `!zamanla 1h 5 Merhaba!`
   (1 saat aralıklarla 5 kez "Merhaba!" gönderir)

2. Terminal komutu:
   `!terminal echo "Merhaba Dünya"`
   (Terminal üzerinde komut çalıştırır)

3. Modül yükleme:
   `!botinstall chat_tools`
   (chat_tools modülünü yükler)

⚠️ **Önemli Notlar:**
• Komutlar sadece sizin tarafınızdan kullanılabilir
• Terminal komutlarını dikkatli kullanın
• Modülleri güvenilir kaynaklardan yükleyin
"""

@Client.on_message(filters.command(["help", "yardim"], prefixes=Config.CMD_PREFIX) & filters.me)
async def show_help(client: Client, message: Message):
    """Yardım mesajını göster"""
    try:
        await message.edit(HELP_TEXT)
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")

# Hoşgeldin mesajı
@Client.on_message(filters.command("start", prefixes=Config.CMD_PREFIX) & filters.private)
async def start_command(client: Client, message: Message):
    """Hoşgeldin mesajını göster"""
    try:
        welcome_text = f"""
👋 Merhaba {message.from_user.first_name}!

🤖 Ben bir UserBot'um. İşte yapabileceklerim:

• ⏰ Zamanlanmış mesajlar
• 📦 Özel modüller yükleme
• 🛠️ Terminal komutları
• 🔄 Ve daha fazlası!

Komutları görmek için !help yazabilirsiniz.
"""
        await message.reply(welcome_text)
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}") 