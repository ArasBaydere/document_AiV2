# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy() # db nesnesi burada tanımlanıyor, app.py'de init_app ile bağlanacak

# Sohbet oturumlarını saklar
class ChatSession(db.Model):
    __tablename__ = 'chat_session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False) # Hangi kullanıcının sohbeti
    title = db.Column(db.String(200), nullable=False) # Sohbet başlığı
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Oluşturulma zamanı
    # Sohbet oturumuna ait mesajlar
    messages = db.relationship('Message', backref='session', lazy=True, cascade="all, delete-orphan", order_by='Message.timestamp')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat()
        }

# Sohbet mesajlarını saklar
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id', ondelete='CASCADE'), nullable=False) # Hangi sohbete ait
    sender = db.Column(db.String(50), nullable=False) # Mesajı gönderen (user/bot)
    content = db.Column(db.Text, nullable=False) # Mesaj içeriği
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # Mesajın gönderilme zamanı

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

# Ürün kategorilerini saklar
class Kategori(db.Model):
    __tablename__ = 'kategoriler'
    id = db.Column(db.Integer, primary_key=True)
    KategoriAdiTr = db.Column(db.String(255), nullable=False) # Kategori adı (Türkçe)
    parent_id = db.Column(db.Integer, db.ForeignKey('kategoriler.id'), nullable=True) # Üst kategori ID'si (hiyerarşi için)

# Ürün bilgilerini saklar
class Urun(db.Model):
    __tablename__ = 'urunler'
    id = db.Column(db.Integer, primary_key=True)
    UrunKodu = db.Column(db.String(255), nullable=False, unique=True) # Ürün kodu (benzersiz)
    UrunAdiTR = db.Column(db.String(255), nullable=False) # Ürün adı (Türkçe)
    OzelliklerTR = db.Column(db.Text) # Ürün özellikleri (Türkçe metin)
    BilgiTR = db.Column(db.Text) # Ek bilgi (Türkçe metin)
    KategoriID = db.Column(db.Integer, db.ForeignKey('kategoriler.id'), nullable=True) # Ait olduğu kategori ID'si
    kategori = db.relationship('Kategori', backref='urunler_list', lazy=True) # Kategori ilişkisi

    def to_dict(self):
        return {
            'id': self.id,
            'UrunKodu': self.UrunKodu,
            'UrunAdiTR': self.UrunAdiTR,
            'OzelliklerTR': self.OzelliklerTR,
            'BilgiTR': self.BilgiTR,
            'KategoriID': self.KategoriID
        }
