from engine import GEEManager, Mosaic
from consts.bands import S2_BAND

gee = GEEManager()
gee.initialize()

EXTRA_BANDS = ["ndvi", "ndwi", "gcvi", "evi2", "savi", "nbr", "nbr2", "mndwi", "ndmi"]

CLASSIFICATION_BANDS = list(S2_BAND.values()) + EXTRA_BANDS

mosaic_builder = Mosaic(
    aoi_path = "cars/PI-2204501-4004DC019E0A484EA143F1F35D50F45F.kml",
    classification_bands = CLASSIFICATION_BANDS,
)

mosaic = mosaic_builder.compute_mosaic()

mosaic_builder.export_mosaic(mosaic)
