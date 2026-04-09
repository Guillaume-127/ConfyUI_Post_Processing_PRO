import torch
import numpy as np
import cv2

class LensDistortionPRO:
    """
    Lens Distortion PRO
    Simulates high-fidelity barrel and pincushion distortion of a real optical lens.
    Uses a simplified Brown-Conrady model.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "distort": ("FLOAT", {"default": 0.01, "min": -0.2, "max": 0.2, "step": 0.001}),
                "zoom": ("FLOAT", {"default": 1.05, "min": 1.0, "max": 1.5, "step": 0.01}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_distortion"
    CATEGORY = "Post_Processing_PRO/Optics"
    
    def apply_distortion(self, image, distort, zoom):
        # image shape is [B, H, W, C] in normalized float range [0.0, 1.0]
        batch_size, h, w, c = image.shape
        out_images = []
        
        # Precompute the distortion maps to optimize performance over batch
        # Center of the image
        cx, cy = w / 2.0, h / 2.0
        
        # Generate grid coordinates
        x = np.arange(w, dtype=np.float32) - cx
        y = np.arange(h, dtype=np.float32) - cy
        X, Y = np.meshgrid(x, y)
        
        # Calculate squared distance from center
        R_sq = X**2 + Y**2
        max_R_sq = cx**2 + cy**2
        r_sq_norm = R_sq / (max_R_sq + 1e-6) # Normalized to maintain relative scale
        
        # Calculate distortion factor (Brown-Conrady radial model k1)
        # Factor > 1.0 pushes source pixels outward (creates a barrel-like expansion view)
        factor = 1.0 + distort * r_sq_norm
        
        # Compensate for image shrinkage/expansion by applying zoom
        factor = factor / zoom
        
        # Map back to absolute grid coordinates
        map_x = X * factor + cx
        map_y = Y * factor + cy
        
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)
        
        # Process each frame/image in the batch
        for i in range(batch_size):
            # Convert Tensor [H, W, C] back to numpy and prepare for OpenCV
            img = image[i].cpu().numpy()
            
            # Apply reverse mapping via cv2.remap for high performance and quality
            distorted_img = cv2.remap(
                img, 
                map_x, 
                map_y, 
                interpolation=cv2.INTER_LANCZOS4, # High quality interpolation
                borderMode=cv2.BORDER_REFLECT101  # Natural edge padding
            )
            out_images.append(distorted_img)
            
        # Convert back to Tensor [B, H, W, C]
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
