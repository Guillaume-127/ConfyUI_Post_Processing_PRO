import torch
import numpy as np
import cv2

class CinematicAdaptiveSharpeningPRO:
    """
    Cinematic Adaptive Sharpening PRO (CAS Equivalent)
    Intelligently enhances fine details and local contrast without causing aggressive edge ringing
    or introducing unnecessary noise in smooth areas.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "sharpen_strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.05}),
                "edge_protection": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_cas"
    CATEGORY = "Post_Processing_PRO/Effects"
    
    def apply_cas(self, image, sharpen_strength, edge_protection):
        batch_size, h, w, c = image.shape
        out_images = []
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Extract Luminance for sharpening (keeps colors strictly safe from chrominance fringing)
            # We treat RGB explicitly using perceptual weighting
            Y = 0.299 * img[:,:,0] + 0.587 * img[:,:,1] + 0.114 * img[:,:,2]
            
            # Standard Unsharp Mask logic isolated on luminance
            blurred_Y = cv2.GaussianBlur(Y, (0, 0), sigmaX=1.5)
            high_pass = Y - blurred_Y
            
            # Adaptive Protection based on local contrast to prevent ringing
            local_max = cv2.dilate(Y, np.ones((3,3)))
            local_min = cv2.erode(Y, np.ones((3,3)))
            local_contrast = local_max - local_min
            
            # Protection mask: reduces sharpening as local contrast goes dangerously high
            protection_mask = np.clip(1.0 - (local_contrast * edge_protection), 0.0, 1.0)
            
            # Scale the high frequency details
            adaptive_detail = high_pass * sharpen_strength * protection_mask
            
            # Recombining details uniformly across original RGB channels to maintain saturation purity
            detail_tensor = np.stack([adaptive_detail]*3, axis=-1)
            result = img + detail_tensor
            
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
