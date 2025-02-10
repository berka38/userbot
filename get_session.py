from pyrogram import Client
import asyncio
from pyrogram.errors import RPCError

async def main():
    print("\n🔄 Session String Oluşturucu")
    print("=" * 50)

    # API bilgilerini al
    api_id = input("\n📝 API ID'nizi girin: ")
    api_hash = input("📝 API HASH'inizi girin: ")
    phone = input("📱 Telefon numaranızı girin (örn: +905551234567): ")

    print("\n🔄 Telegram'a bağlanılıyor...")

    try:
        # İstemciyi oluştur
        async with Client(
            "my_account",
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone,
            in_memory=True
        ) as app:
            # Session string'i al
            session_string = await app.export_session_string()
            print("\n✅ Session string başarıyla oluşturuldu!")
            print("\n⚠️ BU KODU RENDER.COM'DA SESSION_STRING OLARAK EKLEYİN:")
            print("=" * 50)
            print(f"\n{session_string}\n")
            print("=" * 50)
            print("\n❗ BU KODU GÜVENLİ BİR YERDE SAKLAYIN!")
            
    except RPCError as e:
        print(f"\n❌ Telegram API Hatası: {str(e)}")
    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")

    input("\n⏎ Çıkmak için Enter'a basın...")

if __name__ == "__main__":
    asyncio.run(main()) 