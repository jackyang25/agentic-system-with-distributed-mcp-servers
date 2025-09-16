from __future__ import annotations

import hashlib
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# --- Optional BaseMessage import for type hints only ---
try:
    from langchain_core.messages import BaseMessage  # type: ignore
except Exception:  # fallback so this script runs without langchain
    BaseMessage = Any  # type: ignore


# --- Deterministic helpers (stub data generators) ---
def _seed_from(key: str) -> int:
    return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % (2**31 - 1)


def _det_uniform(key: str, a: float, b: float) -> float:
    rnd = random.Random(_seed_from(key))
    return rnd.uniform(a, b)


# Median home value stub (USD)
def fetch_median_home_value(zip_code: str) -> int:
    return int(round(_det_uniform("median_" + zip_code, 150_000, 1_200_000), -3))


# Feature stubs
def fetch_zip_features(zip_code: str) -> Dict[str, Any]:
    u = _det_uniform
    return {
        "school_rating": round(u("school_" + zip_code, 4.5, 9.5), 1),  # 0–10
        "transit_score": int(u("transit_" + zip_code, 20, 95)),  # 0–100
        "safety_index": int(u("safety_" + zip_code, 40, 90)),  # 0–100
        "walkability": int(u("walk_" + zip_code, 30, 98)),  # 0–100
    }


# --- City, ST parsing and ZIP lookup ---
CITY_ST_RE = re.compile(r"^\s*([^,]+)\s*,\s*([A-Za-z]{2})\s*$")


def parse_city_state(s: str) -> Tuple[str, str]:
    m = CITY_ST_RE.match(s or "")
    if not m:
        raise ValueError(
            "location_preferences.city must be 'City, ST' (e.g., 'Austin, TX')."
        )
    return m.group(1).strip(), m.group(2).upper()


def zips_for_city(city: str, state: str) -> List[str]:
    try:
        from uszipcode import SearchEngine  # optional

        se = SearchEngine(simple_zipcode=True)
        rows = se.by_city_and_state(city, state) or []
        return sorted({z.zipcode for z in rows if z.zipcode})
    except Exception:
        # Fallback: deterministic pseudo ZIPs so the script runs without deps
        base = int(str(_seed_from(city + state))[:5])
        return [f"{(base + i) % 99999:05d}" for i in range(5)]


# --- Nodes (4 total) ---
def prepare(state: GeoScoutState) -> None:
    state["current_step"] = "prepare"
    state["step_count"] += 1
    lp = state.get("location_preferences") or {}
    city = lp.get("city")
    budget = lp.get("budget_max")
    if not city or not isinstance(budget, int) or budget <= 0:
        raise ValueError(
            "Provide location_preferences.city='City, ST' and a positive budget_max."
        )
    # init results
    state["geo_scout_results"] = {
        "region": city,
        "budget_max": budget,
        "items": [],
        "errors": [],
    }


def zips_and_medians(
    state: GeoScoutState, cache: Dict[str, Tuple[int, datetime]], ttl_days: int = 90
) -> List[str]:
    state["current_step"] = "zips_and_medians"
    state["step_count"] += 1
    region = state["geo_scout_results"]["region"]
    city, st = parse_city_state(region)
    zips = zips_for_city(city, st)

    now = datetime.utcnow()
    medians: Dict[str, int] = {}
    for z in zips:
        if z in cache:
            val, asof = cache[z]
            if now - asof <= timedelta(days=ttl_days):
                medians[z] = val
                continue
        val = fetch_median_home_value(z)
        medians[z] = val
        cache[z] = (val, now)

    state["geo_scout_results"]["medians"] = medians  # optional debug
    return zips


def filter_and_scores(state: GeoScoutState, zips: List[str]) -> List[Dict[str, Any]]:
    state["current_step"] = "filter_and_scores"
    state["step_count"] += 1
    budget = state["geo_scout_results"]["budget_max"]
    med = state["geo_scout_results"]["medians"]
    kept = [z for z in zips if med.get(z, 10**12) <= budget]
    dropped = sorted(set(zips) - set(kept))
    if dropped:
        state["geo_scout_results"]["errors"].append(
            f"dropped over-budget zips: {', '.join(dropped)}"
        )

    rows: List[Dict[str, Any]] = []
    for z in kept:
        f = fetch_zip_features(z)
        rows.append(
            {
                "zip": z,
                "median_home_value": med[z],
                "school_rating": f["school_rating"],
                "transit_score": f["transit_score"],
                "safety_index": f["safety_index"],
                "walkability": f["walkability"],
            }
        )
    return rows


def build_and_eval(state: GeoScoutState, rows: List[Dict[str, Any]]) -> None:
    state["current_step"] = "build_and_eval"
    state["step_count"] += 1
    budget = state["geo_scout_results"]["budget_max"]
    clean = [r for r in rows if r["median_home_value"] <= budget]
    state["geo_scout_results"]["items"] = clean
    state["workflow_status"] = "completed"


# --- Runner ---
def run_geoscout_workflow(
    location_preferences: Dict[str, Any],
    session_id: str = "sess-1",
    messages: Optional[List[Any]] = None,
    cache: Optional[Dict[str, Tuple[int, datetime]]] = None,
) -> GeoScoutState:
    state: GeoScoutState = {
        "messages": list(messages or []),
        "current_step": "",
        "step_count": 0,
        "workflow_status": "in_progress",
        "location_preferences": location_preferences,
        "geo_scout_results": None,
        "error_count": 0,
        "session_id": session_id,
    }
    cache = cache or {}

    try:
        prepare(state)
        z = zips_and_medians(state, cache)
        rows = filter_and_scores(state, z)
        build_and_eval(state, rows)
    except Exception as e:
        state["workflow_status"] = "error"
        state["error_count"] += 1
        state["geo_scout_results"] = state.get("geo_scout_results") or {
            "region": "",
            "budget_max": 0,
            "items": [],
            "errors": [],
        }
        state["geo_scout_results"]["errors"].append(str(e))
    return state
