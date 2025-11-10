# vton/hf_tryon.py
from pathlib import Path
import shutil, uuid, tempfile
from django.conf import settings
from gradio_client import Client, handle_file  # use handle_file
from PIL import Image, ImageOps

SPACE = "JeremelleV/emergrade" 
#SPACE = "https://huggingface.co/spaces/JeremelleV/idmvton"
client = Client(SPACE)

def _exif_upright_copy(src_path: str) -> str:
    """
    Make a temp copy with EXIF orientation applied (no resize).
    Returns a new local path; original remains untouched.
    """
    try:
        with Image.open(src_path) as im:
            im2 = ImageOps.exif_transpose(im)   # handles 3/6/8 automatically
            suffix = Path(src_path).suffix or ".png"
            fd, tmp = tempfile.mkstemp(suffix=suffix)
            Path(tmp).unlink(missing_ok=True)   # we'll save via Pillow, not the raw handle
            im2.save(tmp)
            return tmp
    except Exception:
        # If anything goes wrong (no EXIF etc.), just return original
        return src_path

def run_tryon(human_path, garment_path, desc="", steps=30, seed=42, crop=False):
    # 1) Normalize inputs so the model sees them upright (no resizing)
    human_fixed   = _exif_upright_copy(human_path)
    garment_fixed = _exif_upright_copy(garment_path)

    editor_input = {
        "background": handle_file(human_fixed),
        "layers": [],
        "composite": None,
    }

    # 2) Call the Space (no float seed/steps)
    try:
        out_path, mask_path = client.predict(
            dict=editor_input,
            garm_img=handle_file(garment_fixed),
            garment_des=desc or "",
            is_checked=True,
            is_checked_crop=bool(crop),
            denoise_steps=int(steps),
            seed=int(seed),
            api_name="/tryon",
        )
    except Exception as e:
        # surface to template/logs so you know it didn’t reach the Space
        raise RuntimeError(f"HF call failed: {type(e).__name__}: {e}")


    # 3) Copy outputs verbatim (DO NOT rotate/resize) → ensures no distortion
    media_root = Path(settings.MEDIA_ROOT) / "tryon"
    media_root.mkdir(parents=True, exist_ok=True)
    media_url  = settings.MEDIA_URL.rstrip("/") + "/"

    def save_unique(src_fp: str, tag: str) -> str:
        src = Path(src_fp)
        name = f"{src.stem}_{tag}_{uuid.uuid4().hex[:8]}{src.suffix}"
        dst = media_root / name
        shutil.copy2(src, dst)          # byte-for-byte copy; no re-encode
        return f"{media_url}tryon/{name}"

    out_url  = save_unique(out_path,  "out")
    mask_url = save_unique(mask_path, "mask")
    return out_url, mask_url