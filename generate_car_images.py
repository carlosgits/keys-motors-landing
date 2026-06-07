"""
Generate photorealistic used car images for Keys Motors landing page via OpenAI gpt-image-1.

Usage:
    set OPENAI_API_KEY=sk-...   # Windows
    export OPENAI_API_KEY=sk-... # Unix
    python generate_car_images.py [--model gpt-image-1|dall-e-3]

Generates 7 images saved to ./assets/cars/:
  1. hero-sedan.jpg       (Honda Civic LX silver — sedan tab + Civic inventory card)
  2. hero-suv.jpg         (Nissan Rogue gray — SUV tab)
  3. hero-truck.jpg       (Ford F-150 XL blue — truck tab + F-150 inventory card)
  4. hero-van.jpg         (Honda Odyssey silver minivan — van tab)
  5. hero-tradein.jpg     (older worn sedan — trade-in tab)
  6. hero-financing.jpg   (key handoff scene — financing tab)
  7. inv-camry.jpg        (Toyota Camry LE white — Camry inventory card)

Visual direction: PHOTOREALISTIC, GRITTY, REAL USED CAR DEALERSHIP feel.
NO marketing-style polish. NO luxury cars. Used basic economy vehicles
at a West Palm Beach BHPH dealership.
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY env var first", file=sys.stderr)
    sys.exit(1)

ENDPOINT = "https://api.openai.com/v1/images/generations"
OUT_DIR = Path(__file__).resolve().parent / "assets" / "cars"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Shared style direction injected into every prompt
STYLE = (
    "Photorealistic photograph, shot with a Canon 5D Mark IV and 35mm lens, "
    "natural daytime lighting (overcast or golden hour), authentic and slightly gritty, "
    "real used car dealership aesthetic — NOT a marketing photo, NOT studio lighting. "
    "Subtle imperfections: small dust on paint, slight wear, real-world parking lot environment. "
    "Wide horizontal framing 3:2 aspect. No watermarks, no text overlays. "
    "Avoid any luxury or sports car appearance — this is a basic economy used vehicle."
)


CARS = [
    {
        "filename": "hero-sedan.jpg",
        "prompt": (
            "A used 2018 Honda Civic LX sedan in pearl white, photographed at a "
            "used car dealership lot in West Palm Beach Florida. Three-quarter front "
            "angle showing the headlights and grille. Basic economy trim with stock "
            "steel wheels and no aftermarket modifications. Slight dust on paint. "
            "Paved asphalt lot with chain-link fence and palm trees in soft-focus background. "
            "Overcast daytime lighting. A small dealer license plate frame is visible. "
            f"{STYLE}"
        )
    },
    {
        "filename": "hero-suv.jpg",
        "prompt": (
            "A used 2019 Nissan Rogue SV crossover SUV in dark gray, photographed at "
            "a used car dealership lot in West Palm Beach Florida. Three-quarter front "
            "angle. Basic family SUV trim, no premium package. Stock 17-inch alloy wheels. "
            "Slightly dusty body. Paved asphalt lot with chain-link fence and palm trees "
            "in soft-focus background. Overcast natural daytime lighting. "
            f"{STYLE}"
        )
    },
    {
        "filename": "hero-truck.jpg",
        "prompt": (
            "A used 2017 Ford F-150 XL regular cab pickup truck in blue, photographed at "
            "a used car dealership lot in West Palm Beach Florida. Three-quarter front "
            "angle. Basic work truck trim — steel wheels, vinyl floor, NOT Raptor or "
            "Platinum or any premium variant. Slightly dirty exterior, real working truck "
            "appearance. Paved asphalt lot with palm trees in soft-focus background. "
            "Daytime natural lighting. "
            f"{STYLE}"
        )
    },
    {
        "filename": "hero-van.jpg",
        "prompt": (
            "A used 2017 Honda Odyssey EX minivan in silver, photographed at a used car "
            "dealership lot in West Palm Beach Florida. Three-quarter front angle. Basic "
            "family minivan, sliding side door visible. Stock alloy wheels. Some minor wear. "
            "Paved asphalt lot with chain-link fence and palm trees in soft-focus background. "
            "Overcast daytime lighting. "
            f"{STYLE}"
        )
    },
    {
        "filename": "hero-tradein.jpg",
        "prompt": (
            "An older worn used 2008 Toyota Corolla sedan in faded beige, parked at a "
            "used car dealership trade-in intake area in West Palm Beach Florida. "
            "Three-quarter front angle showing visible wear: small scratches on bumper, "
            "faded paint on hood from sun damage, slightly dusty windshield. Real "
            "10-to-15-year-old commuter car appearance. Other older trade-in vehicles "
            "partially visible in soft-focus background. Daytime natural lighting. "
            f"{STYLE}"
        )
    },
    {
        "filename": "hero-financing.jpg",
        "prompt": (
            "A warm authentic photograph of a friendly Hispanic family (mid-30s couple "
            "with one young child around 6 years old) receiving silver car keys from "
            "a middle-aged Black male car salesman at a used car dealership in West Palm "
            "Beach Florida. Daytime natural lighting. Family looking happy and relieved. "
            "Used basic Honda or Toyota sedan partially visible in background. "
            "Authentic working-class feeling, photojournalistic style — NOT a polished "
            "stock photo, NOT staged. Wear-appropriate casual clothing on family. "
            f"{STYLE}"
        )
    },
    {
        "filename": "inv-camry.jpg",
        "prompt": (
            "A used 2019 Toyota Camry LE sedan in pearl white, photographed at a used "
            "car dealership lot in West Palm Beach Florida. Side profile angle. "
            "Basic mid-size sedan trim — stock 17-inch alloy wheels, no spoiler, no "
            "aftermarket mods. Slight dust. Paved asphalt lot with chain-link fence "
            "and palm trees in soft-focus background. Overcast daytime lighting. "
            f"{STYLE}"
        )
    },
]


def generate(prompt: str, filename: str, model: str = "gpt-image-1") -> bool:
    out_path = OUT_DIR / filename
    if out_path.exists() and out_path.stat().st_size > 50_000:
        print(f"  [OK]{filename} already exists ({out_path.stat().st_size} bytes), skipping")
        return True

    if model == "gpt-image-1":
        body = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "n": 1,
            "size": "1536x1024",
            "quality": "high",
        }
    else:  # dall-e-3 fallback
        body = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1792x1024",
            "quality": "hd",
            "response_format": "b64_json",
        }

    data = json.dumps(body).encode("utf-8")
    req = Request(
        ENDPOINT, data=data, method="POST",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )

    for attempt in range(3):
        try:
            t0 = time.time()
            with urlopen(req, timeout=180) as r:
                resp_text = r.read().decode("utf-8")
            resp = json.loads(resp_text)
            elapsed = time.time() - t0

            if "data" not in resp or not resp["data"]:
                print(f"  [FAIL]{filename}: empty response — {resp}", file=sys.stderr)
                return False

            entry = resp["data"][0]
            b64 = entry.get("b64_json")
            if not b64:
                print(f"  [FAIL]{filename}: no b64_json in response — {entry}", file=sys.stderr)
                return False

            img_bytes = base64.b64decode(b64)
            out_path.write_bytes(img_bytes)
            print(f"  [OK]{filename}: {len(img_bytes):,} bytes in {elapsed:.1f}s")
            return True

        except HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:500]
            print(f"  [WARN]{filename}: HTTP {e.code} on attempt {attempt+1}: {err_body}", file=sys.stderr)
            if e.code in (429, 500, 503):
                time.sleep(8 * (attempt + 1))
                continue
            if model == "gpt-image-1" and e.code in (400, 403):
                # Fall back to dall-e-3 on model-related failures
                print(f"    -> falling back to dall-e-3", file=sys.stderr)
                return generate(prompt, filename, model="dall-e-3")
            return False
        except (URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  [WARN]{filename}: {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))

    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-image-1", choices=["gpt-image-1", "dall-e-3"])
    args = parser.parse_args()

    print(f"Generating {len(CARS)} images with {args.model} -> {OUT_DIR}")
    print()
    successes, failures = 0, 0
    for car in CARS:
        print(f"[{car['filename']}]")
        if generate(car["prompt"], car["filename"], args.model):
            successes += 1
        else:
            failures += 1
        time.sleep(2)  # gentle rate limiting

    print()
    print(f"Done. {successes} success / {failures} failed.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
