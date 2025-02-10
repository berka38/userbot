import os
import sys
import time
import subprocess
from pyrogram import Client

def print_colored(text, color="white"):
    """Renkli metin yazdırma"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[97m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['end']}")

def clear_screen():
    """Ekranı temizle"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    """Program başlığını göster"""
    banner = """
    ╔════════════════════════════════════════╗
    ║          UserBot Kurulum Sihirbazı     ║
    ╚════════════════════════════════════════╝
    """
    print_colored(banner, "blue")

def check_python_version():
    """Python sürümünü kontrol et"""
    if sys.version_info < (3, 8):
        print_colored("❌ Python 3.8 veya daha yüksek bir sürüm gerekli!", "red")
        sys.exit(1)

def install_requirements():
    """Gerekli paketleri kur"""
    print_colored("\n📦 Gerekli paketler yükleniyor...", "yellow")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print_colored("✅ Paketler başarıyla yüklendi!", "green")
    except subprocess.CalledProcessError:
        print_colored("❌ Paket yüklemesi başarısız oldu!", "red")
        sys.exit(1)

def get_telegram_api():
    """Telegram API bilgilerini al"""
    print_colored("\n🔑 Telegram API Bilgileri", "yellow")
    print_colored("\nTelegram API bilgilerini almak için:", "white")
    print_colored("1. https://my.telegram.org adresine gidin", "white")
    print_colored("2. Telefonunuzla giriş yapın", "white")
    print_colored("3. 'API Development Tools' bölümüne girin", "white")
    print_colored("4. Yeni bir uygulama oluşturun", "white")
    print_colored("5. Size verilen API ID ve API HASH değerlerini buraya girin\n", "white")
    
    while True:
        api_id = input("API ID: ").strip()
        if api_id.isdigit():
            break
        print_colored("❌ API ID sadece rakamlardan oluşmalıdır!", "red")
    
    api_hash = input("API HASH: ").strip()
    return api_id, api_hash

def get_session_string(api_id, api_hash):
    """Session string oluştur"""
    print_colored("\n📱 Session String Oluşturuluyor", "yellow")
    print_colored("Telegram hesabınıza giriş yapmanız gerekiyor...\n", "white")
    
    try:
        with Client(
            "my_account",
            api_id=api_id,
            api_hash=api_hash,
            in_memory=True
        ) as app:
            session_string = app.export_session_string()
            print_colored("\n✅ Session string başarıyla oluşturuldu!", "green")
            return session_string
    except Exception as e:
        print_colored(f"\n❌ Session string oluşturma hatası: {str(e)}", "red")
        sys.exit(1)

def create_env_file(api_id, api_hash, session_string):
    """Yapılandırma dosyasını oluştur"""
    env_content = f"""# Telegram API bilgileri
API_ID={api_id}
API_HASH={api_hash}
SESSION_STRING={session_string}

# MongoDB bağlantısı
MONGODB_URL=mongodb+srv://folunted:bert123@cluster0.lbuyo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=userbot_db

# Port ayarı
PORT=10000"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

def show_render_instructions(session_string):
    """Render.com kurulum talimatlarını göster"""
    print_colored("\n🚀 Render.com Kurulum Talimatları", "yellow")
    print_colored("\n1. https://render.com adresine gidin", "white")
    print_colored("2. GitHub hesabınızla giriş yapın", "white")
    print_colored("3. 'New +' butonuna tıklayın ve 'Web Service' seçin", "white")
    print_colored("4. GitHub repository'nizi bağlayın", "white")
    print_colored("5. Environment Variables bölümüne şu değişkenleri ekleyin:", "white")
    print_colored("\nAPI_ID = (yukarıda girdiğiniz API ID)", "blue")
    print_colored("API_HASH = (yukarıda girdiğiniz API HASH)", "blue")
    print_colored(f"SESSION_STRING = {session_string}", "blue")
    print_colored("PORT = 10000", "blue")
    print_colored("\n6. 'Create Web Service' butonuna tıklayın", "white")
    print_colored("7. Deploy işlemi otomatik başlayacak", "white")

def main():
    """Ana kurulum fonksiyonu"""
    try:
        clear_screen()
        show_banner()
        
        # Python sürümünü kontrol et
        check_python_version()
        
        # Gerekli paketleri kur
        install_requirements()
        
        # Telegram API bilgilerini al
        api_id, api_hash = get_telegram_api()
        
        # Session string oluştur
        session_string = get_session_string(api_id, api_hash)
        
        # Yapılandırma dosyasını oluştur
        print_colored("\n⚙️ Yapılandırma dosyası oluşturuluyor...", "yellow")
        create_env_file(api_id, api_hash, session_string)
        print_colored("✅ Yapılandırma dosyası oluşturuldu!", "green")
        
        # Render.com talimatlarını göster
        show_render_instructions(session_string)
        
        print_colored("\n🎉 Kurulum başarıyla tamamlandı!", "green")
        print_colored("\nℹ️ Yukarıdaki talimatları takip ederek Render.com'da bot'u başlatabilirsiniz.", "white")
        print_colored("❗ SESSION_STRING'i güvenli bir yerde saklayın!", "yellow")
        
        input("\n⏎ Çıkmak için Enter'a basın...")
        
    except KeyboardInterrupt:
        print_colored("\n\n❌ Kurulum iptal edildi!", "red")
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n\n❌ Bir hata oluştu: {str(e)}", "red")
        sys.exit(1)

if __name__ == "__main__":
    main() 