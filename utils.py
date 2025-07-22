"""
Yardımcı fonksiyonlar: log, dosya işleme, ürün eşleştirme ve skorlamada kullanılır.
"""

from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, request, jsonify, current_app
from docx import Document
import os
import json
import re
from config import Config # Config sınıfını import ediyoruz
import difflib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from rapidfuzz import fuzz

# --- Hata Ayıklama Log Sistemi ---
_debug_log = [] # Bu liste uygulama çalıştığı sürece bellekte kalacak

def add_debug_message(message_text, level="INFO"):
    """Uygulama içi debug loguna zaman damgalı bir mesaj ekler. Log boyutu aşıldığında en eski logu siler."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message_text
    }
    _debug_log.append(log_entry)
    # Config'den MAX_DEBUG_LOG_SIZE değerini doğrudan al
    # Bu, uygulama bağlamı dışında da çalışmasını sağlar
    max_size = Config.MAX_DEBUG_LOG_SIZE
    if len(_debug_log) > max_size:
        _debug_log.pop(0) # Eski logları sil

def get_debug_log_entries():
    """Bellekteki debug log listesini döndürür."""
    return _debug_log

# --- / Hata Ayıklama Log Sistemi ---

# --- Oturum ve Yetkilendirme Dekoratoru ---
def login_required(f):
    """Kullanıcı oturumu yoksa login sayfasına yönlendirir."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            add_debug_message(f"Giriş yapılmamış kullanıcı, {request.path} adresine yönlendirildi.", level="WARNING")
            return redirect(url_for('auth.login')) # auth blueprint'ine yönlendiriyoruz
        return f(*args, **kwargs)
    return decorated_function

# --- Belge İşleme ---
def process_uploaded_file_general(file):
    """Hem .docx hem .txt dosyaları işler ve metin içeriğini döndürür. Geçersiz dosya tipinde None döner."""
    from werkzeug.utils import secure_filename
    add_debug_message(f"Dosya işleniyor: {file.filename}", level="INFO")
    filename = secure_filename(file.filename)
    ext = filename.lower().rsplit('.', 1)[-1]
    if ext not in ('docx', 'txt'):
        add_debug_message(f'Yüklenen dosya uzantısı geçersiz: {filename}', level="ERROR")
        return None
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file_raw_content = ""
    try:
        file.save(filepath)
        add_debug_message(f"Dosya geçici olarak kaydedildi: {filepath}", level="INFO")
        if ext == 'docx':
            from docx import Document
            document = Document(filepath)
            docx_text = [para.text for para in document.paragraphs]
            file_raw_content = "\n".join(docx_text)
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                file_raw_content = f.read()
        add_debug_message(f"{ext.upper()} içeriği başarıyla metne çevrildi.", level="INFO")
        return file_raw_content
    except Exception as e:
        add_debug_message(f'Dosya dönüştürme hatası: {str(e)}', level="ERROR")
        return None
    finally:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                add_debug_message(f"Geçici dosya silindi: {filepath}", level="INFO")
        except Exception as e:
            add_debug_message(f"Geçici dosya silinirken hata: {str(e)}", level="ERROR")

# --- Veritabanı ve Formatlama Fonksiyonları ---
def get_all_categories_with_hierarchy_sqlalchemy():
    """Veritabanından tüm kategorileri çeker ve bir sözlük yapısında döndürür."""
    # models.py'deki db nesnesini ve Kategori modelini import etmeliyiz
    from models import db, Kategori
    add_debug_message("Kategoriler veritabanından çekiliyor...", level="INFO")
    try:
        categories_list = Kategori.query.order_by(Kategori.parent_id.asc(), Kategori.KategoriAdiTr.asc()).all()
        categories_dict = {cat.id: {'id': cat.id, 'name': cat.KategoriAdiTr, 'parent_id': cat.parent_id, 'children': []} for cat in categories_list}
        
        # Hiyerarşik yapıyı oluştur
        for cat_id, cat_info in categories_dict.items():
            parent_id = cat_info['parent_id']
            if parent_id is not None and parent_id != 0 and parent_id in categories_dict:
                categories_dict[parent_id]['children'].append(cat_info)
        
        # Sadece üst seviye kategorileri al (parent_id'si olmayan veya 0 olanlar)
        top_level_categories = [cat_info for cat_id, cat_info in categories_dict.items() if cat_info['parent_id'] is None or cat_info['parent_id'] == 0]
        
        add_debug_message(f"Veritabanından {len(categories_list)} kategori çekildi ve hiyerarşi oluşturuldu.", level="INFO")
        return top_level_categories # Liste olarak döndür
    except Exception as e:
        add_debug_message(f"Kategoriler çekilirken hata oluştu: {str(e)}", level="ERROR")
        return []

def format_categories_for_gemini(categories):
    """
    Kategori listesini Gemini'nin anlayacağı metin formatına dönüştürür ve hiyerarşiyi vurgular.
    Bu versiyon, Gemini'ye bir kategoriye spesifik olarak değinilmediğinde alt kategorileri nasıl bulacağını belirtir.
    """
    add_debug_message("Kategoriler Gemini için formatlanıyor.", level="INFO")
    if not categories:
        return "Mevcut kategori bulunmamaktadır."

    category_lines = []

    def build_category_string(cat_node, level=0):
        indent = "   " * level # 3 boşluk ile girinti
        
        is_leaf = not bool(cat_node['children']) # Çocukları yoksa yaprak kategoridir

        status_text = "(YAPRAK KATEGORİ)" if is_leaf else ""
        category_lines.append(f"{indent}- ID: {cat_node['id']}, Adı: {cat_node['name']} {status_text}")
        
        # Çocukları alfabetik sıraya göre sırala
        sorted_children = sorted(cat_node['children'], key=lambda x: x['name'])
        for child in sorted_children:
            build_category_string(child, level + 1)

    # Top level categories (parent_id is None or 0)
    # Kök seviye kategorileri alfabetik sıraya göre sırala
    sorted_top_level = sorted(categories, key=lambda x: x['name'])

    for top_cat in sorted_top_level:
        build_category_string(top_cat)

    formatted_string = (
        "Mevcut Kategoriler Listesi (ID, Adları ve Hiyerarşik Yapı):\n"
        "Her kategori, eğer altında başka kategori yoksa 'YAPRAK KATEGORİ' olarak işaretlenmiştir. "
        "YAPRAK KATEGORİ'ler ürün eşleştirmede en öncelikli olanlardır.\n\n"
        "**ÇOK ÖNEMLİ KURALLAR:**\n"
        "1.  **Öncelik: En Spesifik YAPRAK KATEGORİ**: Şartname içeriğinde, doğrudan ve kesin olarak belirtilen (örneğin '2MP Bullet IP Kamera', '10TB HDD') YAPRAK KATEGORİ'leri eşleştir. YALNIZCA o spesifik YAPRAK KATEGORİ'yi seç.\n"
        "2.  **Genel Üst Kategori Durumu**: Eğer şartname metninde bir ürün veya sistem genel bir üst kategori adı (örneğin 'Bullet IP Kameralar', 'NVR Kayıt Cihazları' veya 'HDD') ile anılıyorsa ve o üst kategorinin altında birden fazla YAPRAK KATEGORİ bulunuyorsa (örn. 'Bullet IP Kameralar' altında '2MP', '4MP', '5MP', '8MP', '12MP' gibi), ve şartnamede bu alt detay (örn. MP değeri, depolama boyutu) belirtilmiyorsa, o zaman **o üst kategorinin altındaki TÜM İLGİLİ YAPRAK KATEGORİ'leri eşleştirme listesine ekle.** Örneğin, 'Bullet IP Kameralar' denildiğinde ve MP değeri belirtilmediğinde, '2MP Bullet IP Kameralar', '4MP Bullet IP Kameralar', '5MP Bullet IP Kameralar', '8MP Bullet IP Kameralar' ve '12MP Bullet IP Kameralar' hepsini seç. Aynı şekilde 'HDD' denildiğinde, '10TB HDD', '18TB HDD' gibi tüm ilgili yaprak HDD kategorilerini seç.\n"
        "3.  **Alaka Düzeyi**: Belgenin içeriğiyle **ÇOK GÜÇLÜ BİR İLİŞKİSİ OLAN** kategorileri seçmeye odaklan. Minimum 5, maksimum 10 kategori seçmeye çalış.\n\n"
    )
    formatted_string += "\n".join(category_lines)
    return formatted_string

def product_to_gemini_dict(product, matched_keywords=None):
    # Bu fonksiyon, ürün nesnesini Gemini'nin anlayacağı bir sözlüğe dönüştürür.
    # OzelliklerTR ve BilgiTR metin alanlarını doğrudan gönderiyoruz.
    return {
        'id': product.id,
        'UrunKodu': product.UrunKodu,
        'UrunAdiTR': product.UrunAdiTR,
        'OzelliklerTR': product.OzelliklerTR,
        'BilgiTR': product.BilgiTR,
        'KategoriID': product.KategoriID,
        'matched_keywords_by_backend': matched_keywords if matched_keywords is not None else [] # Backend'in eşleştirdiği kelimeler
    }

def filter_and_score_products_simple(products, extracted_specs_keywords):
    add_debug_message("Ürünler basit anahtar kelime eşleşmesi ile filtreleniyor ve skorlanıyor.", level="INFO")
    scored_products = []
    
    # Tüm anahtar kelimeleri tek bir listede topla ve küçük harfe çevir
    # extracted_specs_keywords Gemini'den gelen 'extracted_specifications' listesi olacak
    all_specs_keywords_lower = [kw.lower().strip() for kw_list in extracted_specs_keywords.values() for kw in kw_list]

    for product in products:
        score = 0
        product_text = (product.OzelliklerTR or "") + " " + (product.BilgiTR or "")
        product_text_lower = product_text.lower() # Küçük harfe çevirerek arama yap

        matched_keywords_for_product = []

        for keyword in all_specs_keywords_lower:
            # Basit 'içerir' kontrolü (Regex yok)
            if keyword in product_text_lower:
                score += 1
                matched_keywords_for_product.append(keyword)
            
        scored_products.append({
            'product': product,
            'score': score,
            'matched_keywords': matched_keywords_for_product
        })
    
    # En yüksek skora göre sırala
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    add_debug_message(f"Toplam {len(scored_products)} ürün skorlandı. En yüksek skor: {scored_products[0]['score'] if scored_products else 'N/A'}", level="INFO")
    return scored_products

def score_single_product(product, all_specs_keywords_lower):
    score = 0
    product_text = ((getattr(product, 'OzelliklerTR', '') or "") + " " + (getattr(product, 'BilgiTR', '') or "")).lower()
    matched_keywords_for_product = []
    for keyword in all_specs_keywords_lower:
        if not keyword:
            continue
        if keyword in product_text:
            score += 2
            matched_keywords_for_product.append(keyword)
        else:
            words = keyword.split()
            for w in words:
                if w and w in product_text:
                    score += 1
                    matched_keywords_for_product.append(w)
            for word in product_text.split():
                try:
                    similarity = fuzz.ratio(keyword, word) / 100.0
                    if similarity >= 0.8:
                        score += 1
                        matched_keywords_for_product.append(f"{keyword}~{word}")
                        break
                except Exception:
                    pass
    return {
        'product': product,
        'score': score,
        'matched_keywords': list(set(matched_keywords_for_product))
    }

def filter_and_score_products_advanced(products, extracted_specs_keywords):
    add_debug_message(f"Skorlama BAŞLADI (multiprocessing+rapidfuzz). Ürün sayısı: {len(products)}, Anahtar kelime sayısı: {sum(len(v) for v in extracted_specs_keywords.values())}", level="INFO")
    start_time = time.time()
    scored_products = []
    all_specs_keywords_lower = [kw.lower().strip() for kw_list in extracted_specs_keywords.values() for kw in kw_list]
    try:
        with ProcessPoolExecutor() as executor:
            future_to_product = {executor.submit(score_single_product, product, all_specs_keywords_lower): product for product in products}
            for idx, future in enumerate(as_completed(future_to_product)):
                if idx % 10 == 0:
                    add_debug_message(f"Multiprocessing skorlama: {idx}. ürün tamamlandı...", level="DEBUG")
                try:
                    scored_products.append(future.result())
                except Exception as e:
                    add_debug_message(f"Bir ürün skorlanırken hata: {str(e)}", level="ERROR")
        add_debug_message(f"Skorlama BİTTİ (multiprocessing). Toplam süre: {time.time() - start_time:.2f} sn, Toplam skorlanan ürün: {len(scored_products)}", level="INFO")
    except Exception as e:
        add_debug_message(f"Multiprocessing skorlama ana döngüsünde hata: {str(e)}", level="ERROR")
        raise
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    add_debug_message(f"Toplam {len(scored_products)} ürün skorlandı (multiprocessing). En yüksek skor: {scored_products[0]['score'] if scored_products else 'N/A'}", level="INFO")
    return scored_products
