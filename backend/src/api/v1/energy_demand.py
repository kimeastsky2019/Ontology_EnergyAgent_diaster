"""Energy Demand Analysis API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
import logging
import os
import shutil
import tempfile

from src.database import get_db
from src.models.user import User
from src.api.v1.auth import get_current_user
from src.agents.energy_demand_agent import EnergyDemandAgent
from src.services.mcp_service import mcp_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Create agent instance (auto-registers with MCP)
_energy_demand_agent = EnergyDemandAgent()

# Upload directory
UPLOAD_DIR = "/tmp/energy_data_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/analyze")
async def analyze_energy_demand(
    data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Analyze energy demand using AI agent"""
    try:
        # Use MCP service to send request to agent
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "analyze",
            data
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Analysis failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Energy demand analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze/public")
async def analyze_energy_demand_public(
    data: Optional[Dict[str, Any]] = None,
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Analyze energy demand (public access, no auth required) - supports file upload"""
    try:
        request_data = {}
        
        # Handle file upload
        if file:
            # Save uploaded file
            file_location = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File uploaded to {file_location}")
            request_data["data_path"] = file_location
        elif data:
            request_data = data
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either file or data must be provided"
            )
        
        # Use MCP service to send request to agent
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "analyze",
            request_data
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Analysis failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Energy demand analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/preprocess")
async def preprocess_data(
    data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Preprocess energy data"""
    try:
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "preprocess_data",
            data
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Preprocessing failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data preprocessing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preprocessing failed: {str(e)}"
        )


@router.post("/validate-quality")
async def validate_data_quality(
    data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Validate data quality"""
    try:
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "validate_data_quality",
            data
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Validation failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data quality validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/detect-anomalies")
async def detect_anomalies(
    data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Detect anomalies in energy data"""
    try:
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "detect_anomalies",
            data
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Anomaly detection failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}"
        )


@router.post("/train-model")
async def train_forecast_model(
    data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Train forecasting model"""
    try:
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "train_forecast_model",
            data
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Model training failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model training error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )


@router.post("/predict")
async def generate_predictions(
    params: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate energy demand predictions"""
    try:
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "generate_predictions",
            params
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Prediction failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/statistics")
async def get_statistics(
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get energy demand statistics"""
    try:
        response = await mcp_service.send_request(
            "energy-demand-agent",
            "get_statistics",
            {}
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Statistics retrieval failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Statistics retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Statistics retrieval failed: {str(e)}"
        )

