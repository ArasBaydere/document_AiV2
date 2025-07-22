import pytest
from utils import filter_and_score_products_advanced
from concurrent.futures import ProcessPoolExecutor, as_completed
from rapidfuzz import fuzz

class DummyProduct:
    def __init__(self, OzelliklerTR, BilgiTR):
        self.OzelliklerTR = OzelliklerTR
        self.BilgiTR = BilgiTR

def test_filter_and_score_products_advanced_basic():
    products = [
        DummyProduct("4MP, PoE, IP67", "Dış ortam, Motorlu Zoom"),
        DummyProduct("2MP, Analog, IP66", "İç ortam, Sabit Lens"),
        DummyProduct("8MP, PoE, IP67", "Dış ortam, Akıllı Analiz")
    ]
    extracted_specs = {"kamera": ["4MP", "PoE", "IP67"]}
    scored = filter_and_score_products_advanced(products, extracted_specs)
    assert scored[0]['product'].OzelliklerTR == "4MP, PoE, IP67"
    assert scored[0]['score'] > scored[1]['score']
    assert scored[0]['score'] > 0 

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
    import time
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