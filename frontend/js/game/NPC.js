export class NPC {
    /**
     * @param {CanvasRenderingContext2D} ctx
     * @param {number} x
     * @param {number} y
     * @param {string} name
     * @param {object} colorScheme  - { primary, secondary, accent, description }
     * @param {string} description
     */
    constructor(ctx, x, y, name, colorScheme, description) {
        this.ctx = ctx;
        this.x = x;
        this.y = y;
        this.name = name;
        this.colorScheme = colorScheme;
        this.description = description;

        this.SCALE = 3;
        this.width = 16 * this.SCALE;
        this.height = 24 * this.SCALE;
        this.speed = 25;

        // Wander AI
        this.direction = { x: 0, y: 0 };
        this.directionTimer = 0;
        this.directionInterval = 2000 + Math.random() * 2000;
        this.changeDirection();

        // Idle bob animation
        this.bobOffset = 0;
        this.bobDirection = 1;
        this.bobTimer = 0;

        // Walk animation
        this.isWalking = false;
        this.animationFrame = 0;
        this.animationTimer = 0;
    }

    changeDirection() {
        const dirs = [
            { x: 1, y: 0 }, { x: -1, y: 0 },
            { x: 0, y: 1 }, { x: 0, y: -1 },
            { x: 0, y: 0 },
        ];
        this.direction = dirs[Math.floor(Math.random() * dirs.length)];
    }

    update(dt) {
        // Direction change timer
        this.directionTimer += dt;
        if (this.directionTimer >= this.directionInterval) {
            this.changeDirection();
            this.directionTimer = 0;
            this.directionInterval = 2000 + Math.random() * 2000;
        }

        // Move
        const dx = this.direction.x * this.speed * (dt / 1000);
        const dy = this.direction.y * this.speed * (dt / 1000);
        this.x += dx;
        this.y += dy;

        this.isWalking = this.direction.x !== 0 || this.direction.y !== 0;

        // Boundary collision (stay in village plaza)
        const margin = 30;
        if (this.x < margin) { this.x = margin; this.changeDirection(); }
        if (this.x > 700 - this.width) { this.x = 700 - this.width; this.changeDirection(); }
        if (this.y < 70) { this.y = 70; this.changeDirection(); }
        if (this.y > 500 - this.height) { this.y = 500 - this.height; this.changeDirection(); }

        // Bob animation (idle only)
        if (!this.isWalking) {
            this.bobTimer += dt;
            if (this.bobTimer >= 30) {
                this.bobTimer = 0;
                this.bobOffset += this.bobDirection * 0.5;
                if (this.bobOffset > 2 || this.bobOffset < -2) this.bobDirection *= -1;
            }
        } else {
            // Walk animation frame
            this.animationTimer += dt;
            if (this.animationTimer >= 200) {
                this.animationFrame = (this.animationFrame + 1) % 2;
                this.animationTimer = 0;
            }
            this.bobOffset = 0;
        }
    }

    render() {
        const ctx = this.ctx;
        const s = this.SCALE;
        const drawX = Math.round(this.x);
        const drawY = Math.round(this.y + (this.isWalking ? 0 : this.bobOffset));

        this._drawSprite(ctx, drawX, drawY, s, this.animationFrame);

        // Name label
        ctx.fillStyle = '#000';
        ctx.font = '7px "Press Start 2P"';
        ctx.textAlign = 'center';
        ctx.fillText(this.name.split(' ').pop(), drawX + this.width / 2 + 1, this.y - 6);

        ctx.fillStyle = '#ffd700';
        ctx.fillText(this.name.split(' ').pop(), drawX + this.width / 2, this.y - 7);
    }

    /**
     * Draw 16x24 pixel sprite with persona-specific features.
     * Uses fillRect for pixel-art effect.
     */
    _drawSprite(ctx, px, py, s, frame) {
        const C = this.colorScheme;
        const walkBounce = this.isWalking && frame === 1 ? -s : 0;

        const p = (dx, dy, color) => {
            ctx.fillStyle = color;
            ctx.fillRect(px + dx * s, py + dy * s + walkBounce, s, s);
        };

        const r = (dx, dy, w, h, color) => {
            ctx.fillStyle = color;
            ctx.fillRect(px + dx * s, py + dy * s + walkBounce, w * s, h * s);
        };

        const primary   = C.primary;
        const secondary = C.secondary;
        const skin      = C.skin      || '#e8c8a8';
        const outline   = '#0a0a1a';

        // ─── Shared: call persona-specific body ───
        switch (this.name) {
            case 'Albert Einstein':  this._drawEinstein(p, r, s, walkBounce, px, py, skin, primary, secondary); break;
            case 'Nikola Tesla':      this._drawTesla(p, r, s, walkBounce, px, py, skin, primary, secondary); break;
            case 'APJ Abdul Kalam':  this._drawKalam(p, r, s, walkBounce, px, py, skin, primary, secondary); break;
            case 'Mahatma Gandhi':    this._drawGandhi(p, r, s, walkBounce, px, py, skin, primary, secondary); break;
            default:                 this._drawGeneric(p, r, s, walkBounce, px, py, skin, primary);
        }
    }

    _drawEinstein(p, r, s, walkBounce, px, py, skin, primary, secondary) {
        // Wild white hair (prominent)
        r(2, 1, 12, 2, secondary);  // top wild hair
        r(1, 2, 14, 2, secondary);
        r(0, 3, 16, 2, secondary);   // very wide hair
        r(1, 3, 14, 2, skin);       // face under hair

        // Face
        r(2, 3, 12, 4, skin);

        // Wild side hair
        r(0, 4, 2, 3, secondary);
        r(14, 4, 2, 3, secondary);

        // Chin
        r(3, 7, 10, 1, skin);

        // Neck
        r(6, 8, 4, 1, skin);

        // Body (purple coat)
        r(3, 9, 10, 5, primary);
        r(2, 9, 1, 4, '#5a3a7a');
        r(13, 9, 1, 4, '#5a3a7a');
        r(5, 9, 6, 1, primary);

        // Coat buttons
        p(7, 10, '#ffd700'); p(7, 12, '#ffd700');

        // Arms
        r(0, 10, 2, 4, primary);
        r(14, 10, 2, 4, primary);

        // Pants
        r(3, 14, 4, 3, '#2a3a4a');
        r(9, 14, 4, 3, '#2a3a4a');
        r(7, 14, 2, 3, skin);

        // Shoes
        r(3, 17, 5, 1, '#1a1a1a');
        r(9, 17, 5, 1, '#1a1a1a');

        // Mustache (Einstein hallmark)
        r(5, 5, 6, 1, secondary);
    }

    _drawTesla(p, r, s, walkBounce, px, py, skin, primary, secondary) {
        // Sleek silver hair
        r(2, 1, 12, 2, secondary);
        r(2, 2, 12, 2, secondary);
        r(1, 3, 14, 2, secondary);

        // Face
        r(2, 3, 12, 4, skin);

        // Sharp angular features - slicked hair
        r(0, 3, 2, 3, secondary);
        r(14, 3, 2, 3, secondary);

        r(3, 7, 10, 1, skin);
        r(6, 8, 4, 1, skin);

        // Body (blue suit, sharp)
        r(3, 9, 10, 5, primary);
        r(2, 9, 1, 4, '#2a4a7a');
        r(13, 9, 1, 4, '#2a4a7a');

        // Tie
        r(7, 9, 2, 4, secondary);

        // Arms (suit sleeves)
        r(0, 10, 2, 4, primary);
        r(14, 10, 2, 4, primary);

        // Pants
        r(3, 14, 4, 3, '#2a3a4a');
        r(9, 14, 4, 3, '#2a3a4a');
        r(7, 14, 2, 3, skin);

        // Shoes
        r(3, 17, 5, 1, '#1a1a1a');
        r(9, 17, 5, 1, '#1a1a1a');

        // Pince-nez glasses (Tesla wore them)
        r(4, 4, 7, 1, '#aaaaaa');
        p(5, 4, '#1a1a1a');
        p(9, 4, '#1a1a1a');
    }

    _drawKalam(p, r, s, walkBounce, px, py, skin, primary, secondary) {
        // Simple dark hair/head
        r(3, 1, 10, 2, '#2a2a2a');
        r(2, 2, 12, 2, '#2a2a2a');
        r(2, 3, 12, 2, skin);

        // Face
        r(2, 3, 12, 4, skin);
        r(1, 4, 1, 2, '#2a2a2a');
        r(14, 4, 1, 2, '#2a2a2a');

        r(3, 7, 10, 1, skin);
        r(6, 8, 4, 1, skin);

        // Body (green kurta)
        r(3, 9, 10, 5, primary);
        r(2, 9, 1, 4, '#3a7a4a');
        r(13, 9, 1, 4, '#3a7a4a');
        r(5, 9, 6, 1, primary);

        // Kurta collar
        r(6, 9, 4, 1, secondary);
        r(7, 10, 2, 2, secondary);

        // Arms (kurta sleeves)
        r(0, 10, 2, 4, primary);
        r(14, 10, 2, 4, primary);

        // Simple pants
        r(3, 14, 4, 3, secondary);
        r(9, 14, 4, 3, secondary);
        r(7, 14, 2, 3, skin);

        // Sandals
        r(3, 17, 5, 1, '#5a3a1a');
        r(9, 17, 5, 1, '#5a3a1a');

        // Kind gentle expression (soft eyes)
        p(5, 4, skin); p(5, 5, '#2a2a2a');
        p(9, 4, skin); p(9, 5, '#2a2a2a');
    }

    _drawGandhi(p, r, s, walkBounce, px, py, skin, primary, secondary) {
        // Bald head with round glasses
        r(3, 1, 10, 2, skin);
        r(2, 2, 12, 2, skin);
        r(2, 3, 12, 2, skin);

        // Round glasses frame
        r(3, 4, 4, 1, '#5a3a1a');
        r(9, 4, 4, 1, '#5a3a1a');
        r(3, 4, 1, 3, '#5a3a1a');
        r(7, 4, 1, 3, '#5a3a1a');  // bridge
        r(12, 4, 1, 3, '#5a3a1a');
        r(4, 5, 3, 2, skin); // lens left
        r(9, 5, 3, 2, skin);  // lens right

        // Simple eyes behind glasses
        p(5, 5, '#2a2a2a');
        p(10, 5, '#2a2a2a');

        // Face
        r(2, 3, 12, 4, skin);
        r(1, 4, 1, 2, skin);
        r(14, 4, 1, 2, skin);
        r(3, 7, 10, 1, skin);
        r(6, 8, 4, 1, skin);

        // Body (saffron robe)
        r(3, 9, 10, 5, primary);
        r(2, 9, 1, 4, '#c88030');
        r(13, 9, 1, 4, '#c88030');
        r(5, 9, 6, 1, primary);

        // Robe fold
        r(7, 10, 2, 3, '#c88030');

        // Arms
        r(0, 10, 2, 4, primary);
        r(14, 10, 2, 4, primary);

        // Lower robe
        r(3, 14, 10, 4, primary);

        // Sandals
        r(4, 18, 3, 1, '#5a3a1a');
        r(9, 18, 3, 1, '#5a3a1a');
    }

    _drawGeneric(p, r, s, walkBounce, px, py, skin, primary) {
        // Fallback: simple colored rectangle character
        r(3, 1, 10, 2, skin);
        r(2, 2, 12, 5, primary);
        r(3, 7, 10, 1, skin);
        r(6, 8, 4, 1, skin);
        r(3, 9, 10, 5, primary);
        r(3, 14, 10, 4, '#2a3a4a');
        r(3, 18, 5, 1, '#1a1a1a');
        r(9, 18, 5, 1, '#1a1a1a');
    }

    /**
     * Draw a 64x64 portrait for the dialog box.
     * @param {CanvasRenderingContext2D} pctx
     */
    drawPortrait(pctx) {
        const size = 64;
        pctx.clearRect(0, 0, size, size);

        // Background
        pctx.fillStyle = '#0a0a1a';
        pctx.fillRect(0, 0, size, size);

        // Scale: our sprites are 16x24, draw them at 4x = 64x96
        // Center the 64x96 portrait in the 64x64 canvas (shows head + partial body)
        const scale = 4;
        const offsetX = 0;
        const offsetY = -24; // shift up to show more face

        const C = this.colorScheme;
        const skin = C.skin || '#e8c8a8';

        const p = (dx, dy, color) => {
            pctx.fillStyle = color;
            pctx.fillRect(offsetX + dx * scale, offsetY + dy * scale, scale, scale);
        };

        const r = (dx, dy, w, h, color) => {
            pctx.fillStyle = color;
            pctx.fillRect(offsetX + dx * scale, offsetY + dy * scale, w * scale, h * scale);
        };

        // Draw full-body sprite scaled into portrait (head + torso)
        switch (this.name) {
            case 'Albert Einstein':  this._portraitEinstein(p, r, skin, C.primary, C.secondary); break;
            case 'Nikola Tesla':      this._portraitTesla(p, r, skin, C.primary, C.secondary); break;
            case 'APJ Abdul Kalam':  this._portraitKalam(p, r, skin, C.primary, C.secondary); break;
            case 'Mahatma Gandhi':    this._portraitGandhi(p, r, skin, C.primary, C.secondary); break;
            default:                 this._portraitGeneric(p, r, skin, C.primary); break;
        }

        // Border
        pctx.strokeStyle = C.primary;
        pctx.lineWidth = 2;
        pctx.strokeRect(1, 1, size - 2, size - 2);
    }

    _portraitEinstein(p, r, skin, primary, secondary) {
        r(2, 1, 12, 2, secondary);
        r(1, 2, 14, 2, secondary);
        r(0, 3, 16, 2, secondary);
        r(1, 3, 14, 2, skin);
        r(2, 3, 12, 4, skin);
        r(0, 4, 2, 3, secondary);
        r(14, 4, 2, 3, secondary);
        r(3, 7, 10, 1, skin);
        r(5, 5, 6, 1, secondary); // mustache
        // Eyes
        p(5, 4, '#2a2a2a'); p(6, 4, '#2a2a2a');
        p(8, 4, '#2a2a2a'); p(9, 4, '#2a2a2a');
        // Body
        r(3, 8, 10, 5, primary);
        r(2, 8, 1, 4, '#5a3a7a');
        r(13, 8, 1, 4, '#5a3a7a');
        p(7, 9, '#ffd700'); p(7, 11, '#ffd700');
    }

    _portraitTesla(p, r, skin, primary, secondary) {
        r(2, 1, 12, 2, secondary);
        r(2, 2, 12, 2, secondary);
        r(1, 3, 14, 2, secondary);
        r(2, 3, 12, 4, skin);
        r(0, 3, 2, 3, secondary);
        r(14, 3, 2, 3, secondary);
        r(3, 7, 10, 1, skin);
        // Glasses
        r(3, 4, 4, 1, '#aaaaaa');
        r(9, 4, 4, 1, '#aaaaaa');
        r(3, 4, 1, 3, '#aaaaaa');
        r(7, 4, 1, 3, '#aaaaaa');
        r(12, 4, 1, 3, '#aaaaaa');
        p(5, 5, '#2a2a2a'); p(6, 5, '#2a2a2a');
        p(9, 5, '#2a2a2a'); p(10, 5, '#2a2a2a');
        // Body
        r(3, 8, 10, 5, primary);
        r(7, 8, 2, 4, secondary); // tie
    }

    _portraitKalam(p, r, skin, primary, secondary) {
        r(3, 1, 10, 2, '#2a2a2a');
        r(2, 2, 12, 2, '#2a2a2a');
        r(2, 3, 12, 2, skin);
        r(2, 3, 12, 4, skin);
        r(1, 4, 1, 2, '#2a2a2a');
        r(14, 4, 1, 2, '#2a2a2a');
        r(3, 7, 10, 1, skin);
        // Gentle eyes
        p(5, 5, '#2a2a2a'); p(6, 5, '#2a2a2a');
        p(8, 5, '#2a2a2a'); p(9, 5, '#2a2a2a');
        // Body (kurta)
        r(3, 8, 10, 5, primary);
        r(6, 8, 4, 1, secondary);
        r(7, 9, 2, 2, secondary);
    }

    _portraitGandhi(p, r, skin, primary, secondary) {
        r(3, 1, 10, 2, skin);
        r(2, 2, 12, 2, skin);
        r(2, 3, 12, 2, skin);
        r(2, 3, 12, 4, skin);
        r(1, 4, 1, 2, skin);
        r(14, 4, 1, 2, skin);
        r(3, 7, 10, 1, skin);
        // Round glasses
        r(3, 4, 4, 1, '#5a3a1a');
        r(9, 4, 4, 1, '#5a3a1a');
        r(3, 4, 1, 3, '#5a3a1a');
        r(7, 4, 1, 3, '#5a3a1a');
        r(12, 4, 1, 3, '#5a3a1a');
        p(4, 5, '#2a2a2a'); p(5, 5, '#2a2a2a');
        p(9, 5, '#2a2a2a'); p(10, 5, '#2a2a2a');
        // Body (saffron)
        r(3, 8, 10, 5, primary);
        r(2, 8, 1, 4, '#c88030');
        r(13, 8, 1, 4, '#c88030');
    }

    _portraitGeneric(p, r, skin, primary) {
        r(3, 1, 10, 2, skin);
        r(2, 2, 12, 6, primary);
    }

    getBounds() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height,
            centerX: this.x + this.width / 2,
            centerY: this.y + this.height / 2,
        };
    }
}
