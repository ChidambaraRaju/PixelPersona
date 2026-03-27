import { Game } from './game/Game.js';

window.addEventListener('DOMContentLoaded', () => {
    const game = new Game('game-canvas');
    game.start();
    window.game = game; // Debug access
});