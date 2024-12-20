document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const newlineButton = document.getElementById('newlineButton');
    const newChatButton = document.getElementById('newChatButton');
    const chatList = document.getElementById('chatList');
    const toggleSidebarButton = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');
    const showSidebarButton = document.getElementById('showSidebar');

    let currentChatId = null;

    // 自动调整文本框高度
    function adjustTextareaHeight() {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
    }

    // 监听输入事件，调整高度
    messageInput.addEventListener('input', adjustTextareaHeight);

    // 添加换行按钮功能
    newlineButton.addEventListener('click', function() {
        const cursorPos = messageInput.selectionStart;
        const textBefore = messageInput.value.substring(0, cursorPos);
        const textAfter = messageInput.value.substring(cursorPos);
        
        messageInput.value = textBefore + '\n' + textAfter;
        messageInput.selectionStart = messageInput.selectionEnd = cursorPos + 1;
        
        adjustTextareaHeight();
        messageInput.focus();
    });

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        content = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = content;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function loadChat(chatId) {
        currentChatId = chatId;
        messagesContainer.innerHTML = '';
        
        try {
            const response = await fetch(`/api/chat/${chatId}`);
            const messages = await response.json();
            
            messages.forEach(msg => {
                addMessage(msg.content, msg.role === 'user');
            });
            
            // 更新活动状态
            document.querySelectorAll('.chat-item').forEach(item => {
                item.classList.remove('active');
                if (item.dataset.id === chatId) {
                    item.classList.add('active');
                }
            });
        } catch (error) {
            console.error('Error loading chat:', error);
        }
    }

    async function createNewChat() {
        try {
            const response = await fetch('/api/chat/new', {
                method: 'POST'
            });
            const data = await response.json();
            
            // 刷新聊天列表
            const chatsResponse = await fetch('/api/chats');
            const chats = await chatsResponse.json();
            updateChatList(chats);
            
            // 加载新聊天
            loadChat(data.chat_id);
        } catch (error) {
            console.error('Error creating new chat:', error);
        }
    }

    function updateChatList(chats) {
        chatList.innerHTML = chats.map(chat => `
            <div class="chat-item" data-id="${chat.id}">
                <i class="ri-message-3-line"></i>
                <div class="chat-content">
                    <div class="chat-preview">${chat.preview}</div>
                    <div class="chat-date">${chat.date}</div>
                </div>
                <div class="delete-indicator">
                    <i class="ri-delete-bin-line"></i>
                </div>
            </div>
        `).join('');
        
        // 绑定点击和长按事件
        document.querySelectorAll('.chat-item').forEach(item => {
            // 点击加载聊天
            item.addEventListener('click', () => loadChat(item.dataset.id));

            // 长按删除
            item.addEventListener('touchstart', handleTouchStart);
            item.addEventListener('touchend', handleTouchEnd);
            item.addEventListener('touchmove', handleTouchMove);
            
            // 为桌面端添加鼠标事件
            item.addEventListener('mousedown', handleMouseDown);
            item.addEventListener('mouseup', handleMouseUp);
            item.addEventListener('mouseleave', handleMouseUp);
        });
    }

    async function sendMessage() {
        if (!currentChatId) {
            await createNewChat();
        }

        const message = messageInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        messageInput.value = '';
        messageInput.style.height = 'auto';

        try {
            const response = await fetch(`/api/chat/${currentChatId}/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            addMessage(data.response, false);
            
            // 刷新聊天列表
            const chatsResponse = await fetch('/api/chats');
            const chats = await chatsResponse.json();
            updateChatList(chats);
        } catch (error) {
            console.error('Error:', error);
            addMessage('抱歉，发生了错误，请稍后重试。', false);
        }
    }

    // 发送按钮点击事件
    sendButton.addEventListener('click', sendMessage);

    // 新对话按钮点击事件
    newChatButton.addEventListener('click', createNewChat);

    // 处理键盘事件
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            if (e.shiftKey) {
                return;
            } else {
                e.preventDefault();
                sendMessage();
            }
        }
    });

    // 初始化：如果有聊天记录，加载最新的聊天
    const chatItems = document.querySelectorAll('.chat-item');
    if (chatItems.length > 0) {
        loadChat(chatItems[0].dataset.id);
    }

    // 添加侧边栏折叠功能
    toggleSidebarButton.addEventListener('click', function(e) {
        e.stopPropagation();  // 阻止事件冒泡
        sidebar.classList.toggle('collapsed');
        // 更新图标
        const icon = this.querySelector('i');
        if (sidebar.classList.contains('collapsed')) {
            icon.className = 'ri-arrow-right-s-line';
        } else {
            icon.className = 'ri-arrow-left-s-line';
        }
    });

    // 修改点击事件处理，防止事件冒泡
    showSidebarButton.addEventListener('click', function(e) {
        e.stopPropagation();  // 阻止事件冒泡
        sidebar.classList.remove('collapsed');
        const toggleIcon = toggleSidebarButton.querySelector('i');
        toggleIcon.className = 'ri-arrow-left-s-line';
    });

    // 修改折叠按钮事件，添加点击其他区域关闭侧边栏功能
    document.addEventListener('click', function(e) {
        // 如果点击的不是侧边栏内的元素，也不是显示按钮
        if (!sidebar.contains(e.target) && 
            !showSidebarButton.contains(e.target) && 
            !sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
            const toggleIcon = toggleSidebarButton.querySelector('i');
            toggleIcon.className = 'ri-arrow-right-s-line';
        }
    });

    // 长按删除相关变量
    let longPressTimer;
    const longPressDuration = 500; // 长按时间阈值（毫秒）

    // 长按处理函数
    function handleTouchStart(e) {
        startLongPress(e.currentTarget);
    }

    function handleMouseDown(e) {
        startLongPress(e.currentTarget);
    }

    function startLongPress(element) {
        longPressTimer = setTimeout(() => {
            element.classList.add('deleting');
        }, longPressDuration);
    }

    function handleTouchEnd(e) {
        endLongPress(e.currentTarget);
    }

    function handleMouseUp(e) {
        endLongPress(e.currentTarget);
    }

    function handleTouchMove(e) {
        clearTimeout(longPressTimer);
    }

    function endLongPress(element) {
        clearTimeout(longPressTimer);
        if (element.classList.contains('deleting')) {
            showDeleteConfirm(element.dataset.id);
        }
    }

    // 显示删除确认
    function showDeleteConfirm(chatId) {
        if (confirm('确定要删除这个对话吗？')) {
            deleteChat(chatId);
        } else {
            // 取消删除状态
            document.querySelectorAll('.chat-item').forEach(item => {
                item.classList.remove('deleting');
            });
        }
    }

    // 删除聊天
    async function deleteChat(chatId) {
        try {
            const response = await fetch(`/api/chat/${chatId}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                // 刷新聊天列表
                const chatsResponse = await fetch('/api/chats');
                const chats = await chatsResponse.json();
                updateChatList(chats);
                
                // 如果删除的是当前聊天，加载最新的聊天
                if (chatId === currentChatId) {
                    const chatItems = document.querySelectorAll('.chat-item');
                    if (chatItems.length > 0) {
                        loadChat(chatItems[0].dataset.id);
                    } else {
                        messagesContainer.innerHTML = '';
                        currentChatId = null;
                    }
                }
            }
        } catch (error) {
            console.error('Error deleting chat:', error);
            alert('删除失败，请稍后重试');
        }
    }
}); 