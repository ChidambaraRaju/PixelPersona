export class NPC {
    constructor(ctx, x, y, name, color, description) {
        this.ctx = ctx;
        this.x = x;
        this.y = y;
        this.name = name;
        this.color = color;
        this.description = description;
        this.width = 24;
        this.height = 32;
        this.speed = 30; // slower than player

        // Wander AI
        this.direction = { x: 0, y: 0 };
        this.directionTimer = 0;
        this.directionInterval = 2000 + Math.random() * 2000; // 2-4 seconds
        this.changeDirection();

        // Idle animation
        this.bobOffset = 0;
        this.bobDirection = 1;
    }

    changeDirection() {
        // Random direction
        const directions = [
            { x: 1, y: 0 }, { x: -1, y: 0 },
            { x: 0, y: 1 }, { x: 0, y: -1 },
            { x: 0, y: 0 }  // idle
        ];
        this.direction = directions[Math.floor(Math.random() * directions.length)];
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
        this.x += this.direction.x * this.speed * (dt / 1000);
        this.y += this.direction.y * this.speed * (dt / 1000);

        // Boundary collision (stay in village area)
        if (this.x < 100) { this.x = 100; this.changeDirection(); }
        if (this.x > 700 - this.width) { this.x = 700 - this.width; this.changeDirection(); }
        if (this.y < 100) { this.y = 100; this.changeDirection(); }
        if (this.y > 500 - this.height) { this.y = 500 - this.height; this.changeDirection(); }

        // Bob animation
        this.bobOffset += this.bobDirection * 0.5;
        if (this.bobOffset > 2 || this.bobOffset < 0) this.bobDirection *= -1;
    }

    render() {
        // Character box
        this.ctx.fillStyle = this.color;
        this.ctx.fillRect(this.x, this.y + this.bobOffset, this.width, this.height);

        // Eyes (white)
        this.ctx.fillStyle = '#fff';
        this.ctx.fillRect(this.x + 6, this.y + 8 + this.bobOffset, 4, 4);
        this.ctx.fillRect(this.x + 14, this.y + 8 + this.bobOffset, 4, 4);
    }

    getBounds() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height,
            centerX: this.x + this.width / 2,
            centerY: this.y + this.height / 2
        };
    }
}
