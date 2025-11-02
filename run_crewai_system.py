#!/usr/bin/env python3
"""
CrewAI Energy System Runner
===========================

Script to run the CrewAI-based energy analysis system.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crewai_energy_system import EnergyCrewOrchestrator, CrewEvent, EventType
from crewai_config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/crewai_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def run_demo_workflow():
    """Run a demonstration workflow"""
    logger.info("Starting CrewAI Energy System Demo...")
    
    # Initialize orchestrator
    orchestrator = EnergyCrewOrchestrator()
    
    try:
        # Run sequential workflow
        logger.info("Running sequential workflow...")
        results = await orchestrator.run_sequential_workflow()
        
        # Print results summary
        logger.info("Workflow Results Summary:")
        for crew_name, result in results.items():
            logger.info(f"  {crew_name}: {str(result)[:100]}...")
        
        # Add some events to demonstrate event handling
        logger.info("Adding demonstration events...")
        
        # Data ingestion event
        data_event = CrewEvent(
            event_type=EventType.DATA_INGESTION,
            timestamp=datetime.now(),
            source_crew="data_ingestion",
            target_crew="forecasting",
            data={"quality_score": 0.95, "samples_collected": 1000},
            priority=2
        )
        orchestrator.add_event(data_event)
        
        # Anomaly detection event
        anomaly_event = CrewEvent(
            event_type=EventType.ANOMALY_DETECTION,
            timestamp=datetime.now(),
            source_crew="anomaly",
            target_crew="demand_control",
            data={"anomalies_detected": 3, "severity": "medium"},
            priority=3
        )
        orchestrator.add_event(anomaly_event)
        
        # Process events
        orchestrator.process_events()
        
        logger.info("Demo workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo workflow failed: {e}")
        raise

async def run_continuous_monitoring():
    """Run continuous monitoring mode"""
    logger.info("Starting continuous monitoring mode...")
    
    orchestrator = EnergyCrewOrchestrator()
    
    try:
        while True:
            logger.info("Running monitoring cycle...")
            
            # Run parallel workflow for quick data collection
            results = await orchestrator.run_parallel_workflow()
            
            # Check for critical events
            if orchestrator.event_queue:
                logger.info(f"Processing {len(orchestrator.event_queue)} pending events...")
                orchestrator.process_events()
            
            # Wait before next cycle
            await asyncio.sleep(300)  # 5 minutes
            
    except KeyboardInterrupt:
        logger.info("Continuous monitoring stopped by user")
    except Exception as e:
        logger.error(f"Continuous monitoring failed: {e}")
        raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CrewAI Energy System")
    parser.add_argument(
        "--mode",
        choices=["demo", "continuous", "api"],
        default="demo",
        help="Run mode: demo, continuous, or api server"
    )
    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Check configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Check configuration
    if args.config_check:
        config = get_config()
        logger.info("Configuration check:")
        logger.info(f"  OpenAI API Key: {'✓' if config['openai']['api_key'] else '✗'}")
        logger.info(f"  Weather API Key: {'✓' if config['weather']['api_key'] else '✗'}")
        logger.info(f"  Database URL: {config['database']['url']}")
        return
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Run based on mode
    if args.mode == "demo":
        asyncio.run(run_demo_workflow())
    elif args.mode == "continuous":
        asyncio.run(run_continuous_monitoring())
    elif args.mode == "api":
        # Import and run FastAPI server
        from crewai_energy_system import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()
