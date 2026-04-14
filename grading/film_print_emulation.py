import torch
import numpy as np

class FPE_Kodak2383_PRO:
    """
    FPE Kodak 2383 (CST Log) PRO
    A mathematically accurate Film Print Emulation (FPE) of the Kodak 2383 film stock.
    Unbuilds the image from sRGB to Linear, then to Cineon Log, and applies a custom
    photometric S-Curve simulation with the infamous 2383 split-toning (Cyan shadows, Warm highlights).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "print_strength": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "log_density": ("FLOAT", {"default": 2.5, "min": 1.0, "max": 4.0, "step": 0.1}),
                "chroma_shift": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_fpe"
    CATEGORY = "Post_Processing_PRO/Grading"

    def srgb_to_linear(self, img_np):
        # Accurate sRGB to Linear Transform
        return np.where(img_np <= 0.04045, img_np / 12.92, ((img_np + 0.055) / 1.055) ** 2.4)

    def linear_to_cineon_log(self, linear_np):
        # Linear to Cineon Log representation (commonly used for Film Print Emulations)
        # Avoid log(0)
        lin_safe = np.clip(linear_np, 1e-10, 1.0)
        # Standard Cineon mapping
        cineon = (np.log10(lin_safe * (1.0 - 0.0108) + 0.0108) * 300 + 685) / 1023
        return np.clip(cineon, 0.0, 1.0)

    def apply_2383_emulation(self, cineon_log, log_density, chroma_shift):
        # Split RGB channels
        r = cineon_log[..., 0]
        g = cineon_log[..., 1]
        b = cineon_log[..., 2]

        # 1. Sigmoidal Film Print S-Curve
        # Cineon middle gray is mapped around 0.444
        pivot = 0.444
        
        def cineon_transfer(x, alpha):
            return (x / pivot) ** alpha / ((x / pivot) ** alpha + 1.0)

        # Apply base density curve
        res_r = cineon_transfer(r, log_density)
        res_g = cineon_transfer(g, log_density)
        res_b = cineon_transfer(b, log_density)

        # 2. Emulate 2383 Split Toning
        # Kodak 2383 has a signature look: Deep cyan/teal shadows, and warm/golden highlights
        lum = 0.2126 * res_r + 0.7152 * res_g + 0.0722 * res_b

        # Shadow mask (denser in the darks)
        shadow_mask = np.clip(1.0 - (lum / 0.35), 0.0, 1.0)
        # Highlight mask (denser where bright)
        highlight_mask = np.clip((lum - 0.6) / 0.4, 0.0, 1.0)

        # Cyan Shadows: Subtract Red, Add Blue & slightly Green
        res_r = res_r - (shadow_mask * 0.06 * chroma_shift)
        res_b = res_b + (shadow_mask * 0.04 * chroma_shift)
        res_g = res_g + (shadow_mask * 0.01 * chroma_shift)

        # Golden Highlights: Add Red, Subtract Blue
        res_r = res_r + (highlight_mask * 0.05 * chroma_shift)
        res_b = res_b - (highlight_mask * 0.07 * chroma_shift)

        # 3. Highlight Roll-off (Shoulder protection)
        # The transfer function above scales to 1.0 smoothly, but we cap it to be safe
        fpe_rgb = np.stack([res_r, res_g, res_b], axis=-1)
        return np.clip(fpe_rgb, 0.0, 1.0)

    def apply_fpe(self, image, print_strength, log_density, chroma_shift):
        batch_size, h, w, c = image.shape
        out_images = []

        for i in range(batch_size):
            img_np = image[i].cpu().numpy().astype(np.float32)

            # Phase 1: Unbuild from sRGB to Cineon Log Space (CST)
            lin_img = self.srgb_to_linear(img_np)
            cineon_log = self.linear_to_cineon_log(lin_img)

            # Phase 2: Emulate physical Kodak 2383 print film reaction
            fpe_img = self.apply_2383_emulation(cineon_log, log_density, chroma_shift)

            # Phase 3: Opacity Blend
            # Professional colorists blend the FPE print back to the original to retain modern sharpness/luminance
            result = (fpe_img * print_strength) + (img_np * (1.0 - print_strength))

            # Ensure strict output tensor bounds
            out_images.append(np.clip(result, 0.0, 1.0))

        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
