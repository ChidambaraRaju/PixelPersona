import { World } from './World.js';
import { Player } from './Player.js';

export class Game {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 800;
        this.canvas.height = 600;
        this.running = false;
        this.lastTime = 0;
        this.world = new World(this.ctx);
        this.player = new Player(this.ctx, 400, 300);
    }

    start() {
        this.running = true;
        this.loop();
    }

    stop() {
        this.running = false;
    }

    loop(timestamp = 0) {
        if (!this.running) return;

        const deltaTime = timestamp - this.lastTime;
        this.lastTime = timestamp;

        this.update(deltaTime);
        this.render();

        requestAnimationFrame((t) => this.loop(t));
    }

    update(dt) {
        this.player.update(dt);
    }

    render() {
        this.world.render();
        this.player.render();
    }
}