import torch
import numpy as np
import cv2

class VeilingGlarePRO:
    """
    Veiling Glare PRO
    Simulates light bouncing between physical lens elements, causing a subtle black lift 
    and loss of contrast, driven geometrically by the luminosity of the scene.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "glare_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
                "dispersion": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.05}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_veiling_glare"
    CATEGORY = "Post_Processing_PRO/Optics"
    
    def apply_veiling_glare(self, image, glare_strength, dispersion):
        batch_size, h, w, c = image.shape
        out_images = []
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Veiling glare is essentially extremely out-of-focus light hitting the sensor.
            # To simulate this efficiently, we downscale the image significantly, blur it, and upscale.
            
            # Dispersion controls how much the light spreads across the whole frame vs local
            # dispersion=1.0 is full frame uniform glare. dispersion=0.1 is more localized.
            scale_factor = int(256 * (1.1 - dispersion)) 
            scale_factor = max(4, scale_factor)
            
            low_res = cv2.resize(img, (scale_factor, scale_factor), interpolation=cv2.INTER_AREA)
            
            # Blur the low_res image to simulate light scatter inside lens barrel
            blurred_low_res = cv2.GaussianBlur(low_res, (0, 0), sigmaX=scale_factor/2.0)
            
            # Upscale back to original resolution
            glare_map = cv2.resize(blurred_low_res, (w, h), interpolation=cv2.INTER_CUBIC)
            
            # The glare acts as a black lift, effectively raising minimum luminance.
            # We use Screen blend mode for natural light addition
            glare_map = np.clip(glare_map * glare_strength, 0.0, 1.0)
            result = 1.0 - (1.0 - img) * (1.0 - glare_map)
            
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
