# config.py

import os
# from werkzeug.security import generate_password_hash # Şifre hash'leme için kullanılabilir

class Config:
    # Flask Uygulama Ayarları
    SECRET_KEY = os.urandom(24) # Oturumlar için güvenli bir gizli anahtar
    UPLOAD_FOLDER = 'uploads/' # Dosya yükleme klasörü
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Maksimum 16 MB dosya boyutu

    # Veritabanı Ayarları
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sartname_nokta' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600
    }

    # Gemini API Ayarları
    GEMINI_API_KEY = "AIzaSyDNIyyQRQvb-pE-dS0kz5ymGnTN_cz1lC0"
    GEMINI_MODEL_NAME = 'gemini-1.5-flash'

    # Hata Ayıklama Log Ayarları
    MAX_DEBUG_LOG_SIZE = 200

    # Kullanıcılar: Şifreler artık hash'li! (werkzeug.security.generate_password_hash ile üretildi)
    USERS = {
        "admin": "scrypt:32768:8:1$MylWA86BYgO83R6A$b7341215253e8030e40cf3431c2043dc488c207da1f30b2b70b6c8cbc7302d70e493d1a43c71dfeaa9328c5557a32b7ffb691d3dfb28156e19e8b3f783137b25",
        "kullanici": "scrypt:32768:8:1$XCHoPIBB2hzj207c$3c4a050762823a6b412d33ea11aaff312e18795b3b88cb48626dd4298e35adf68adc96b670c768faa4b48c2c9c818b380531bd6a32072281bd6741b0cf82f869"
    }
    # Not: Şifre kontrolü için check_password_hash fonksiyonu kullanılmalı.
