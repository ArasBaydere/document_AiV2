document.addEventListener('DOMContentLoaded', () => {
    const chatList = document.getElementById('chatList');
    const newChatBtn = document.getElementById('newChatBtn');
    const chatMessages = document.getElementById('chatMessages');
    const currentChatTitle = document.getElementById('currentChatTitle');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const attachFileBtn = document.getElementById('attachFileBtn');
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const messageInputArea = document.getElementById('messageInputArea');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const renameChatBtn = document.getElementById('renameChatBtn');
    const deleteChatBtn = document.getElementById('deleteChatBtn');

    // Debug Panel Elementleri
    const debugPanel = document.getElementById('debugPanel');
    const toggleDebugBtn = document.getElementById('toggleDebugBtn');
    const closeDebugBtn = document.getElementById('closeDebugBtn');
    const refreshDebugBtn = document.getElementById('refreshDebugBtn');
    const debugLogContent = document.getElementById('debugLogContent');
    const appContainer = document.querySelector('.app-container'); // Ana kapsayıcı

    let currentChatId = null; // Aktif sohbetin ID'si
    let debugPanelOpen = false; // Debug panelinin açık/kapalı durumu

    // --- Yardımcı Fonksiyonlar ---

    // Markdown içeriğini HTML'e dönüştür (basit bir yaklaşım)
    function renderMarkdown(markdown) {
        // Not: Bu sadece basit bir Markdown parser'dır.
        // Daha karmaşık Markdown için marked.js gibi bir kütüphane kullanmanız önerilir.

        let html = markdown;

        // Başlıklar (### Başlık, ## Başlık, # Başlık)
        html = html.replace(/^### (.*$)/gmi, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gmi, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gmi, '<h1>$1</h1>');

        // Kalın Metin (**metin**)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Madde İşaretli Listeler (* Madde) - Çok temel
        // Her satırı bir liste öğesi olarak ele alıp sonra ul içine sarar
        const listItems = html.split('\n').map(line => {
            if (line.startsWith('* ')) {
                return `<li>${line.substring(2).trim()}</li>`;
            }
            return line;
        });
        html = listItems.join('\n'); // Tekrar birleştir

        // Ardışık li etiketlerini ul içine sar (çok basit bir kontrol)
        let inList = false;
        html = html.split('\n').map(line => {
            if (line.startsWith('<li>') && !inList) {
                inList = true;
                return `<ul>${line}`;
            } else if (!line.startsWith('<li>') && inList) {
                inList = false;
                return `</ul>${line}`;
            }
            return line;
        }).join('\n');
        if (inList) { // Eğer liste sonlanmadan metin biterse
            html += '</ul>';
        }


        // Kod blokları (```json...```, ```...```) ve inline kod (`kod`)
        html = html.replace(/```json\n([\s\S]*?)\n```/g, (match, code) => {
            return `<pre><code class="language-json">${escapeHtml(code)}</code></pre>`;
        });
        html = html.replace(/```([\s\S]*?)\n([\s\S]*?)\n```/g, (match, lang, code) => {
            return `<pre><code class="language-${escapeHtml(lang.trim())}">${escapeHtml(code)}</code></pre>`;
        });
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Linkler [metin](url)
        html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');

        // Yeni satır karakterlerini <br> ile değiştir (önemli: kod bloklarından sonra yapılmalı)
        html = html.replace(/\n/g, '<br>');


        return `<div class="markdown-content">${html}</div>`;
    }

    // HTML özel karakterlerini kaçış karakterlerine dönüştürür
    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Yükleniyor göstergesini ayarlar
    function showLoading(show) {
        console.log(`showLoading çağrıldı: ${show ? 'true' : 'false'}`); // Hata ayıklama için eklendi
        if (show) {
            loadingIndicator.classList.remove('hidden');
            messageInputArea.classList.add('disabled'); // .disabled sınıfı opacity ve pointer-events'ı ayarlar
            sendMessageBtn.disabled = true;
            attachFileBtn.disabled = true;
            messageInput.disabled = true;
        } else {
            loadingIndicator.classList.add('hidden');
            messageInputArea.classList.remove('disabled');
            sendMessageBtn.disabled = false;
            attachFileBtn.disabled = false;
            messageInput.disabled = false;
        }
    }

    // Sohbete yeni mesaj ekler
    function addMessageToChat(sender, content, timestamp) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`; // user veya bot sınıfı
        
        const messageBubble = document.createElement('div');
        messageBubble.className = `message-bubble`;
        
        // Mesaj içeriğini markdown olarak render et
        messageBubble.innerHTML = renderMarkdown(content);

        const timestampSpan = document.createElement('span');
        timestampSpan.className = `message-timestamp`;
        timestampSpan.textContent = new Date(timestamp).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

        messageBubble.appendChild(timestampSpan);
        messageDiv.appendChild(messageBubble);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // En alta kaydır
    }

    // Belirli bir sohbetin mesajlarını gösterir
    function displayChatMessages(messages) {
        chatMessages.innerHTML = ''; // Önceki mesajları temizle
        if (messages.length === 0) {
            chatMessages.innerHTML = `
                <div class="empty-chat-message">
                    <p>Henüz mesaj yok.</p>
                    <p>Şartname dosyanızı yükleyerek veya metin girerek başlayabilirsiniz.</p>
                </div>
            `;
            return;
        }
        messages.forEach(msg => {
            addMessageToChat(msg.sender, msg.content, msg.timestamp);
        });
    }

    // Sohbet listesini backend'den yükler
    async function loadChatList() {
        console.log("Sohbet listesi yükleniyor..."); // Hata ayıklama için eklendi
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) {
                if (response.status === 401) { // Unauthorized
                    window.location.href = '/login'; // Giriş sayfasına yönlendir
                    return;
                }
                throw new Error('Sohbet listesi alınamadı.');
            }
            const chats = await response.json();
            chatList.innerHTML = ''; // Listeyi temizle
            if (chats.length === 0) {
                chatList.innerHTML = '<div class="loading-message">Henüz sohbet yok.</div>';
                return;
            }

            chats.forEach(chat => {
                const chatItem = document.createElement('div');
                chatItem.id = `chat-${chat.id}`;
                chatItem.className = `chat-list-item ${currentChatId === chat.id ? 'selected' : ''}`;
                chatItem.innerHTML = `
                    <div>
                        <p>${chat.title}</p>
                        <small>${new Date(chat.created_at).toLocaleDateString('tr-TR', { year: 'numeric', month: 'short', day: 'numeric' })}</small>
                    </div>
                `;
                chatItem.addEventListener('click', () => selectChat(chat.id));
                chatList.appendChild(chatItem);
            });
        } catch (error) {
            console.error('Sohbet listesi yüklenirken hata:', error);
            chatList.innerHTML = `<div class="loading-message error-message">Sohbetler yüklenemedi: ${error.message}</div>`;
        }
    }

    // Bir sohbeti seçer ve mesajlarını yükler
    async function selectChat(chatId) {
        if (currentChatId === chatId) return; // Aynı sohbete tekrar tıklanırsa
        
        // Önceki seçili sohbeti kaldır
        if (currentChatId) {
            const prevSelected = document.getElementById(`chat-${currentChatId}`);
            if (prevSelected) {
                prevSelected.classList.remove('selected');
            }
        }

        currentChatId = chatId;
        // Yeni seçili sohbeti işaretle
        const newSelected = document.getElementById(`chat-${currentChatId}`);
        if (newSelected) {
            newSelected.classList.add('selected');
        }

        showLoading(true); // Mesajlar yüklenirken yükleniyor göster
        messageInputArea.classList.remove('disabled'); // Girişi etkinleştir
        renameChatBtn.style.display = 'inline-flex';
        deleteChatBtn.style.display = 'inline-flex';

        try {
            console.log(`Sohbet ID ${chatId} mesajları çekiliyor...`); // Hata ayıklama için eklendi
            const response = await fetch(`/api/chat/${chatId}/messages`);
            if (!response.ok) {
                if (response.status === 401) { window.location.href = '/login'; return; }
                throw new Error('Sohbet mesajları alınamadı.');
            }
            const data = await response.json();
            currentChatTitle.textContent = data.chat_info.title;
            displayChatMessages(data.messages);
            console.log(`Sohbet ID ${chatId} mesajları başarıyla yüklendi.`); // Hata ayıklama için eklendi
        } catch (error) {
            console.error('Mesajlar yüklenirken hata:', error);
            chatMessages.innerHTML = `<div class="empty-chat-message error-message">Mesajlar yüklenemedi: ${error.message}</div>`;
        } finally {
            console.log(`selectChat finally bloğu çalıştı.`); // Hata ayıklama için eklendi
            showLoading(false);
        }
    }

    // Mesaj gönderme fonksiyonu
    async function sendMessage() {
        const messageText = messageInput.value.trim();
        const file = fileInput.files[0];

        if (!messageText && !file) {
            alert('Lütfen bir mesaj yazın veya bir dosya seçin.');
            return;
        }
        if (!currentChatId) {
            alert('Lütfen önce bir sohbet seçin veya yeni bir sohbet başlatın.');
            return;
        }

        // Kullanıcının mesajını hemen göster
        if (messageText) {
            addMessageToChat('user', messageText, new Date());
        } else if (file) {
            addMessageToChat('user', `[Dosya Yüklendi: ${file.name}]`, new Date());
        }

        showLoading(true);
        messageInput.value = '';
        fileInput.value = null;
        fileNameDisplay.textContent = '';
        fileNameDisplay.classList.add('hidden');

        const formData = new FormData();
        formData.append('chat_id', currentChatId);
        if (messageText) {
            formData.append('message', messageText);
        }
        if (file) {
            formData.append('file', file);
        }

        const lastMessageCount = chatMessages.children.length;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                if (response.status === 401) { window.location.href = '/login'; return; }
                const errorData = await response.json();
                throw new Error(errorData.message || 'Mesaj gönderilirken bir hata oluştu.');
            }

            const data = await response.json();
            if (data.success) {
                // Hemen güncellemeye çalış
                await selectChat(currentChatId);

                // Eğer bot cevabı hemen gelmediyse, polling başlat
                const response2 = await fetch(`/api/chat/${currentChatId}/messages`);
                const chatData = await response2.json();
                if (chatData.messages.length === lastMessageCount) {
                    await pollForNewBotMessage(currentChatId, lastMessageCount);
                }
            } else {
                alert('Hata: ' + data.message);
                if (chatMessages.lastChild) { chatMessages.lastChild.remove(); }
            }
        } catch (error) {
            console.error('Mesaj gönderme hatası:', error);
            alert('Mesaj gönderme başarısız: ' + error.message);
            if (chatMessages.lastChild) { chatMessages.lastChild.remove(); }
        } finally {
            showLoading(false);
            if (debugPanelOpen) {
                fetchDebugLogs();
            }
        }
    }

    // Polling fonksiyonu: Belirli aralıklarla yeni bot mesajı geldi mi kontrol eder
    async function pollForNewBotMessage(chatId, lastMessageCount, maxAttempts = 15, interval = 2000) {
        let attempts = 0;
        while (attempts < maxAttempts) {
            const response = await fetch(`/api/chat/${chatId}/messages`);
            if (response.ok) {
                const data = await response.json();
                // Yeni mesaj geldi mi kontrol et
                if (data.messages.length > lastMessageCount) {
                    displayChatMessages(data.messages);
                    return true; // Yeni mesaj geldi
                }
            }
            await new Promise(resolve => setTimeout(resolve, interval));
            attempts++;
        }
        return false; // Süre doldu, yeni mesaj gelmedi
    }

    // Yeni sohbet oluşturma fonksiyonu
    async function createNewChat() {
        const title = prompt("Yeni sohbet başlığını girin:", `Yeni Sohbet ${new Date().toLocaleString()}`);
        if (!title) return;

        showLoading(true);
        try {
            console.log("Yeni sohbet oluşturuluyor..."); // Hata ayıklama için eklendi
            const response = await fetch('/api/chat/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: title })
            });
            if (!response.ok) {
                if (response.status === 401) { window.location.href = '/login'; return; }
                throw new Error('Yeni sohbet oluşturulamadı.');
            }
            const newChat = await response.json();
            await loadChatList(); // Sohbet listesini yeniden yükle
            selectChat(newChat.id); // Yeni oluşturulan sohbeti seç
            currentChatTitle.textContent = newChat.title;
            console.log(`Yeni sohbet başarıyla oluşturuldu: ID=${newChat.id}`); // Hata ayıklama için eklendi
        } catch (error) {
            console.error('Yeni sohbet oluşturulurken hata:', error);
            alert('Yeni sohbet oluşturulamadı: ' + error.message);
        } finally {
            console.log("createNewChat finally bloğu çalıştı."); // Hata ayıklama için eklendi
            showLoading(false);
            if (debugPanelOpen) {
                fetchDebugLogs();
            }
        }
    }

    // Sohbeti yeniden adlandırma fonksiyonu
    async function renameChat() {
        if (!currentChatId) {
            alert('Yeniden adlandırmak için önce bir sohbet seçin.');
            return;
        }
        const newTitle = prompt("Sohbetin yeni başlığını girin:", currentChatTitle.textContent);
        if (!newTitle || newTitle.trim() === currentChatTitle.textContent.trim()) return;

        showLoading(true);
        try {
            console.log(`Sohbet ID ${currentChatId} yeniden adlandırılıyor...`); // Hata ayıklama için eklendi
            const response = await fetch(`/api/chat/${currentChatId}/rename`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });
            if (!response.ok) {
                if (response.status === 401) { window.location.href = '/login'; return; }
                const errorData = await response.json();
                throw new Error(errorData.message || 'Sohbet yeniden adlandırılamadı.');
            }
            currentChatTitle.textContent = newTitle;
            await loadChatList(); // Sohbet listesini güncelleyelim
            console.log(`Sohbet ID ${currentChatId} başarıyla yeniden adlandırıldı.`); // Hata ayıklama için eklendi
        } catch (error) {
            console.error('Sohbet yeniden adlandırılırken hata:', error);
            alert('Sohbet yeniden adlandırılamadı: ' + error.message);
        } finally {
            console.log("renameChat finally bloğu çalıştı."); // Hata ayıklama için eklendi
            showLoading(false);
            if (debugPanelOpen) {
                fetchDebugLogs();
            }
        }
    }

    // Sohbet silme fonksiyonu
    async function deleteChat() {
        if (!currentChatId) {
            alert('Silmek için önce bir sohbet seçin.');
            return;
        }
        if (!confirm('Bu sohbeti ve tüm mesajlarını silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.')) {
            return;
        }

        showLoading(true);
        try {
            console.log(`Sohbet ID ${currentChatId} siliniyor...`); // Hata ayıklama için eklendi
            const response = await fetch(`/api/chat/${currentChatId}/delete`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                if (response.status === 401) { window.location.href = '/login'; return; }
                const errorData = await response.json();
                throw new Error(errorData.message || 'Sohbet silinirken hata oluştu.');
            }
            alert('Sohbet başarıyla silindi.');
            currentChatId = null; // Aktif sohbeti sıfırla
            currentChatTitle.textContent = 'Bir sohbet seçin veya yeni bir tane başlatın';
            chatMessages.innerHTML = `
                <div class="empty-chat-message">
                    <p>👋 Merhaba! Notka Şartname Asistanı'na hoş geldiniz.</p>
                    <p>Yeni bir sohbet başlatın veya soldan mevcut bir sohbeti seçin.</p>
                    <p>Şartname dosyanızı yükleyerek veya metin girerek başlayabilirsiniz.</p>
                </div>
            `;
            messageInputArea.classList.add('disabled'); // Girişi deaktive et
            renameChatBtn.style.display = 'none';
            deleteChatBtn.style.display = 'none';
            await loadChatList(); // Sohbet listesini yeniden yükle
            console.log(`Sohbet ID ${currentChatId} başarıyla silindi.`); // Hata ayıklama için eklendi
        } catch (error) {
            console.error('Sohbet silinirken hata:', error);
            alert('Sohbet silinemedi: ' + error.message);
        } finally {
            console.log("deleteChat finally bloğu çalıştı."); // Hata ayıklama için eklendi
            showLoading(false);
            if (debugPanelOpen) {
                fetchDebugLogs();
            }
        }
    }

    // --- Debug Panel Fonksiyonları ---
    function toggleDebugPanel() {
        debugPanelOpen = !debugPanelOpen;
        debugPanel.classList.toggle('open', debugPanelOpen);
        appContainer.classList.toggle('debug-open', debugPanelOpen); // Ana konteynere sınıf ekle/kaldır

        if (debugPanelOpen) {
            console.log("Debug paneli açıldı, loglar çekiliyor..."); // Hata ayıklama için eklendi
            fetchDebugLogs(); // Açıldığında logları çek
        } else {
            console.log("Debug paneli kapatıldı."); // Hata ayıklama için eklendi
        }
    }

    async function fetchDebugLogs() {
        debugLogContent.innerHTML = '<div class="loading-message">Loglar yükleniyor...</div>';
        try {
            console.log("Debug logları backend'den çekiliyor..."); // Hata ayıklama için eklendi
            const response = await fetch('/api/debug_log');
            if (!response.ok) {
                if (response.status === 401) { window.location.href = '/login'; return; }
                throw new Error('Debug logları alınamadı.');
            }
            const logs = await response.json();
            displayDebugLogs(logs);
            console.log(`Toplam ${logs.length} debug logu yüklendi.`); // Hata ayıklama için eklendi
        } catch (error) {
            console.error('Debug logları yüklenirken hata:', error);
            debugLogContent.innerHTML = `<div class="loading-message error-message">Loglar yüklenemedi: ${error.message}</div>`;
        }
    }

    function displayDebugLogs(logs) {
        debugLogContent.innerHTML = '';
        if (logs.length === 0) {
            debugLogContent.innerHTML = '<div class="loading-message">Henüz log kaydı yok.</div>';
            return;
        }
        logs.forEach(log => {
            const logEntryDiv = document.createElement('div');
            logEntryDiv.className = `log-entry ${log.level}`; // INFO, WARNING, ERROR, CRITICAL, DEBUG
            logEntryDiv.innerHTML = `
                <span class="timestamp">${log.timestamp}</span>
                <strong>${log.level}:</strong> ${escapeHtml(log.message)}
            `;
            debugLogContent.appendChild(logEntryDiv);
        });
        debugLogContent.scrollTop = debugLogContent.scrollHeight; // En alta kaydır
    }


    // --- Olay Dinleyicileri ---
    newChatBtn.addEventListener('click', createNewChat);
    sendMessageBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { // Shift+Enter yeni satır, Enter gönder
            e.preventDefault();
            sendMessage();
        }
    });

    attachFileBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = fileInput.files[0].name;
            fileNameDisplay.classList.remove('hidden');
        } else {
            fileNameDisplay.textContent = '';
            fileNameDisplay.classList.add('hidden');
        }
    });

    renameChatBtn.addEventListener('click', renameChat);
    deleteChatBtn.addEventListener('click', deleteChat);

    toggleDebugBtn.addEventListener('click', toggleDebugPanel);
    closeDebugBtn.addEventListener('click', toggleDebugPanel); // Kapatma butonu da aynı işi yapsın
    refreshDebugBtn.addEventListener('click', fetchDebugLogs);


    // Uygulama başlangıcında sohbet listesini yükle
    loadChatList();

    // Otomatik periyodik yenileme
    setInterval(() => {
        if (currentChatId) {
            selectChat(currentChatId);
        }
    }, 3000);
});
