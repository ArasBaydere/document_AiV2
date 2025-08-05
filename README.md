📄 Nokta Şartname Asistanı (Document AI V2)
<div align="center">
<img src="https://img.shields.io/badge/version-2.0-blue.svg" alt="Version 2.0">
<img src="https://img.shields.io/badge/python-3.7%2B-green.svg" alt="Python 3.7+">
<img src="https://img.shields.io/badge/flask-2.2%2B-red.svg" alt="Flask 2.2+">
<img src="https://img.shields.io/badge/AI-Google_Gemini-purple.svg" alt="Google Gemini">
<img src="https://img.shields.io/badge/license-Proprietary-yellow.svg" alt="License">
</div>

<div align="center">
<h3>Yapay Zeka Destekli Teknik Şartname Analiz ve Ürün Eşleştirme Platformu</h3>
<p><i>Şartnameleri anlamlandıran, analiz eden ve en uygun ürünleri öneren yeni nesil AI çözümü</i></p>
</div>

📋 İçindekiler
Proje Tanıtımı

Temel Özellikler

Sistem Mimarisi

Kurulum

Çalıştırma ve Kullanım

Dizin Yapısı

Teknik Detaylar

Güvenlik Notları

Yapılacaklar ve Geliştirmeler

Sık Sorulan Sorular

İletişim & Destek

🚀 Proje Tanıtımı
Nokta Şartname Asistanı, teknik şartnameleri yapay zeka teknolojisi ile analiz ederek müşteri ihtiyaçlarını belirleyen ve en uygun ürün önerilerinde bulunan yenilikçi bir web uygulamasıdır. Google Gemini AI entegrasyonuyla donatılmış sistem, çeşitli formatlardaki (.docx, .pdf, .txt, veya görüntü dosyaları) şartname belgelerini ve metin girişlerini işleyerek, ilgili kategorileri ve teknik gereksinimleri tespit eder ve veritabanında bulunan en uygun ürünleri seçer.

🎯 Amaç ve Hedef Kitle

Satış Ekipleri: Müşteri şartnamelerine hızlı ve doğru ürün önerileri sunarak satış süreçlerini hızlandırmak.

Teknik Danışmanlar: Karmaşık teknik belgelerde gereksinim analizi yaparak doğru çözümlere ulaşmak.

Teklif Hazırlama Ekipleri: Şartname analizi ve ürün seçiminde zaman kazanarak verimlilik artışı sağlamak.

Ürün Yöneticileri: Pazar ihtiyaçlarını belirleyerek ürün geliştirme stratejileri oluşturmak.

🌟 Neden Nokta Şartname Asistanı?

Zaman Tasarrufu: Uzun şartnameleri manuel inceleme süresini %90'a kadar azaltır.

Doğruluk: Yapay zeka ile teknik gereksinimleri yüksek doğrulukla tespit eder.

Verimlilik: Uygun ürün seçimi ve teklif hazırlama sürecini otomatikleştirir.

Kullanım Kolaylığı: Sohbet tabanlı arayüz ile her seviyedeki kullanıcı için erişilebilirdir.

Öğrenme Kabiliyeti: Her kullanımda daha iyi hale gelen yapay zeka algoritması.

💎 Temel Özellikler
🔐 Kullanıcı Yönetimi
Oturum Tabanlı Kimlik Doğrulama: Güvenli erişim kontrolü sağlar.

Kullanıcı Rolleri: Yönetici ve standart kullanıcı yetkilendirmesi sunar.

Çoklu Oturum Desteği: Aynı hesapla farklı cihazlardan erişim imkanı tanır.

Özelleştirilmiş Deneyim: Kullanıcıya özel sohbet geçmişi ve tercihler.

💬 Sohbet Tabanlı Arayüz
Sohbet Geçmişi: Geçmiş şartname analizlerine kolay erişim sağlar.

Sohbet Yönetimi: Konuşmaları yeniden adlandırma ve silme özellikleri sunar.

Gerçek Zamanlı İşleme: Anında yanıt ve akıcı kullanıcı deneyimi sağlar.

Modern Bildirim Sistemi: İşlem durumunu anlık olarak kullanıcıya bildirir.

📄 Belge ve Metin Analizi
Çoklu Format Desteği: DOCX, PDF, TXT ve görüntü dosyaları (.jpg, .png).

Uzun Metin Girişi: Direkt yapıştırma ile şartname analizi yapılabilir.

Otomatik Kategori Tespiti: Hiyerarşik kategori yapısında en uygun eşleşme bulunur.

Teknik Gereksinim Çıkarımı: Anahtar teknik özellikler ve spesifikasyonlar belirlenir.

OCR Entegrasyonu: Görüntü dosyalarından metin çıkarma özelliği.

🤖 Yapay Zeka Motoru
Google Gemini Entegrasyonu: Gelişmiş doğal dil işleme yetenekleri.

Çok Aşamalı İşlem: Kategori tespiti, özellik çıkarma, ürün eşleştirme aşamalarını içerir.

Özelleştirilmiş Prompt Mühendisliği: Teknik şartnamelere özel optimizasyon yapılmıştır.

Bağlam Duyarlı Analiz: Teknik terminolojiyi ve bağlamı doğru şekilde anlamlandırır.

🔍 Ürün Eşleştirme
Detaylı Gerekçelendirme: Her önerilen ürün için uyum ve gerekçe açıklaması sunar.

Karşılanmayan Gereksinimler: Eksik özelliklerin şeffaf bildirimi yapılır.

Alternatif Ürünler: Farklı seçeneklerin karşılaştırmalı sunumu sağlanır.

Özellik Bazlı Karşılaştırma: Şartname gereksinimleri ile ürün özellikleri arasında eşleştirme.

🐞 Hata Ayıklama ve İzleme
Dahili Debug Paneli: Gerçek zamanlı log izleme imkanı.

Ayrıntılı Log Kaydı: İşlem adımlarının detaylı kaydı tutulur.

Hata Yönetimi: Sorunların etkili tespiti ve çözümü sağlanır.

Performans Metrikleri: İşlem süreleri ve kaynak kullanımı izlenir.

🏗 Sistem Mimarisi
Backend (Sunucu Tarafı)
Web Framework: Flask 2.2+ (Python 3.7+ tabanlı)

ORM: SQLAlchemy 2.5+ (Veritabanı soyutlama katmanı)

Veritabanı: MySQL/MariaDB (varsayılan, değiştirilebilir)

AI Entegrasyonu: Google Gemini API (v0.3+)

Belge İşleme:

python-docx: DOCX dosyalarını okuma

pdfplumber: PDF metin çıkarımı

pdf2image: PDF görselleştirme

pytesseract: OCR işlemleri

Frontend (İstemci Tarafı)
Temel Teknolojiler: HTML5, CSS3, Vanilla JavaScript

Template Engine: Jinja2 (Flask entegrasyonlu)

Kullanıcı Arayüzü:

Tek sayfalı uygulama mantığı

Sohbet tabanlı arayüz

Responsive tasarım

Bildirim Sistemi: SweetAlert2 entegrasyonu

Dinamik Etkileşim: AJAX ve Fetch API

Veri Akışı Diyagramı
Kullanıcı Dosyası → Format Tespiti → Ön İşleme → Metin Çıkarımı → Metin Temizleme → AI Analizi
Dağıtım (Deployment) Mimarisi
Geliştirme Ortamı: Flask dahili sunucusu (Debug açık).

Üretim Ortamı: Waitress WSGI sunucusu (Yüksek performans).

Güvenlik: HTTPS desteği, oturum yönetimi, giriş kontrolü.

Ölçeklenebilirlik: Çoklu işlem (multi-process) desteği.

⚙️ Kurulum
Ön Gereksinimler
Python 3.7 veya üzeri

MySQL/MariaDB veya uyumlu bir veritabanı sistemi

pip (Python paket yöneticisi)

Google Gemini API anahtarı

Tesseract OCR ve Poppler (sistem bağımlılıkları)

Adım 1: Depoyu Klonlama
Bash

git clone https://github.com/ArasBaydere/document_AiV2.git
cd document_AiV2
Adım 2: Sanal Ortam Oluşturma (İsteğe Bağlı, Önerilen)
Bash

python -m venv venv

# Windows için
venv\Scripts\activate

# Linux/Mac için
source venv/bin/activate
Adım 3: Bağımlılıkları Yükleme
Bash

pip install -r requirements.txt
Adım 4: Sistem Bağımlılıklarını Yükleme
Windows için:
Tesseract OCR ve Poppler'ı sisteminize yükleyin ve config.py dosyasında yollarını belirtin.

Linux için:

Bash

sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
macOS için:

Bash

brew install tesseract poppler
Adım 5: Yapılandırma
config.py dosyasını açarak gerekli ayarlamaları yapın:

Python

# Veritabanı bağlantı bilgileri
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://KULLANICI:ŞIFRE@localhost:3306/VERITABANI_ADI'

# Google Gemini API anahtarı
GEMINI_API_KEY = 'GEMINI_API_ANAHTARINIZ'

# Diğer ayarlar
SECRET_KEY = 'güvenli_gizli_anahtar'
UPLOAD_FOLDER = 'uploads'

# OCR ve PDF işleme için yollar (Windows için)
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Path\To\Poppler\bin'
Adım 6: Veritabanı Oluşturma
İlk çalıştırmada tablolar otomatik oluşturulacaktır, ancak veritabanını önceden oluşturmanız gerekir:

SQL

CREATE DATABASE IF NOT EXISTS VERITABANI_ADI CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
🚦 Çalıştırma ve Kullanım
Geliştirme Ortamında Çalıştırma
Bash

python app.py
Üretim Ortamında Çalıştırma (Waitress ile)
Bash

python run.py
Erişim
Uygulama varsayılan olarak şu adreslerde çalışır:

Geliştirme: http://127.0.0.1:5000

Üretim: http://127.0.0.1:8000

📱 Kullanıcı Rehberi
Giriş ve Kimlik Doğrulama
/login sayfasına erişerek kullanıcı adı ve şifrenizle giriş yapın.
Demo kullanıcı bilgileri:

Kullanıcı: admin, Şifre: password123

Kullanıcı: kullanici, Şifre: sifre123

Şartname Analizi
Ana sayfada "Yeni Sohbet" butonuna tıklayın.
Aşağıdaki yöntemlerden biriyle şartnameyi yükleyin:

Dosya Yükleme: Dosya simgesine tıklayarak DOCX, PDF, TXT veya görüntü dosyası seçin.

Metin Yapıştırma: Şartname metnini mesaj kutusuna yapıştırın ve gönderin.

Görüntü Yükleme: JPG, PNG formatındaki şartname görsellerini yükleyin.

Sistem şartnameyi analiz edecek ve yapay zeka modelini kullanarak uygun ürün önerilerini sunacaktır.

Sohbet Yönetimi
Yeniden Adlandırma: Sohbet başlığı yanındaki düzenleme simgesine tıklayın.

Silme: Çöp kutusu simgesine tıklayarak sohbeti silin.

Geçmiş Görüntüleme: Sol paneldeki sohbet listesinden önceki analizlere erişin.

Mesaj Görüntüleme: Ana panelde kronolojik sırayla mesajları görüntüleyin.

Hata Ayıklama Paneli
Panel Erişimi: Sağ üstteki debug simgesine tıklayarak açın.

Log İnceleme: Sistemdeki işlem adımlarını ve hataları gerçek zamanlı izleyin.

Log Yenileme: Yenileme simgesini kullanarak güncel logları alın.

Panel Kapatma: X simgesine tıklayarak veya tekrar debug simgesine tıklayarak kapatın.

📁 Dizin Yapısı
document_AiV2/
│
├── app.py                   # Ana uygulama girişi
├── run.py                   # Üretim sunucusu (Waitress) yapılandırması
├── config.py                # Uygulama yapılandırma ayarları
├── requirements.txt         # Bağımlılık listesi
│
├── models/                  # Veritabanı modelleri
│   ├── __init__.py
│   ├── category.py          # Kategori modeli (hiyerarşik yapı)
│   ├── product.py           # Ürün modeli (kategori ilişkileri)
│   ├── chat_session.py      # Sohbet oturumu modeli
│   └── message.py           # Mesaj modeli
│
├── services/                # İş mantığı servisleri
│   ├── __init__.py
│   ├── gemini_service.py    # Google Gemini AI entegrasyonu ve prompt yönetimi
│   ├── chat_service.py      # Sohbet yönetimi servisi
│   ├── file_service.py      # Dosya işleme ve dönüştürme servisi
│   └── product_service.py   # Ürün eşleştirme ve filtreleme servisi
│
├── routes/                  # API ve sayfa yönlendirmeleri
│   ├── __init__.py
│   ├── auth.py              # Kimlik doğrulama rotaları (giriş/çıkış)
│   ├── api.py               # REST API rotaları
│   └── pages.py             # Sayfa görünüm rotaları
│
├── templates/               # Jinja2 şablonları
│   ├── index.html           # Ana sayfa şablonu (sohbet arayüzü)
│   └── login.html           # Giriş sayfası şablonu
│
├── static/                  # Statik dosyalar
│   ├── css/
│   │   └── style.css        # Ana stil dosyası
│   ├── js/
│   │   └── main.js          # Frontend mantığı (sohbet, AJAX, UI)
│   └── img/                 # Resimler ve simgeler
│
├── utils/                   # Yardımcı araçlar
│   ├── __init__.py
│   ├── logger.py            # Loglama araçları
│   ├── auth_utils.py        # Kimlik doğrulama yardımcıları
│   └── file_utils.py        # Dosya işleme yardımcıları
│
└── uploads/                 # Yüklenen dosyalar (çalışma zamanında oluşturulur)
🔧 Teknik Detaylar
Veritabanı Modelleri
Category: Hiyerarşik yapı (parent_id ile self-referential ilişki). Kategori adı, açıklaması ve alt/üst kategori ilişkilerini barındırır. Recursive sorgular için optimize edilmiştir.

Product: Kategorilere many-to-many ilişki. Ürün kodu, adı, özellikleri ve bilgileri saklar. JSON formatında ek özellikler tutabilir.

ChatSession: Kullanıcı oturumları ve sohbet başlıklarını içerir. Soft-delete özelliği mevcuttur.

Message: Sohbet mesajlarını (kullanıcı ve bot) saklar. Mesaj içeriği, gönderen, zaman damgası ve sohbet oturumuna ilişkin foreign key'i bulunur.

Yapay Zeka İş Akışı
Kategori ve Özellik Çıkarma: Şartname metni Gemini API ile işlenir ve eşleşen kategoriler ile teknik özellikler JSON formatında çıkarılır.

Ürün Filtreleme: Tespit edilen kategoriler ve özellikler kullanılarak veritabanında potansiyel ürünler sorgulanır ve filtrelenir.

Ürün Değerlendirme ve Öneri: Filtrelenen ürünler ve şartname gereksinimleri Gemini API ile karşılaştırılarak en uygun ürünler, gerekçeleri ve karşılanamayan gereksinimler belirlenir.

File Processing Pipeline
Kullanıcı Dosyası → Format Tespiti → Ön İşleme → Metin Çıkarımı → Metin Temizleme → AI Analizi
DOCX İşleme: python-docx ile metin çıkarımı, stil ve tablo desteği.

PDF İşleme: pdfplumber ile metin çıkarımı, gerektiğinde OCR kullanımı.

Görüntü İşleme: pdf2image ve pytesseract ile OCR işlemi.

🔒 Güvenlik Notları
⚠️ Önemli Uyarı: Mevcut sürüm bir demo/prototip olarak tasarlanmıştır ve aşağıdaki güvenlik eksikliklerini içermektedir:

Şifreler düz metin olarak saklanmaktadır.

Gizli anahtarlar çevre değişkenleri yerine config.py dosyasında bulunmaktadır.

Gelişmiş güvenlik önlemleri (2FA, oturum süreleri vb.) eksiktir.

Giriş koruması (rate limiting, brute force koruması) yoktur.

Üretim Ortamı İçin Önerilen Güvenlik İyileştirmeleri
Şifre Güvenliği: werkzeug.security modülünü kullanarak şifreleri hash'leyin.

Python

from werkzeug.security import generate_password_hash, check_password_hash

# Şifre hash'leme
password_hash = generate_password_hash('kullanıcı_şifresi')

# Şifre doğrulama
is_valid = check_password_hash(password_hash, 'girilen_şifre')
Çevre Değişkenleri: Gizli anahtarları .env dosyasıyla yönetin.

Python

from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
HTTPS Yapılandırması: waitress ile SSL sertifikalarını kullanarak HTTPS desteği ekleyin.

Python

from waitress import serve
import ssl

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

serve(app, host='0.0.0.0', port=8443, ssl_context=ssl_context)
CSRF Koruması: Flask-WTF ile CSRF korumasını etkinleştirin.

Python

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
📈 Yapılacaklar ve Geliştirmeler
[ ] Güvenlik İyileştirmeleri

[ ] Şifre hashleme implementasyonu

[ ] API anahtarlarının çevre değişkenlerine taşınması

[ ] CSRF korumasının eklenmesi

[ ] Rate limiting uygulanması

[ ] Kullanıcı Yönetimi

[ ] Şifremi unuttum işlevi

[ ] Kullanıcı profil sayfası

[ ] Yeni kullanıcı kaydı

[ ] Dosya İşleme İyileştirmeleri

[ ] Excel (.xlsx) desteği

[ ] ZIP arşiv desteği

[ ] Sürükle-bırak dosya yükleme geliştirmeleri

[ ] Yapay Zeka İyileştirmeleri

[ ] Önceki şartname analizlerinden öğrenme

[ ] Çoklu dil desteği (İngilizce, Almanca)

[ ] Arayüz Geliştirmeleri

[ ] Mobil uyumlu tasarım

[ ] Tema seçenekleri (koyu/açık mod)

[ ] WebSocket entegrasyonu ile gerçek zamanlı mesajlaşma

[ ] Entegrasyon Modülleri

[ ] CRM sistemleri entegrasyonu

[ ] ERP sistemleri entegrasyonu

[ ] Raporlama ve Analiz

[ ] Şartname istatistikleri ve trend analizi

[ ] Ürün önerileri başarı metrikleri

❓ Sık Sorulan Sorular
S: Şartname analizi ne kadar sürede tamamlanır?
C: Şartname uzunluğu ve karmaşıklığına bağlı olarak 15-60 saniye arasında değişebilir. Görüntü tabanlı analizler OCR işlemi nedeniyle daha uzun sürebilir.

S: Hangi dosya formatları destekleniyor?
C: Şu anda DOCX, PDF, TXT formatındaki belgeler ve JPG, PNG formatındaki görüntüler desteklenmektedir.

S: Sistem veritabanına bağlanamazsa ne olur?
C: Sistem veritabanı bağlantı sorunlarını otomatik olarak tespit eder ve kullanıcıya bildirir. Hata ayıklama panelinde detaylı log bilgileri görüntülenebilir.

S: Veritabanına yeni ürünler nasıl eklenir?
C: Veritabanına yeni ürünler ve kategoriler manuel olarak veya toplu içe aktarma ile eklenebilir. Şu anda bir yönetim arayüzü bulunmamaktadır, SQL sorguları kullanılmalıdır.

📞 İletişim & Destek
Bu proje ile ilgili sorularınız veya özel geliştirme talepleriniz için proje sahibi ile iletişime geçin:

E-posta: bilgi@noktaai.com

Web: www.noktaai.com

Telefon: +90 555 123 4567

Hata Raporları ve Öneriler
Hataları veya geliştirme önerilerini repo üzerinde Issue açarak veya e-posta ile iletebilirsiniz.

<div align="center">
<p>© 2025 Nokta AI Teknolojileri. Tüm hakları saklıdır.</p>
<p>Bu dokümantasyon ve proje özel lisans altındadır. İzinsiz kullanımı ve dağıtımı yasaktır.</p>
</div>
