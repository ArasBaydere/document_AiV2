# run.py

from waitress import serve
from app import app, db # app ve db nesnelerini app.py'den import ediyoruz
from models import Kategori, Urun, ChatSession, Message # Modelleri import ediyoruz (db.create_all için gerekli)
from utils import add_debug_message # Debug fonksiyonunu import ediyoruz

if __name__ == "__main__":
    print("Waitress sunucusu başlatılıyor...")
    print("Uygulama şurada çalışıyor: http://0.0.0.0:8000")
    
    # Uygulama bağlamı içinde veritabanı tablolarını oluşturma/kontrol etme
    with app.app_context():
        try:
            db.create_all() # Tüm tanımlı modeller için tabloları oluşturur
            print("Veritabanı tabloları kontrol edildi/oluşturuldu (Waitress başlatılırken).")
            add_debug_message("Veritabanı tabloları kontrol edildi/oluşturuldu (Waitress başlatılırken).", level="INFO")
        except Exception as e:
            print(f"HATA: Veritabanı tabloları oluşturulurken hata oluştu: {e}")
            add_debug_message(f"HATA: Veritabanı tabloları oluşturulurken hata oluştu: {str(e)}", level="CRITICAL")
            print("Lütfen MySQL veritabanınızın (sartname_nokta) mevcut olduğundan ve kullanıcı bilgilerinizin doğru olduğundan emin olun.")
            print("Uygulama yine de başlatılacak ancak veritabanı sorunları yaşanabilir.")

    serve(app, host='0.0.0.0', port=8000)
    # Host: '0.0.0.0' dış IP adreslerinden erişime izin verir.
    # Eğer sadece kendi bilgisayarınızda erişmek istiyorsanız '127.0.0.1' kullanabilirsiniz.
    # Port: Uygulamanın dinleyeceği port numarası. 8000 yaygın bir seçimdir.
