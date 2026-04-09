import torch
import numpy as np
import cv2

class FilmGrainPRO:
    """
    Film Grain PRO
    Generates genuine physical film-like noise on the frame, featuring scalable 
    clumping (thickness) and optional monochromatic structures.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 2.0, "step": 0.01}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 5.0, "step": 0.1}),
                "monochromatic": ("BOOLEAN", {"default": False}),
            }
        }
        
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_film_grain"
    CATEGORY = "Post_Processing_PRO/Effects"
    
    def apply_film_grain(self, image, strength, scale, monochromatic):
        batch_size, h, w, c = image.shape
        out_images = []
        
        # Calculate resolution for generating the grain map
        # scale > 1.0 makes the grain chunks bigger
        grain_h = max(1, int(h / scale))
        grain_w = max(1, int(w / scale))
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Generate gaussian noise
            if monochromatic:
                noise = np.random.normal(0.0, 0.5, (grain_h, grain_w))
                noise = np.stack([noise]*3, axis=-1)
            else:
                noise = np.random.normal(0.0, 0.5, (grain_h, grain_w, 3))
                
            # Upsample if dealing with thick grain scale
            if scale != 1.0:
                noise = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
                
            # Add to the image using a linear light approach, mimicking exposure variance
            result = img + (noise * strength)
            
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
