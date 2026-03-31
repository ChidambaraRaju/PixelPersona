// Simple beep sounds using Web Audio API

export class SoundManager {
    constructor() {
        this.ctx = null;
        this.enabled = true;
    }

    init() {
        if (this.ctx) return;
        try {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API not supported');
            this.enabled = false;
        }
    }

    play(type) {
        if (!this.enabled || !this.ctx) return;

        // Resume context if suspended (browser autoplay policy)
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        gain.connect(this.ctx.destination);

        switch(type) {
            case 'step':
                osc.frequency.value = 100;
                gain.gain.value = 0.05;
                osc.type = 'square';
                break;
            case 'interact':
                osc.frequency.value = 440;
                gain.gain.value = 0.1;
                osc.type = 'sine';
                break;
            case 'chat':
                osc.frequency.value = 660;
                gain.gain.value = 0.08;
                osc.type = 'triangle';
                break;
            default:
                osc.frequency.value = 220;
                gain.gain.value = 0.1;
        }

        osc.start();
        osc.stop(this.ctx.currentTime + 0.08);
    }

    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
}
