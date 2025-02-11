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

def run_streamlit():
    """Run the Streamlit dashboard"""
    try:
        logger.info("Starting Streamlit dashboard...")
        streamlit_cmd = [
            sys.executable,  # Use the same Python interpreter
            "-m", "streamlit", "run",
            "backend/visualization/app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ]
        return subprocess.Popen(
            streamlit_cmd,
            env=os.environ.copy()
        )
    except Exception as e:
        logger.error(f"Failed to start Streamlit: {e}")
        return None

def run_analysis_pipeline():
    """Run the initial analysis pipeline"""
    try:
        logger.info("Running initial project analysis...")
        subprocess.run([
            sys.executable,  # Use the same Python interpreter
            "backend/scripts/run_analysis_pipeline.py"
        ], check=True, env=os.environ.copy())
    except subprocess.CalledProcessError as e:
        logger.error(f"Analysis pipeline failed: {e}")
    except Exception as e:
        logger.error(f"Error running analysis pipeline: {e}")

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
        # Run initial analysis
        run_analysis_pipeline()
        
        # Start Streamlit
        streamlit_process = run_streamlit()
        if streamlit_process:
            processes.append(streamlit_process)
            
            # Print access URLs
            logger.info("\n" + "="*50)
            logger.info("Services started successfully!")
            logger.info("Access the dashboard at: http://localhost:8501")
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