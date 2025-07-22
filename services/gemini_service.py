# services/gemini_service.py

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError, ClientError
import re
import json
from flask import current_app # Flask uygulamasının config'ine erişmek için
from utils import add_debug_message, format_categories_for_gemini, product_to_gemini_dict

class GeminiService:
    def __init__(self, app=None):
        self.model = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        api_key = app.config.get('GEMINI_API_KEY')
        model_name = app.config.get('GEMINI_MODEL_NAME')

        if api_key and api_key != "YOUR_GEMINI_API_KEY":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            add_debug_message(f"Gemini modeli '{model_name}' başarıyla yapılandırıldı.", level="INFO")
        else:
            self.model = None
            add_debug_message("UYARI: Gemini API anahtarı ayarlanmadı veya varsayılan değerde. Gemini servisleri kullanılamayacak.", level="WARNING")

    def _call_gemini(self, prompt, initial_history=None):
        if not self.model:
            add_debug_message("Gemini modeli yapılandırılmadığı için çağrı yapılamıyor.", level="ERROR")
            raise Exception("Gemini API anahtarı ayarlanmadı.")

        try:
            chat_session = self.model.start_chat(history=initial_history or [])
            response = chat_session.send_message(prompt)
            add_debug_message("Gemini'den yanıt alındı.", level="INFO")
            return response.text
        except GoogleAPICallError as e:
            add_debug_message(f"Gemini API çağrısı hatası: {str(e)}", level="CRITICAL")
            raise
        except ClientError as e:
            add_debug_message(f"Gemini istemci hatası: {str(e)}", level="CRITICAL")
            raise
        except Exception as e:
            add_debug_message(f"Beklenmeyen Gemini çağrısı hatası: {str(e)}", level="CRITICAL")
            raise

    def extract_categories_and_specs(self, file_raw_content, user_message_text, all_categories_data_tree):
        add_debug_message("Gemini Aşama 1 başlatılıyor: Kategori ve Anahtar Kelime Çıkarımı.", level="INFO")
        formatted_categories = format_categories_for_gemini(all_categories_data_tree)
        
        stage1_prompt = (
            "Sen bir şartname asistanısın ve yüklenen teknik şartname belgesini analiz ediyorsun. Amacın, belgenin içeriğine **EN UYGUN** ve **EN İLGİLİ** kategorileri belirlemek ve ayrıca şartnameden geçen **anahtar kelimeleri ve metinsel gereksinimleri** (ürünlerin 'OzelliklerTR' ve 'BilgiTR' alanlarında doğrudan geçebilecek ifadeler) çıkarmaktır.\n\n"
            f"Aşağıda, analiz etmen gereken teknik şartname belgesinin içeriği bulunmaktadır:\n\n"
            f"--- BELGE İÇERİĞİ BAŞLANGICI ---\n"
            f"{file_raw_content if file_raw_content else 'Belge içeriği sağlanmadı.'}\n"
            f"--- BELGE İÇERİĞİ SONU ---\n\n"
            f"{formatted_categories}\n\n"
            "Yukarıdaki teknik şartname belgesi içeriğini ve 'Mevcut Kategoriler Listesi'ni analiz et. Belgenin içeriğine **EN KESİN VE EN ÖZEL** kategori(ler)i belirle. "
            "Aşağıdaki kuralları **KESİNLİKLE** uygula:\n"
            "1.  **Öncelik: En Spesifik YAPRAK KATEGORİ**: Şartname içeriğinde, doğrudan ve kesin olarak belirtilen (örneğin '2MP Bullet IP Kamera', '10TB HDD') YAPRAK KATEGORİ'leri eşleştir. YALNIZCA o spesifik YAPRAK KATEGORİ'yi seç.\n"
            "2.  **Genel Üst Kategori Durumu**: Eğer şartname metninde bir ürün veya sistem genel bir üst kategori adı (örneğin 'Bullet IP Kameralar', 'NVR Kayıt Cihazları' veya 'HDD') ile anılıyorsa ve o üst kategorinin altında birden fazla YAPRAK KATEGORİ bulunuyorsa (örn. 'Bullet IP Kameralar' altında '2MP', '4MP', '5MP', '8MP', '12MP' gibi), ve şartnamede bu alt detay (örn. MP değeri, depolama boyutu) belirtilmiyorsa, o zaman **o üst kategorinin altındaki TÜM İLGİLİ YAPRAK KATEGORİ'leri eşleştirme listesine ekle.** Örneğin, 'Bullet IP Kameralar' denildiğinde ve MP değeri belirtilmediğinde, '2MP Bullet IP Kameralar', '4MP Bullet IP Kameralar', '5MP Bullet IP Kameralar', '8MP Bullet IP Kameralar' ve '12MP Bullet IP Kameralar' hepsini seç. Aynı şekilde 'HDD' denildiğinde, '10TB HDD', '18TB HDD' gibi tüm ilgili yaprak HDD kategorilerini seç.\n"
            "3.  **Alaka Düzeyi**: Belgenin içeriğiyle **ÇOK GÜÇLÜ BİR İLİŞKİSİ OLAN** kategorileri seçmeye odaklan. Minimum 5, maksimum 10 kategori seçmeye çalış.\n"
            "4.  **Anahtar Teknik Özellikleri ve İfadeleri Çıkarma**: Şartnamede belirtilen tüm kritik teknik özellikleri ve metinsel gereksinimleri (örn. '4MP', 'PoE', 'IP67', '10TB', '16 Kanal', 'Motorlu Zoom', 'X Marka', '2 yıl garanti') tam olarak ürünlerin 'OzelliklerTR' veya 'BilgiTR' metin alanlarında geçebilecek şekilde metinsel anahtar kelimeler/ifadeler olarak çıkar. Bu özellik ve ifadeleri 'extracted_specifications' nesnesi altında, ilgili anahtar (kamera, nvr, depolama, genel vb.) altında bir liste olarak döndür.\n"
            "5.  **Sayı Limiti**: Belge içeriğindeki ürün tanımları ve özelliklerine göre mantıklı sayıda, maksimum 5-7 tane, en fazla 10 tane en alakalı kategori ID'si döndürmeye çalış.\n\n"
            "Yanıtını SADECE aşağıdaki JSON formatında döndür. JSON objesi 'matched_categories' anahtarı altında bir dizi (array) ve 'extracted_specifications' anahtarı altında çıkarılan özelliklerin metinsel bir objesini içermelidir. Eğer hiç kategori veya özellik bulamazsan, ilgili anahtar için boş dizi veya obje döndür.\n\n"
            f"Örnek JSON Çıktısı Formatı:\n"
            f"```json\n"
            f"{{\n"
            f"   \"matched_categories\": [\n"
            f"     {{ \"id\": 116, \"name\": \"2MP Bullet IP Kameralar\" }},\n"
            f"     {{ \"id\": 117, \"name\": \"4MP Bullet IP Kameralar\" }},\n"
            f"     {{ \"id\": 469, \"name\": \"12MP Bullet IP Kameralar\" }},\n"
            f"     {{ \"id\": 498, \"name\": \"10TB HDD\" }},\n"
            f"     {{ \"id\": 509, \"name\": \"18TB HDD\" }}\n"
            f"   ],\n"
            f"   \"extracted_specifications\": {{\n"
            f"     \"kamera\": [\n"
            f"       \"4MP\",\n"
            f"       \"PoE\",\n"
            f"       \"IR 30 metre\",\n"
            f"       \"IP67\",\n"
            f"       \"Dış Ortam\",\n"
            f"       \"Motorlu Zoom\"\n"
            f"     ],\n"
            f"     \"depolama\": [\n"
            f"       \"10TB\",\n"
            f"       \"HDD\",\n"
            f"       \"CCTV\"\n"
            f"     ],\n"
            f"     \"nvr\": [\n"
            f"       \"16 Kanal\",\n"
            f"       \"4K Kayıt\",\n"
            f"       \"2 Disk Yuvası\"\n"
            f"     ],\n"
            f"     \"genel\": [\n"
            f"       \"X Marka\",\n"
            f"       \"2 Yıl Garanti\"\n"
            f"     ]\n"
            f"   }},\n"
            f"   \"analysis_summary\": \"Belge, MP değeri belirtilmeden 'Bullet IP Kameralar' ve TB değeri belirtilmeden 'HDD' gibi genel ifadeler içermektedir. Bu nedenle, ilgili tüm alt yaprak IP Kamera ve HDD kategorileri eşleştirilmiştir. Ayrıca, şartnameden kameranın 4MP olması, IP67 ve PoE gibi anahtar özellikler çıkarılmıştır.\"\n"
            f"}}\n"
            f"```\n"
        )
        add_debug_message(f"Gemini Aşama 1 Prompt hazırlandı (ilk 500 karakter: '{stage1_prompt[:500]}')", level="DEBUG")

        response_text = self._call_gemini(stage1_prompt, initial_history=[
            {'role': 'model', 'parts': ["Ben Nokta Şartname Asistanıyım. Şimdi belgeyi kategorilerle eşleştiriyorum ve anahtar özelliklerini çıkarıyorum."]}
        ])
        
        json_match = re.search(r'```json\n({.*?})\n```', response_text, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
            try:
                parsed_json = json.loads(json_string)
                add_debug_message("Aşama 1 yanıtı JSON olarak başarıyla ayrıştırıldı.", level="INFO")
                return parsed_json.get("matched_categories", []), parsed_json.get("extracted_specifications", {}), parsed_json.get("analysis_summary", "")
            except json.JSONDecodeError as e:
                add_debug_message(f"Aşama 1 JSON parse hatası: {e}. Yanıt: {json_string[:100]}...", level="ERROR")
                raise Exception(f"Kategori ve özellik eşleştirme yanıtı işlenemedi: {e}")
        else:
            add_debug_message("Gemini Aşama 1 yanıtında JSON bloğu bulunamadı.", level="WARNING")
            raise Exception(f"Kategori ve özellik eşleştirmesi için beklenen JSON formatı bulunamadı. Orijinal yanıt: {response_text}")

    def get_product_recommendations(self, file_raw_content, user_message_text, extracted_specifications, recommended_products_for_gemini_stage3, max_products=4):
        add_debug_message("Gemini Aşama 3 başlatılıyor: Nihai Ürün Seçimi ve Sunumu.", level="INFO")
        products_json_string = json.dumps(recommended_products_for_gemini_stage3, ensure_ascii=False, indent=2)
        add_debug_message(f"Aşama 3 için ürün JSON stringi hazırlandı (ilk 200 karakter: {products_json_string[:200]}...)", level="DEBUG")

        stage3_prompt = (
            "Sen bir şartname asistanısın. Kullanıcının teknik şartnamesini, şartnameden çıkarılan anahtar gereksinimleri ve bu gereksinimlere göre filtrelenmiş ürün listesini sana iletiyorum.\n\n"
            f"--- ORİJİNAL ŞARTNAME İÇERİĞİ ---\n"
            f"{file_raw_content if file_raw_content else user_message_text}\n" 
            f"--- /ORİJİNAL ŞARTNAME İÇERİĞİ ---\n\n"
            f"--- ŞARTNAMEDEN ÇIKARILAN ANAHTAR TEKNİK GEREKSİNİMLER (Kelime/İfade Tabanlı) ---\n"
            f"{json.dumps(extracted_specifications, ensure_ascii=False, indent=2) if extracted_specifications else 'Belirtilmedi.'}\n"
            f"--- /ŞARTNAMEDEN ÇIKARILAN ANAHTAR TEKNİK GEREKSİNİMLER ---\n\n"
            f"--- FİLTRELENMİŞ VE POTANSİYEL OLARAK UYGUN ÜRÜN LİSTESİ (Backend tarafından sağlandı) ---\n"
            f"{products_json_string}\n"
            f"--- /FİLTRELENMİŞ VE POTANSİYEL OLARAK UYGUN ÜRÜN LİSTESİ ---\n\n"
            "Yukarıdaki tüm bilgileri (orijinal şartname, çıkarılan gereksinimler ve filtrelenmiş ürün listesi) dikkatlice analiz et. "
            "Amacın, şartnamedeki tüm gereksinimleri (özellikle 'ŞARTNAMEDEN ÇIKARILAN ANAHTAR TEKNİK GEREKSİNİMLER' kısmındaki maddeler ve orijinal şartname içeriği) en iyi ve en kesin şekilde karşılayan ürünleri seçmektir.\n"
            "Seçtiğin her ürün için: ürün kodu, ürün adı, 'OzelliklerTR' ve 'BilgiTR' alanlarından alınan en ilgili 3-5 adet anahtar teknik özelliği (özellikle şartnamede aranan) belirt. Bu özellikleri madde madde listele. Ayrıca bu ürünü neden önerdiğine dair kısa ve açıklayıcı bir gerekçe (justification) sun.\n"
            "Her ürün için ayrıca, şartnameden çıkarılan gereksinimler arasında bu ürünün karşılamadığı (eksik kalan) gereksinimleri de 'unmet_requirements' başlığı altında madde madde listele. Eğer ürün tüm gereksinimleri karşılıyorsa 'Tüm gereksinimler karşılanıyor.' yaz.\n"
            f"Minimum 3, maksimum {max_products} ürün önerisi yap. Eğer 3'ten az uygun ürün bulursan, bulduğun kadarını öner.\n\n"
            "Yanıtını SADECE aşağıdaki JSON formatında döndür. 'recommended_products' anahtarı altında bir dizi olmalı, her dizi elemanı 'product_code', 'product_name', 'key_features' (array olarak), 'justification' (neden önerildiği) ve 'unmet_requirements' (array veya string) içermelidir.\n"
            "Ayrıca, 'recommendation_summary' anahtarı altında genel bir özet metin ekle.\n\n"
            f"Örnek JSON Çıktısı Formatı:\n"
            f"```json\n"
            f"{{\n"
            f"   \"recommended_products\": [\n"
            f"     {{\n"
            f"       \"product_code\": \"XYZ123\",\n"
            f"       \"product_name\": \"Bullet IP Kamera 4MP\",\n"
            f"       \"key_features\": [\"4MP çözünürlük\", \"30m IR Gece Görüşü\", \"IP67 Dış Ortam Koruması\", \"PoE Destekli\"],\n"
            f"       \"justification\": \"Şartnamede belirtilen 4MP çözünürlük ve IP67 dış ortam koruması gereksinimlerini tam olarak karşılamaktadır. Ayrıca PoE desteği kurulum kolaylığı sağlar.\",\n"
            f"       \"unmet_requirements\": \"Tüm gereksinimler karşılanıyor.\"\n"
            f"     }},\n"
            f"     {{\n"
            f"       \"product_code\": \"ABC456\",\n"
            f"       \"product_name\": \"NVR Kayıt Cihazı 16 Kanal 2HDD\",\n"
            f"       \"key_features\": [\"16 Kanal\", \"Min. 2 Disk Yuvası (10TB)\", \"4K Kayıt Desteği\"],\n"
            f"       \"justification\": \"Şartnamedeki 16 kanal kapasitesi ve depolama gereksinimlerini karşılamakta olup, mevcut disk kapasitesi şartnameye uygun depolama alanı sunar.\",\n"
            f"       \"unmet_requirements\": [\"RAID desteği yok\"]\n"
            f"     }}\n"
            f"   ],\n"
            f"   \"recommendation_summary\": \"Analiz edilen şartnameye göre belirlenen anahtar gereksinimler (çözünürlük, depolama kapasitesi, çevresel dayanıklılık vb.) doğrultusunda en uygun ürünler seçilmiştir. Önerilen ürünler, şartname maddelerini eksiksiz karşılamaktadır.\"\n"
            f"}}\n"
            f"```\n"
        )
        add_debug_message(f"Gemini Aşama 3 Prompt hazırlandı (ilk 500 karakter: '{stage3_prompt[:500]}')", level="DEBUG")

        response_text = self._call_gemini(stage3_prompt, initial_history=[
            {'role': 'model', 'parts': ["Şartnameye en uygun ürünleri seçiyorum."]}
        ])

        json_match = re.search(r'```json\n({.*?})\n```', response_text, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
            try:
                parsed_json = json.loads(json_string)
                add_debug_message("Aşama 3 yanıtı JSON olarak başarıyla ayrıştırıldı.", level="INFO")
                return parsed_json.get("recommended_products", []), parsed_json.get("recommendation_summary", "Ürün önerileri yapıldı.")
            except json.JSONDecodeError as e:
                add_debug_message(f"Aşama 3 JSON parse hatası: {e}. Yanıt: {json_string[:100]}...", level="ERROR")
                raise Exception(f"Ürün önerileri yanıtı işlenemedi: {e}")
        else:
            add_debug_message("Gemini Aşama 3 yanıtında JSON bloğu bulunamadı.", level="WARNING")
            raise Exception(f"Ürün önerileri için beklenen JSON formatı bulunamadı. Orijinal yanıt: {response_text}")

# GeminiService'i doğrudan burada başlatmak yerine, app.py'de init_app ile başlatacağız.
# gemini_service = GeminiService() # Bu satır kaldırıldı.
