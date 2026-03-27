import { NPC } from './NPC.js';

export class NPCManager {
    constructor(ctx) {
        this.ctx = ctx;
        this.npcs = [];
    }

    init(personas) {
        // Create NPCs for each persona at different positions
        const positions = [
            { x: 200, y: 200 },
            { x: 550, y: 200 },
            { x: 200, y: 400 },
            { x: 550, y: 400 }
        ];

        const colors = ['#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff'];

        personas.forEach((persona, i) => {
            const pos = positions[i];
            this.npcs.push(new NPC(
                this.ctx,
                pos.x, pos.y,
                persona.name,
                colors[i],
                persona.description
            ));
        });
    }

    update(dt) {
        this.npcs.forEach(npc => npc.update(dt));
    }

    render() {
        this.npcs.forEach(npc => npc.render());
    }

    getNPCs() {
        return this.npcs;
    }
}
