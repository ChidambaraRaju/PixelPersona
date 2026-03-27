export class Interaction {
    constructor(player, npcManager, onInteract) {
        this.player = player;
        this.npcManager = npcManager;
        this.onInteract = onInteract; // callback(npc)
        this.interactionRadius = 60; // pixels
        this.nearestNPC = null;

        // Listen for spacebar
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.nearestNPC) {
                e.preventDefault();
                this.onInteract(this.nearestNPC);
            }
        });
    }

    update() {
        const playerBounds = this.player.getBounds();
        let nearest = null;
        let nearestDist = Infinity;

        this.npcManager.getNPCs().forEach(npc => {
            const npcBounds = npc.getBounds();
            const dx = playerBounds.centerX - npcBounds.centerX;
            const dy = playerBounds.centerY - npcBounds.centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < this.interactionRadius && dist < nearestDist) {
                nearest = npc;
                nearestDist = dist;
            }
        });

        this.nearestNPC = nearest;
    }

    render(ctx) {
        if (this.nearestNPC) {
            const bounds = this.nearestNPC.getBounds();

            // Draw interaction prompt above NPC
            ctx.fillStyle = '#000';
            ctx.font = '8px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('SPACE to chat', bounds.centerX, bounds.y - 15);

            ctx.fillStyle = '#fff';
            ctx.fillText('SPACE to chat', bounds.centerX - 1, bounds.y - 16);
        }
    }

    getNearestNPC() {
        return this.nearestNPC;
    }
}
