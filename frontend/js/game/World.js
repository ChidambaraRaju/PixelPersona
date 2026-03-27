export class World {
    constructor(ctx) {
        this.ctx = ctx;
        this.width = 800;
        this.height = 600;
        this.tileSize = 32;

        // Simple village colors
        this.colors = {
            ground: '#1a1a2e',
            path: '#2d2d44',
            grass: '#0f1a0f',
            building: '#3d3d5c',
            buildingRoof: '#5c5c8a'
        };
    }

    render() {
        this.drawGround();
        this.drawPaths();
        this.drawBuildings();
    }

    drawGround() {
        // Base ground
        this.ctx.fillStyle = this.colors.grass;
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Village floor area
        this.ctx.fillStyle = this.colors.ground;
        this.ctx.fillRect(100, 100, 600, 400);
    }

    drawPaths() {
        this.ctx.fillStyle = this.colors.path;
        // Horizontal path
        this.ctx.fillRect(0, 280, 800, 40);
        // Vertical path
        this.ctx.fillRect(380, 0, 40, 600);
    }

    drawBuildings() {
        // Simple pixel buildings for atmosphere
        const buildings = [
            { x: 120, y: 120, w: 80, h: 60 },
            { x: 600, y: 120, w: 80, h: 60 },
            { x: 120, y: 420, w: 80, h: 60 },
            { x: 600, y: 420, w: 80, h: 60 }
        ];

        buildings.forEach(b => {
            // Building body
            this.ctx.fillStyle = this.colors.building;
            this.ctx.fillRect(b.x, b.y, b.w, b.h);
            // Roof
            this.ctx.fillStyle = this.colors.buildingRoof;
            this.ctx.fillRect(b.x - 5, b.y - 15, b.w + 10, 20);
        });
    }
}