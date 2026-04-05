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

        // Game systems
        this.world = new World(this.ctx);
        this.player = new Player(this.ctx, 400, 300);
        this.npcManager = new NPCManager(this.ctx);
        this.interaction = new Interaction(
            this.player,
            this.npcManager,
            (npc) => this._onNPCInteract(npc)
        );

        // Minimap
        this.minimapCanvas = document.getElementById('minimap-canvas');
        this.minimapCtx = this.minimapCanvas.getContext('2d');

        // Dialog state
        this.dialogOpen = false;

        // NPC interaction callback
        this._onNPCInteractCallback = onNPCInteract;

        // HUD NPC indicator
        this.npcIndicatorEl = document.getElementById('npc-indicator');
        this.npcIndicatorNameEl = document.getElementById('npc-indicator-name');
        this.npcIndicatorDescEl = document.getElementById('npc-indicator-desc');

        this.initNPCs();

        // Animate loading bar
        this._animateLoading();
    }

    async _animateLoading() {
        const bar = document.getElementById('loading-bar');
        if (!bar) return;
        const steps = [20, 45, 70, 90, 100];
        for (const w of steps) {
            bar.style.width = w + '%';
            await new Promise(r => setTimeout(r, 300));
        }
    }

    async initNPCs() {
        try {
            const response = await fetch('http://localhost:8000/personas');
            const data = await response.json();
            this.npcManager.init(
                Object.entries(data.personas).map(([name, desc]) => ({ name, description: desc }))
            );
        } catch (e) {
            this.npcManager.init([
                { name: 'Albert Einstein', description: 'German-born theoretical physicist' },
                { name: 'Nikola Tesla', description: 'Inventor and electrical engineer' },
                { name: 'APJ Abdul Kalam', description: 'Aerospace scientist and 11th President of India' },
                { name: 'Mahatma Gandhi', description: 'Leader of Indian independence movement' },
            ]);
        }
        this._hideLoading();
    }

    _hideLoading() {
        const loading = document.getElementById('loading-screen');
        if (loading) {
            loading.classList.add('fade-out');
            setTimeout(() => loading.remove(), 600);
        }
    }

    _onNPCInteract(npc) {
        this.openDialog(npc);
        if (this._onNPCInteractCallback) {
            this._onNPCInteractCallback(npc);
        }
    }

    openDialog(npc) {
        this.dialogOpen = true;
        this.npcManager.freeze(npc.name);
        if (window.chatManager) {
            window.chatManager.open(npc);
        }
        // Update HUD indicator
        this.npcIndicatorNameEl.textContent = npc.name;
        this.npcIndicatorDescEl.textContent = npc.description;
        this.npcIndicatorEl.classList.remove('hidden');
    }

    closeDialog() {
        this.dialogOpen = false;
        this.npcManager.unfreeze();
        this.npcIndicatorEl.classList.add('hidden');
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

        // Cap delta to avoid spiral of death
        const dt = Math.min(deltaTime, 100);

        this.update(dt);
        this.render();

        requestAnimationFrame((t) => this.loop(t));
    }

    update(dt) {
        // Player updates (checks isDialogOpen internally)
        this.player.update(dt);

        // NPCs always update (even during dialog)
        this.npcManager.update(dt);

        // Interaction prompt updates
        this.interaction.update();

        // Update HUD NPC indicator based on proximity
        const nearest = this.interaction.getNearestNPC();
        if (nearest && !this.dialogOpen) {
            this.npcIndicatorNameEl.textContent = nearest.name;
            this.npcIndicatorDescEl.textContent = nearest.description;
            this.npcIndicatorEl.classList.remove('hidden');
        } else if (!nearest || this.dialogOpen) {
            this.npcIndicatorEl.classList.add('hidden');
        }
    }

    render() {
        // Clear
        this.ctx.clearRect(0, 0, 800, 600);

        // 1. World (sky, ground, plaza, fountain, trees, buildings)
        this.world.render();

        // 2. NPCs (y-sorted for depth)
        this.npcManager.render();

        // 3. Player
        this.player.render();

        // 4. Interaction prompt (above nearest NPC)
        this.interaction.render(this.ctx);

        // 5. Minimap
        this.renderMinimap();
    }

    renderMinimap() {
        const ctx = this.minimapCtx;
        const w = 80, h = 60;

        // Sky / grass background
        ctx.fillStyle = '#1a2e1a';
        ctx.fillRect(0, 0, w, h);

        // Plaza (scaled: 600x400 → 60x40 at offset 10,10)
        ctx.fillStyle = '#3d3d5c';
        ctx.fillRect(10, 10, 60, 40);

        // Cross path
        ctx.fillStyle = '#2a2a40';
        ctx.fillRect(0, 25, 80, 4);   // horizontal
        ctx.fillRect(38, 0, 4, 60);   // vertical

        // Fountain (small center dot)
        ctx.fillStyle = '#4a6a8a';
        ctx.fillRect(37, 26, 6, 4);

        // Buildings (corner dots)
        ctx.fillStyle = '#ffd700';
        ctx.fillRect(10, 10, 2, 2);
        ctx.fillRect(68, 10, 2, 2);
        ctx.fillRect(10, 48, 2, 2);
        ctx.fillRect(68, 48, 2, 2);

        // NPCs (colored dots)
        for (const npc of this.npcManager.getNPCs()) {
            ctx.fillStyle = npc.colorScheme.primary;
            const nx = Math.round(10 + (npc.x / 800) * 60);
            const ny = Math.round(10 + (npc.y / 600) * 40);
            ctx.fillRect(nx - 1, ny - 1, 3, 3);
        }

        // Player (white dot, larger)
        ctx.fillStyle = '#ffffff';
        const px = Math.round(10 + (this.player.x / 800) * 60);
        const py = Math.round(10 + (this.player.y / 600) * 40);
        ctx.fillRect(px - 2, py - 2, 4, 4);
    }
}
