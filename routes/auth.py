# routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session
# from werkzeug.security import check_password_hash # Şifre hash'leme kullanılmayacağı için kaldırıldı
from utils import add_debug_message
from flask import current_app # Config'e erişmek için

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = current_app.config.get('USERS', {}) # Config'den kullanıcıları al
        
        # Şifreleri doğrudan karşılaştırıyoruz (hash'leme kullanılmadığı için)
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            add_debug_message(f"Kullanıcı '{username}' başarılı şekilde giriş yaptı.", level="INFO")
            return redirect(url_for('chat.index')) # chat blueprint'indeki index rotasına yönlendir
        else:
            error = 'Yanlış kullanıcı adı veya şifre.'
            add_debug_message(f"Giriş denemesi başarısız: Kullanıcı '{username}'.", level="WARNING")
            return render_template('login.html', error=error)
    add_debug_message("Giriş sayfası yüklendi.", level="INFO")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'Bilinmeyen Kullanıcı')
    add_debug_message(f"Kullanıcı '{username}' çıkış yaptı.", level="INFO")
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('auth.login')) # auth blueprint'indeki login rotasına yönlendir
