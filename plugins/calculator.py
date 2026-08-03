# =============================================================================
#  Плагин: Калькулятор
#  Версия: 1.0.0
#  Категория: utilities
# =============================================================================

import math
import re
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "1.0.0"
CATEGORY = "utilities"


def init(client):
    commands = [
        ".calc <выражение> - Вычислить выражение",
        ".calc sqrt <число> - Квадратный корень",
        ".calc sin <число> - Синус (градусы)",
        ".calc cos <число> - Косинус (градусы)",
        ".calc tan <число> - Тангенс (градусы)",
        ".calc factorial <число> - Факториал",
        ".calc log <число> - Десятичный логарифм",
        ".calc ln <число> - Натуральный логарифм",
        ".calc power <число> <степень> - Возведение в степень"
    ]
    description = "🧮 Калькулятор - Математические вычисления"
    add_handler("calculator", commands, description)


async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.calc\s+(.+)"))
    @rishabh()
    async def calculator(event):
        try:
            expr = event.pattern_match.group(1).strip()
            result = None
            label = "Результат"

            # Проверка на команды
            parts = expr.split()
            if len(parts) > 0:
                cmd = parts[0].lower()

                if cmd == "sqrt" and len(parts) > 1:
                    num = float(parts[1])
                    result = math.sqrt(num)
                    label = "Квадратный корень"
                elif cmd == "sin" and len(parts) > 1:
                    num = float(parts[1])
                    result = math.sin(math.radians(num))
                    label = "Синус"
                elif cmd == "cos" and len(parts) > 1:
                    num = float(parts[1])
                    result = math.cos(math.radians(num))
                    label = "Косинус"
                elif cmd == "tan" and len(parts) > 1:
                    num = float(parts[1])
                    result = math.tan(math.radians(num))
                    label = "Тангенс"
                elif cmd == "factorial" and len(parts) > 1:
                    num = int(parts[1])
                    result = math.factorial(num)
                    label = "Факториал"
                elif cmd == "log" and len(parts) > 1:
                    num = float(parts[1])
                    result = math.log10(num)
                    label = "Десятичный логарифм"
                elif cmd == "ln" and len(parts) > 1:
                    num = float(parts[1])
                    result = math.log(num)
                    label = "Натуральный логарифм"
                elif cmd == "power" and len(parts) > 2:
                    base = float(parts[1])
                    exp = float(parts[2])
                    result = math.pow(base, exp)
                    label = "Возведение в степень"
                else:
                    # Обычное выражение
                    allowed = re.sub(r'[^0-9+\-*/(). ]', '', expr)
                    result = eval(allowed)

            await event.reply(f"🧮 **{label}:**\n\n`{expr}` = **{result}**")

        except ZeroDivisionError:
            await event.reply("❌ Ошибка: Деление на ноль!")
        except ValueError:
            await event.reply("❌ Ошибка: Неверный ввод. Проверьте число.")
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)}")