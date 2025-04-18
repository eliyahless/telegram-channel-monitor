import os
import base64
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, storage_dir='.secure'):
        """Инициализация менеджера безопасности"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, mode=0o700)  # Только владелец имеет доступ
        self.key_file = self.storage_dir / 'key.secure'
        self.salt_file = self.storage_dir / 'salt.secure'
        self.fernet = self._initialize_encryption()
        
    def _generate_salt(self):
        """Генерация соли для ключа шифрования"""
        return os.urandom(16)
        
    def _derive_key(self, salt):
        """Получение ключа шифрования из мастер-пароля"""
        load_dotenv()
        master_password = os.getenv('MASTER_PASSWORD', 'default_secure_password').encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password))
        
    def _initialize_encryption(self):
        """Инициализация системы шифрования"""
        try:
            if not self.salt_file.exists():
                salt = self._generate_salt()
                self.salt_file.write_bytes(salt)
            else:
                salt = self.salt_file.read_bytes()
                
            key = self._derive_key(salt)
            return Fernet(key)
            
        except Exception as e:
            logger.error(f"Ошибка инициализации шифрования: {e}")
            raise
            
    def encrypt_data(self, data):
        """Шифрование данных"""
        try:
            json_data = json.dumps(data).encode()
            return self.fernet.encrypt(json_data)
        except Exception as e:
            logger.error(f"Ошибка шифрования данных: {e}")
            return None
            
    def decrypt_data(self, encrypted_data):
        """Расшифровка данных"""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Ошибка расшифровки данных: {e}")
            return None
            
class RateLimiter:
    def __init__(self):
        """Инициализация ограничителя запросов"""
        self.requests = {}
        self.timeframes = {
            'per_second': 1,
            'per_minute': 60,
            'per_hour': 3600
        }
        self.limits = {
            'per_second': 2,
            'per_minute': 20,
            'per_hour': 180
        }
        
    def _clean_old_requests(self, timeframe):
        """Очистка устаревших запросов"""
        current_time = datetime.now().timestamp()
        self.requests = {
            key: timestamp 
            for key, timestamp in self.requests.items()
            if current_time - timestamp < timeframe
        }
        
    def check_rate_limit(self, identifier):
        """Проверка ограничений частоты запросов"""
        current_time = datetime.now().timestamp()
        
        # Проверяем все временные рамки
        for timeframe_name, timeframe in self.timeframes.items():
            self._clean_old_requests(timeframe)
            
            # Подсчитываем количество запросов в текущем временном окне
            requests_in_timeframe = sum(
                1 for timestamp in self.requests.values()
                if current_time - timestamp < timeframe
            )
            
            if requests_in_timeframe >= self.limits[timeframe_name]:
                wait_time = timeframe - (current_time - min(self.requests.values()))
                return False, wait_time
                
        # Добавляем новый запрос
        self.requests[f"{identifier}_{current_time}"] = current_time
        return True, 0
        
class IPBlocker:
    def __init__(self, storage_dir='.secure'):
        """Инициализация блокировщика IP"""
        self.storage_dir = Path(storage_dir)
        self.blocked_ips_file = self.storage_dir / 'blocked_ips.json'
        self.suspicious_ips = {}
        self.blocked_ips = self._load_blocked_ips()
        
    def _load_blocked_ips(self):
        """Загрузка списка заблокированных IP"""
        try:
            if self.blocked_ips_file.exists():
                with open(self.blocked_ips_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки списка заблокированных IP: {e}")
            return {}
            
    def _save_blocked_ips(self):
        """Сохранение списка заблокированных IP"""
        try:
            with open(self.blocked_ips_file, 'w') as f:
                json.dump(self.blocked_ips, f)
        except Exception as e:
            logger.error(f"Ошибка сохранения списка заблокированных IP: {e}")
            
    def check_ip(self, ip, action='default'):
        """Проверка IP на подозрительную активность"""
        current_time = datetime.now().timestamp()
        
        # Проверяем, не заблокирован ли IP
        if ip in self.blocked_ips:
            block_data = self.blocked_ips[ip]
            if block_data['expires'] > current_time:
                return False, block_data['expires'] - current_time
            else:
                del self.blocked_ips[ip]
                self._save_blocked_ips()
                
        # Проверяем подозрительную активность
        if ip not in self.suspicious_ips:
            self.suspicious_ips[ip] = {
                'actions': [],
                'warnings': 0
            }
            
        self.suspicious_ips[ip]['actions'].append({
            'time': current_time,
            'action': action
        })
        
        # Очищаем старые действия (старше часа)
        self.suspicious_ips[ip]['actions'] = [
            action for action in self.suspicious_ips[ip]['actions']
            if current_time - action['time'] < 3600
        ]
        
        # Проверяем частоту действий
        if len(self.suspicious_ips[ip]['actions']) > 100:  # Более 100 действий в час
            self.suspicious_ips[ip]['warnings'] += 1
            
        # Если слишком много предупреждений, блокируем IP
        if self.suspicious_ips[ip]['warnings'] >= 3:
            self.blocked_ips[ip] = {
                'reason': 'Подозрительная активность',
                'expires': current_time + 86400  # Блокировка на 24 часа
            }
            self._save_blocked_ips()
            return False, 86400
            
        return True, 0
        
class SecurityAuditor:
    def __init__(self):
        """Инициализация аудитора безопасности"""
        self.security_events = []
        self.alert_threshold = 5
        
    def log_event(self, event_type, details, severity='info'):
        """Логирование события безопасности"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details,
            'severity': severity
        }
        self.security_events.append(event)
        
        # Если событие критическое, проверяем необходимость оповещения
        if severity == 'critical':
            self._check_alert_threshold()
            
    def _check_alert_threshold(self):
        """Проверка необходимости оповещения о проблемах безопасности"""
        current_time = datetime.now()
        recent_critical_events = [
            event for event in self.security_events
            if (event['severity'] == 'critical' and
                (current_time - datetime.fromisoformat(event['timestamp'])) < timedelta(minutes=5))
        ]
        
        if len(recent_critical_events) >= self.alert_threshold:
            self._send_security_alert(recent_critical_events)
            
    def _send_security_alert(self, events):
        """Отправка оповещения о проблемах безопасности"""
        # Здесь можно добавить отправку уведомлений через телеграм или email
        logger.critical(f"ВНИМАНИЕ! Обнаружено {len(events)} критических событий безопасности!")
        for event in events:
            logger.critical(f"Событие: {event['type']}, Детали: {event['details']}")
            
    def get_security_report(self):
        """Получение отчета о безопасности"""
        return {
            'total_events': len(self.security_events),
            'critical_events': len([e for e in self.security_events if e['severity'] == 'critical']),
            'recent_events': [e for e in self.security_events[-10:]],  # Последние 10 событий
            'statistics': self._calculate_statistics()
        }
        
    def _calculate_statistics(self):
        """Расчет статистики безопасности"""
        current_time = datetime.now()
        last_24h = [
            event for event in self.security_events
            if (current_time - datetime.fromisoformat(event['timestamp'])) < timedelta(hours=24)
        ]
        
        return {
            'events_24h': len(last_24h),
            'critical_24h': len([e for e in last_24h if e['severity'] == 'critical']),
            'types_distribution': self._get_event_types_distribution(last_24h)
        }
        
    def _get_event_types_distribution(self, events):
        """Получение распределения типов событий"""
        distribution = {}
        for event in events:
            event_type = event['type']
            distribution[event_type] = distribution.get(event_type, 0) + 1
        return distribution 