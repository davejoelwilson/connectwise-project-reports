#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from pathlib import Path
import signal
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'CONNECTWISE_URL',
        'CONNECTWISE_COMPANY',
        'CONNECTWISE_PUBLIC_KEY',
        'CONNECTWISE_PRIVATE_KEY',
        'CONNECTWISE_CLIENT_ID',
        'OPENAI_API_KEY',
        'AGENTOPS_API_KEY'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file")
        sys.exit(1)

def run_backend():
    """Run the FastAPI backend server"""
    try:
        logger.info("Starting FastAPI backend...")
        backend_cmd = [
            sys.executable,
            "-m", "uvicorn",
            "backend.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ]
        return subprocess.Popen(
            backend_cmd,
            env=os.environ.copy()
        )
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        return None

def run_frontend():
    """Run the Next.js frontend"""
    try:
        logger.info("Starting Next.js frontend...")
        frontend_cmd = [
            "npm",
            "run", "dev"
        ]
        return subprocess.Popen(
            frontend_cmd,
            cwd="frontend/ai-dashboard",
            env=os.environ.copy()
        )
    except Exception as e:
        logger.error(f"Failed to start frontend: {e}")
        return None

def cleanup(processes):
    """Clean up processes on shutdown"""
    logger.info("Shutting down services...")
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def main():
    """Main entry point"""
    # Check environment
    check_environment()
    
    # Create necessary directories
    data_dir = Path('data')
    for subdir in ['detailed', 'analysis', 'ai_analysis']:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    # Track processes for cleanup
    processes = []
    
    try:
        # Start backend first
        backend_process = run_backend()
        if backend_process:
            processes.append(backend_process)
            # Wait a bit for backend to start
            time.sleep(2)
        
        # Start frontend
        frontend_process = run_frontend()
        if frontend_process:
            processes.append(frontend_process)
            
            # Print access URLs
            logger.info("\n" + "="*50)
            logger.info("Services started successfully!")
            logger.info("Access the dashboard at: http://localhost:3000")
            logger.info("API documentation at: http://localhost:8000/docs")
            logger.info("="*50 + "\n")
            
            # Wait for interrupt
            try:
                while all(p.poll() is None for p in processes):
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received shutdown signal...")
            
    finally:
        cleanup(processes)
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main() 