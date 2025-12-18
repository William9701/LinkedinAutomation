from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

from .routes import posts, schedule, topics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LinkedIn Automation API",
    description="API for automated and manual LinkedIn content posting",
    version="2.0.0"
)

# Configure CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://frontend-j3h2zermj-obi-williams-projects.vercel.app",
        "*"  # Allow all origins for now
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(posts.router, prefix="/api", tags=["Posts"])
app.include_router(schedule.router, prefix="/api", tags=["Schedule"])
app.include_router(topics.router, prefix="/api", tags=["Topics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LinkedIn Automation API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
