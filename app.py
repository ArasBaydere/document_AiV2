# app.py

from flask import Flask
import os
from config import Config # Yapılandırma sınıfını import ediyoruz
from models import db # db nesnesini import ediyoruz
from routes.auth import auth_bp # Auth Blueprint'i import ediyoruz
from routes.chat import chat_bp # Chat Blueprint'i import ediyoruz
from utils import add_debug_message # Debug fonksiyonunu import ediyoruz
from services.gemini_service import GeminiService # GeminiService sınıfını import ediyoruz
from models import Kategori, Urun, ChatSession, Message # db.create_all için gerekli modeller
# from werkzeug.security import generate_password_hash # Şifre hash'leme kullanılmayacağı için kaldırıldı

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) # Config sınıfından ayarları yükle

    # Yükleme klasörünü kontrol et ve oluştur (eğer yoksa)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        add_debug_message(f"'{app.config['UPLOAD_FOLDER']}' klasörü oluşturuldu.", level="INFO")

    # Veritabanını Flask uygulamasına bağla
    db.init_app(app)
    add_debug_message("Veritabanı Flask uygulamasına bağlandı.", level="INFO")

    # GeminiService'i başlat ve uygulamaya bağla
    # Bu, uygulamanın context'i içinde çalışacağı için güvenlidir.
    app.gemini_service = GeminiService()
    app.gemini_service.init_app(app)
    add_debug_message("GeminiService uygulamaya bağlandı.", level="INFO")

    # Blueprint'leri kaydet
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp) # chat blueprint'i içinde '/' rotası var
    add_debug_message("Blueprint'ler kaydedildi.", level="INFO")

    return app

# Uygulama oluşturma fonksiyonunu çağır
app = create_app()

# Bu blok sadece doğrudan 'app.py' çalıştırıldığında veritabanı tablolarını oluşturmak içindir.
# Waitress ile çalıştırıldığında 'run.py' bu kısmı atlayacaktır.
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all() # Tüm tanımlı modeller için tabloları oluşturur
            print("Veritabanı tabloları oluşturuldu veya zaten mevcut.")
            add_debug_message("Veritabanı tabloları kontrol edildi/oluşturuldu.", level="INFO")
        except Exception as e:
            print(f"Veritabanı tabloları oluşturulurken hata oluştu: {e}")
            add_debug_message(f"Veritabanı tabloları oluşturulurken hata: {str(e)}", level="CRITICAL")
            print("Lütfen MySQL veritabanınızın (sartname_nokta) mevcut olduğundan ve kullanıcı bilgilerinizin doğru olduğundan emin olun.")
            print("Gerekirse tabloları phpMyAdmin üzerinden manuel olarak oluşturun.")
        
        # --- Geçici Şifre Hash Oluşturma Bloğu ---
        # Bu bloğu, hash'leri aldıktan sonra SİLİNİZ veya YORUM SATIRI YAPINIZ!
        # from werkzeug.security import generate_password_hash # Bu import zaten üstte var
        # print("\n--- Yeni Şifre Hash'leri Oluşturuluyor (GEÇİCİ) ---")
        # temp_password_admin = "password123"
        # temp_password_kullanici = "sifre123"
        
        # hashed_admin_password = generate_password_hash(temp_password_admin)
        # hashed_kullanici_password = generate_password_hash(temp_password_kullanici)
        
        # print(f"Admin için '{temp_password_admin}' şifresinin hash'i: {hashed_admin_password}")
        # print(f"Kullanici için '{temp_password_kullanici}' şifresinin hash'i: {hashed_kullanici_password}")
        # print("--- Lütfen bu hash'leri config.py dosyanızdaki USERS sözlüğüne kopyalayın. ---")
        # print("--- Kopyaladıktan sonra bu geçici kod bloğunu app.py dosyasından SİLİNİZ! ---")
        # --- Geçici Şifre Hash Oluşturma Bloğu Sonu ---
