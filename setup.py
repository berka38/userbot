import os
import sys
import time
import subprocess

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

def create_env_file(api_id, api_hash):
    """Yapılandırma dosyasını oluştur"""
    env_content = f"""# Telegram API bilgileri
API_ID={api_id}
API_HASH={api_hash}

# MongoDB bağlantısı
MONGODB_URL=mongodb+srv://folunted:bert123@cluster0.lbuyo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=userbot_db

# Modül repository'si
MODULE_REPO=https://raw.githubusercontent.com/your-repo/modules/main/"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

def create_run_script():
    """Çalıştırma scripti oluştur"""
    if os.name == 'nt':  # Windows
        with open("start.bat", "w", encoding="utf-8") as f:
            f.write('@echo off\n')
            f.write('title UserBot\n')
            f.write('python userbot/main.py\n')
            f.write('pause\n')
    else:  # Linux/Mac
        with open("start.sh", "w") as f:
            f.write('#!/bin/bash\n')
            f.write('python3 userbot/main.py\n')
        os.chmod("start.sh", 0o755)

def main():
    """Ana kurulum fonksiyonu"""
    clear_screen()
    show_banner()
    
    # Python sürümünü kontrol et
    check_python_version()
    
    # Gerekli paketleri kur
    install_requirements()
    
    # Telegram API bilgilerini al
    api_id, api_hash = get_telegram_api()
    
    # Yapılandırma dosyasını oluştur
    print_colored("\n⚙️ Yapılandırma dosyası oluşturuluyor...", "yellow")
    create_env_file(api_id, api_hash)
    print_colored("✅ Yapılandırma dosyası oluşturuldu!", "green")
    
    # Çalıştırma scripti oluştur
    print_colored("\n📜 Çalıştırma scripti oluşturuluyor...", "yellow")
    create_run_script()
    print_colored("✅ Çalıştırma scripti oluşturuldu!", "green")
    
    # Kurulum tamamlandı
    print_colored("\n🎉 Kurulum başarıyla tamamlandı!", "green")
    print_colored("\nUserBot'u başlatmak için:", "white")
    if os.name == 'nt':
        print_colored("➜ start.bat dosyasına çift tıklayın", "yellow")
    else:
        print_colored("➜ ./start.sh komutunu çalıştırın", "yellow")
    
    print_colored("\nİyi kullanımlar! 👋", "blue")
    time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n❌ Kurulum iptal edildi!", "red")
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n\n❌ Bir hata oluştu: {str(e)}", "red")
        sys.exit(1) 