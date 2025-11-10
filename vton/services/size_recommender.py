from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class SizeRow:
    label: str
    chest: float | None = None
    shoulder: float | None = None
    length: float | None = None
    waist: float | None = None
    hip: float | None = None
    inseam: float | None = None

@dataclass
class ProductChart:
    sku: str
    name: str
    category: str
    stretch: bool
    units: str
    sizes: List[SizeRow]

def _ease_for(category: str, stretch: bool) -> Tuple[float, float]:
    if category == "top_knit" and stretch: return (4.0, 8.0)
    if category in {"top_woven", "shirt"}: return (8.0, 12.0)
    return (6.0, 10.0)

def recommend_top_size(user_cm: dict, chart: ProductChart) -> Tuple[Optional[str], str]:
    u_chest = float(user_cm.get("chest", 0.0))
    u_shoulder = user_cm.get("shoulder")
    ease_min, ease_max = _ease_for(chart.category, chart.stretch)
    target_min, target_max = u_chest + ease_min, u_chest + ease_max
    mid = (target_min + target_max) / 2.0

    candidates = []
    for s in chart.sizes:
        if s.chest is None: 
            continue
        meets_min = s.chest >= target_min
        score = abs(s.chest - mid)
        penalty = abs(s.shoulder - u_shoulder) * 0.1 if (u_shoulder and s.shoulder) else 0.0
        candidates.append((meets_min, score + penalty, s))

    if not candidates:
        return None, "No size data available."
    pool = [c for c in candidates if c[0]] or candidates
    best = sorted(pool, key=lambda x: x[1])[0][2]

    blurb = (
        f"Your chest {u_chest:.1f} cm; target {target_min:.1f}–{target_max:.1f} cm "
        f"(ease +{ease_min:.0f}–{ease_max:.0f}). Size {best.label} chest {best.chest:.1f} cm."
    )
    if pool is candidates and pool is not [c for c in candidates if c[0]]:
        blurb += " No size met minimum ease; suggesting closest available."
    return best.label, blurb
