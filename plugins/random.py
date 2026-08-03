# =============================================================================
#  Плагин: Конвертер единиц
#  Версия: 1.0.0
#  Категория: utilities
# =============================================================================

from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "1.0.0"
CATEGORY = "utilities"

# Курсы валют (можно обновлять)
CURRENCY_RATES = {
    'usd': 1.0,
    'eur': 0.92,
    'rub': 92.5,
    'kzt': 470,
    'uah': 41.2,
    'gbp': 0.79,
    'cny': 7.25,
    'jpy': 150.0
}


def init(client):
    commands = [
        ".unit <число> <из> to <в> - Конвертировать единицы",
        ".unit length <число> <из> to <в> - Конвертировать длину",
        ".unit weight <число> <из> to <в> - Конвертировать вес",
        ".unit currency <число> <из> to <в> - Конвертировать валюту"
    ]
    description = "📏 Единицы - Конвертер единиц измерения"
    add_handler("unit", commands, description)


async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.unit\s+(.+)"))
    @rishabh()
    async def unit(event):
        try:
            expr = event.pattern_match.group(1).strip()
            parts = expr.split()

            if len(parts) < 4:
                await event.reply("❌ Использование: `.unit 10 km to mi`")
                return

            # Определение типа конвертации
            if parts[0] in ['length', 'weight', 'currency']:
                unit_type = parts[0]
                value = float(parts[1])
                from_unit = parts[2].lower()
                to_unit = parts[4].lower() if len(parts) > 4 else parts[3].lower()
            else:
                unit_type = 'length'
                value = float(parts[0])
                from_unit = parts[1].lower()
                to_unit = parts[3].lower() if len(parts) > 3 else parts[2].lower()

            # Конвертация длины
            if unit_type == 'length':
                length_units = {
                    'km': 1000, 'm': 1, 'cm': 0.01, 'mm': 0.001,
                    'mi': 1609.34, 'ft': 0.3048, 'in': 0.0254,
                    'yd': 0.9144, 'nm': 1852
                }
                
                if from_unit not in length_units or to_unit not in length_units:
                    await event.reply("❌ Неизвестная единица длины.")
                    return
                
                result = value * length_units[from_unit] / length_units[to_unit]
                await event.reply(f"📏 **{value} {from_unit}** = **{result:.4f} {to_unit}**")

            # Конвертация веса
            elif unit_type == 'weight':
                weight_units = {
                    'kg': 1, 'g': 0.001, 'mg': 0.000001,
                    'lb': 0.453592, 'oz': 0.0283495, 't': 1000
                }
                
                if from_unit not in weight_units or to_unit not in weight_units:
                    await event.reply("❌ Неизвестная единица веса.")
                    return
                
                result = value * weight_units[from_unit] / weight_units[to_unit]
                await event.reply(f"⚖️ **{value} {from_unit}** = **{result:.4f} {to_unit}**")

            # Конвертация валют
            elif unit_type == 'currency':
                if from_unit not in CURRENCY_RATES or to_unit not in CURRENCY_RATES:
                    await event.reply("❌ Неизвестная валюта.")
                    return
                
                result = value * CURRENCY_RATES[from_unit] / CURRENCY_RATES[to_unit]
                await event.reply(f"💱 **{value} {from_unit.upper()}** = **{result:.2f} {to_unit.upper()}**")

            else:
                await event.reply("❌ Неизвестный тип. Используйте: length, weight, currency")

        except ValueError:
            await event.reply("❌ Ошибка: Неверное число.")
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)}")