// Utilities for rendering pixel art sprites

export class SpriteRenderer {
    constructor(ctx) {
        this.ctx = ctx;
    }

    // Draw a simple pixel character from a color
    drawPixelCharacter(x, y, width, height, color, eyeColor = '#fff') {
        const ctx = this.ctx;
        const pixelSize = 4;

        // Body
        ctx.fillStyle = color;
        ctx.fillRect(x, y, width, height);

        // Pixel eyes (simple)
        ctx.fillStyle = eyeColor;
        ctx.fillRect(x + 6, y + 8, pixelSize, pixelSize);
        ctx.fillRect(x + 14, y + 8, pixelSize, pixelSize);
    }
}
