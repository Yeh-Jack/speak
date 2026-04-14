"""GPU detection and configuration utilities for NVIDIA and AMD GPUs.

Supports NVIDIA (CUDA) and AMD (ROCm) GPUs for LLM inference.
Automatically detects GPU vendor and configures llama-cpp-python backend.

Usage:
    from app.utils.gpu_utils import gpu_manager

    # Detect all GPUs
    gpus = gpu_manager.detect_all_gpus()

    # Get best GPU for LLM
    best = gpu_manager.get_best_gpu()

    # Get llama-cpp-python backend config
    config = gpu_manager.get_llama_config("/path/to/model.gguf")
"""

import logging
import subprocess
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class GPUVendor(Enum):
    """GPU vendor types."""
    NVIDIA = "nvidia"
    AMD = "amd"
    UNKNOWN = "unknown"


class GPUBackend(Enum):
    """llama-cpp-python GPU backends."""
    CUDA = "cuda"        # NVIDIA
    ROCM = "rocm"        # AMD
    CPU = "cpu"          # CPU-only


@dataclass
class GPUInfo:
    """GPU information container."""
    id: int
    name: str
    vendor: GPUVendor
    total_memory_mb: float
    free_memory_mb: float
    used_memory_mb: float
    load_percent: float = 0.0
    temperature_celsius: Optional[float] = None
    driver_version: Optional[str] = None
    backend: GPUBackend
    is_available: bool = True


class GPUManager:
    """GPU manager for NVIDIA and AMD LLM configuration."""

    # VRAM estimates per layer for Q4_K_M quantized models (in MB)
    LAYER_MEMORY_ESTIMATES = {
        "3B": 80,    # Llama 3.2 3B
        "5B": 100,   # Gemma 4 5B
        "7B": 150,   # Qwen2.5 7B
        "8B": 170,   # Gemma 4 8B
    }

    # Total layers per model size
    MODEL_LAYERS = {
        "3B": 28,
        "5B": 28,
        "7B": 35,
        "8B": 36,
    }

    # Safety buffer to leave free VRAM (in MB)
    VRAM_SAFETY_BUFFER_MB = 1024

    def __init__(self):
        self._gpus: List[GPUInfo] = []
        self._detected_vendors: set = set()
        self._nvidia_available = False
        self._amd_available = False

    def detect_all_gpus(self) -> List[GPUInfo]:
        """Detect GPUs from NVIDIA and AMD."""
        self._gpus = []
        self._detected_vendors.clear()

        # Detect in priority order
        self._detect_nvidia()
        self._detect_amd()

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
            import gputil

            gpus = gputil.getGPUs()
            if not gpus:
                return False

            for i, gpu in enumerate(gpus):
                info = GPUInfo(
                    id=len(self._gpus),
                    name=gpu.name,
                    vendor=GPUVendor.NVIDIA,
                    total_memory_mb=gpu.memoryTotal,
                    free_memory_mb=gpu.memoryFree,
                    used_memory_mb=gpu.memoryUsed,
                    load_percent=gpu.load * 100 if hasattr(gpu, 'load') else 0.0,
                    temperature_celsius=getattr(gpu, 'temperature', None),
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

    def _detect_amd(self) -> bool:
        """Detect AMD GPUs using pyamdgpuinfo or rocm-smi."""
        # Try pyamdgpuinfo first (Linux only)
        try:
            import pyamdgpuinfo

            for device in pyamdgpuinfo.get_devices():
                info = GPUInfo(
                    id=len(self._gpus),
                    name=device.name or "AMD GPU",
                    vendor=GPUVendor.AMD,
                    total_memory_mb=device.memory_info.vram_total / (1024**2),
                    free_memory_mb=device.memory_info.vram_free / (1024**2),
                    used_memory_mb=(device.memory_info.vram_total - device.memory_info.vram_free) / (1024**2),
                    backend=GPUBackend.ROCM,
                )
                self._gpus.append(info)
                self._detected_vendors.add(GPUVendor.AMD)

            self._amd_available = True
            logger.info(f"Detected {len(pyamdgpuinfo.get_devices())} AMD GPU(s) via pyamdgpuinfo")
            return True

        except ImportError:
            logger.debug("pyamdgpuinfo not available")
        except Exception as e:
            logger.debug(f"pyamdgpuinfo detection failed: {e}")

        # Fallback: try rocm-smi
        return self._detect_amd_rocm_smi()

    def _detect_amd_rocm_smi(self) -> bool:
        """Detect AMD GPUs using rocm-smi command."""
        try:
            result = subprocess.run(
                ["rocm-smi", "--showproductname", "--showvram", "--showuse"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return self._parse_rocm_smi(result.stdout)
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.debug("rocm-smi not available")
        except Exception as e:
            logger.debug(f"rocm-smi detection failed: {e}")

        return False

    def _parse_rocm_smi(self, output: str) -> bool:
        """Parse rocm-smi output."""
        lines = output.strip().split('\n')
        gpu_count = 0

        for line in lines:
            if 'GPU' in line and 'VRAM' in line:
                gpu_count += 1
                info = GPUInfo(
                    id=len(self._gpus),
                    name=f"AMD GPU {gpu_count}",
                    vendor=GPUVendor.AMD,
                    total_memory_mb=0,
                    free_memory_mb=0,
                    used_memory_mb=0,
                    backend=GPUBackend.ROCM,
                )
                self._gpus.append(info)
                self._detected_vendors.add(GPUVendor.AMD)

        if gpu_count > 0:
            self._amd_available = True
            logger.info(f"Detected {gpu_count} AMD GPU(s) via rocm-smi")
            return True

        return False

    def get_best_gpu(self) -> Optional[GPUInfo]:
        """Get the best GPU for LLM inference."""
        if not self._gpus:
            self.detect_all_gpus()

        if not self._gpus:
            return None

        # Priority: NVIDIA > AMD
        priority_map = {
            GPUVendor.NVIDIA: 2,
            GPUVendor.AMD: 1,
            GPUVendor.UNKNOWN: 0,
        }

        # Sort by priority and free VRAM
        sorted_gpus = sorted(
            self._gpus,
            key=lambda g: (priority_map.get(g.vendor, 0), g.free_memory_mb),
            reverse=True
        )

        return sorted_gpus[0] if sorted_gpus else None

    def calculate_optimal_gpu_layers(
        self,
        model_size: str = "7B",
        gpu: Optional[GPUInfo] = None
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
                f"Insufficient VRAM on {gpu.name}: "
                f"{gpu.free_memory_mb:.0f}MB free. Using CPU-only."
            )
            return 0

        layer_memory = self.LAYER_MEMORY_ESTIMATES.get(model_size, 150)
        total_layers = self.MODEL_LAYERS.get(model_size, 35)

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
        self,
        model_path: str,
        env_gpu_layers: Optional[str] = None,
        model_size: str = "7B"
    ) -> Dict[str, Any]:
        """
        Get complete llama-cpp-python configuration.

        Returns dict with:
            - model_path: str
            - n_gpu_layers: int
            - n_ctx: int
            - backend: str (cuda/rocm/cpu)
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

                if requested > available:
                    logger.warning(
                        f"Requested {requested} layers exceeds available VRAM. "
                        f"Using {available} layers."
                    )
                    layers = available
                else:
                    total = self.MODEL_LAYERS.get(model_size, 35)
                    layers = min(requested, total)
            except ValueError:
                layers = self.calculate_optimal_gpu_layers(model_size, gpu)

        config["n_gpu_layers"] = layers
        config["backend"] = gpu.backend.value

        logger.info(
            f"LLM Config: {layers} layers on {gpu.name} "
            f"({gpu.backend.value})"
        )

        return config

    def get_gpu_summary(self) -> Dict[str, Any]:
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
            ]
        }


# Singleton instance
gpu_manager = GPUManager()


# Convenience functions
def detect_all_gpus() -> List[GPUInfo]:
    """Detect all GPUs."""
    return gpu_manager.detect_all_gpus()


def get_best_gpu() -> Optional[GPUInfo]:
    """Get best GPU for LLM."""
    return gpu_manager.get_best_gpu()


def calculate_gpu_layers(model_size: str = "7B") -> int:
    """Calculate optimal GPU layers."""
    return gpu_manager.calculate_optimal_gpu_layers(model_size)


def get_llama_config(
    model_path: str,
    env_gpu_layers: Optional[str] = None,
    model_size: str = "7B"
) -> Dict[str, Any]:
    """Get llama-cpp-python configuration."""
    return gpu_manager.get_llama_config(model_path, env_gpu_layers, model_size)


def get_gpu_summary() -> Dict[str, Any]:
    """Get GPU summary."""
    return gpu_manager.get_gpu_summary()
