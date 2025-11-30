from engine import GEEManager, Mosaic, Classifier, Filtering
from consts import S2_BAND
from helpers import interval

gee = GEEManager()
gee.initialize()

CLASSIFICATION_BANDS = list(S2_BAND.values())

date = "2024-11-11"

start, end = interval(date)

mosaic_builder = Mosaic(
    aoi_path = "cars/PI-2204501-4004DC019E0A484EA143F1F35D50F45F.kml",
    start_date = "2025-10-11",
    end_date = "2025-11-11",
    classification_bands = CLASSIFICATION_BANDS,
    extra_index = []
)

mosaic = mosaic_builder.compute_mosaic()

mosaic_builder.export_mosaic(mosaic)
