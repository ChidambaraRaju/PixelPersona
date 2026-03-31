export class Interaction {
    constructor(player, npcManager, onInteract) {
        this.player = player;
        this.npcManager = npcManager;
        this.onInteract = onInteract; // callback(npc)
        this.interactionRadius = 70; // pixels
        this.nearestNPC = null;
        // Store chatManager reference immediately — window may not be set yet
        this._chatManager = null;

        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.nearestNPC) {
                const cm = this._getChatManager();
                if (cm && cm.isDialogOpen()) {
                    e.preventDefault();
                    return;
                }
                e.preventDefault();
                this.onInteract(this.nearestNPC);
                if (window.soundManager) window.soundManager.play('interact');
            }
        });
    }

    _getChatManager() {
        if (this._chatManager) return this._chatManager;
        if (
            typeof window !== 'undefined' &&
            window.chatManager &&
            typeof window.chatManager.isDialogOpen === 'function'
        ) {
            this._chatManager = window.chatManager;
        }
        return this._chatManager;
    }

    update() {
        const playerBounds = this.player.getBounds();
        let nearest = null;
        let nearestDist = Infinity;

        for (const npc of this.npcManager.getNPCs()) {
            const npcBounds = npc.getBounds();
            const dx = playerBounds.centerX - npcBounds.centerX;
            const dy = playerBounds.centerY - npcBounds.centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < this.interactionRadius && dist < nearestDist) {
                nearest = npc;
                nearestDist = dist;
            }
        }

        this.nearestNPC = nearest;
    }

    render(ctx) {
        if (!this.nearestNPC) return;
        const cm = this._getChatManager();
        if (cm && cm.isDialogOpen()) return;

        const bounds = this.nearestNPC.getBounds();
        const cx = bounds.centerX;

        // Prompt box background
        ctx.fillStyle = 'rgba(10, 10, 26, 0.85)';
        const boxW = 80;
        const boxH = 14;
        ctx.fillRect(cx - boxW / 2, bounds.y - 28, boxW, boxH);

        // Border
        ctx.strokeStyle = '#ffd700';
        ctx.lineWidth = 1;
        ctx.strokeRect(cx - boxW / 2, bounds.y - 28, boxW, boxH);

        // Blinking "SPACE" text
        const blink = Math.floor(Date.now() / 400) % 2 === 0;
        if (blink) {
            ctx.fillStyle = '#ffd700';
            ctx.font = '6px "Press Start 2P"';
            ctx.textAlign = 'center';
            ctx.fillText('SPACE', cx, bounds.y - 18);
        }

        // "▼" arrow
        ctx.fillStyle = '#ffd700';
        ctx.font = '7px "Press Start 2P"';
        ctx.textAlign = 'center';
        ctx.fillText('\u25BC', cx, bounds.y - 6);
    }

    getNearestNPC() {
        return this.nearestNPC;
    }
}
