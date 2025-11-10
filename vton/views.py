# vton/views.py
import json, pathlib, os, tempfile, traceback
from django.shortcuts import render
from .hf_tryon import run_tryon
from .services.size_recommender import ProductChart, SizeRow, recommend_top_size
from django.http import JsonResponse

def vton_tryon_api(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required"}, status=405)

    person  = request.FILES.get("person")
    garment = request.FILES.get("garment")
    if not (person and garment):
        return JsonResponse({"ok": False, "error": "Please attach person and garment images."}, status=400)

    def save_tmp(fobj):
        suffix = pathlib.Path(fobj.name).suffix or ".png"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        for chunk in fobj.chunks(): tmp.write(chunk)
        tmp.flush(); tmp.close()
        return tmp.name

    p_path = save_tmp(person); g_path = save_tmp(garment)
    try:
        out_url, _mask_url = run_tryon(p_path, g_path)
        return JsonResponse({"ok": True, "out_url": out_url})
    except Exception as e:
        print("TRY-ON ERROR:", e); print(traceback.format_exc())
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
    finally:
        for p in (p_path, g_path):
            try: os.remove(p)
            except: pass

_CHARTS = None
def load_charts():
    global _CHARTS
    if _CHARTS is None:
        try:
            p = pathlib.Path(__file__).resolve().parent / "data" / "uniqlo_sizes.json"
            data = json.loads(p.read_text())
        except Exception:
            # Don't block Try-On if size data is missing
            data = {"products": []}

        charts = {}
        for prod in data.get("products", []):
            charts[("uniqlo", prod["sku"])] = ProductChart(
                sku=prod["sku"], name=prod["name"],
                category=prod["category"], stretch=bool(prod["stretch"]),
                units=prod["units"], sizes=[SizeRow(**s) for s in prod["sizes"]],
            )
        _CHARTS = charts
    return _CHARTS

def vton_demo(request):
    ctx = {}
    charts = load_charts()

    if request.method == "POST":
        action   = (request.POST.get("action") or "").strip().lower()
        company  = (request.POST.get("company") or "").strip().lower()
        product  = (request.POST.get("product_id") or "").strip()

        # demo body measurements (don’t crash if blanks)
        def _float_or(val, default):
            try: return float(val)
            except Exception: return default
        user_cm = {
            "chest": _float_or(request.POST.get("chest"), 92.0),
            "shoulder": _float_or(request.POST.get("shoulder"), 42.0),
        }

        person  = request.FILES.get("person")
        garment = request.FILES.get("garment")

        def save_tmp(fobj):
            suffix = pathlib.Path(fobj.name).suffix or ".png"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            for chunk in fobj.chunks(): tmp.write(chunk)
            tmp.flush(); tmp.close()
            return tmp.name

        # ---- Try-On path ----
        if action == "tryon" or (person and garment):
            if not (person and garment):
                ctx["error"] = "Please add a person image and a garment image, then click Try On."
            else:
                p_path = save_tmp(person); g_path = save_tmp(garment)
                try:
                    out_url, _mask_url = run_tryon(p_path, g_path)
                    ctx["out_url"] = out_url
                except Exception as e:
                    print("TRY-ON ERROR:", e)
                    print(traceback.format_exc())
                    ctx["error"] = f"Try-on failed: {e}"
                finally:
                    for p in (p_path, g_path):
                        try: os.remove(p)
                        except: pass

        # ---- Size-check path ----
        elif action == "check_size":
            chart = charts.get((company, product))
            if chart:
                size_label, blurb = recommend_top_size(user_cm, chart)
                ctx["size_blurb"] = f"We recommend size {size_label}. {blurb}" if size_label else blurb
            else:
                ctx["size_blurb"] = (
                    "We couldn’t find size data for that company / product ID "
                    "(demo uses: Mock Company + uniqlo_u_crew_001)."
                )

        # Echo inputs back to the template
        ctx.update({
            "company": company,
            "product_id": product,
            "chest": user_cm["chest"],
            "shoulder": user_cm["shoulder"],
        })

    ctx["companies"] = ["Uniqlo"]
    ctx["demo_product_hint"] = "12345"
    return render(request, "vton_demo.html", ctx)
