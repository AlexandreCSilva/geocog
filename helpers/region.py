import os
import ee
from dotenv import load_dotenv

load_dotenv()
project_name = os.getenv("PROJECT_NAME")

CLIME_ZONES = f"projects/{project_name}/assets/koppen_geiger"

def get_climate_zone(aoi):
    climate = ee.Image(CLIME_ZONES)

    climate = climate.resample("bilinear")

    climate_class = climate.reduceRegion(
        reducer=ee.Reducer.mode(),
        geometry=aoi,
        scale=1000,
        maxPixels=1e13
    ).get("b1")

    return climate_class

def get_season_months(climate_code):
    if climate_code in ["Aw", "Am", "Af"]:
        return {
            "wet":   ["12","01","02","03","04","05"],
            "dry":   ["06","07","08","09","10","11"]
        }

    if climate_code in ["BSh", "BSk"]:
        return {
            "wet":   ["01","02","03","04"],
            "dry":   ["05","06","07","08","09","10","11","12"]
        }

    if climate_code in ["Cfa", "Cfb"]:
        return {
            "wet":   ["10","11","12","01","02","03"],
            "dry":   ["04","05","06","07","08","09"]
        }

    if climate_code in ["Cwa", "Cwb"]:
        return {
            "wet":   ["10","11","12","01","02","03"],
            "dry":   ["04","05","06","07","08","09"]
        }

    return {
        "wet": ["12","01","02","03","04","05"],
        "dry": ["06","07","08","09","10","11"]
    }
