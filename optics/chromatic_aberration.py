import torch
import numpy as np

class ChromaticAberrationPRO:
    """
    Chromatic Aberration PRO (Standard)
    Performs a standard, aggressive uniform shift of color channels. Emulates cheap 90s vintage lenses 
    or synthetic digital glitches across the entire frame.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "shift_x": ("INT", {"default": 3, "min": -100, "max": 100, "step": 1}),
                "shift_y": ("INT", {"default": 1, "min": -100, "max": 100, "step": 1}),
            }
        }
        
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_linear_ca"
    CATEGORY = "Post_Processing_PRO/Optics"
    
    def apply_linear_ca(self, image, shift_x, shift_y):
        batch_size, h, w, c = image.shape
        out_images = []
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            R, G, B = img[:,:,0], img[:,:,1], img[:,:,2]
            
            if shift_x != 0 or shift_y != 0:
                # Roll slices for performance
                shifted_R = np.roll(R, (shift_y, shift_x), axis=(0, 1))
                shifted_B = np.roll(B, (-shift_y, -shift_x), axis=(0, 1))
                
                # Cleanup edge wrap-around artifacts
                if shift_y > 0:
                    shifted_R[:shift_y, :] = R[:shift_y, :]
                    shifted_B[-shift_y:, :] = B[-shift_y:, :]
                elif shift_y < 0:
                    shifted_R[shift_y:, :] = R[shift_y:, :]
                    shifted_B[:-shift_y, :] = B[:-shift_y, :]
                    
                if shift_x > 0:
                    shifted_R[:, :shift_x] = R[:, :shift_x]
                    shifted_B[:, -shift_x:] = B[:, -shift_x:]
                elif shift_x < 0:
                    shifted_R[:, shift_x:] = R[:, shift_x:]
                    shifted_B[:, :-shift_x] = B[:, :-shift_x]
                    
                result = np.stack([shifted_R, G, shifted_B], axis=-1)
            else:
                result = img
                
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
