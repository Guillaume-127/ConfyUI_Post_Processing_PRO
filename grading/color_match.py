import torch
import numpy as np
import cv2

class CinematicColorMatchPRO:
    """
    Cinematic Color Match PRO
    Transfers the color grading (color palette and contrast) from a reference image
    to the target image using the Reinhard color transfer algorithm in L*a*b* space.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "reference_image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_color_match"
    CATEGORY = "Post_Processing_PRO/Grading"
    
    def get_mean_and_std(self, x):
        x_mean, x_std = cv2.meanStdDev(x)
        x_mean = np.hstack(np.around(x_mean, 4))
        x_std = np.hstack(np.around(x_std, 4))
        return x_mean, x_std

    def color_transfer(self, source, target):
        # Convert to LAB color space
        # OpenCV converts float32 RGB [0-1] to LAB: L [0-100], a/b [-127, 127] roughly
        s_lab = cv2.cvtColor(source, cv2.COLOR_RGB2Lab)
        t_lab = cv2.cvtColor(target, cv2.COLOR_RGB2Lab)
        
        s_mean, s_std = self.get_mean_and_std(s_lab)
        t_mean, t_std = self.get_mean_and_std(t_lab)
        
        # Avoid division by zero
        s_std = np.clip(s_std, 1e-6, None)
        
        # Split channels
        s_l, s_a, s_b = cv2.split(s_lab)
        
        # Apply Reinhard color transfer
        # Shift the source distribution to match the target distribution
        r_l = ((s_l - s_mean[0]) * (t_std[0] / s_std[0])) + t_mean[0]
        r_a = ((s_a - s_mean[1]) * (t_std[1] / s_std[1])) + t_mean[1]
        r_b = ((s_b - s_mean[2]) * (t_std[2] / s_std[2])) + t_mean[2]
        
        # Recombine channels
        result_lab = cv2.merge((r_l, r_a, r_b))
        
        # Convert back back to RGB
        result_rgb = cv2.cvtColor(result_lab, cv2.COLOR_Lab2RGB)
        return result_rgb

    def apply_color_match(self, image, reference_image, strength):
        batch_size, h, w, c = image.shape
        
        # Reference image might have a different batch size. We use the first image as the hard reference.
        ref_numpy = reference_image[0].cpu().numpy().astype(np.float32)
        
        out_images = []
        
        for i in range(batch_size):
            img = image[i].cpu().numpy().astype(np.float32)
            
            # Map the color to the target
            matched = self.color_transfer(img, ref_numpy)
            
            # Blend based on strength
            result = (matched * strength) + (img * (1.0 - strength))
            
            # Clip back to safe Tensor float bounds
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
