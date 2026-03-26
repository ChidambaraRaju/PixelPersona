#!/usr/bin/env python3
"""PixelPersona Backend - Main entry point."""
import uvicorn
from pixelpersona.api.routes import app

if __name__ == "__main__":
    uvicorn.run(
        "pixelpersona.api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )