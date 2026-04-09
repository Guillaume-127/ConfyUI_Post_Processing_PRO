import torch
import numpy as np
import cv2

class SubsurfaceDiffusionPRO:
    """
    Subsurface Diffusion PRO
    Simulates light penetrating the epidermis and illuminating the blood vessels.
    Blurs the Red channel exclusively to soften skin without losing pore details in Green/Blue.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "red_scatter_radius": ("INT", {"default": 15, "min": 1, "max": 100, "step": 1}),
                "strength": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_subsurface"
    CATEGORY = "Post_Processing_PRO/Effects"
    
    def apply_subsurface(self, image, red_scatter_radius, strength):
        batch_size, h, w, c = image.shape
        out_images = []
        
        blur_ksize = int(red_scatter_radius) | 1
        sigma = blur_ksize / 3.0
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Split channels
            R, G, B = img[:,:,0], img[:,:,1], img[:,:,2]
            
            # Apply Scatter to Red Channel
            if blur_ksize > 1:
                scattered_R = cv2.GaussianBlur(R, (blur_ksize, blur_ksize), sigmaX=sigma, sigmaY=sigma)
            else:
                scattered_R = R
                
            # Blend
            final_R = (R * (1.0 - strength)) + (scattered_R * strength)
            
            # Recombine with untouched Green and Blue channels
            result = np.stack([final_R, G, B], axis=-1)
            
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
