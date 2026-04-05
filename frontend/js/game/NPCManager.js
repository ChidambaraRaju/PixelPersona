import { NPC } from './NPC.js';

// Persona color schemes for procedural sprites
const PERSONA_SCHEMES = {
    'Albert Einstein': {
        primary:   '#6a4a8a',   // purple coat
        secondary: '#f0f0f0',   // white hair
        skin:      '#e8c8a8',
    },
    'Nikola Tesla': {
        primary:   '#3a5a8a',   // blue suit
        secondary: '#c0c0c0',   // silver hair
        skin:      '#e8d8c8',
    },
    'APJ Abdul Kalam': {
        primary:   '#4a8a5a',   // green kurta
        secondary: '#e8d8a8',   // cream / off-white
        skin:      '#c8a878',
    },
    'Mahatma Gandhi': {
        primary:   '#e8a040',   // saffron robe
        secondary: '#2a2a2a',   // dark accents / glasses
        skin:      '#d8b888',
    },
};

export class NPCManager {
    constructor(ctx) {
        this.ctx = ctx;
        this.npcs = [];
        this.frozenNPCName = null;
    }

    init(personas) {
        // Predefined positions for 4 NPCs
        const positions = [
            { x: 200, y: 200 },
            { x: 500, y: 200 },
            { x: 200, y: 380 },
            { x: 500, y: 380 },
        ];

        personas.forEach((persona, i) => {
            const scheme = PERSONA_SCHEMES[persona.name] || {
                primary: '#8a8a8a', secondary: '#aaaaaa', skin: '#e8c8a8',
            };
            this.npcs.push(new NPC(
                this.ctx,
                positions[i].x,
                positions[i].y,
                persona.name,
                scheme,
                persona.description
            ));
        });
    }

    update(dt) {
        // Set frozen state each frame
        for (const npc of this.npcs) {
            npc.isFrozen = (npc.name === this.frozenNPCName);
            npc.update(dt);
        }
    }

    render() {
        // Sort by y position for depth ordering
        const sorted = [...this.npcs].sort((a, b) => a.y - b.y);
        sorted.forEach(npc => npc.render());
    }

    getNPCs() {
        return this.npcs;
    }

    getNPCByName(name) {
        return this.npcs.find(n => n.name === name) || null;
    }

    freeze(name) {
        this.frozenNPCName = name;
    }

    unfreeze() {
        this.frozenNPCName = null;
    }
}
