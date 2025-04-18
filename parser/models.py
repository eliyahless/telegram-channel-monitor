from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ParsedMessage:
    id: str
    text: str
    city: str
    tags: List[str]
    is_hot: bool
    short: str
    link: str
    source: str
    created_at: datetime = datetime.now()

    def to_dict(self) -> Dict:
        """Конвертирует объект в словарь для JSON"""
        return {
            "id": self.id,
            "text": self.text,
            "city": self.city,
            "tags": self.tags,
            "is_hot": self.is_hot,
            "short": self.short,
            "link": self.link,
            "source": self.source,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ParsedMessage':
        """Создает объект из словаря"""
        return cls(
            id=data['id'],
            text=data['text'],
            city=data['city'],
            tags=data['tags'],
            is_hot=data['is_hot'],
            short=data['short'],
            link=data['link'],
            source=data['source'],
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        ) 