import hashlib
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List


# ---------- Deterministic helpers (stub data generators) ----------
def _seed_from(key: str) -> int:
    return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % (2**31 - 1)


def _det_uniform(key: str, a: float, b: float) -> float:
    rnd = random.Random(_seed_from(key))
    return rnd.uniform(a, b)


def _det_int(key: str, lo: int, hi: int) -> int:
    rnd = random.Random(_seed_from(key))
    return rnd.randint(lo, hi)


# Prebaked ZIPs for a few regions; fallback generates 5 deterministic ZIPs
REGION_ZIPS = {
    "Austin, TX": ["78701", "78702", "78704", "78745", "78751"],
    "Seattle, WA": ["98101", "98102", "98103", "98105", "98115"],
    "Brooklyn, NY": ["11201", "11205", "11211", "11215", "11231"],
}


def enumerate_zips_for_region(region: str) -> List[str]:
    if region in REGION_ZIPS:
        return REGION_ZIPS[region]
    # Fallback: generate 5 pseudo ZIPs deterministically
    base = _det_int(region, 10000, 99900)
    return [f"{base + i:05d}" for i in range(5)]


# Median home value stub (USD), deterministic per ZIP
def fetch_median_home_value(zip_code: str) -> int:
    # 150k–1.2M, skew by leading digits
    base = _det_uniform(zip_code, 150_000, 1_200_000)
    return int(round(base, -3))


# Feature stubs, all 0–100 except school_rating 0–10
def fetch_zip_features(zip_code: str) -> Dict[str, Any]:
    return {
        "school_rating": round(
            _det_uniform("school_" + zip_code, 4.5, 9.5), 1
        ),  # 0–10 scale typical
        "transit_score": int(_det_uniform("transit_" + zip_code, 20, 95)),
        "safety_index": int(_det_uniform("safety_" + zip_code, 40, 90)),
        "walkability": int(_det_uniform("walk_" + zip_code, 30, 98)),
    }


# ---------- Nodes ----------
def intake(state: GeoScoutState) -> GeoScoutState:
    if not state.region or state.budget_max <= 0:
        state.errors.append("invalid input")
    return state


def enumerate_zips(state: GeoScoutState) -> GeoScoutState:
    state.zips = enumerate_zips_for_region(state.region)
    return state


def get_medians_cached(state: GeoScoutState, ttl_days: int = 90) -> GeoScoutState:
    now = datetime.utcnow()
    for z in state.zips:
        cached = state.cache.get(z)
        if cached:
            val, asof = cached
            if now - asof <= timedelta(days=ttl_days):
                state.medians[z] = val
                continue
        val = fetch_median_home_value(z)
        state.medians[z] = val
        state.cache[z] = (val, now)
    return state


def filter_budget(state: GeoScoutState) -> GeoScoutState:
    kept = [z for z in state.zips if state.medians.get(z, 10**12) <= state.budget_max]
    dropped = [z for z in state.zips if z not in kept]
    if dropped:
        state.errors.append(f"dropped over-budget zips: {', '.join(dropped)}")
    state.zips = kept
    return state


def fetch_scores(state: GeoScoutState) -> GeoScoutState:
    for z in state.zips:
        state.features[z] = fetch_zip_features(z)
    return state


def build_output(state: GeoScoutState) -> GeoScoutState:
    rows = []
    for z in state.zips:
        feat = state.features.get(z, {})
        rows.append(
            {
                "zip": z,
                "median_home_value": state.medians.get(z),
                "school_rating": feat.get("school_rating"),
                "transit_score": feat.get("transit_score"),
                "safety_index": feat.get("safety_index"),
                "walkability": feat.get("walkability"),
            }
        )
    state.results = rows
    return state


def eval_check(state: GeoScoutState) -> GeoScoutState:
    violators = [
        r
        for r in state.results
        if r["median_home_value"] is None or r["median_home_value"] > state.budget_max
    ]
    if violators:
        bad = ", ".join(v["zip"] for v in violators)
        state.errors.append(f"eval failed for: {bad}. Removing violators.")
        state.results = [
            r
            for r in state.results
            if r["median_home_value"] is not None
            and r["median_home_value"] <= state.budget_max
        ]
    return state


# ---------- Runner (sequential, mimics __start__ → __end__) ----------
def run_geoscout(region: str, budget_max: int, cache=None) -> Dict[str, Any]:
    state = GeoScoutState(region=region, budget_max=budget_max, cache=(cache or {}))
    for step in (
        intake,
        enumerate_zips,
        get_medians_cached,
        filter_budget,
        fetch_scores,
        build_output,
        eval_check,
    ):
        state = step(state) if step not in (get_medians_cached,) else step(state)
    return {
        "region": state.region,
        "budget_max": state.budget_max,
        "results": state.results,  # JSON list of {zip, median_home_value, school_rating, transit_score, safety_index, walkability}
        "errors": state.errors,
        "cache_size": len(state.cache),
    }


# ---------- Demo ----------
if __name__ == "__main__":
    out = run_geoscout("Austin, TX", budget_max=600_000)
    from pprint import pprint

    pprint(out)
