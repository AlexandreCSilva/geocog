import ee
from datetime import datetime, timedelta
from consts import BANDS_MAP

S2_CLOUD_PROB = 'COPERNICUS/S2_CLOUD_PROBABILITY'
CSP_COLLECTION = "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"
MAX_CLOUD_PROBABILITY = 30
MAX_CSP = 35

# Retira nuvens do satélite Sentinel 2
def mask_clouds(img):
    # --- BQA mask ---
    bqa = img.select('BQA')
    bqa_mask = bqa.bitwiseAnd(1<<10).eq(0)\
                  .And(bqa.bitwiseAnd(1<<11).eq(0))

    # --- Cloud probability mask ---
    cloud_prob = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY') \
        .filter(ee.Filter.eq('system:index', img.get('system:index'))) \
        .first()
    
    prob_mask = ee.Image(ee.Algorithms.If(
        cloud_prob,
        cloud_prob.select('probability').lt(MAX_CLOUD_PROBABILITY),
        ee.Image(1)  # fallback
    ))

    # --- SCL clear mask ---
    scl = img.select('SCL')
    scl_clear = scl_clear = (
        scl.eq(4)   # Vegetação
        .Or(scl.eq(5))  # Vegetação
        .Or(scl.eq(6))  # Solo
        .Or(scl.eq(7))  # Solo / Rocha
        .Or(scl.eq(11)) # Água
    )

    # --- Cloud Score Plus mask ---
    csp_img = (
        ee.ImageCollection(CSP_COLLECTION)
        .filter(ee.Filter.eq("system:index", img.get("system:index")))
        .first()
    )

    csp_mask = ee.Image(
        ee.Algorithms.If(
            csp_img,
            csp_img.select("cs").lt(MAX_CSP),
            ee.Image(1)   # fallback sem CSP
        )
    )

    final_mask = bqa_mask.And(prob_mask).And(scl_clear).And(csp_mask)

    return img.updateMask(final_mask)


def rename_bands(img, font="SENTINEL2"):
    mapper = BANDS_MAP[font]
    
    BANDS = list(mapper.keys())
    BANDS_NAMES = list(mapper.values())
    
    return img.select(BANDS).rename(BANDS_NAMES)

def interval(date: str, interval=2):
    date_formated = datetime.strptime(date, "%Y-%m-%d")
    time_interval = timedelta(weeks=interval)

    before = (date_formated - time_interval).strftime("%Y-%m-%d")
    after = (date_formated + time_interval).strftime("%Y-%m-%d")

    return before, after
