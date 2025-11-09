import os, tempfile, traceback
from django.shortcuts import render
from .hf_tryon import run_tryon

def vton_demo(request):
    ctx = {}
    if request.method == "POST":
        person = request.FILES.get("person")
        garment = request.FILES.get("garment")

        def save_tmp(f):
            suffix = os.path.splitext(f.name)[-1] or ".png"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            for chunk in f.chunks(): tmp.write(chunk)
            tmp.flush(); tmp.close()
            return tmp.name

        if person and garment:
            p_path = save_tmp(person)
            g_path = save_tmp(garment)
            try:
                out_url, mask_url = run_tryon(p_path, g_path)
                ctx["out_url"] = out_url
                #ctx["mask_url"] = mask_url
            except Exception as e:
                print("TRY-ON ERROR:", e)
                print(traceback.format_exc())
                ctx["error"] = f"Try-on failed: {e}"
            finally:
                for p in (p_path, g_path):
                    try: os.remove(p)
                    except: pass

    return render(request, "vton_demo.html", ctx)
