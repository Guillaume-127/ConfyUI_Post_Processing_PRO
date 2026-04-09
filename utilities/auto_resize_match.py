import torch
import numpy as np
import cv2

class AutoResizeMatchPRO:
    """
    Auto Resize Match PRO
    Automatically resizes an input image to match the exact dimensions of a reference image.
    Uses high-fidelity interpolations (Lanczos4, Bicubic) to ensure pixel-perfect compositing.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "reference_image": ("IMAGE",),
                "interpolation": (["lanczos", "bicubic", "bilinear", "nearest"],),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "match_size"
    CATEGORY = "Post_Processing_PRO/Utilities"
    
    def match_size(self, image, reference_image, interpolation):
        batch_size, h_in, w_in, c_in = image.shape
        _, h_ref, w_ref, _ = reference_image.shape
        
        # S'il n'y a pas besoin de redimensionner, on retourne l'image d'origine pour optimiser.
        if h_ref == h_in and w_ref == w_in:
            return (image,)
            
        out_images = []
        
        # Mappage de l'interpolation OpenCV demandée
        interp_method = cv2.INTER_LANCZOS4
        if interpolation == "bicubic":
            interp_method = cv2.INTER_CUBIC
        elif interpolation == "bilinear":
            interp_method = cv2.INTER_LINEAR
        elif interpolation == "nearest":
            interp_method = cv2.INTER_NEAREST
            
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Redimensionnement optimisé via OpenCV
            resized = cv2.resize(img, (w_ref, h_ref), interpolation=interp_method)
            
            out_images.append(resized)
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
