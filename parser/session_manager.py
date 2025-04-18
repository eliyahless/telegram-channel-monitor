import os
import logging
import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    FloodWaitError,
    AuthKeyUnregisteredError,
    SessionRevokedError,
    SecurityError
)
from dotenv import load_dotenv, set_key
from .security import SecurityManager, RateLimiter, IPBlocker, SecurityAuditor

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SessionStorage:
    def __init__(self, storage_dir='.sessions'):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.session_file = self.storage_dir / 'session_data.json'
        
    def save_session(self, phone, session_string, two_factor_password=None):
        """Сохраняет данные сессии"""
        try:
            data = {}
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    
            # Хешируем телефон для безопасности
            phone_hash = hashlib.sha256(phone.encode()).hexdigest()
            
            data[phone_hash] = {
                'session_string': session_string,
                'two_factor_password': two_factor_password,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(data, f)
                
            # Также сохраняем в .env для совместимости
            set_key('.env', 'SESSION_STRING', session_string)
            
            logger.info("Сессия успешно сохранена")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении сессии: {e}")
            return False
            
    def load_session(self, phone):
        """Загружает данные сессии"""
        try:
            if not self.session_file.exists():
                return None
                
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                
            phone_hash = hashlib.sha256(phone.encode()).hexdigest()
            if phone_hash in data:
                session_data = data[phone_hash]
                # Проверяем, не устарела ли сессия (старше 7 дней)
                last_updated = datetime.fromisoformat(session_data['last_updated'])
                if datetime.now() - last_updated > timedelta(days=7):
                    logger.warning("Сессия устарела")
                    return None
                return session_data
            return None
        except Exception as e:
            logger.error(f"Ошибка при загрузке сессии: {e}")
            return None
            
    def clear_session(self, phone):
        """Очищает данные сессии"""
        try:
            if not self.session_file.exists():
                return
                
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                
            phone_hash = hashlib.sha256(phone.encode()).hexdigest()
            if phone_hash in data:
                del data[phone_hash]
                with open(self.session_file, 'w') as f:
                    json.dump(data, f)
                set_key('.env', 'SESSION_STRING', '')
                logger.info("Сессия очищена")
        except Exception as e:
            logger.error(f"Ошибка при очистке сессии: {e}")

class SessionManager:
    def __init__(self):
        load_dotenv()
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.phone = os.getenv('PHONE')
        
        # Инициализация компонентов безопасности
        self.security_manager = SecurityManager()
        self.rate_limiter = RateLimiter()
        self.ip_blocker = IPBlocker()
        self.security_auditor = SecurityAuditor()
        
        # Настройки сессии
        self.session_storage_dir = Path('.secure/sessions')
        self.session_storage_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
    async def _safe_request(self, func, *args, **kwargs):
        """Безопасное выполнение запроса с учетом ограничений"""
        identifier = f"{func.__name__}_{args}"
        
        # Проверка IP (если доступно)
        client_ip = kwargs.pop('client_ip', None)
        if client_ip:
            is_allowed, wait_time = self.ip_blocker.check_ip(client_ip, func.__name__)
            if not is_allowed:
                self.security_auditor.log_event(
                    'ip_blocked',
                    f"IP {client_ip} заблокирован на {wait_time} секунд",
                    'warning'
                )
                raise SecurityError(f"IP заблокирован. Подождите {wait_time} секунд")
                
        # Проверка ограничений частоты запросов
        is_allowed, wait_time = self.rate_limiter.check_rate_limit(identifier)
        if not is_allowed:
            self.security_auditor.log_event(
                'rate_limit',
                f"Превышен лимит запросов для {func.__name__}",
                'warning'
            )
            await asyncio.sleep(wait_time)
            
        try:
            result = await func(*args, **kwargs)
            self.security_auditor.log_event(
                'api_request',
                f"Успешный запрос {func.__name__}",
                'info'
            )
            return result
        except FloodWaitError as e:
            self.security_auditor.log_event(
                'flood_wait',
                f"FloodWait для {func.__name__}: {e.seconds} секунд",
                'warning'
            )
            await asyncio.sleep(e.seconds)
            return await self._safe_request(func, *args, **kwargs)
        except Exception as e:
            self.security_auditor.log_event(
                'api_error',
                f"Ошибка в {func.__name__}: {str(e)}",
                'error'
            )
            raise
            
    def _encrypt_session(self, session_string):
        """Шифрование строки сессии"""
        return self.security_manager.encrypt_data({
            'session': session_string,
            'created_at': datetime.now().isoformat(),
            'phone': self.phone
        })
        
    def _decrypt_session(self, encrypted_data):
        """Расшифровка строки сессии"""
        data = self.security_manager.decrypt_data(encrypted_data)
        if not data:
            return None
            
        # Проверяем срок действия сессии (7 дней)
        created_at = datetime.fromisoformat(data['created_at'])
        if datetime.now() - created_at > timedelta(days=7):
            return None
            
        return data['session']
        
    async def _authorize_client(self, client):
        """Безопасная авторизация клиента"""
        try:
            if not await client.is_user_authorized():
                self.security_auditor.log_event(
                    'auth_required',
                    f"Требуется авторизация для {self.phone}",
                    'info'
                )
                
                await self._safe_request(client.send_code_request, self.phone)
                
                code = input('Введите код из Telegram (или "q" для выхода): ')
                if code.lower() == 'q':
                    return False
                    
                try:
                    await self._safe_request(client.sign_in, self.phone, code)
                except SessionPasswordNeededError:
                    password = input('Введите пароль двухфакторной аутентификации: ')
                    await self._safe_request(client.sign_in, password=password)
                    
                # Сохраняем зашифрованную сессию
                session_string = client.session.save()
                encrypted_session = self._encrypt_session(session_string)
                
                session_file = self.session_storage_dir / f"{hashlib.sha256(self.phone.encode()).hexdigest()}.session"
                session_file.write_bytes(encrypted_session)
                
                self.security_auditor.log_event(
                    'auth_success',
                    f"Успешная авторизация для {self.phone}",
                    'info'
                )
                
            return True
            
        except Exception as e:
            self.security_auditor.log_event(
                'auth_error',
                f"Ошибка авторизации: {str(e)}",
                'error'
            )
            return False
            
    async def get_client(self):
        """Получение защищенного клиента"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Пробуем загрузить существующую сессию
                session_file = self.session_storage_dir / f"{hashlib.sha256(self.phone.encode()).hexdigest()}.session"
                
                if session_file.exists():
                    encrypted_session = session_file.read_bytes()
                    session_string = self._decrypt_session(encrypted_session)
                    
                    if session_string:
                        client = TelegramClient(
                            StringSession(session_string),
                            self.api_id,
                            self.api_hash
                        )
                        await client.connect()
                        
                        # Проверяем валидность сессии
                        try:
                            me = await self._safe_request(client.get_me)
                            if me:
                                self.security_auditor.log_event(
                                    'session_restored',
                                    f"Успешное восстановление сессии для {me.first_name}",
                                    'info'
                                )
                                return client
                        except (AuthKeyUnregisteredError, SessionRevokedError):
                            self.security_auditor.log_event(
                                'session_invalid',
                                "Сессия устарела или была отозвана",
                                'warning'
                            )
                            session_file.unlink(missing_ok=True)
                            
                # Создаем новую сессию
                client = TelegramClient(
                    StringSession(),
                    self.api_id,
                    self.api_hash
                )
                await client.connect()
                
                if await self._authorize_client(client):
                    return client
                    
            except Exception as e:
                self.security_auditor.log_event(
                    'client_error',
                    f"Ошибка при создании клиента: {str(e)}",
                    'error'
                )
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(5)
                else:
                    self.security_auditor.log_event(
                        'max_retries',
                        "Превышено максимальное количество попыток",
                        'critical'
                    )
                    return None
        
        return None
        
    async def close_client(self, client):
        """Безопасное закрытие клиента"""
        try:
            if client:
                await client.disconnect()
                self.security_auditor.log_event(
                    'client_disconnected',
                    "Клиент успешно отключен",
                    'info'
                )
        except Exception as e:
            self.security_auditor.log_event(
                'disconnect_error',
                f"Ошибка при закрытии клиента: {str(e)}",
                'error'
            )
            
    def get_security_report(self):
        """Получение отчета о безопасности"""
        return self.security_auditor.get_security_report() 