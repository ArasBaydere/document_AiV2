# config.py

import os
# from werkzeug.security import generate_password_hash # Şifre hash'leme kullanılmayacağı için kaldırıldı

class Config:
    # Flask Uygulama Ayarları
    SECRET_KEY = os.urandom(24) # Oturumlar için güvenli bir gizli anahtar
    UPLOAD_FOLDER = 'uploads/' # Dosya yükleme klasörü
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Maksimum 16 MB dosya boyutu

    # Veritabanı Ayarları
    # MySQL için bağlantı dizesi: kullanıcı:şifre@host:port/veritabanı_adı
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sartname_nokta' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Bellek kullanımını azaltmak için izlemeyi kapat
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True, # Bağlantıların aktif olup olmadığını kontrol eder
        "pool_recycle": 3600 # Bağlantıları her saatte bir yeniden kullanır (saniye cinsinden)
    }

    # Gemini API Ayarları
    # BURAYI KENDİ API ANAHTARINIZLA DEĞİŞTİRİN
    # Üretim ortamında bu anahtarı çevre değişkenlerinden okumanız şiddetle önerilir.
    GEMINI_API_KEY = "AIzaSyDNIyyQRQvb-pE-dS0kz5ymGnTN_cz1lC0"
    GEMINI_MODEL_NAME = 'gemini-1.5-flash'

    # Hata Ayıklama Log Ayarları
    MAX_DEBUG_LOG_SIZE = 200 # Log boyutunu artırdım

    # Basit kullanıcı veritabanı (üretim için daha gelişmiş bir sisteme ihtiyaç var)
    # DİKKAT: Şifreler düz metin olarak saklanmaktadır. Bu bir güvenlik riskidir.
    USERS = {
        "admin": "password123", # Düz metin şifre
        "kullanici": "sifre123" # Düz metin şifre
    }
