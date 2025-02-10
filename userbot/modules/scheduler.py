import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from ..config.config import Config

active_schedules = {}

def parse_time(time_str: str) -> int:
    """Zaman stringini saniyeye çevirir (örn: 1h, 30m, 5s)"""
    unit = time_str[-1].lower()
    value = int(time_str[:-1])
    
    if unit == 'h':
        return value * 3600
    elif unit == 'm':
        return value * 60
    elif unit == 's':
        return value
    else:
        raise ValueError("Geçersiz zaman formatı! Kullanım: 1h, 30m, 5s")

async def send_scheduled_message(client: Client, chat_id: int, message: str, interval: int, repeat: int):
    """Belirtilen aralıklarla mesaj gönderir"""
    count = 0
    while count < repeat:
        await asyncio.sleep(interval)
        try:
            await client.send_message(chat_id, message)
            count += 1
        except Exception as e:
            print(f"Mesaj gönderme hatası: {e}")
            break

@Client.on_message(filters.command("zamanla", prefixes=Config.CMD_PREFIX) & filters.me)
async def schedule_message(client: Client, message: Message):
    """!zamanla <süre> <tekrar> <mesaj> komutu ile mesaj zamanlar"""
    try:
        # Komutu parçalara ayır
        cmd = message.text.split(maxsplit=3)
        if len(cmd) < 4:
            await message.reply("Kullanım: !zamanla <süre> <tekrar> <mesaj>")
            return

        _, time_str, repeat_str, msg = cmd
        
        # Parametreleri işle
        interval = parse_time(time_str)
        repeat = int(repeat_str)
        
        if repeat <= 0:
            await message.reply("Tekrar sayısı pozitif bir sayı olmalıdır!")
            return
            
        # Zamanlamayı başlat
        task_id = f"{message.chat.id}_{datetime.now().timestamp()}"
        task = asyncio.create_task(
            send_scheduled_message(client, message.chat.id, msg, interval, repeat)
        )
        active_schedules[task_id] = task
        
        await message.reply(
            f"Mesaj zamanlandı!\n"
            f"Aralık: {time_str}\n"
            f"Tekrar: {repeat}\n"
            f"Mesaj: {msg}"
        )
        
    except ValueError as e:
        await message.reply(str(e))
    except Exception as e:
        await message.reply(f"Bir hata oluştu: {str(e)}")

@Client.on_message(filters.command("iptal", prefixes=Config.CMD_PREFIX) & filters.me)
async def cancel_schedules(client: Client, message: Message):
    """Aktif zamanlanmış mesajları iptal eder"""
    chat_tasks = [
        task_id for task_id in active_schedules
        if task_id.startswith(f"{message.chat.id}_")
    ]
    
    for task_id in chat_tasks:
        task = active_schedules.pop(task_id)
        task.cancel()
    
    await message.reply(f"{len(chat_tasks)} adet zamanlanmış mesaj iptal edildi.") 