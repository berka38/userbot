import os
import json
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from .config import Config

class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._local_db_file = "userbot_data.json"
        self._data = {}
        self._load_local_db()

    def _load_local_db(self):
        """Yerel veritabanını yükle veya oluştur"""
        try:
            if os.path.exists(self._local_db_file):
                with open(self._local_db_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            else:
                self._data = {
                    "users": {},
                    "modules": {},
                    "settings": {}
                }
                self._save_local_db()
        except Exception as e:
            print(f"⚠️ Yerel veritabanı yüklenirken hata: {str(e)}")
            self._data = {
                "users": {},
                "modules": {},
                "settings": {}
            }

    def _save_local_db(self):
        """Yerel veritabanını kaydet"""
        try:
            with open(self._local_db_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Yerel veritabanı kaydedilirken hata: {str(e)}")

    async def connect(self):
        """Veritabanına bağlan"""
        try:
            # MongoDB'ye bağlanmayı dene
            self.client = AsyncIOMotorClient(Config.MONGODB_URL)
            self.db = self.client[Config.DB_NAME]
            # Test bağlantısı
            await self.db.command('ping')
            print("✅ MongoDB'ye bağlandı!")
        except Exception as e:
            print(f"⚠️ MongoDB bağlantı hatası: {str(e)}")
            print("ℹ️ Yerel veritabanı kullanılıyor...")
            self.client = None
            self.db = None

    async def disconnect(self):
        """Veritabanı bağlantısını kapat"""
        if self.client:
            self.client.close()
        self._save_local_db()

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini getir"""
        try:
            if self.db:
                return await self.db.users.find_one({"user_id": user_id})
            else:
                return self._data["users"].get(str(user_id))
        except Exception as e:
            print(f"⚠️ Kullanıcı bilgisi alınırken hata: {str(e)}")
            return None

    async def save_user(self, user_data: Dict[str, Any]):
        """Kullanıcı bilgilerini kaydet/güncelle"""
        try:
            if self.db:
                await self.db.users.update_one(
                    {"user_id": user_data["user_id"]},
                    {"$set": user_data},
                    upsert=True
                )
            else:
                self._data["users"][str(user_data["user_id"])] = user_data
                self._save_local_db()
        except Exception as e:
            print(f"⚠️ Kullanıcı bilgisi kaydedilirken hata: {str(e)}")

    async def get_modules(self, user_id: int) -> list:
        """Kullanıcının yüklü modüllerini getir"""
        try:
            if self.db:
                user = await self.get_user(user_id)
                return user.get("modules", []) if user else []
            else:
                user = self._data["users"].get(str(user_id), {})
                return user.get("modules", [])
        except Exception as e:
            print(f"⚠️ Modül listesi alınırken hata: {str(e)}")
            return []

    async def add_module(self, user_id: int, module_name: str, module_data: Dict[str, Any]):
        """Yeni modül ekle"""
        try:
            if self.db:
                await self.db.users.update_one(
                    {"user_id": user_id},
                    {
                        "$push": {
                            "modules": {
                                "name": module_name,
                                "enabled": True,
                                "data": module_data
                            }
                        }
                    },
                    upsert=True
                )
            else:
                if str(user_id) not in self._data["users"]:
                    self._data["users"][str(user_id)] = {"modules": []}
                
                self._data["users"][str(user_id)]["modules"].append({
                    "name": module_name,
                    "enabled": True,
                    "data": module_data
                })
                self._save_local_db()
        except Exception as e:
            print(f"⚠️ Modül eklenirken hata: {str(e)}")

    async def toggle_module(self, user_id: int, module_name: str, enabled: bool):
        """Modülü etkinleştir/devre dışı bırak"""
        try:
            if self.db:
                await self.db.users.update_one(
                    {
                        "user_id": user_id,
                        "modules.name": module_name
                    },
                    {
                        "$set": {
                            "modules.$.enabled": enabled
                        }
                    }
                )
            else:
                user = self._data["users"].get(str(user_id))
                if user and "modules" in user:
                    for module in user["modules"]:
                        if module["name"] == module_name:
                            module["enabled"] = enabled
                            break
                self._save_local_db()
        except Exception as e:
            print(f"⚠️ Modül durumu değiştirilirken hata: {str(e)}")

    async def remove_module(self, user_id: int, module_name: str):
        """Modülü kaldır"""
        try:
            if self.db:
                await self.db.users.update_one(
                    {"user_id": user_id},
                    {
                        "$pull": {
                            "modules": {
                                "name": module_name
                            }
                        }
                    }
                )
            else:
                user = self._data["users"].get(str(user_id))
                if user and "modules" in user:
                    user["modules"] = [
                        m for m in user["modules"]
                        if m["name"] != module_name
                    ]
                self._save_local_db()
        except Exception as e:
            print(f"⚠️ Modül kaldırılırken hata: {str(e)}")

# Global veritabanı nesnesi
db = Database() 