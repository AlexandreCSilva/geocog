import os
import json
import ee
import geopandas as gpd
from datetime import datetime

project_name = os.getenv("PROJECT_NAME")

GAUL_LEVEL1 = "FAO/GAUL/2015/level1"
BIOMES = f"projects/{project_name}/assets/BR_Biomas_2019"

SEASONS_BY_BIOME = {
    "AMAZONIA": ("11-01", "04-30", "05-01", "10-31"),
    "CERRADO":  ("10-01", "03-31", "04-01", "09-30"),
    "CAATINGA": ("01-15", "06-15", "06-16", "01-14"),
    "MATAATLANTICA": ("10-01", "03-31", "04-01", "09-30"),
    "PAMPA": ("10-01", "03-31", "04-01", "09-30"),
    "PANTANAL": ("11-01", "03-31", "04-01", "10-31"),
}

SEASONS_BY_STATE = {
    "AMAZONAS": ("11-01", "05-31", "06-01", "10-31"),
    "PARA": ("11-01", "05-31", "06-01", "10-31"),
    "MATO GROSSO": ("10-01", "03-31", "04-01", "09-30"),
    "MATO GROSSO DO SUL": ("10-01", "03-31", "04-01", "09-30"),
    "CEARA": ("02-01", "05-31", "06-01", "01-31"),
    "BAHIA": ("11-01", "04-30", "05-01", "10-31"),
    "SÃO PAULO": ("10-01", "03-31", "04-01", "09-30"),
    "RIO GRANDE DO SUL": ("09-15", "03-31", "04-01", "09-14"),
}

def identify_state(ee_geom):
    states = ee.FeatureCollection(GAUL_LEVEL1).filterBounds(ee_geom)
    names = states.aggregate_array("ADM1_NAME")
    return names.getInfo()

def identify_biome(ee_geom):
    fc = ee.FeatureCollection(BIOMES)
    found = fc.filterBounds(ee_geom)
    names = found.aggregate_array("biome").getInfo() if found.size().getInfo() > 0 else []
    
    return names

def months_to_dates(year, mmdd):
    mm, dd = mmdd.split("-")
    return f"{year}-{mm}-{dd}"

def get_season_periods(ee_geom, year=2024):
    year = year or datetime.utcnow().year
    biome_names = identify_biome(ee_geom)
    
    if biome_names:
        b = biome_names[0].upper()
        if b in SEASONS_BY_BIOME:
            wet0, wet1, dry0, dry1 = SEASONS_BY_BIOME[b]
            return {
                "biome": b,
                "wet": (months_to_dates(year, wet0), months_to_dates(year, wet1)),
                "dry": (months_to_dates(year, dry0), months_to_dates(year, dry1))
            }

    states = identify_state(ee_geom)
    state = states[0].upper() if states else None

    if state and state in SEASONS_BY_STATE:
        wet0, wet1, dry0, dry1 = SEASONS_BY_STATE[state]
        return {
            "state": state,
            "wet": (months_to_dates(year, wet0), months_to_dates(year, wet1)),
            "dry": (months_to_dates(year, dry0), months_to_dates(year, dry1))
        }

    return {
        "biome": None,
        "state": None,
        "wet": (months_to_dates(year, "10-01"), months_to_dates(year, "03-31")),
        "dry": (months_to_dates(year, "04-01"), months_to_dates(year, "09-30"))
    }
