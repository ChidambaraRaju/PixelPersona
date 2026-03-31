export class World {
    constructor(ctx) {
        this.ctx = ctx;
        this.width = 800;
        this.height = 600;

        // Pre-generate stars (deterministic)
        this.stars = this._generateStars(60);

        // Tile size for cobblestone grid
        this.tileSize = 32;

        // Colors
        this.c = {
            skyTop: '#0a0a1a',
            skyBot: '#1a1a3a',
            grass: '#1a2e1a',
            grassLight: '#1e3420',
            cobble: '#3d3d5c',
            cobbleLight: '#4d4d6c',
            path: '#2a2a40',
            pathWorn: '#242438',
            fountainBase: '#3a5a7a',
            fountainWater: '#4a6a8a',
            fountainHighlight: '#6a8aaa',
            building: '#2a2a40',
            buildingLight: '#353550',
            windowGlow: '#ffd700',
            windowGlowDim: '#c4a000',
            trunk: '#3a2a1a',
            foliage: '#1a3a1a',
            foliageLight: '#2a5a2a',
            lanternAmber: '#f4a460',
            lanternGlow: '#ffd700',
        };

        // Village layout constants
        this.plaza = { x: 100, y: 100, w: 600, h: 400 };
        this.pathH = { y: 270, h: 40 };   // horizontal path
        this.pathV = { x: 380, w: 40 };   // vertical path
        this.fountain = { x: 360, y: 250, w: 80, h: 80 };
    }

    _generateStars(count) {
        // Deterministic star positions using a seeded-like approach
        const stars = [];
        let seed = 42;
        const rand = () => {
            seed = (seed * 16807 + 0) % 2147483647;
            return (seed - 1) / 2147483646;
        };
        for (let i = 0; i < count; i++) {
            stars.push({
                x: Math.floor(rand() * 800),
                y: Math.floor(rand() * 220),          // only in sky area
                size: rand() > 0.7 ? 2 : 1,
                alpha: 0.4 + rand() * 0.6,
            });
        }
        return stars;
    }

    render() {
        this.drawSky();
        this.drawStars();
        this.drawGround();
        this.drawCobblestones();
        this.drawPaths();
        this.drawFountain();
        this.drawTrees();
        this.drawBuildings();
        this.drawLanternGlows();
    }

    drawSky() {
        const ctx = this.ctx;
        const gradient = ctx.createLinearGradient(0, 0, 0, 260);
        gradient.addColorStop(0, this.c.skyTop);
        gradient.addColorStop(1, this.c.skyBot);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 800, 260);
    }

    drawStars() {
        const ctx = this.ctx;
        for (const s of this.stars) {
            ctx.globalAlpha = s.alpha;
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(s.x, s.y, s.size, s.size);
        }
        ctx.globalAlpha = 1;
    }

    drawGround() {
        const ctx = this.ctx;
        // Grass ground extending beyond plaza
        ctx.fillStyle = this.c.grass;
        ctx.fillRect(0, 0, 800, 600);

        // Subtle grass texture patches
        ctx.fillStyle = this.c.grassLight;
        for (let x = 0; x < 800; x += 48) {
            for (let y = 0; y < 600; y += 48) {
                if ((x + y) % 96 === 0) {
                    ctx.fillRect(x, y, 16, 16);
                }
            }
        }

        // Plaza base (darker ground area)
        const { x, y, w, h } = this.plaza;
        ctx.fillStyle = this.c.cobble;
        ctx.fillRect(x, y, w, h);
    }

    drawCobblestones() {
        const ctx = this.ctx;
        const { x, y, w, h } = this.plaza;
        const ts = this.tileSize;

        for (let tx = x; tx < x + w; tx += ts) {
            for (let ty = y; ty < y + h; ty += ts) {
                // Skip path areas
                const inPathH = ty >= y + this.pathH.y - y && ty < y + this.pathH.y - y + this.pathH.h;
                const inPathV = tx >= x + this.pathV.x - x && tx < x + this.pathV.x - x + this.pathV.w;

                if (inPathH || inPathV) continue;

                // Alternating tile color for cobblestone effect
                const isLight = ((tx / ts) + (ty / ts)) % 2 === 0;
                ctx.fillStyle = isLight ? this.c.cobbleLight : this.c.cobble;
                ctx.fillRect(tx + 1, ty + 1, ts - 2, ts - 2);

                // Small mortar lines (darker gaps)
                ctx.fillStyle = this.c.path;
                ctx.fillRect(tx, ty, ts, 1);
                ctx.fillRect(tx, ty, 1, ts);
            }
        }
    }

    drawPaths() {
        const ctx = this.ctx;
        const { x, y, w, h } = this.plaza;

        // Horizontal worn path
        const phY = y + this.pathH.y - y;
        ctx.fillStyle = this.c.pathWorn;
        ctx.fillRect(x, phY, w, this.pathH.h);

        // Worn texture on horizontal path
        ctx.fillStyle = this.c.path;
        for (let px = x; px < x + w; px += 16) {
            if ((px / 16) % 2 === 0) {
                ctx.fillRect(px, phY, 8, this.pathH.h);
            }
        }

        // Vertical worn path
        const pvX = x + this.pathV.x - x;
        ctx.fillStyle = this.c.pathWorn;
        ctx.fillRect(pvX, y, this.pathV.w, h);

        // Worn texture on vertical path
        ctx.fillStyle = this.c.path;
        for (let py = y; py < y + h; py += 16) {
            if ((py / 16) % 2 === 0) {
                ctx.fillRect(pvX, py, this.pathV.w, 8);
            }
        }
    }

    drawFountain() {
        const ctx = this.ctx;
        const { x, y, w, h } = this.fountain;
        const cx = x + w / 2;
        const cy = y + h / 2;

        // Outer rim
        ctx.fillStyle = this.c.fountainBase;
        ctx.beginPath();
        ctx.ellipse(cx, cy + 8, w / 2, h / 4, 0, 0, Math.PI * 2);
        ctx.fill();

        // Water surface
        ctx.fillStyle = this.c.fountainWater;
        ctx.beginPath();
        ctx.ellipse(cx, cy + 6, w / 2 - 6, h / 4 - 4, 0, 0, Math.PI * 2);
        ctx.fill();

        // Water highlight
        ctx.fillStyle = this.c.fountainHighlight;
        ctx.beginPath();
        ctx.ellipse(cx - 10, cy + 2, 12, 6, -0.3, 0, Math.PI * 2);
        ctx.fill();

        // Center pillar
        ctx.fillStyle = this.c.fountainBase;
        ctx.fillRect(cx - 6, y + 10, 12, 30);

        // Top water spout
        ctx.fillStyle = this.c.fountainHighlight;
        ctx.beginPath();
        ctx.ellipse(cx, y + 8, 8, 4, 0, 0, Math.PI * 2);
        ctx.fill();
    }

    drawTrees() {
        const ctx = this.ctx;
        // Four corner trees
        const positions = [
            { x: 110, y: 95 },
            { x: 610, y: 95 },
            { x: 110, y: 440 },
            { x: 610, y: 440 },
        ];

        for (const pos of positions) {
            this._drawTree(pos.x, pos.y);
        }
    }

    _drawTree(x, y) {
        const ctx = this.ctx;

        // Trunk
        ctx.fillStyle = this.c.trunk;
        ctx.fillRect(x + 14, y + 50, 12, 30);

        // Foliage layers (bottom to top)
        ctx.fillStyle = this.c.foliage;
        ctx.beginPath();
        ctx.moveTo(x + 20, y);
        ctx.lineTo(x + 44, y + 55);
        ctx.lineTo(x - 4, y + 55);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = this.c.foliageLight;
        ctx.beginPath();
        ctx.moveTo(x + 20, y + 10);
        ctx.lineTo(x + 38, y + 45);
        ctx.lineTo(x + 2, y + 45);
        ctx.closePath();
        ctx.fill();

        // Lantern glow near tree
        const lx = x + 20;
        const ly = y + 30;
        const glow = ctx.createRadialGradient(lx, ly, 2, lx, ly, 28);
        glow.addColorStop(0, 'rgba(244, 164, 96, 0.35)');
        glow.addColorStop(1, 'rgba(244, 164, 96, 0)');
        ctx.fillStyle = glow;
        ctx.fillRect(x - 10, y + 5, 60, 55);

        // Lantern orb
        ctx.fillStyle = this.c.lanternAmber;
        ctx.beginPath();
        ctx.arc(lx, ly, 5, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = this.c.lanternGlow;
        ctx.beginPath();
        ctx.arc(lx, ly, 3, 0, Math.PI * 2);
        ctx.fill();
    }

    drawBuildings() {
        const ctx = this.ctx;
        const positions = [
            { x: 100, y: 75 },   // top-left
            { x: 620, y: 75 },  // top-right
            { x: 100, y: 445 }, // bottom-left
            { x: 620, y: 445 }, // bottom-right
        ];

        for (const pos of positions) {
            this._drawBuilding(pos.x, pos.y);
        }
    }

    _drawBuilding(x, y) {
        const ctx = this.ctx;
        const bw = 80;
        const bh = 70;

        // Main building body
        ctx.fillStyle = this.c.building;
        ctx.fillRect(x, y, bw, bh);

        // Roof
        ctx.fillStyle = this.c.buildingLight;
        ctx.beginPath();
        ctx.moveTo(x - 8, y);
        ctx.lineTo(x + bw / 2, y - 20);
        ctx.lineTo(x + bw + 8, y);
        ctx.closePath();
        ctx.fill();

        // Roof edge
        ctx.fillStyle = this.c.building;
        ctx.fillRect(x - 10, y - 4, bw + 20, 6);

        // Lit windows (warm glow)
        const windows = [
            { wx: x + 10, wy: y + 20 },
            { wx: x + 45, wy: y + 20 },
            { wx: x + 10, wy: y + 42 },
            { wx: x + 45, wy: y + 42 },
        ];

        for (const w of windows) {
            // Window glow
            const wglow = ctx.createRadialGradient(w.wx + 6, w.wy + 8, 1, w.wx + 6, w.wy + 8, 18);
            wglow.addColorStop(0, 'rgba(255, 215, 0, 0.3)');
            wglow.addColorStop(1, 'rgba(255, 215, 0, 0)');
            ctx.fillStyle = wglow;
            ctx.fillRect(w.wx - 12, w.wy - 10, 36, 36);

            // Window frame
            ctx.fillStyle = this.c.windowGlowDim;
            ctx.fillRect(w.wx, w.wy, 14, 16);
            // Window inner glow
            ctx.fillStyle = this.c.windowGlow;
            ctx.fillRect(w.wx + 2, w.wy + 2, 10, 12);
            // Window cross
            ctx.fillStyle = this.c.building;
            ctx.fillRect(w.wx + 6, w.wy, 2, 16);
            ctx.fillRect(w.wx, w.wy + 7, 14, 2);
        }
    }

    drawLanternGlows() {
        // Extra ambient glow pools on ground near trees
        const ctx = this.ctx;
        const glowPositions = [
            { x: 130, y: 145 },
            { x: 630, y: 145 },
            { x: 130, y: 490 },
            { x: 630, y: 490 },
        ];

        for (const g of glowPositions) {
            const glow = ctx.createRadialGradient(g.x, g.y, 2, g.x, g.y, 40);
            glow.addColorStop(0, 'rgba(244, 164, 96, 0.12)');
            glow.addColorStop(1, 'rgba(244, 164, 96, 0)');
            ctx.fillStyle = glow;
            ctx.fillRect(g.x - 40, g.y - 40, 80, 80);
        }
    }
}
