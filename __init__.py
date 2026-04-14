from .optics.lens_distortion import LensDistortionPRO
from .optics.veiling_glare import VeilingGlarePRO
from .optics.lateral_chromatic_aberration import LateralChromaticAberrationPRO
from .optics.chromatic_aberration import ChromaticAberrationPRO

from .effects.halation import HalationPRO
from .effects.specular_micro_bloom import SpecularMicroBloomPRO
from .effects.sensor_heat_noise import SensorHeatNoisePRO
from .effects.bayer_dithering import BayerDitheringPRO
from .effects.subsurface_diffusion import SubsurfaceDiffusionPRO
from .effects.film_grain import FilmGrainPRO
from .effects.cinematic_adaptive_sharpening import CinematicAdaptiveSharpeningPRO

from .grading.color_match import CinematicColorMatchPRO

from .utilities.auto_resize_match import AutoResizeMatchPRO

# Mapping the Node Class implementation to a unique internal identifier for ComfyUI
NODE_CLASS_MAPPINGS = {
    # Optics
    "LensDistortionPRO": LensDistortionPRO,
    "VeilingGlarePRO": VeilingGlarePRO,
    "LateralChromaticAberrationPRO": LateralChromaticAberrationPRO,
    "ChromaticAberrationPRO": ChromaticAberrationPRO,
    
    # Effects
    "HalationPRO": HalationPRO,
    "SpecularMicroBloomPRO": SpecularMicroBloomPRO,
    "SensorHeatNoisePRO": SensorHeatNoisePRO,
    "BayerDitheringPRO": BayerDitheringPRO,
    "SubsurfaceDiffusionPRO": SubsurfaceDiffusionPRO,
    "FilmGrainPRO": FilmGrainPRO,
    "CinematicAdaptiveSharpeningPRO": CinematicAdaptiveSharpeningPRO,
    
    # Grading
    "CinematicColorMatchPRO": CinematicColorMatchPRO,
    
    # Utilities
    "AutoResizeMatchPRO": AutoResizeMatchPRO
}

# Display name mapping for the ComfyUI nodes search & UI
NODE_DISPLAY_NAME_MAPPINGS = {
    # Optics
    "LensDistortionPRO": "Lens Distortion PRO",
    "VeilingGlarePRO": "Veiling Glare PRO",
    "LateralChromaticAberrationPRO": "Lateral Chromatic Aberration PRO",
    "ChromaticAberrationPRO": "Chromatic Aberration PRO",
    
    # Effects
    "HalationPRO": "Halation PRO",
    "SpecularMicroBloomPRO": "Specular Micro-Bloom PRO",
    "SensorHeatNoisePRO": "Sensor Heat Noise PRO",
    "BayerDitheringPRO": "Bayer Dithering PRO",
    "SubsurfaceDiffusionPRO": "Subsurface Diffusion PRO",
    "FilmGrainPRO": "Film Grain PRO",
    "CinematicAdaptiveSharpeningPRO": "Cinematic Adaptive Sharpening PRO",
    
    # Grading
    "CinematicColorMatchPRO": "Cinematic Color Match PRO",
    
    # Utilities
    "AutoResizeMatchPRO": "Auto Resize Match PRO"
}

# Exporting these enables ComfyUI logic to seamlessly parse and load our custom nodes
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
