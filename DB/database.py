import json
from pathlib import Path
from typing import Any, Dict, Optional
from config.config import Config
from core.logger import get_logger

logger = get_logger()

USE_MONGO = bool(Config.MONGO_URI)
mongo_client = None
mongo_db = None


async def init_db():
    global USE_MONGO, mongo_client, mongo_db
    if not USE_MONGO:
        logger.info("📁 Используется JSON хранилище")
        return
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_client = AsyncIOMotorClient(Config.MONGO_URI)
        await mongo_client.admin.command('ping')
        mongo_db = mongo_client.get_database('terazm')
        logger.info("✅ MongoDB подключена")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB ошибка: {e}")
        logger.info("📁 Используется JSON хранилище")
        USE_MONGO = False
        mongo_client = None
        mongo_db = None


def _get_json_path(collection: str) -> Path:
    base = Path("DB")
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{collection}.json"


def _load_json(collection: str) -> Dict:
    path = _get_json_path(collection)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_json(collection: str, data: Dict):
    path = _get_json_path(collection)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def db_get(collection: str, key: Optional[str] = None, default: Any = None) -> Any:
    if USE_MONGO and mongo_db:
        try:
            col = mongo_db[collection]
            doc = await col.find_one({"_id": collection})
            if doc:
                if key is None:
                    doc.pop("_id", None)
                    return doc
                return doc.get(key, default)
            return default
        except Exception:
            pass
    data = _load_json(collection)
    if key is None:
        return data if data else default
    return data.get(key, default)


async def db_set(collection: str, key: str, value: Any):
    if USE_MONGO and mongo_db:
        try:
            col = mongo_db[collection]
            await col.update_one({"_id": collection}, {"$set": {key: value}}, upsert=True)
            return
        except Exception:
            pass
    data = _load_json(collection)
    data[key] = value
    _save_json(collection, data)


async def db_delete(collection: str, key: str):
    if USE_MONGO and mongo_db:
        try:
            col = mongo_db[collection]
            await col.update_one({"_id": collection}, {"$unset": {key: ""}})
            return
        except Exception:
            pass
    data = _load_json(collection)
    if key in data:
        del data[key]
        _save_json(collection, data)


async def db_incr(collection: str, key: str, amount: int = 1) -> int:
    if USE_MONGO and mongo_db:
        try:
            col = mongo_db[collection]
            result = await col.find_one_and_update(
                {"_id": collection},
                {"$inc": {key: amount}},
                upsert=True,
                return_document=True
            )
            return result.get(key, 0)
        except Exception:
            pass
    data = _load_json(collection)
    data[key] = data.get(key, 0) + amount
    _save_json(collection, data)
    return data[key]