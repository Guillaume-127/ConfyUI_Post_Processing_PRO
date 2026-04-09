import torch
import numpy as np
import cv2

class LateralChromaticAberrationPRO:
    """
    Lateral Chromatic Aberration PRO
    Simulates the physical inability of a lens to focus all colors to the same convergence point.
    Displaces the red and blue channels radially from the center of the image.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "red_dispersion": ("FLOAT", {"default": 0.003, "min": -0.05, "max": 0.05, "step": 0.001}),
                "blue_dispersion": ("FLOAT", {"default": -0.003, "min": -0.05, "max": 0.05, "step": 0.001}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_aberration"
    CATEGORY = "Post_Processing_PRO/Optics"
    
    def apply_aberration(self, image, red_dispersion, blue_dispersion):
        batch_size, h, w, c = image.shape
        out_images = []
        
        # Center of the image
        cx, cy = w / 2.0, h / 2.0
        
        # Grid coordinates
        x = np.arange(w, dtype=np.float32) - cx
        y = np.arange(h, dtype=np.float32) - cy
        X, Y = np.meshgrid(x, y)
        
        # Normalized squared distance from center
        R_sq = X**2 + Y**2
        max_R_sq = cx**2 + cy**2
        r_sq_norm = R_sq / (max_R_sq + 1e-6)
        
        # Scaling factors for R and B based on distance from center
        # Green remains at 1.0 (perfectly in focus reference)
        factor_R = 1.0 + red_dispersion * r_sq_norm
        factor_B = 1.0 + blue_dispersion * r_sq_norm
        
        # Map source coordinates
        map_x_R = (X * factor_R + cx).astype(np.float32)
        map_y_R = (Y * factor_R + cy).astype(np.float32)
        
        map_x_B = (X * factor_B + cx).astype(np.float32)
        map_y_B = (Y * factor_B + cy).astype(np.float32)
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Split channels
            # ComfyUI is RGB format by default
            R, G, B = img[:,:,0], img[:,:,1], img[:,:,2]
            
            # Apply displacement using high quality interpolation
            distorted_R = cv2.remap(R, map_x_R, map_y_R, interpolation=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT101)
            distorted_B = cv2.remap(B, map_x_B, map_y_B, interpolation=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT101)
            
            # Recombine
            result = np.stack([distorted_R, G, distorted_B], axis=-1)
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
