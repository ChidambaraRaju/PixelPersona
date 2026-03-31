import { Game } from './game/Game.js';
import { ChatManager } from './chat/ChatManager.js';
import { SoundManager } from './game/SoundManager.js';

let game;
let chatManager;
let soundManager;

function bootstrap() {
    chatManager = new ChatManager();

    soundManager = new SoundManager();
    window.soundManager = soundManager;

    // Initialize sound on first user interaction (browser autoplay policy)
    const initSound = () => {
        soundManager.init();
        window.removeEventListener('click', initSound);
        window.removeEventListener('keydown', initSound);
    };
    window.addEventListener('click', initSound, { once: true });
    window.addEventListener('keydown', initSound, { once: true });

    game = new Game('game-canvas', (npc) => {
        // When Space is pressed near NPC, dialog opens
        // (handled internally by Game → Interaction → chatManager.open)
    });

    window.game = game;
    window.chatManager = chatManager;

    // Wire dialog close back to game
    const _chatClose = chatManager.close.bind(chatManager);
    chatManager.close = () => {
        _chatClose();
        game.closeDialog();
    };

    game.start();
}

window.addEventListener('DOMContentLoaded', bootstrap);
