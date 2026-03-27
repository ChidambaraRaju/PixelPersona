import { chatStream } from '../api/client.js';

export class ChatManager {
    constructor() {
        this.modal = document.getElementById('chat-modal');
        this.messagesContainer = document.getElementById('chat-messages');
        this.input = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('chat-send');
        this.closeBtn = document.getElementById('chat-close');
        this.personaName = null;

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.closeBtn.addEventListener('click', () => this.close());
    }

    open(personaName) {
        this.personaName = personaName;
        this.messagesContainer.innerHTML = '';
        this.modal.classList.remove('hidden');
        this.input.focus();

        // Add welcome message
        this.addMessage('system', `Chat started with ${personaName}. Ask anything!`);
    }

    close() {
        this.modal.classList.add('hidden');
        this.personaName = null;
    }

    addMessage(type, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${type}`;
        msgDiv.textContent = content;
        this.messagesContainer.appendChild(msgDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    sendMessage() {
        const message = this.input.value.trim();
        if (!message || !this.personaName) return;

        this.input.value = '';

        // Add user message
        this.addMessage('user', message);

        // Add typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message persona typing';
        typingDiv.textContent = '...';
        this.messagesContainer.appendChild(typingDiv);

        // Stream response
        chatStream(
            this.personaName,
            message,
            (chunk) => {
                // Remove typing indicator on first chunk
                if (typingDiv.parentNode) {
                    typingDiv.remove();
                }
                // Append chunk
                this.addMessage('persona', chunk);
            },
            () => {
                // Done
                if (typingDiv.parentNode) typingDiv.remove();
            },
            (error) => {
                // Error
                if (typingDiv.parentNode) typingDiv.remove();
                this.addMessage('error', error);
            }
        );
    }
}
