# Post_Processing_PRO for ComfyUI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Node-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![GitHub Repo stars](https://img.shields.io/github/stars/Guillaume-127/ConfyUI_Post_Processing_PRO?style=social)

A professional, high-fidelity post-processing node suite curated for ComfyUI. `Post_Processing_PRO` simulates precise physical analog camera behaviors using advanced mathematical modeling, taking your AI rendering pipelines closer to real cinematography.

**Directly compatible with ComfyUI Manager.**

## 🎯 Pro Usage & Philosophy
> **Note on Defaults**: These nodes are engineered strictly for **high-end professional usage** and photorealism. As such, the default parameters are deliberately set to be extremely subtle. In high-end cinema and professional optical compositing, realism is born from almost imperceptible, physically accurate imperfections, rather than aggressive, over-the-top filters. If a node seems "too light" at first glance, it means it is working exactly as intended! A photorealistic render requires accumulation, not heavy-handed processing.

## Features

### 🎞️ Optics (`Post_Processing_PRO/Optics`)
Simulate real-world camera lens physical properties.

1. **Lens Distortion PRO**
   - Simulates barrel and pincushion effects using the Brown-Conrady equations. Perfectly suited for compositing AI generations over real footage, or increasing naturalistic aesthetics by breaking perfect geometry.
2. **Lateral Chromatic Aberration PRO**
   - Displaces Red and Blue channels radially from the center. It replicates how physical lenses fail to focus all color wavelengths perfectly at the edges, keeping the center sharp while fringing the borders.
3. **Chromatic Aberration PRO (Standard)**
   - Performs a standard, aggressive uniform shift of color channels globally. Emulates cheap 90s vintage lenses or synthetic digital glitches across the entire frame.
4. **Veiling Glare PRO**
   - Introduces a mathematically realistic "black lift" (loss of contrast) driven by light bouncing back and forth across physical internal lens elements. Softens the harshness of AI renders.

### 🧪 Effects (`Post_Processing_PRO/Effects`)
Mimics the legendary physical oxidation, sensor biology, and light physics phenomena.

1. **Halation PRO**
   - Simulates the legendary physical oxidation and chemical blooming of red and spectral light hitting analog silver-halide film stocks. 
2. **Specular Micro-Bloom PRO**
   - A hyper-targeted bloom that affects only the extreme highlights (pores, sweat, eye reflections) adding a micro-diffusion (1-3px). Makes portraits instantly feel wet and alive rather than artificially plastic.
3. **Cinematic Adaptive Sharpening PRO (CAS)**
   - Intelligently enhances fine details and local contrast without causing aggressive edge ringing or introducing unnecessary noise in smooth areas.
4. **Sensor Heat Noise PRO**
   - Reproduces the chromatic noise (Red/Blue dominant) that pollutes the deep shadows of digital sensors (due to thermal heating). Specifically targets regions under 15% luminance to avoid ruining well-lit areas.
5. **Film Grain PRO**
   - Generates genuine physical film-like noise on the frame, featuring scalable clumping (thickness) and optional monochromatic structures.
6. **Bayer Dithering PRO**
   - Reintroduces the mathematical grid texture of a physical CFA (Color Filter Array). Invaluable for breaking up AI-generated smooth gradients and preventing 8-bit color banding.
7. **Subsurface Diffusion PRO**
   - Simulates light penetrating the epidermis (skin) by exclusively diffusing the Red channel of the image, while ensuring the Green and Blue channels remain perfectly sharp to retain crisp pore resolution.

### 🎨 Grading (`Post_Processing_PRO/Grading`)
Professional color science and digital intermediate tools.

1. **Cinematic Color Match PRO**
   - Transmutes the exact color grading palette and contrast of any reference image (a frame from your favorite movie) onto your AI generation. It uses mathematically rigorous Reinhard L*a*b* color transfer to match the mood flawlessly without distorting pixels. Includes a strength blend slider.

2. **FPE Kodak 2383 (CST Log) PRO**
   - Emulates the highly sought-after Kodak 2383 film stock used in Hollywood blockbusters. It mathematically unbuilds the AI image (sRGB -> Linear -> Cineon Log) and applies a rigorous photometric response curve to achieve dense cyans in the shadows, warm cinematic highlights, and a smooth highlight roll-off. Blend the density to your liking.

### 🛠️ Utilities (`Post_Processing_PRO/Utilities`)
Essential production tools to handle high-end pipelines.

1. **Auto Resize Match PRO**
   - Instantly interpolates an input image to perfectly match the resolution (Width X Height) of a reference image. Essential for aligning AI masks or layers.

## Installation

1. Go to your `ComfyUI/custom_nodes/` directory.
2. Clone this repository: `git clone https://github.com/yourusername/Post_Processing_PRO`
3. Restart ComfyUI.

## License
[GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0) - Open source, copyleft license. See the `LICENSE` file for details.
