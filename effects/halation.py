import torch
import numpy as np
import cv2

class HalationPRO:
    """
    Halation PRO
    Simulates light oxidation effects on cinematic analog film stock, by blooming highlights
    and tinting them with a soft glow, then blending them back.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "strength": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                "radius": ("INT", {"default": 20, "min": 1, "max": 100, "step": 1}),
                "red_tint": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
                "green_tint": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 2.0, "step": 0.01}),
                "blue_tint": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 2.0, "step": 0.01}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_halation"
    CATEGORY = "Post_Processing_PRO/Effects"
    
    def apply_halation(self, image, threshold, strength, radius, red_tint, green_tint, blue_tint):
        # image shape is [B, H, W, C] -> Tensor RGB format
        batch_size, h, w, c = image.shape
        out_images = []
        
        # Ensure kernel size is odd for GaussianBlur
        blur_ksize = int(radius) | 1 
        
        # OpenCV processes the array directly, no need for BGR conversion 
        # since we treat data generically by plane. RGB is safely preserved.
        tint = np.array([red_tint, green_tint, blue_tint], dtype=np.float32)
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # 1. Isolate High Luminance parts using a soft roll-off threshold
            highlights = np.maximum(img - threshold, 0.0)
            highlights = highlights / (1.0 - threshold + 1e-6) # Normalize back to 0-1
            
            # 2. Bloom/Glow with Gaussian Blur
            if blur_ksize > 1:
                # Dynamic sigma generation relative to blur radius
                sigma = blur_ksize / 3.0
                blurred = cv2.GaussianBlur(highlights, (blur_ksize, blur_ksize), sigmaX=sigma, sigmaY=sigma)
            else:
                blurred = highlights
                
            # 3. Add Film Stock Tinting & Strength
            halo = blurred * tint * strength
            
            # 4. Film Composite Blend via Screen blend mode
            # Screen(A, B) = 1.0 - (1.0 - A) * (1.0 - B)
            halo = np.clip(halo, 0.0, 1.0)
            img_clip = np.clip(img, 0.0, 1.0)
            blended = 1.0 - (1.0 - img_clip) * (1.0 - halo)
            
            out_images.append(np.clip(blended, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
