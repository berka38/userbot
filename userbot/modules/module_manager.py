import os
import aiohttp
import importlib
import inspect
from pyrogram import Client, filters
from pyrogram.types import Message
from ..config.config import Config
from ..config.database import db

async def download_module(module_name: str) -> tuple[bool, str]:
    """Modülü uzak depodan indir"""
    url = f"{Config.MODULE_REPO}{module_name}.py"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Modül dosyasını kaydet
                    module_path = os.path.join(Config.MODULES_DIR, f"{module_name}.py")
                    with open(module_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    return True, "Modül başarıyla indirildi."
                else:
                    return False, f"Modül bulunamadı: {response.status}"
    except Exception as e:
        return False, f"İndirme hatası: {str(e)}"

async def load_module(module_name: str) -> tuple[bool, str]:
    """Modülü yükle ve kontrol et"""
    try:
        module = importlib.import_module(f"modules.{module_name}")
        
        # Modülü yeniden yükle (eğer daha önce yüklendiyse)
        importlib.reload(module)
        
        # Modül fonksiyonlarını kontrol et
        valid_handlers = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "handler"):
                valid_handlers.append(name)
        
        if not valid_handlers:
            return False, "Modülde geçerli komut işleyici bulunamadı."
        
        return True, f"Modül başarıyla yüklendi. Komutlar: {', '.join(valid_handlers)}"
        
    except Exception as e:
        return False, f"Modül yükleme hatası: {str(e)}"

@Client.on_message(filters.command("botinstall", prefixes=Config.CMD_PREFIX) & filters.me)
async def install_module(client: Client, message: Message):
    """!botinstall <modül_adı> komutu ile yeni modül yükle"""
    try:
        if len(message.command) != 2:
            await message.reply("Kullanım: !botinstall <modül_adı>")
            return
        
        module_name = message.command[1].lower()
        status_msg = await message.reply("Modül indiriliyor...")
        
        # Modülü indir
        success, download_msg = await download_module(module_name)
        if not success:
            await status_msg.edit(download_msg)
            return
            
        # Modülü yükle
        success, load_msg = await load_module(module_name)
        if not success:
            await status_msg.edit(load_msg)
            return
            
        # Veritabanına kaydet
        await db.add_module(
            message.from_user.id,
            module_name,
            {"installed_at": message.date.timestamp()}
        )
        
        await status_msg.edit(f"✅ {load_msg}")
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command(["botmodules", "modules"], prefixes=Config.CMD_PREFIX) & filters.me)
async def list_modules(client: Client, message: Message):
    """Yüklü modülleri listele"""
    try:
        modules = await db.get_modules(message.from_user.id)
        if not modules:
            await message.reply("Henüz hiç modül yüklenmemiş.")
            return
            
        module_list = []
        for module in modules:
            status = "✅" if module["enabled"] else "❌"
            module_list.append(f"{status} {module['name']}")
            
        await message.reply(
            "📦 Yüklü Modüller:\n" + "\n".join(module_list)
        )
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command(["bottoggle", "toggle"], prefixes=Config.CMD_PREFIX) & filters.me)
async def toggle_module(client: Client, message: Message):
    """Modülü etkinleştir/devre dışı bırak"""
    try:
        if len(message.command) != 2:
            await message.reply("Kullanım: !bottoggle <modül_adı>")
            return
            
        module_name = message.command[1].lower()
        modules = await db.get_modules(message.from_user.id)
        
        module_exists = False
        current_state = False
        
        for module in modules:
            if module["name"] == module_name:
                module_exists = True
                current_state = module["enabled"]
                break
                
        if not module_exists:
            await message.reply(f"❌ Modül bulunamadı: {module_name}")
            return
            
        # Durumu değiştir
        new_state = not current_state
        await db.toggle_module(message.from_user.id, module_name, new_state)
        
        status = "etkinleştirildi ✅" if new_state else "devre dışı bırakıldı ❌"
        await message.reply(f"Modül {status}: {module_name}")
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command(["botuninstall", "uninstall"], prefixes=Config.CMD_PREFIX) & filters.me)
async def uninstall_module(client: Client, message: Message):
    """Modülü kaldır"""
    try:
        if len(message.command) != 2:
            await message.reply("Kullanım: !botuninstall <modül_adı>")
            return
            
        module_name = message.command[1].lower()
        
        # Modül dosyasını sil
        module_path = os.path.join(Config.MODULES_DIR, f"{module_name}.py")
        if os.path.exists(module_path):
            os.remove(module_path)
            
        # Veritabanından kaldır
        await db.remove_module(message.from_user.id, module_name)
        
        await message.reply(f"✅ Modül kaldırıldı: {module_name}")
        
    except Exception as e:
        await message.reply(f"❌ Hata: {str(e)}") 