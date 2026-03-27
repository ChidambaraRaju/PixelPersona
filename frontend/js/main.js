import { Game } from './game/Game.js';
import { ChatManager } from './chat/ChatManager.js';

let game;
let chatManager;

window.addEventListener('DOMContentLoaded', () => {
    chatManager = new ChatManager();

    game = new Game('game-canvas', (npc) => {
        chatManager.open(npc.name);
    });

    game.start();
    window.game = game;
});
