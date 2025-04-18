from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///gift_shop.db')
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    name = Column(String)
    stars = Column(Integer, default=0)
    transactions = relationship("Transaction", back_populates="user")

class Gift(Base):
    __tablename__ = 'gifts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    gift_id = Column(Integer, ForeignKey('gifts.id'))
    amount = Column(Integer)
    user = relationship("User", back_populates="transactions")
    gift = relationship("Gift")

def init_db():
    """Инициализация базы данных"""
    Base.metadata.create_all(engine)
    session = Session()
    
    # Создаем тестовые подарки, если их нет
    if not session.query(Gift).first():
        gifts = [
            Gift(name="Подарок 1", description="Описание подарка 1", price=10, image_url=""),
            Gift(name="Подарок 2", description="Описание подарка 2", price=20, image_url=""),
            Gift(name="Подарок 3", description="Описание подарка 3", price=30, image_url="")
        ]
        session.add_all(gifts)
        session.commit()
    
    session.close()

def create_user(telegram_id: int, name: str):
    """Создание нового пользователя"""
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, name=name)
        session.add(user)
        session.commit()
    session.close()
    return user

def get_user_stars(telegram_id: int) -> int:
    """Получение баланса звезд пользователя"""
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    stars = user.stars if user else 0
    session.close()
    return stars

def add_stars(telegram_id: int, amount: int):
    """Добавление звезд пользователю"""
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.stars += amount
        session.commit()
    session.close()

def remove_stars(telegram_id: int, amount: int) -> bool:
    """Списание звезд с баланса пользователя"""
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user and user.stars >= amount:
        user.stars -= amount
        session.commit()
        session.close()
        return True
    session.close()
    return False

def get_gifts():
    """Получение списка всех подарков"""
    session = Session()
    gifts = session.query(Gift).all()
    session.close()
    return gifts 