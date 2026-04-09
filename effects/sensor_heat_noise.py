import torch
import numpy as np

class SensorHeatNoisePRO:
    """
    Sensor Heat Noise PRO
    Simulates thermal chromatic noise in the darkest areas of physical digital sensors.
    It targets only the deep shadows (luminance < shadow_threshold).
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "shadow_threshold": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 0.5, "step": 0.01}),
                "noise_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
                "red_noise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
                "blue_noise": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 2.0, "step": 0.05}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_heat_noise"
    CATEGORY = "Post_Processing_PRO/Effects"
    
    def apply_heat_noise(self, image, shadow_threshold, noise_strength, red_noise, blue_noise):
        batch_size, h, w, c = image.shape
        out_images = []
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Calculate perceptive luminance
            luminance = 0.299 * img[:,:,0] + 0.587 * img[:,:,1] + 0.114 * img[:,:,2]
            
            # Generate a mask for shadows. 
            # 1.0 when luminance is 0, 0.0 when luminance >= shadow_threshold
            shadow_mask = np.maximum(shadow_threshold - luminance, 0.0) / (shadow_threshold + 1e-6)
            # Smooth step for a more organic falloff
            shadow_mask = shadow_mask * shadow_mask * (3.0 - 2.0 * shadow_mask)
            
            # Generate Gaussian High Frequency Noise (Normal Distribution)
            # Uniform noise often creates mathematical grids that cause Moiré/linear artifacts on monitors.
            # Normal distribution concentrates around 0.0 with true organic peaks.
            noise_r = np.random.normal(0.0, 0.5, (h, w)) * red_noise
            noise_g = np.random.normal(0.0, 0.5, (h, w)) * 0.2 # Very little green noise
            noise_b = np.random.normal(0.0, 0.5, (h, w)) * blue_noise
            
            noise_map = np.stack([noise_r, noise_g, noise_b], axis=-1)
            
            # Micro-blur to break the pure 1x1 digital pixel stiffness
            # This causes the noise to clump slightly like real physical sensor structures
            noise_map = cv2.GaussianBlur(noise_map, (3, 3), sigmaX=0.6)
            
            # Apply Noise scaled by the shadow mask and overall strength
            result = img + (noise_map * np.expand_dims(shadow_mask, axis=-1) * noise_strength)
            
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
