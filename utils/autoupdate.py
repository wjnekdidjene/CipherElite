import os
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from core.logger import get_logger
from config.config import Config

logger = get_logger()
VERSION = "1.0.0"

PROJECT_ROOT = Path(__file__).parent.parent
UPDATE_INFO_FILE = PROJECT_ROOT / "DB" / "update_info.json"


class AutoUpdater:
    def __init__(self):
        self.last_check = None
        self.last_update = None
        self.update_available = False
        self.current_branch = Config.BRANCH or "elite"
        self.repo_url = Config.UPSTREAM_REPO or "https://github.com/rishabhops/CipherElite"
        self._load_state()

    def _load_state(self):
        try:
            if UPDATE_INFO_FILE.exists():
                import json
                with open(UPDATE_INFO_FILE, 'r') as f:
                    data = json.load(f)
                    self.last_check = data.get('last_check')
                    self.last_update = data.get('last_update')
                    self.update_available = data.get('update_available', False)
        except Exception as e:
            logger.debug(f"Ошибка загрузки состояния обновлений: {e}")

    def _save_state(self):
        try:
            import json
            UPDATE_INFO_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(UPDATE_INFO_FILE, 'w') as f:
                json.dump({
                    'last_check': self.last_check,
                    'last_update': self.last_update,
                    'update_available': self.update_available
                }, f, indent=2)
        except Exception as e:
            logger.debug(f"Ошибка сохранения состояния обновлений: {e}")

    def _is_git_repo(self) -> bool:
        return (PROJECT_ROOT / ".git").exists()

    def _run_git_command(self, *args) -> tuple:
        try:
            result = subprocess.run(
                ['git'] + list(args),
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            logger.error(f"Ошибка выполнения Git-команды: {e}")
            return "", str(e), 1

    def _fetch_remote(self) -> bool:
        logger.info("🔄 Проверка обновлений...")
        stdout, stderr, code = self._run_git_command('fetch', 'origin', self.current_branch)
        if code != 0:
            logger.error(f"Ошибка fetch: {stderr}")
            return False
        return True

    def _get_current_commit(self) -> str:
        stdout, _, code = self._run_git_command('rev-parse', 'HEAD')
        if code == 0 and stdout:
            return stdout
        return ""

    def _get_remote_commit(self) -> str:
        stdout, _, code = self._run_git_command('rev-parse', f'origin/{self.current_branch}')
        if code == 0 and stdout:
            return stdout
        return ""

    async def check_for_updates(self, force: bool = False) -> bool:
        if not self._is_git_repo():
            logger.warning("⚠️ Проект не является Git-репозиторием")
            return False

        if not force and self.last_check:
            try:
                last_check = datetime.fromisoformat(self.last_check)
                if datetime.now() - last_check < timedelta(hours=6):
                    return self.update_available
            except:
                pass

        self.last_check = datetime.now().isoformat()

        if not self._fetch_remote():
            self._save_state()
            return False

        current = self._get_current_commit()
        remote = self._get_remote_commit()

        if not current or not remote:
            self._save_state()
            return False

        self.update_available = (current != remote)
        self._save_state()

        if self.update_available:
            logger.info(f"📦 Доступны обновления! {current[:8]} -> {remote[:8]}")
        else:
            logger.info("✅ Обновлений нет")

        return self.update_available

    async def perform_update(self) -> bool:
        if not self._is_git_repo():
            logger.warning("⚠️ Проект не является Git-репозиторием")
            return False

        logger.info("🔄 Начинаю обновление...")

        stdout, stderr, code = self._run_git_command('pull', 'origin', self.current_branch)
        if code != 0:
            logger.error(f"Ошибка обновления: {stderr}")
            return False

        self.last_update = datetime.now().isoformat()
        self.update_available = False
        self._save_state()

        logger.info(f"✅ Обновление успешно!")
        return True


updater = AutoUpdater()


def start_updater():
    logger.info("🔄 Система обновлений запущена")

    async def background_updater():
        while True:
            try:
                await asyncio.sleep(21600)
                if await updater.check_for_updates():
                    logger.info("📦 Обнаружены обновления!")
            except Exception as e:
                logger.error(f"Ошибка в фоновом обновлении: {e}")

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(background_updater())
    else:
        loop.run_until_complete(background_updater())


async def check_update_manual() -> dict:
    result = {
        "update_available": False,
        "current": "",
        "remote": "",
        "message": ""
    }

    if not updater._is_git_repo():
        result["message"] = "Проект не является Git-репозиторием"
        return result

    await updater.check_for_updates(force=True)

    current = updater._get_current_commit()
    remote = updater._get_remote_commit()

    result["current"] = current[:8] if current else "Нет"
    result["remote"] = remote[:8] if remote else "Нет"
    result["update_available"] = updater.update_available

    if updater.update_available:
        result["message"] = "📦 Доступны обновления!"
    else:
        result["message"] = "✅ Ваша версия актуальна"

    return result


async def perform_update_manual() -> dict:
    result = {
        "success": False,
        "message": ""
    }

    if not updater._is_git_repo():
        result["message"] = "Проект не является Git-репозиторием"
        return result

    success = await updater.perform_update()
    result["success"] = success

    if success:
        result["message"] = "✅ Обновление успешно! Перезапустите бота."
    else:
        result["message"] = "❌ Ошибка обновления. Проверьте логи."

    return result