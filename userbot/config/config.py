from typing import Optional
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # Telegram API bilgileri
    API_ID: Optional[int] = int(os.getenv("API_ID", "0"))
    API_HASH: Optional[str] = os.getenv("API_HASH")
    
    # Oturum dosyası
    SESSION_NAME: str = "userbot"
    
    # Komut öneki
    CMD_PREFIX: str = "!"
    
    # MongoDB bağlantısı
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "userbot_db")
    
    # Web panel bağlantısı
    PANEL_URL: str = "http://localhost:3000"
    API_PORT: int = 8000
    
    # Modül ayarları
    MODULE_REPO: str = os.getenv("MODULE_REPO", "https://raw.githubusercontent.com/your-repo/modules/main/")
    MODULES_DIR: str = "userbot/modules"

    @classmethod
    def validate(cls) -> bool:
        """Gerekli yapılandırma değerlerinin varlığını kontrol et"""
        try:
            # API_ID kontrol et
            if cls.API_ID == 0:
                return False
            
            # API_HASH kontrol et
            if not cls.API_HASH or not cls.API_HASH.strip():
                return False
                
            return True
            
        except Exception:
            return False 