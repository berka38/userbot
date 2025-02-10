from pyrogram import Client

print("🔄 Session String Oluşturucu")
print("=" * 50)

# API bilgilerini al
api_id = input("\n📝 API ID'nizi girin: ")
api_hash = input("📝 API HASH'inizi girin: ")
phone = input("📱 Telefon numaranızı girin (örn: +905551234567): ")

print("\n🔄 Telegram'a bağlanılıyor...")

# İstemciyi oluştur ve başlat
app = Client(
    "my_account",
    api_id=api_id,
    api_hash=api_hash,
    phone_number=phone,
    in_memory=True
)

with app:
    # Session string'i al
    session_string = app.export_session_string()
    print("\n✅ Session string başarıyla oluşturuldu!")
    print("\n⚠️ BU KODU RENDER.COM'DA SESSION_STRING OLARAK EKLEYİN:")
    print("=" * 50)
    print(f"\n{session_string}\n")
    print("=" * 50)
    print("\n❗ BU KODU GÜVENLİ BİR YERDE SAKLAYIN!")

input("\n⏎ Çıkmak için Enter'a basın...") 