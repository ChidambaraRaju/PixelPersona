export class Player {
    constructor(ctx, x, y) {
        this.ctx = ctx;
        this.x = x;
        this.y = y;

        // Sprite scale: each "pixel" in our 16x24 sprite is drawn as SCALE × SCALE px on canvas
        this.SCALE = 3;
        this.width = 16 * this.SCALE;
        this.height = 24 * this.SCALE;

        this.speed = 150; // pixels per second

        // Animation state
        this.direction = 'down';  // 'up', 'down', 'left', 'right'
        this.isWalking = false;
        this.animationFrame = 0;  // 0 or 1 for 2-frame walk
        this.animationTimer = 0;
        this.animationSpeed = 150; // ms per frame

        // Chat manager reference (may not be set yet)
        this._chatManager = null;

        // Movement keys
        this.keys = { up: false, down: false, left: false, right: false };

        // Step sound throttle
        this.stepTimer = 0;
        this.stepInterval = 280; // ms

        // Initialize input
        this._setupControls();
    }

    _setupControls() {
        window.addEventListener('keydown', (e) => {
            const cm = this._getChatManager();
            if (cm && cm.isDialogOpen()) return;
            switch (e.code) {
                case 'ArrowUp': case 'KeyW': this.keys.up = true; break;
                case 'ArrowDown': case 'KeyS': this.keys.down = true; break;
                case 'ArrowLeft': case 'KeyA': this.keys.left = true; break;
                case 'ArrowRight': case 'KeyD': this.keys.right = true; break;
            }
        });

        window.addEventListener('keyup', (e) => {
            switch (e.code) {
                case 'ArrowUp': case 'KeyW': this.keys.up = false; break;
                case 'ArrowDown': case 'KeyS': this.keys.down = false; break;
                case 'ArrowLeft': case 'KeyA': this.keys.left = false; break;
                case 'ArrowRight': case 'KeyD': this.keys.right = false; break;
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

    update(dt) {
        const cm = this._getChatManager();
        if (cm && cm.isDialogOpen()) return;

        let dx = 0, dy = 0;
        if (this.keys.up) dy -= 1;
        if (this.keys.down) dy += 1;
        if (this.keys.left) dx -= 1;
        if (this.keys.right) dx += 1;

        // Normalize diagonal
        if (dx !== 0 && dy !== 0) {
            dx *= 0.707;
            dy *= 0.707;
        }

        const wasMoving = this.isWalking;
        this.isWalking = dx !== 0 || dy !== 0;

        // Update direction
        if (dx > 0) this.direction = 'right';
        else if (dx < 0) this.direction = 'left';
        else if (dy > 0) this.direction = 'down';
        else if (dy < 0) this.direction = 'up';

        // Apply movement
        this.x += dx * this.speed * (dt / 1000);
        this.y += dy * this.speed * (dt / 1000);

        // Boundary
        this.x = Math.max(0, Math.min(800 - this.width, this.x));
        this.y = Math.max(0, Math.min(600 - this.height, this.y));

        // Animation frame update
        if (this.isWalking) {
            this.animationTimer += dt;
            if (this.animationTimer >= this.animationSpeed) {
                this.animationFrame = (this.animationFrame + 1) % 2;
                this.animationTimer = 0;

                // Step sound
                if (window.soundManager) {
                    window.soundManager.play('step');
                }
            }
        } else {
            this.animationFrame = 0;
            this.animationTimer = 0;
        }
    }

    render() {
        this._drawSprite(this.direction, this.animationFrame, this.isWalking);
    }

    /**
     * Draw a 16x24 pixel art character.
     * Colors: blue adventurer with brown hair.
     * direction: 'up' | 'down' | 'left' | 'right'
     * frame: 0 | 1 (walk bounce offset)
     * walking: boolean
     */
    _drawSprite(direction, frame, walking) {
        const ctx = this.ctx;
        const s = this.SCALE;  // pixel size
        const px = Math.round(this.x);
        const py = Math.round(this.y) + (walking && frame === 1 ? -s : 0);

        // Color palette
        const C = {
            hair:    '#3a2a1a',
            skin:    '#e8c8a8',
            shirt:   '#4a6a9a',
            shirtD:  '#3a5a8a',
            pants:   '#2a3a4a',
            shoe:    '#1a1a1a',
            outline: '#0a0a1a',
            eye:     '#ffffff',
            eyePup:  '#1a1a1a',
        };

        // Helper: draw one "pixel" (s×s rect)
        const p = (dx, dy, color) => {
            ctx.fillStyle = color;
            ctx.fillRect(px + dx * s, py + dy * s, s, s);
        };

        // Helper: fill rect (for multi-pixel shapes)
        const r = (dx, dy, w, h, color) => {
            ctx.fillStyle = color;
            ctx.fillRect(px + dx * s, py + dy * s, w * s, h * s);
        };

        // ─── Hair / Head outline ───
        r(3, 1, 10, 1, C.hair);       // top of head
        r(2, 2, 12, 1, C.hair);       // head top
        r(1, 3, 14, 1, C.hair);       // head
        r(1, 4, 14, 3, C.skin);       // face (skin) - wider
        r(1, 7, 14, 1, C.hair);       // chin
        r(2, 8, 12, 1, C.outline);    // neck outline

        // Back hair (for up-facing or sides)
        if (direction === 'up') {
            r(3, 2, 10, 5, C.hair);
            r(2, 3, 12, 3, C.hair);
        } else if (direction === 'left') {
            r(11, 2, 4, 5, C.hair);
        } else if (direction === 'right') {
            r(1, 2, 4, 5, C.hair);
        }

        // ─── Eyes ───
        if (direction !== 'up') {
            if (direction === 'down') {
                // Two eyes looking forward
                p(4, 4, C.eye); p(5, 4, C.eye);
                p(4, 5, C.eyePup); p(5, 5, C.eyePup);
                p(9, 4, C.eye); p(10, 4, C.eye);
                p(9, 5, C.eyePup); p(10, 5, C.eyePup);
            } else if (direction === 'left') {
                // Left profile eye
                p(3, 4, C.eye); p(4, 4, C.eye);
                p(3, 5, C.eyePup); p(4, 5, C.eyePup);
            } else if (direction === 'right') {
                // Right profile eye
                p(10, 4, C.eye); p(11, 4, C.eye);
                p(10, 5, C.eyePup); p(11, 5, C.eyePup);
            }
        }

        // ─── Body / Shirt ───
        r(3, 9, 10, 5, C.shirt);        // torso
        r(2, 9, 1, 4, C.shirtD);        // left shading
        r(13, 9, 1, 4, C.shirtD);       // right shading
        // Collar
        r(6, 9, 4, 1, C.shirtD);

        // Arms
        if (direction === 'left') {
            r(0, 10, 2, 4, C.shirt);
            r(14, 10, 2, 3, C.shirtD); // back arm
        } else if (direction === 'right') {
            r(14, 10, 2, 4, C.shirt);
            r(0, 10, 2, 3, C.shirtD);  // back arm
        } else {
            r(0, 10, 2, 4, C.shirt);
            r(14, 10, 2, 4, C.shirt);
        }

        // ─── Pants ───
        r(3, 14, 4, 3, C.pants);
        r(9, 14, 4, 3, C.pants);
        r(3, 14, 1, 3, C.outline);
        r(12, 14, 1, 3, C.outline);

        // Leg gap
        r(7, 14, 2, 3, C.skin);

        // Walking animation: legs shift
        if (walking) {
            if (frame === 0) {
                // Neutral stance - slightly wider
                r(3, 14, 4, 3, C.pants);
                r(9, 14, 4, 3, C.pants);
            } else {
                // Step pose
                r(2, 14, 4, 3, C.pants);
                r(10, 14, 4, 3, C.pants);
            }
        }

        // ─── Shoes ───
        r(2, 17, 5, 1, C.shoe);
        r(9, 17, 5, 1, C.shoe);
        r(2, 18, 5, 1, C.shoe); // sole
        r(9, 18, 5, 1, C.shoe);
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
