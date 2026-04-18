# Image Pipeline Reference

## Setup

### ERNIE-Image-Turbo (ComfyUI)

**Prerequisites**: All model files already downloaded to `/Users/dawei/ComfyUI/models/`

| Component | Path | Size |
|-----------|------|------|
| Diffusion model (GGUF Q5_K_M) | `models/diffusion_models/ernie-image-turbo-Q5_K_M.gguf` | 5.5 GB |
| Prompt Enhancer | `models/text_encoders/ernie-image-prompt-enhancer.safetensors` | 6.4 GB |
| Ministral text encoder | `models/text_encoders/ministral-3-3b.safetensors` | 7.2 GB |
| VAE | `models/vae/flux2-vae.safetensors` | 0.3 GB |

**Start ComfyUI**:
```bash
cd /Users/dawei/ComfyUI
python main.py
```

ComfyUI runs on `http://127.0.0.1:8188` by default.

**Workflow**: `/Users/dawei/ComfyUI/ernie-image-turbo-gguf-workflow.json`

Key mutable nodes:
- Node 11 (`PrimitiveStringMultiline`): Prompt text
- Node 5 (`EmptyFlux2LatentImage`): Width/height
- Node 12 (`PrimitiveBoolean`): Prompt enhancement on/off

**Apple Silicon note**: Use `PYTORCH_ENABLE_MPS_FALLBACK=1` if encountering MPS errors.

### GLM-OCR

**Model**: `zai-org/GLM-OCR` (0.9B params, safetensors, 2.65GB, already downloaded)

**Model location**: `~/.cache/huggingface/hub/models--zai-org--GLM-OCR/`

**Start inference server**:
```bash
cd /Users/dawei/claude-playground/seo-forge
python scripts/glm_ocr_server.py --port 8190
```

The server loads `zai-org/GLM-OCR` from HuggingFace cache. First startup takes ~10s for model loading.

GLM-OCR runs on `http://127.0.0.1:8190` by default.

**API format**: OpenAI-compatible chat completions with vision support.

**Dependencies**: `transformers`, `Pillow`, `torch` (installed in system Python).

**Usage example**:
```bash
# Health check
curl http://127.0.0.1:8190/health

# Verify an image
python scripts/seo_forge.py glm-ocr-verify \
  --image-path ./photo.jpg \
  --expected-subject "modern office workspace"
```

## Dimension Guidelines

| Slot | Dimensions | Aspect Ratio | Notes |
|------|-----------|-------------|-------|
| Cover image | 1024x1024 or 1536x1024 | 1:1 or 3:2 | Square or landscape |
| Inline image | 768x512 | 3:2 | Smaller for article body |
| Hero banner | 1536x640 | ~5:2 | Wide landscape for headers |

## Prompt Engineering Tips

1. **Be descriptive**: "A sunlit modern office with wooden desk, potted plant, and laptop, warm color grading" beats "office"
2. **Avoid text**: ERNIE-Image struggles with text in images. Don't ask for signs, labels, or documents
3. **Use prompt enhancer**: Keep it ON for most cases. Disable (`--no-enhance`) only for precise prompt control
4. **Chinese articles**: Write prompts in English. The visual output is universal
5. **Cover images**: Add "professional photography, clean composition" for higher quality
6. **Negative space**: Include "with negative space for text overlay" if the blog design overlays text on cover images

## OCR Verification

GLM-OCR is used to verify that web-searched images match the expected article context:

1. The `image-architect` agent identifies the expected subject for each image slot
2. Candidate images from web search are downloaded locally
3. `glm-ocr-verify` sends the image to GLM-OCR with the expected subject
4. If `matches: true`, the image is accepted; otherwise, try the next candidate
5. After 3 failed candidates, refine the search query and retry (max 3 attempts)
6. If all attempts fail, fall back to Unsplash

## CLI Quick Reference

```bash
# Check ComfyUI availability
python scripts/seo_forge.py comfyui-check

# Generate an image
python scripts/seo_forge.py comfyui-generate --prompt "description" --width 1024 --height 1024

# Generate without prompt enhancement
python scripts/seo_forge.py comfyui-generate --prompt "precise description" --no-enhance

# Check GLM-OCR availability
python scripts/seo_forge.py glm-ocr-check

# Verify an image matches expected subject
python scripts/seo_forge.py glm-ocr-verify --image-path ./img.jpg --expected-subject "office workspace"

# Register image metadata
python scripts/seo_forge.py image-register --article-id ID --slot cover --source generate --path ./img.png --alt "alt text"
```