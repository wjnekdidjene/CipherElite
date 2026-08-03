# =============================================================================
#  Модуль: Автообновление
#  Версия: 1.0.0
# =============================================================================

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from core.logger import get_logger
from core.i18n import get_text
from config.config import Config

logger = get_logger()
VERSION = "1.0.0"

# Путь к проекту
PROJECT_ROOT = Path(__file__).parent.parent
GIT_DIR = PROJECT_ROOT / ".git"

# Файл для хранения информации о последнем обновлении
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
        """Загрузка состояния обновлений"""
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
        """Сохранение состояния обновлений"""
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
        """Проверка, является ли папка Git-репозиторием"""
        return GIT_DIR.exists() and GIT_DIR.is_dir()

    def _run_git_command(self, *args) -> tuple:
        """Выполнение Git-команды и возврат (stdout, stderr, код)"""
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

    def _get_remote_url(self) -> str:
        """Получение URL удалённого репозитория"""
        stdout, _, code = self._run_git_command('remote', 'get-url', 'origin')
        if code == 0 and stdout:
            return stdout
        return self.repo_url

    def _fetch_remote(self) -> bool:
        """Получение обновлений с удалённого репозитория"""
        logger.info("🔄 Проверка обновлений...")
        stdout, stderr, code = self._run_git_command('fetch', 'origin', self.current_branch)
        if code != 0:
            logger.error(f"Ошибка fetch: {stderr}")
            return False
        return True

    def _get_current_commit(self) -> str:
        """Получение текущего хеша коммита"""
        stdout, _, code = self._run_git_command('rev-parse', 'HEAD')
        if code == 0 and stdout:
            return stdout
        return ""

    def _get_remote_commit(self) -> str:
        """Получение хеша последнего коммита на удалённом репозитории"""
        stdout, _, code = self._run_git_command('rev-parse', f'origin/{self.current_branch}')
        if code == 0 and stdout:
            return stdout
        return ""

    def _has_uncommitted_changes(self) -> bool:
        """Проверка наличия несохранённых изменений"""
        stdout, _, code = self._run_git_command('status', '--porcelain')
        return bool(stdout) if code == 0 else False

    async def check_for_updates(self, force: bool = False) -> bool:
        """Проверка наличия обновлений"""
        if not self._is_git_repo():
            logger.warning("⚠️ Проект не является Git-репозиторием")
            return False

        # Проверка не чаще раза в час (если не принудительно)
        if not force and self.last_check:
            try:
                last_check = datetime.fromisoformat(self.last_check)
                if datetime.now() - last_check < timedelta(hours=1):
                    return self.update_available
            except:
                pass

        self.last_check = datetime.now().isoformat()

        # Получение обновлений
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
        """Выполнение обновления"""
        if not self._is_git_repo():
            logger.warning("⚠️ Проект не является Git-репозиторием")
            return False

        if self._has_uncommitted_changes():
            logger.warning("⚠️ Есть несохранённые изменения. Обновление отменено.")
            return False

        logger.info("🔄 Начинаю обновление...")

        # Получение последних изменений
        stdout, stderr, code = self._run_git_command('pull', 'origin', self.current_branch)
        if code != 0:
            logger.error(f"Ошибка обновления: {stderr}")
            return False

        self.last_update = datetime.now().isoformat()
        self.update_available = False
        self._save_state()

        logger.info(f"✅ Обновление успешно! {stdout}")
        return True

    async def auto_update(self) -> bool:
        """Автоматическая проверка и обновление"""
        if not await self.check_for_updates():
            return False

        logger.info("📦 Начинаю автоматическое обновление...")
        return await self.perform_update()


# Глобальный экземпляр
updater = AutoUpdater()


def start_updater():
    """Запуск системы обновлений (вызывается из __init__.py)"""
    logger.info("🔄 Система обновлений запущена")

    async def background_updater():
        """Фоновый процесс проверки обновлений"""
        while True:
            try:
                # Проверка обновлений каждые 6 часов
                await asyncio.sleep(21600)  # 6 часов

                if await updater.check_for_updates():
                    logger.info("📦 Обнаружены обновления!")
                    # Можно отправить уведомление владельцу
                    # await notify_owner()

            except Exception as e:
                logger.error(f"Ошибка в фоновом обновлении: {e}")

    # Запускаем фоновую задачу
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(background_updater())
    else:
        loop.run_until_complete(background_updater())


async def check_update_manual() -> dict:
    """Ручная проверка обновлений (для команд)"""
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
    """Ручное обновление (для команд)"""
    result = {
        "success": False,
        "message": ""
    }

    if not updater._is_git_repo():
        result["message"] = "Проект не является Git-репозиторием"
        return result

    if updater._has_uncommitted_changes():
        result["message"] = "Есть несохранённые изменения. Сначала сохраните их или отмените."
        return result

    success = await updater.perform_update()
    result["success"] = success

    if success:
        result["message"] = "✅ Обновление успешно! Перезапустите бота."
    else:
        result["message"] = "❌ Ошибка обновления. Проверьте логи."

    return result