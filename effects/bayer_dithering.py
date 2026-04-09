import torch
import numpy as np
import cv2

class BayerDitheringPRO:
    """
    Bayer Pattern Dithering PRO
    Reintroduces the mathematical grid texture of a physical CFA (Color Filter Array).
    Invaluable for breaking up AI-generated smooth gradients and preventing 8-bit color banding.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 0.02, "min": 0.0, "max": 0.2, "step": 0.001}),
                "pattern_size": ("INT", {"default": 1, "min": 1, "max": 4, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_dithering"
    CATEGORY = "Post_Processing_PRO/Effects"
    
    def apply_dithering(self, image, strength, pattern_size):
        batch_size, h, w, c = image.shape
        out_images = []
        
        # Standard 2x2 Bayer Matrix (normalized between -0.5 and +0.5)
        # 0  2
        # 3  1
        bayer_matrix = np.array([
            [0.0, 0.5],
            [0.75, 0.25]
        ], dtype=np.float32) - 0.5
        
        # Scale the matrix if requested (though physically it should be 1 pixel)
        if pattern_size > 1:
            bayer_matrix = cv2.resize(bayer_matrix, (2*pattern_size, 2*pattern_size), interpolation=cv2.INTER_NEAREST)
        
        matrix_h, matrix_w = bayer_matrix.shape
        
        # Tile the matrix to fill the entire image frame
        tiles_y = (h // matrix_h) + 1
        tiles_x = (w // matrix_w) + 1
        dither_map = np.tile(bayer_matrix, (tiles_y, tiles_x))[:h, :w]
        
        # Add a channel dimension for broadcasting RGB
        dither_map = np.expand_dims(dither_map, axis=-1)
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # Subtly add the dither pattern to the image signal
            result = img + (dither_map * strength)
            
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
