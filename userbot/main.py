import os
import sys
import asyncio
import threading
from pyrogram import Client
from userbot.config.config import Config
from userbot.config.database import db
from userbot.web_server import run_web_server

async def create_session():
    """Session string oluştur"""
    try:
        phone = os.getenv("PHONE_NUMBER")
        if not phone:
            print("❌ PHONE_NUMBER bulunamadı!")
            print("⚠️ Render.com'da PHONE_NUMBER değişkeni ekleyin!")
            sys.exit(1)

        print("\n🔄 Session string oluşturuluyor...")
        print(f"📱 {phone} numarası için Telegram'a bağlanılıyor...")
        
        client = Client(
            "userbot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            phone_number=phone,
            in_memory=True
        )
        
        async with client as app:
            code = os.getenv("LOGIN_CODE")
            if not code:
                sent_code = await app.send_code(phone)
                print("\n📬 Telegram'dan gelen kodu Render.com'da LOGIN_CODE olarak ekleyin!")
                print("⚠️ Deploy'u yeniden başlatın!")
                sys.exit(1)
                
            try:
                print("\n🔑 Kod ile giriş yapılıyor...")
                await app.sign_in(phone, code)
            except Exception as e:
                print(f"❌ Giriş hatası: {str(e)}")
                sys.exit(1)
            
            session_string = await app.export_session_string()
            print("\n✅ Session string başarıyla oluşturuldu!")
            print("\n⚠️ BU KODU RENDER.COM'DA SESSION_STRING OLARAK EKLEYİN:")
            print("=" * 50)
            print(f"\n{session_string}\n")
            print("=" * 50)
            print("\n❗ Deploy'u yeniden başlatın!")
            return session_string
            
    except Exception as e:
        print(f"\n❌ Session string oluşturma hatası: {str(e)}")
        sys.exit(1)

class UserBot(Client):
    def __init__(self):
        # Session string'i kontrol et
        session_string = os.getenv("SESSION_STRING")
        if not session_string:
            print("❌ SESSION_STRING bulunamadı!")
            print("\n🔄 Yeni session string oluşturuluyor...")
            loop = asyncio.get_event_loop()
            session_string = loop.run_until_complete(create_session())
            print("\n⚠️ Yukarıdaki session string'i Render.com'a ekleyin!")
            sys.exit(1)
            
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
        
        # Pyrogram istemcisini başlat
        super().__init__(
            name="userbot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=session_string,
            plugins=dict(root="userbot/modules")
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
            
            # MongoDB'ye bağlan
            await self.db.connect()
            
            # Telegram'a bağlan
            print("🔄 Telegram'a bağlanılıyor...")
            await super().start()
            self.me = await self.get_me()
            
            # Kullanıcı bilgilerini kaydet
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
                print("🔑 API_ID ve API_HASH'i kontrol edin.")
            elif "session" in error_msg:
                print("\n❗ Session hatası!")
                print("🔑 SESSION_STRING'i kontrol edin.")
                print("\n⚠️ Lütfen önce yerel bilgisayarınızda setup.py çalıştırın!")
            else:
                print(f"❌ Başlatma hatası: {str(e)}")
            sys.exit(1)

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
            print("❌ API bilgileri eksik!")
            print("🔑 API_ID ve API_HASH'i environment variables'a ekleyin.")
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