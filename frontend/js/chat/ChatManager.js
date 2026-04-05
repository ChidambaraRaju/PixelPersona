import { chatStream } from '../../api/client.js';

export class ChatManager {
    constructor() {
        // DOM references
        this.dialogBox     = document.getElementById('dialog-box');
        this.portraitCvs  = document.getElementById('portrait-canvas');
        this.dialogName   = document.getElementById('dialog-name');
        this.messageLog   = document.getElementById('message-log');
        this.dialogContinue = document.getElementById('dialog-continue');
        this.dialogInput  = document.getElementById('dialog-input');
        this.dialogSend   = document.getElementById('dialog-send');

        // State
        this.isDialogOpen  = false;
        this.currentNPC    = null;
        this.typewriterSpeed = 28;  // chars per second
        this.typewriterTimer = null;
        this.currentFullText = '';
        this.displayedText   = '';
        this.textComplete    = true;
        this.textQueue        = [];

        // Stream state
        this.streamActive    = false;
        this.currentMsgEl    = null;   // active streaming message element

        this._setupEvents();
    }

    _setupEvents() {
        this.dialogSend.addEventListener('click', () => this._submitInput());

        this.dialogInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this._submitInput();
            }
            if (e.key === ' ') {
                e.stopPropagation();
            }
        });

        // Space to continue / close, Escape to quit
        window.addEventListener('keydown', (e) => {
            if (!this.isDialogOpen) return;
            if (e.code === 'Escape') {
                e.preventDefault();
                this.close();
                return;
            }
            if (e.code !== 'Space') return;
            e.preventDefault();

            if (!this.textComplete) {
                this._skipTypewriter();
            } else if (this.textQueue.length === 0 && !this.streamActive) {
                this.close();
            }
        });
    }

    open(npc) {
        this.currentNPC = npc;
        this.isDialogOpen = true;
        this.textQueue = [];
        this.streamActive = false;
        this.messageLog.innerHTML = '';

        // Portrait
        const pctx = this.portraitCvs.getContext('2d');
        npc.drawPortrait(pctx);

        // Name in header
        this.dialogName.textContent = npc.name;

        // Show dialog
        this.dialogBox.classList.remove('hidden');
        this.dialogContinue.classList.add('hidden');
        this.dialogInput.value = '';
        this.dialogInput.focus();

        if (window.soundManager) window.soundManager.play('chat');

        // Welcome greeting
        this._enqueueMessage(npc.name, `Greetings, traveler. I am ${npc.name}. ${npc.description} Ask me anything.`);
    }

    close() {
        this.isDialogOpen = false;
        this.currentNPC = null;
        this._clearTypewriter();
        this.textQueue = [];
        this.dialogBox.classList.add('hidden');
        this.dialogInput.blur(); // Remove focus so Space key works again
        if (window.soundManager) window.soundManager.play('chat');
    }

    isDialogOpen() {
        return this.isDialogOpen;
    }

    _submitInput() {
        if (!this.isDialogOpen || this.streamActive) return;

        const message = this.dialogInput.value.trim();
        if (!message) return;

        this.dialogInput.value = '';

        if (!this.textComplete) {
            this._skipTypewriter();
            this.textQueue.push({ type: 'send', text: message });
            return;
        }

        // Add user message to log
        this._addUserMessage(message);
        this._streamPersonaResponse(message);
    }

    _addUserMessage(text) {
        const el = document.createElement('div');
        el.className = 'dialog-msg msg-user';
        el.innerHTML = `<div class="msg-name">YOU</div><div>「 ${this._escapeHtml(text)} 」</div>`;
        this.messageLog.appendChild(el);
        el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    _addPersonaMessage(name) {
        const el = document.createElement('div');
        el.className = 'dialog-msg msg-persona';
        el.innerHTML = `<div class="msg-name">${this._escapeHtml(name)}</div><div class="persona-text"></div>`;
        this.messageLog.appendChild(el);
        return el;
    }

    _escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    _enqueueMessage(name, text) {
        const el = this._addPersonaMessage(name);
        this.currentMsgEl = el;
        const textEl = el.querySelector('.persona-text');
        this.currentFullText = text;
        this.displayedText = '';
        this.textComplete = false;
        this._startTypewriter(textEl);
    }

    _streamPersonaResponse(message) {
        if (!this.currentNPC) return;

        this.streamActive = true;
        this.dialogContinue.classList.add('hidden');

        const el = this._addPersonaMessage(this.currentNPC.name);
        this.currentMsgEl = el;
        const textEl = el.querySelector('.persona-text');

        this.currentFullText = '';
        this.displayedText = '';
        this.textComplete = false;

        chatStream(
            this.currentNPC.name,
            message,
            (chunk) => {
                this.currentFullText += chunk;
                textEl.textContent = this.currentFullText;
                el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            },
            () => {
                this.streamActive = false;
                this.textComplete = true;
                this.dialogContinue.classList.remove('hidden');
                this._processQueue();
            },
            (error) => {
                this.streamActive = false;
                this.textComplete = true;
                textEl.textContent = `[Error: ${error}]`;
                el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                this.dialogContinue.classList.remove('hidden');
            }
        );
    }

    _startTypewriter(textEl) {
        this._clearTypewriter();
        let charIndex = 0;

        const tick = () => {
            if (charIndex < this.currentFullText.length) {
                const char = this.currentFullText[charIndex];
                this.displayedText += char;
                textEl.textContent = this.displayedText;
                charIndex++;
                const delay = ['.', '!', '?', '—', '\n'].includes(char)
                    ? 160
                    : Math.round(1000 / this.typewriterSpeed);
                this.typewriterTimer = setTimeout(tick, delay);
            } else {
                this.textComplete = true;
                this.dialogContinue.classList.remove('hidden');
                this._processQueue();
            }
        };

        tick();
    }

    _skipTypewriter() {
        this._clearTypewriter();
        this.displayedText = this.currentFullText;
        const textEl = this.currentMsgEl?.querySelector('.persona-text');
        if (textEl) textEl.textContent = this.currentFullText;
        this.textComplete = true;
        this.dialogContinue.classList.remove('hidden');
        this._processQueue();
    }

    _processQueue() {
        if (this.textQueue.length > 0) {
            const next = this.textQueue.shift();
            if (next.type === 'send') {
                this._addUserMessage(next.text);
                this._streamPersonaResponse(next.text);
            }
        }
    }

    _clearTypewriter() {
        if (this.typewriterTimer) {
            clearTimeout(this.typewriterTimer);
            this.typewriterTimer = null;
        }
    }
}
