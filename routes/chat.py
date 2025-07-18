# routes/chat.py

from flask import Blueprint, render_template, request, jsonify, session, current_app
from models import db, ChatSession, Message, Urun # Modelleri import ediyoruz
from utils import add_debug_message, login_required, process_docx_file, get_all_categories_with_hierarchy_sqlalchemy, filter_and_score_products_simple, product_to_gemini_dict
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def index():
    add_debug_message("Ana sayfa (index.html) yüklendi.", level="INFO")
    return render_template('index.html')

@chat_bp.route('/api/chats', methods=['GET'])
@login_required
def get_chats():
    user_id = session['username']
    add_debug_message(f"'{user_id}' kullanıcısı için sohbet listesi isteniyor.", level="INFO")
    chats = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).all()
    add_debug_message(f"'{user_id}' kullanıcısı için {len(chats)} sohbet bulundu.", level="INFO")
    return jsonify([chat.to_dict() for chat in chats])

@chat_bp.route('/api/chat/new', methods=['POST'])
@login_required
def new_chat():
    user_id = session['username']
    data = request.get_json()
    title = data.get('title', f"Yeni Sohbet {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    new_session = ChatSession(user_id=user_id, title=title)
    db.session.add(new_session)
    db.session.commit()
    add_debug_message(f"'{user_id}' kullanıcısı için yeni sohbet oluşturuldu: ID={new_session.id}, Başlık='{title}'", level="INFO")
    
    welcome_message_content = "Notka Şartname Asistanı'na hoş geldiniz! Nasıl yardımcı olabilirim?"
    welcome_message = Message(session_id=new_session.id, sender='bot', content=welcome_message_content)
    db.session.add(welcome_message)
    db.session.commit()
    add_debug_message(f"Yeni sohbete hoş geldiniz mesajı eklendi: Session ID={new_session.id}", level="INFO")

    return jsonify(new_session.to_dict()), 201

@chat_bp.route('/api/chat/<int:chat_id>/messages', methods=['GET'])
@login_required
def get_chat_messages(chat_id):
    chat_session = ChatSession.query.filter_by(id=chat_id, user_id=session['username']).first()
    if not chat_session:
        add_debug_message(f"Sohbet ID={chat_id} bulunamadı veya yetkiniz yok.", level="ERROR")
        return jsonify({'error': 'Sohbet bulunamadı veya yetkiniz yok.'}), 404
    
    messages = [msg.to_dict() for msg in chat_session.messages]
    add_debug_message(f"Sohbet ID={chat_id} için {len(messages)} mesaj getirildi.", level="INFO")
    return jsonify({'chat_info': chat_session.to_dict(), 'messages': messages})

@chat_bp.route('/api/chat/<int:chat_id>/rename', methods=['POST'])
@login_required
def rename_chat(chat_id):
    chat_session = ChatSession.query.filter_by(id=chat_id, user_id=session['username']).first()
    if not chat_session:
        add_debug_message(f"Sohbet ID={chat_id} yeniden adlandırma için bulunamadı veya yetkiniz yok.", level="ERROR")
        return jsonify({'error': 'Sohbet bulunamadı veya yetkiniz yok.'}), 404
    
    data = request.get_json()
    new_title = data.get('title')
    if new_title:
        old_title = chat_session.title
        chat_session.title = new_title
        db.session.commit()
        add_debug_message(f"Sohbet ID={chat_id} başlığı '{old_title}' olarak '{new_title}' olarak değiştirildi.", level="INFO")
        return jsonify(chat_session.to_dict()), 200
    add_debug_message(f"Sohbet ID={chat_id} başlık boş olduğu için yeniden adlandırılamadı.", level="WARNING")
    return jsonify({'error': 'Başlık boş olamaz.'}), 400

@chat_bp.route('/api/chat/<int:chat_id>/delete', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    chat_session = ChatSession.query.filter_by(id=chat_id, user_id=session['username']).first()
    if not chat_session:
        add_debug_message(f"Sohbet ID={chat_id} silme için bulunamadı veya yetkiniz yok.", level="ERROR")
        return jsonify({'error': 'Sohbet bulunamadı veya yetkiniz yok.'}), 404
    
    try:
        db.session.delete(chat_session)
        db.session.commit()
        add_debug_message(f"Sohbet ID={chat_id} ve ilgili mesajları başarıyla silindi.", level="INFO")
        return jsonify({'success': True, 'message': 'Sohbet başarıyla silindi.'}), 200
    except Exception as e:
        db.session.rollback()
        add_debug_message(f"Sohbet ID={chat_id} silinirken hata oluştu: {str(e)}", level="ERROR")
        return jsonify({'error': f'Sohbet silinirken hata oluştu: {str(e)}'}), 500

@chat_bp.route('/api/debug_log', methods=['GET'])
@login_required
def get_debug_log_api(): # Rota adı çakışmasın diye değiştirdim
    from utils import get_debug_log_entries
    add_debug_message("Debug logları istendi.", level="DEBUG")
    return jsonify(get_debug_log_entries())

# --- Ana Chat Mesajı İşleme ---
@chat_bp.route('/chat', methods=['POST'])
@login_required
def handle_chat_message():
    user_message_text = request.form.get('message', '').strip()
    file = request.files.get('file')
    chat_id = request.form.get('chat_id')
    
    add_debug_message(f"Yeni sohbet isteği alındı. Chat ID: {chat_id}, Mesaj: '{user_message_text[:50]}...' Dosya: {file.filename if file else 'Yok'}", level="INFO")

    if not chat_id:
        add_debug_message('Sohbet ID\'si eksik.', level="ERROR")
        return jsonify({'success': False, 'message': 'Sohbet ID\'si eksik.'}), 400

    chat_session = ChatSession.query.filter_by(id=chat_id, user_id=session['username']).first()
    if not chat_session:
        add_debug_message(f'Sohbet ID={chat_id} bulunamadı veya yetkiniz yok.', level="ERROR")
        return jsonify({'success': False, 'message': 'Sohbet bulunamadı veya yetkiniz yok.'}), 404

    # Kullanıcının metin mesajını veritabanına kaydet
    if user_message_text:
        user_text_msg_obj = Message(session_id=chat_session.id, sender='user', content=user_message_text)
        db.session.add(user_text_msg_obj)
        add_debug_message(f"Kullanıcı metin mesajı veritabanına eklendi. Session ID: {chat_session.id}", level="INFO")
    
    file_raw_content = ""
    file_content_for_db = None

    # Eğer dosya yüklendiyse, içeriğini oku
    if file:
        file_raw_content = process_docx_file(file)
        if file_raw_content is None: # Hata oluştuysa
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Belge dönüştürme hatası veya geçersiz dosya tipi.'}), 500
        
        file_content_for_db = f"[ÖNEMLİ TEKNİK ŞARTNAME BELGE İÇERİĞİ: {file.filename}]\n{file_raw_content}"
    
    # Ne mesaj ne de dosya varsa hata döndür
    if not user_message_text and not file_raw_content:
        add_debug_message("Mesaj veya dosya içeriği boş.", level="WARNING")
        return jsonify({'success': False, 'message': 'Lütfen bir mesaj yazın veya dosya yükleyin.'}), 400

    # Dosya içeriğini de kullanıcı mesajı olarak kaydet
    if file_content_for_db:
        file_msg_obj = Message(session_id=chat_session.id, sender='user', content=file_content_for_db)
        db.session.add(file_msg_obj)
        add_debug_message("Dosya içeriği kullanıcı mesajı olarak veritabanına eklendi.", level="INFO")

    try:
        db.session.commit() # Tüm kullanıcı mesajlarını (metin ve dosya) kaydet
        add_debug_message(f"Kullanıcı metin ve dosya mesajları (varsa) veritabanına commit edildi.", level="INFO")
    except Exception as e:
        db.session.rollback()
        add_debug_message(f"Kullanıcı mesajları commit edilirken hata: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'message': 'Mesajlar kaydedilirken hata oluştu.'}), 500

    # --- Gemini API Çağrısı Aşama 1: Kategori ve Anahtar Kelime Çıkarımı ---
    bot_response_parts = []
    extracted_specifications = {} # Varsayılan olarak boş bir sözlük
    matched_categories_from_gemini = [] # Varsayılan olarak boş bir liste

    try:
        all_categories_data_tree = get_all_categories_with_hierarchy_sqlalchemy()
        # current_app.gemini_service ile servise erişiyoruz
        matched_categories_from_gemini, extracted_specifications, analysis_summary = \
            current_app.gemini_service.extract_categories_and_specs(file_raw_content, user_message_text, all_categories_data_tree)
        
        bot_response_parts.append("**Belge İçeriği ile Eşleşen Kategoriler:**")
        if not matched_categories_from_gemini:
            bot_response_parts.append("- Belge içeriğiyle eşleşen kategori bulunamadı.")
            add_debug_message("Aşama 1: Eşleşen kategori bulunamadı.", level="INFO")
        else:
            for cat in matched_categories_from_gemini:
                bot_response_parts.append(f"- ID: {cat.get('id', 'N/A')}, Adı: {cat.get('name', 'Bilinmiyor')}")
            add_debug_message(f"Gemini'den eşleşen kategori ID'leri: {[cat['id'] for cat in matched_categories_from_gemini if 'id' in cat]}", level="INFO")
        
        if extracted_specifications:
            bot_response_parts.append("\n**Şartnameden Çıkarılan Anahtar Özellikler (Kelime/İfade Tabanlı):**")
            for spec_type, specs_list in extracted_specifications.items():
                if specs_list:
                    bot_response_parts.append(f"- **{spec_type.capitalize()}:** {', '.join(specs_list)}")
            add_debug_message(f"Gemini'den çıkarılan özellikler (kelime/ifade): {extracted_specifications}", level="INFO")
        else:
            add_debug_message("Aşama 1: Çıkarılan özellik bulunamadı.", level="INFO")

        if analysis_summary:
            bot_response_parts.append(f"\n**Kategori ve Özellik Analiz Özeti:**\n{analysis_summary}")
            add_debug_message("Aşama 1 analiz özeti eklendi.", level="INFO")

    except Exception as e:
        error_msg = f"Aşama 1 (Kategori ve Özellik Eşleştirme) sırasında hata oluştu: {str(e)}"
        add_debug_message(error_msg, level="CRITICAL")
        bot_response_parts.append(f"\n**Hata:** {error_msg}")


    # --- Backend Aşama 2: Kategoriye Göre Ürünleri Çek ve Python'da Basit Filtrele/Skorla ---
    recommended_products_for_gemini_stage3 = [] # Aşama 3'e gönderilecek ürünler
    
    add_debug_message("Backend Aşama 2 başlatılıyor: Kategoriye Görün Ürün Çekme ve Filtreleme.", level="INFO")
    if matched_categories_from_gemini:
        matched_category_ids = [cat['id'] for cat in matched_categories_from_gemini if 'id' in cat]
        add_debug_message(f"Aşama 2: Filtreleme için kullanılacak kategori ID'leri: {matched_category_ids}", level="INFO")
        
        try:
            initial_products = Urun.query.filter(Urun.KategoriID.in_(matched_category_ids)).all()
            add_debug_message(f"Aşama 2: Kategori ID'lerine göre {len(initial_products)} ürün çekildi.", level="INFO")

            if initial_products:
                if extracted_specifications:
                    scored_products = filter_and_score_products_simple(initial_products, extracted_specifications)
                    products_to_send_to_gemini = scored_products[:10] 
                    add_debug_message(f"Aşama 2: Çıkarılan özelliklere göre {len(products_to_send_to_gemini)} ürün seçildi.", level="INFO")
                else: 
                     add_debug_message("Aşama 2: Çıkarılan özellikler boş olduğu için ürünler detaylı filtrelenemedi. İlk 10 kategori ürünü gönderilecek.", level="WARNING")
                     products_to_send_to_gemini = [{'product': p, 'score': 0, 'matched_keywords': []} for p in initial_products[:10]]
                    
                recommended_products_for_gemini_stage3 = [
                    product_to_gemini_dict(sp['product'], sp['matched_keywords']) 
                    for sp in products_to_send_to_gemini
                ]
                add_debug_message(f"Aşama 2: {len(recommended_products_for_gemini_stage3)} ürün Gemini'ye gönderilmek üzere hazırlandı.", level="INFO")

            else:
                add_debug_message("Aşama 2: Eşleşen kategoriler için hiç ürün bulunamadı.", level="INFO")
                bot_response_parts.append("\n**Uyarı:** Eşleşen kategoriler için veritabanımızda henüz bir ürün bulunmamaktadır.")
                    

        except Exception as e:
            error_msg_stage2 = f"Aşama 2 (Ürün Çekme ve Filtreleme) sırasında hata oluştu: {str(e)}"
            add_debug_message(error_msg_stage2, level="CRITICAL")
            bot_response_parts.append(f"\n**Hata:** {error_msg_stage2}")

    else:
        add_debug_message("Aşama 2: Kategori eşleşmesi olmadığı için ürün çekme atlandı.", level="INFO")
        bot_response_parts.append("\n**Bilgi:** Şartnameye uygun kategoriler bulunamadığı için ürün eşleştirme yapılamadı.")

    # --- Gemini API Çağrısı Aşama 3: Nihai Ürün Seçimi ve Sunumu ---
    if recommended_products_for_gemini_stage3:
        try:
            # current_app.gemini_service ile servise erişiyoruz
            recommended_products, recommendation_summary = \
                current_app.gemini_service.get_product_recommendations(file_raw_content, user_message_text, extracted_specifications, recommended_products_for_gemini_stage3)

            bot_response_parts.append("\n--- **ÖNERİLEN ÜRÜNLER** ---")
            if not recommended_products:
                bot_response_parts.append("Şartname gereksinimlerinize uygun spesifik ürün önerisi bulunamadı.")
                add_debug_message("Aşama 3: Spesifik ürün önerisi bulunamadı.", level="INFO")
            else:
                for prod in recommended_products:
                    product_code = prod.get('product_code', 'N/A')
                    product_name = prod.get('product_name', 'Bilinmiyor')
                    key_features = ", ".join(prod.get('key_features', []))
                    justification = prod.get('justification', '')
                    
                    bot_response_parts.append(f"\n**Ürün Kodu:** {product_code}")
                    bot_response_parts.append(f"**Ürün Adı:** {product_name}")
                    bot_response_parts.append(f"**Anahtar Özellikler:** {key_features}")
                    bot_response_parts.append(f"**Gerekçe:** {justification}")
                    bot_response_parts.append("---")
                add_debug_message(f"Aşama 3: {len(recommended_products)} ürün önerisi oluşturuldu.", level="INFO")
                
                if recommendation_summary:
                    bot_response_parts.append(f"\n**Öneri Özeti:**\n{recommendation_summary}")
                    add_debug_message("Aşama 3 öneri özeti eklendi.", level="INFO")

        except Exception as e:
            error_msg_stage3 = f"Aşama 3 (Nihai Ürün Seçimi) sırasında hata oluştu: {str(e)}"
            add_debug_message(error_msg_stage3, level="CRITICAL")
            bot_response_parts.append(f"\n**Hata:** {error_msg_stage3}")
    else:
        add_debug_message("Aşama 3: Filtrelenecek ürün bulunamadığı için ürün önerisi atlandı.", level="INFO")


    final_response_content = "\n".join(bot_response_parts)
    if not final_response_content.strip():
        final_response_content = "Üzgünüm, isteğiniz işlenirken bir sorun oluştu veya uygun eşleşmeler bulunamadı."
        add_debug_message("Nihai bot yanıtı boştu, varsayılan mesaj gönderildi.", level="WARNING")

    try:
        bot_msg_obj = Message(session_id=chat_session.id, sender='bot', content=final_response_content)
        db.session.add(bot_msg_obj)
        db.session.commit()
        add_debug_message(f"Bot yanıtı veritabanına kaydedildi. Session ID: {chat_session.id}", level="INFO")
    except Exception as e:
        add_debug_message(f"Bot yanıtı veritabanına kaydedilirken hata: {str(e)}", level="ERROR")
        return jsonify({'success': True, 'response': final_response_content, 'message': 'Bot yanıtı kaydedilirken sorun yaşandı ancak yanıt alındı.'}), 200

    add_debug_message(f"Frontende dönülecek yanıt (ilk 100 karakter): {final_response_content[:100]}...", level="INFO")
    return jsonify({'success': True, 'response': final_response_content})
