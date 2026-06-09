"""LLM status and health endpoints."""

from fastapi import APIRouter

from app.services.llm_service import llm_service
from app.utils.gpu_utils import gpu_manager

router = APIRouter()


@router.get("/gpu-status")
async def get_gpu_status():
    """Get GPU detection and configuration status for LLM inference.
    
    Returns information about:
    - Whether GPU is detected
    - GPU details (name, VRAM)
    - Number of GPU layers configured
    - Backend being used (cuda/cpu)
    """
    gpu_summary = gpu_manager.get_gpu_summary()
    gpu_detected = gpu_summary["gpu_count"] > 0
    
    llm_config = None
    if gpu_detected:
        from app.core.config import settings, LLM_MODEL_PATH
        import os
        model_path = LLM_MODEL_PATH / settings.DEFAULT_MODEL
        env_gpu_layers = os.getenv("LLM_GPU_LAYERS", settings.LLM_GPU_LAYERS)
        llm_config = gpu_manager.get_llama_config(
            str(model_path), env_gpu_layers, model_size="2B"
        )
    
    return {
        "gpu_detected": gpu_detected,
        "gpu_info": gpu_summary,
        "llm_config": llm_config,
        "using_gpu_for_inference": llm_config.get("n_gpu_layers", 0) > 0 if llm_config else False,
    }


@router.get("/llm-health")
async def get_llm_health():
    """Check LLM service health and GPU utilization.
    
    Forces LLM model initialization and returns status.
    """
    try:
        llm_service._ensure_model()
        gpu_summary = gpu_manager.get_gpu_summary()
        gpu_detected = gpu_summary["gpu_count"] > 0
        
        return {
            "status": "healthy",
            "model_loaded": llm_service._initialized,
            "gpu_detected": gpu_detected,
            "gpu_count": gpu_summary["gpu_count"],
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "gpu_detected": gpu_summary["gpu_count"] > 0,
        }