import { Game } from './game/Game.js';

let game;
let currentNPC = null;

window.addEventListener('DOMContentLoaded', () => {
    game = new Game('game-canvas', (npc) => {
        // Called when player presses space near NPC
        currentNPC = npc;
        showChatModal(npc.name, npc.description);
    });

    game.start();
    window.game = game;
});

function showChatModal(name, description) {
    const modal = document.getElementById('chat-modal');
    const header = document.getElementById('chat-persona-name');
    header.textContent = name;
    modal.classList.remove('hidden');
    // Focus input
    document.getElementById('chat-input').focus();
}
