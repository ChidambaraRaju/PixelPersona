import { World } from './World.js';
import { Player } from './Player.js';
import { NPCManager } from './NPCManager.js';
import { Interaction } from './Interaction.js';

export class Game {
    constructor(canvasId, onNPCInteract) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 800;
        this.canvas.height = 600;
        this.running = false;
        this.lastTime = 0;
        this.world = new World(this.ctx);
        this.player = new Player(this.ctx, 400, 300);
        this.npcManager = new NPCManager(this.ctx);
        this.onInteractCallback = onNPCInteract;
        this.interaction = new Interaction(this.player, this.npcManager, (npc) => this.onNPCInteract(npc));
        this.initNPCs();
    }

    onNPCInteract(npc) {
        if (this.onInteractCallback) {
            this.onInteractCallback(npc);
        }
    }

    setOnInteractCallback(cb) {
        this.onInteractCallback = cb;
    }

    async initNPCs() {
        try {
            const response = await fetch('http://localhost:8000/personas');
            const data = await response.json();
            this.npcManager.init(Object.entries(data.personas).map(([name, desc]) => ({ name, description: desc })));
        } catch (e) {
            // Fallback if API not available
            this.npcManager.init([
                { name: 'Albert Einstein', description: 'German-born theoretical physicist' },
                { name: 'Nikola Tesla', description: 'Inventor and electrical engineer' },
                { name: 'APJ Abdul Kalam', description: 'Aerospace scientist' },
                { name: 'Mahatma Gandhi', description: 'Indian independence leader' }
            ]);
        }
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
        this.npcManager.update(dt);
        this.interaction.update();
    }

    render() {
        this.world.render();
        this.npcManager.render();
        this.player.render();
        this.interaction.render(this.ctx);
    }
}