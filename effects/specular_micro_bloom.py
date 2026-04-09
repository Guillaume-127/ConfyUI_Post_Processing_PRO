import torch
import numpy as np
import cv2

class SpecularMicroBloomPRO:
    """
    Specular Micro-Bloom PRO
    Targets extreme highlights (pores, sweat, eye reflections) with a physically-based soft knee threshold,
    and applies a multi-layered diffusion to make the skin look organically moist and vibrant.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("FLOAT", {"default": 0.80, "min": 0.0, "max": 1.0, "step": 0.01}),
                "softness": ("FLOAT", {"default": 0.50, "min": 0.0, "max": 1.0, "step": 0.01}),
                "strength": ("FLOAT", {"default": 1.5, "min": 0.0, "max": 10.0, "step": 0.05}),
                "radius": ("INT", {"default": 5, "min": 1, "max": 50, "step": 1}),
                "spread": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 5.0, "step": 0.1}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_micro_bloom"
    CATEGORY = "Post_Processing_PRO/Effects"
    
    def apply_micro_bloom(self, image, threshold, softness, strength, radius, spread):
        batch_size, h, w, c = image.shape
        out_images = []
        
        base_ksize = int(radius) | 1 
        
        for i in range(batch_size):
            img = image[i].cpu().numpy()
            
            # --- SOFT KNEE HIGHLIGHT EXTRACTION ---
            # Une simple extraction (img - seuil) crée un "masque binaire" dur (effet tout ou rien).
            # L'approche "Soft Knee" (standard en VFX cinématique / Unreal Engine) crée une courbe de roll-off.
            
            # On définit l'arc de la courbe basée sur la "softness"
            knee = softness * threshold + 1e-5
            
            # Calcul de la courbe d'adoucissement quadratique
            rq = np.clip(img - threshold + knee, 0.0, 2.0 * knee)
            rq = (rq ** 2) / (4.0 * knee)
            
            # Application de la courbe aux zones sombres à moyennes, 
            # et passage en linéaire brut pour les pics spéculaires lointains
            specular = np.where(img > threshold + knee, img - threshold, rq)
            
            # On normalise la plage de valeur pour que le paramètre "strength" réponde fortement
            specular = np.clip(specular * 2.0, 0.0, 5.0)
            
            # --- MULTI-LAYER DIFFUSION ---
            # La diffusion de la lumière organique dans l'air ou le liquide lacrymal ne répond pas 
            # à une seule passe de Flou, elle utilise un dégradé exponentiel.
            if base_ksize > 1:
                # Couche 1: Le coeur dense du reflet (Sharp)
                sigma1 = base_ksize / 2.0
                bloom1 = cv2.GaussianBlur(specular, (base_ksize, base_ksize), sigmaX=sigma1, sigmaY=sigma1)
                
                # Couche 2: Le halo extérieur ambiant (Spread)
                r2 = int(base_ksize * spread) | 1
                sigma2 = r2 / 2.0
                bloom2 = cv2.GaussianBlur(specular, (r2, r2), sigmaX=sigma2, sigmaY=sigma2)
                
                # Composition optique (Coeur prédominant avec halo léger)
                micro_bloom = (0.7 * bloom1) + (0.3 * bloom2)
            else:
                micro_bloom = specular
                
            # Mode d'incrustation Additif strict (Linear Dodge)
            result = img + (micro_bloom * strength)
            
            out_images.append(np.clip(result, 0.0, 1.0))
            
        out_tensor = torch.from_numpy(np.stack(out_images)).to(image.device)
        return (out_tensor,)
