"""GPU detection and configuration utilities for NVIDIA GPUs.

Supports NVIDIA (CUDA) GPUs for LLM inference.
Automatically detects GPU and configures llama-cpp-python backend.

Usage:
    from app.utils.gpu_utils import gpu_manager

    # Detect all GPUs
    gpus = gpu_manager.detect_all_gpus()

    # Get best GPU for LLM
    best = gpu_manager.get_best_gpu()

    # Get llama-cpp-python backend config
    config = gpu_manager.get_llama_config("/path/to/model.gguf")
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class GPUVendor(Enum):
    """GPU vendor types."""

    NVIDIA = "nvidia"


class GPUBackend(Enum):
    """llama-cpp-python GPU backends."""

    CUDA = "cuda"  # NVIDIA
    CPU = "cpu"  # CPU-only


@dataclass
class GPUInfo:
    """GPU information container."""

    id: int
    name: str
    vendor: GPUVendor
    total_memory_mb: float
    free_memory_mb: float
    used_memory_mb: float
    backend: GPUBackend
    load_percent: float = 0.0
    temperature_celsius: float | None = None
    driver_version: str | None = None
    is_available: bool = True


class GPUManager:
    """GPU manager for NVIDIA LLM configuration."""

    # VRAM estimates per layer for Q4_K_M quantized models (in MB)
    # Only models under 6B are supported
    LAYER_MEMORY_ESTIMATES = {
        "0.5B": 35,  # Qwen3.5 0.5B
        "1.5B": 45,  # Qwen3.5 1.5B
        "2B": 50,  # Qwen3.5-2B (default model)
        "3B": 80,  # Llama 3.2 3B, Qwen3.5 3B
        "4B": 90,  # Gemma 4 4B
        "5B": 100,  # Gemma 4 5B
    }

    # Total layers per model size
    MODEL_LAYERS = {
        "0.5B": 24,
        "1.5B": 28,
        "2B": 28,  # Qwen3.5-2B has 28 layers
        "3B": 28,
        "4B": 34,
        "5B": 28,
    }

    # Safety buffer to leave free VRAM (in MB)
    VRAM_SAFETY_BUFFER_MB = 1024

    def __init__(self):
        self._gpus: list[GPUInfo] = []
        self._detected_vendors: set = set()
        self._nvidia_available = False

    def detect_all_gpus(self) -> list[GPUInfo]:
        """Detect NVIDIA GPUs."""
        self._gpus = []
        self._detected_vendors.clear()

        # Detect NVIDIA GPUs
        self._detect_nvidia()

        if not self._gpus:
            logger.info("No GPU detected, will use CPU-only mode")
        else:
            logger.info(f"Total GPUs detected: {len(self._gpus)}")
            for gpu in self._gpus:
                logger.info(
                    f"  GPU {gpu.id}: {gpu.name} ({gpu.vendor.value}) - "
                    f"VRAM: {gpu.free_memory_mb:.0f}MB free / "
                    f"{gpu.total_memory_mb:.0f}MB total"
                )

        return self._gpus

    def _detect_nvidia(self) -> bool:
        """Detect NVIDIA GPUs using GPUtil."""
        try:
            from GPUtil import GPUtil

            gpus = GPUtil.getGPUs()
            if not gpus:
                return False

            for gpu in gpus:
                info = GPUInfo(
                    id=len(self._gpus),
                    name=gpu.name,
                    vendor=GPUVendor.NVIDIA,
                    total_memory_mb=gpu.memoryTotal,
                    free_memory_mb=gpu.memoryFree,
                    used_memory_mb=gpu.memoryUsed,
                    load_percent=gpu.load * 100 if hasattr(gpu, "load") else 0.0,
                    temperature_celsius=getattr(gpu, "temperature", None),
                    backend=GPUBackend.CUDA,
                )
                self._gpus.append(info)
                self._detected_vendors.add(GPUVendor.NVIDIA)

            self._nvidia_available = True
            logger.info(f"Detected {len(gpus)} NVIDIA GPU(s)")
            return True

        except ImportError:
            logger.debug("GPUtil not available, NVIDIA detection skipped")
        except Exception as e:
            logger.warning(f"NVIDIA GPU detection failed: {e}")

        return False

    def get_best_gpu(self) -> GPUInfo | None:
        """Get the best GPU for LLM inference."""
        if not self._gpus:
            self.detect_all_gpus()

        if not self._gpus:
            return None

        # Sort by free VRAM (highest first)
        sorted_gpus = sorted(
            self._gpus,
            key=lambda g: g.free_memory_mb,
            reverse=True,
        )

        return sorted_gpus[0] if sorted_gpus else None

    def calculate_optimal_gpu_layers(
        self, model_size: str = "2B", gpu: GPUInfo | None = None
    ) -> int:
        """Calculate optimal GPU layers based on available VRAM."""
        if not gpu:
            gpu = self.get_best_gpu()

        if not gpu:
            logger.info("No GPU available, using CPU-only mode")
            return 0

        available_vram = gpu.free_memory_mb - self.VRAM_SAFETY_BUFFER_MB

        if available_vram <= 0:
            logger.warning(
                f"Insufficient VRAM on {gpu.name}: {gpu.free_memory_mb:.0f}MB free. Using CPU-only."
            )
            return 0

        layer_memory = self.LAYER_MEMORY_ESTIMATES.get(model_size, 50)
        total_layers = self.MODEL_LAYERS.get(model_size, 28)

        max_layers = int(available_vram / layer_memory)
        optimal_layers = min(max_layers, total_layers)

        logger.info(
            f"GPU: {gpu.name} ({gpu.vendor.value}) | "
            f"Available: {available_vram:.0f}MB | "
            f"Layer size: {layer_memory}MB | "
            f"Offloading: {optimal_layers}/{total_layers} layers"
        )

        return optimal_layers

    def get_llama_config(
        self, model_path: str, env_gpu_layers: str | None = None, model_size: str = "2B"
    ) -> dict[str, Any]:
        """
        Get complete llama-cpp-python configuration.

        Returns dict with:
            - model_path: str
            - n_gpu_layers: int
            - n_ctx: int
            - backend: str (cuda/cpu)
        """
        config = {
            "model_path": model_path,
            "n_ctx": 4096,
            "verbose": False,
        }

        # Parse environment variable
        if env_gpu_layers == "0":
            config["n_gpu_layers"] = 0
            config["backend"] = "cpu"
            logger.info("CPU-only mode selected via LLM_GPU_LAYERS=0")
            return config

        # Get best GPU
        gpu = self.get_best_gpu()

        if not gpu:
            logger.warning("No GPU detected, falling back to CPU")
            config["n_gpu_layers"] = 0
            config["backend"] = "cpu"
            return config

        # Calculate layers
        if env_gpu_layers == "-1" or env_gpu_layers is None:
            layers = self.calculate_optimal_gpu_layers(model_size, gpu)
        else:
            try:
                requested = int(env_gpu_layers)
                available = self.calculate_optimal_gpu_layers(model_size, gpu)
                total = self.MODEL_LAYERS.get(model_size, 28)

                if requested > available:
                    logger.warning(
                        f"Requested {requested} layers exceeds available VRAM. "
                        f"Using {available} layers."
                    )
                    layers = available
                else:
                    layers = min(requested, total)
            except ValueError:
                layers = self.calculate_optimal_gpu_layers(model_size, gpu)

        config["n_gpu_layers"] = layers
        config["backend"] = gpu.backend.value

        logger.info(f"LLM Config: {layers} layers on {gpu.name} ({gpu.backend.value})")

        return config

    def get_gpu_summary(self) -> dict[str, Any]:
        """Get summary of all detected GPUs."""
        if not self._gpus:
            self.detect_all_gpus()

        return {
            "gpu_count": len(self._gpus),
            "vendors_detected": [v.value for v in self._detected_vendors],
            "gpus": [
                {
                    "id": gpu.id,
                    "name": gpu.name,
                    "vendor": gpu.vendor.value,
                    "total_vram_mb": gpu.total_memory_mb,
                    "free_vram_mb": gpu.free_memory_mb,
                    "backend": gpu.backend.value,
                }
                for gpu in self._gpus
            ],
        }


# Singleton instance
gpu_manager = GPUManager()


# Convenience functions
def detect_all_gpus() -> list[GPUInfo]:
    """Detect all GPUs."""
    return gpu_manager.detect_all_gpus()


def get_best_gpu() -> GPUInfo | None:
    """Get best GPU for LLM."""
    return gpu_manager.get_best_gpu()


def calculate_gpu_layers(model_size: str = "2B") -> int:
    """Calculate optimal GPU layers."""
    return gpu_manager.calculate_optimal_gpu_layers(model_size)


def get_llama_config(
    model_path: str, env_gpu_layers: str | None = None, model_size: str = "2B"
) -> dict[str, Any]:
    """Get llama-cpp-python configuration."""
    return gpu_manager.get_llama_config(model_path, env_gpu_layers, model_size)


def get_gpu_summary() -> dict[str, Any]:
    """Get GPU summary."""
    return gpu_manager.get_gpu_summary()
