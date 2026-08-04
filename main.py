#!/usr/bin/env python3
import asyncio
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.logger import setup_logging
from core.i18n import load_translations
from startup.startup import start_bot
from vars import config

logger = setup_logging()
load_translations(config.LANGUAGE)


class CipherBot:
    __slots__ = ('client', 'bot', '_shutdown')
    
    def __init__(self):
        self.client = None
        self.bot = None
        self._shutdown = False

    async def run(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s, f: asyncio.create_task(self.shutdown()))
        
        logger.info("🚀 Запуск TERAZM...")
        try:
            await start_bot(self)
        except Exception as e:
            logger.critical(f"❌ Ошибка: {e}")
            await self.shutdown()

    async def shutdown(self):
        if self._shutdown:
            return
        self._shutdown = True
        logger.info("🛑 Завершение...")
        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass
        if self.bot:
            try:
                await self.bot.disconnect()
            except:
                pass
        logger.info("✅ Завершено")
        sys.exit(0)


if __name__ == "__main__":
    bot = CipherBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n🛑 Остановка пользователем...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)