import os
import sys
import asyncio
import threading
from pyrogram import Client
from config.config import Config
from config.database import db
from web_server import run_web_server

class UserBot(Client):
    def __init__(self):
        # Ana dizine geç
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(self.base_dir)
        
        # Python modül yoluna ana dizini ekle
        if self.base_dir not in sys.path:
            sys.path.insert(0, self.base_dir)
        
        # Sessions dizinini oluştur
        self.sessions_dir = os.path.join(self.base_dir, "sessions")
        if not os.path.exists(self.sessions_dir):
            try:
                os.makedirs(self.sessions_dir)
            except Exception as e:
                print(f"❌ Sessions dizini oluşturulamadı: {str(e)}")
                sys.exit(1)
        
        # Session dosyası yolu
        self.session_file = os.path.join(self.sessions_dir, "userbot")
        
        # Modül dizini yolu
        modules_path = os.path.join("userbot", "modules")
        
        # Pyrogram istemcisini başlat
        super().__init__(
            name=self.session_file,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root=modules_path),
            workdir=self.sessions_dir
        )
        
        self.me = None
        self.db = db
        self.web_thread = None

    async def start(self):
        """Bot ve veritabanı bağlantılarını başlat"""
        try:
            # Web sunucusunu arka planda başlat
            self.web_thread = threading.Thread(target=run_web_server)
            self.web_thread.daemon = True
            self.web_thread.start()
            
            # MongoDB'ye bağlan (başarısız olursa yerel DB kullanılır)
            await self.db.connect()
            
            # Telegram'a bağlan
            print("🔄 Telegram'a bağlanılıyor...")
            await super().start()
            self.me = await self.get_me()
            
            # Kullanıcı bilgilerini kaydet/güncelle
            await self.db.save_user({
                "user_id": self.me.id,
                "username": self.me.username,
                "first_name": self.me.first_name,
                "last_name": self.me.last_name,
                "is_active": True
            })
            
            print(f"✅ UserBot başlatıldı! Kullanıcı: {self.me.first_name}")
            print(f"ℹ️ Komutları görmek için herhangi bir sohbette !help yazın")
            
        except Exception as e:
            error_msg = str(e).lower()
            if "api_id" in error_msg:
                print("\n❗ API bilgileri eksik veya hatalı!")
                print("🔑 Lütfen setup.py dosyasını çalıştırarak API bilgilerini girin.")
            elif "database" in error_msg:
                print("\n❗ Session dosyası oluşturulamadı!")
                print("🔄 Sessions dizininin yazma izinlerini kontrol edin.")
                # Session dosyasını silmeyi dene
                try:
                    if os.path.exists(f"{self.session_file}.session"):
                        os.remove(f"{self.session_file}.session")
                        print("🔄 Eski session dosyası silindi. Lütfen tekrar deneyin.")
                except:
                    pass
            elif "no module" in error_msg:
                print("\n❗ Modül yolu hatası!")
                print("🔄 Lütfen doğru dizinde olduğunuzdan emin olun.")
                print(f"📂 Çalışma dizini: {os.getcwd()}")
            else:
                print(f"❌ Başlatma hatası: {str(e)}")
            raise e

    async def stop(self):
        """Bot ve veritabanı bağlantılarını kapat"""
        try:
            await self.db.disconnect()
            await super().stop()
            print("\n👋 UserBot durduruldu!")
        except Exception as e:
            print(f"❌ Durdurma hatası: {str(e)}")

def main():
    """Ana fonksiyon"""
    try:
        if not Config.validate():
            print("❌ Lütfen önce setup.py dosyasını çalıştırın!")
            print("🔑 API bilgilerini girmeniz gerekiyor.")
            return
        
        # Eski session dosyasını temizle
        session_file = os.path.join("sessions", "userbot.session")
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                print("🔄 Eski session dosyası temizlendi.")
            except:
                pass
            
        app = UserBot()
        app.run()
        
    except Exception as e:
        print(f"❌ Kritik hata: {str(e)}")
        print("\nℹ️ Yardım için:")
        print("1. setup.py dosyasını tekrar çalıştırın")
        print("2. API bilgilerinin doğru olduğundan emin olun")
        print("3. İnternet bağlantınızı kontrol edin")
        print("4. Sessions dizininin yazma izinlerini kontrol edin")
        print(f"5. Çalışma dizini: {os.getcwd()}")
        print("\n🔍 Hata detayı:")
        print(str(e))

if __name__ == "__main__":
    main() 