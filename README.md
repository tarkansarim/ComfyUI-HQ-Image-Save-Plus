# ComfyUI-HQ-Image-Save-Plus
## Nodes:
- Image
  - Load EXR (Individual file, or batch from folder, with cap/skip/nth controls in the same pattern as VHS load nodes)
  - Load EXR Frames (frame sequence with start/end frames, %04d frame formatting for filenames)
  - Save EXR (RGB or RGBA 32bpc EXR, with full support for batches and either relative paths in the output folder, or absolute paths with version and frame number formatting, and overwrite protection)
  - Save EXR Frames (frame sequence with %04d formatting, optionally save workflow as GUI .json and/or API .json)
  - Save Tiff (RGB 16bpc TIFF, outdated)
- Video
  - Load Video (HDR) — Load video files (MOV, MP4, MKV, etc.) at 16-bit precision via ffmpeg with full OCIO colorspace conversion support. Ideal for HDR workflows such as Topaz Video AI SDR-to-HDR (Rec.2100-PQ) → ACEScg EXR delivery.
- Latent
  - Load Latent EXR (Same VHS style controls now)
  - Save Latent EXR (4 channel latent -> RGBA 32bpc EXR)
- Utility
  - OCIO Info — Display the active OCIO config path and all available colorspaces
  - Download ACES Config — One-click download of the official ACES OCIO config
  - Save Image And Prompt / Save Image And Prompt (incremental) — Save images with workflow metadata
  - Load Image And Prompt — Load images with their saved workflow metadata

## Overview
Save and load images and latents as 32bit EXRs, with professional color management and HDR video support.

### HDR Video Pipeline (Topaz Video AI → ACEScg EXR)
Convert HDR video files to scene-linear EXR for professional delivery. This solves a common problem with **Topaz Video AI's SDR-to-HDR (Hyperion)** workflow: Topaz outputs BT.2100-PQ encoded video (Rec.2020 primaries, ST-2084/PQ transfer), but saving directly to EXR or TIFF produces flat/washed-out images because EXR assumes scene-linear data while PQ is perceptually encoded. The solution is to export from Topaz as **Apple ProRes MOV** (which preserves PQ correctly in the container) and use this pipeline to convert:

1. **Load Video (HDR)** — Decodes ProRes MOV (or any video: MP4, MKV, etc.) at 16-bit precision using ffmpeg. Set `source_colorspace` to `Rec.2100-PQ` for Topaz HDR output. The node applies OCIO to convert PQ to scene-linear, preserving the full HDR range.
2. **ComfyUI processing** — Apply any processing in ComfyUI's sRGB-encoded IMAGE format. HDR values above 1.0 are preserved through the sRGB round-trip so no data is lost.
3. **Save EXR** — Set the target colorspace (e.g. `ACEScg`, `ACES2065-1`, or any OCIO space) to save proper scene-linear EXR files ready for Nuke, Resolve, or any ACES-aware application.

Frame controls (start_frame, end_frame, skip_first_frames, select_every_nth, image_load_cap) let you process specific frame ranges or subsample long videos.

### OCIO Color Space Support
- Load and save EXR with professional color spaces via OpenColorIO (OCIO)
- Tonemap/colorspace options alongside built-in ones (linear, sRGB, Reinhard):
  - ACES: ACEScg, ACES2065-1, ACEScc, ACEScct
  - HDR: Rec.2100-PQ, Rec.2100-HLG
  - Camera Log: ARRI LogC, RED Log3G10 / REDWideGamutRGB, Sony SLog3 / SGamut3, Log film scan (ADX10)
  - Utility: scene-linear Rec.709-sRGB, Raw
- Batch-safe processing for save/load with OCIO (handles (B,H,W,3) and (H,W,3))
- No silent fallbacks: missing dependencies or unknown color spaces raise clear errors at startup

### Requirements
- Python packages (install via `pip install -r requirements.txt`):
  - `opencv-python`
  - `imageio`
  - `opencolorio` (PyOpenColorIO)
- ffmpeg (required for Load Video node): must be on PATH or set `FFMPEG_PATH` environment variable
- OCIO config file: `ocio-v2_demo.ocio`
  - Placed automatically in this node folder (or you can point to your own via `OCIO` env var)

All Python dependencies are validated at startup — if any are missing, the node pack will fail to load with a clear error message listing the missing packages and the pip install command.

### CLI Recommendations
- Launch ComfyUI with higher precision for EXR workflows:
  - `--fp32-vae`
  - Optional: `--precision full`

I recommend adding the `--fp32-vae` CLI argument for more accurate decoding. If you get an error saying that the OpenEXR codec is disabled, see [this issue.](https://github.com/spacepxl/ComfyUI-HQ-Image-Save/issues/8)

Scatterplot of raw red/green values, left=PNG, right=EXR. PNG quantizes the image to 256 possible values per channel (2^8), while the EXR has full floating point precision.

![comparison](https://github.com/spacepxl/ComfyUI-HQ-Image-Save/assets/143970342/ce8107a2-31c9-44af-95af-b9ff8d704f7f)

For latent EXR viewing purposes, if you want a cheap approximation of RGB values from the four latent channels, use this formula:
```
r = (0.298 * r + 0.187 * g - 0.187 * b - 0.184 * a) * 0.18215
g = (0.207 * r + 0.286 * g + 0.189 * b - 0.271 * a) * 0.18215
b = (0.208 * r + 0.173 * g + 0.264 * b - 0.473 * a) * 0.18215
```

## Known Issues

- No load TIFF node, and the TIFF save is bad/outdated
- If you select an OCIO color space that is not present in your config, the node will raise an explicit error listing the failing step
- OpenCV's EXR codec may be disabled by default — set `OPENCV_IO_ENABLE_OPENEXR=1` environment variable or see [this issue](https://github.com/spacepxl/ComfyUI-HQ-Image-Save/issues/8)
