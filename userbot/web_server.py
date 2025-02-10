from aiohttp import web
import asyncio
from datetime import datetime
import json

# Global değişkenler
START_TIME = datetime.now()
bot_status = {"is_running": True}

async def handle_home(request):
    """Ana sayfa"""
    uptime = datetime.now() - START_TIME
    return web.Response(text=f"UserBot is running! Uptime: {str(uptime).split('.')[0]}")

async def handle_status(request):
    """Bot durumu"""
    uptime = datetime.now() - START_TIME
    status = {
        "status": "active" if bot_status["is_running"] else "inactive",
        "uptime": str(uptime).split('.')[0],
        "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return web.Response(text=json.dumps(status), content_type='application/json')

async def start_web_server():
    """Web sunucusunu başlat"""
    app = web.Application()
    app.router.add_get('/', handle_home)
    app.router.add_get('/status', handle_status)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print(f"✅ Web sunucusu başlatıldı: http://localhost:8080")
    
    return runner, site

def run_web_server():
    """Web sunucusunu arka planda çalıştır"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_web_server()) 