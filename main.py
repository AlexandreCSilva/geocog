from engine import GEEManager, Mosaic, Classifier, Filtering
from consts import S2_BAND
from helpers import interval

gee = GEEManager()
gee.initialize()

EXTRA_BANDS = ["ndvi", "ndwi", "gcvi", "evi2", "savi", "gndvi", "nbr"]

CLASSIFICATION_BANDS = list(S2_BAND.values()) + EXTRA_BANDS

date = "2025-11-11"

start, end = interval(date)

mosaic_builder = Mosaic(
    aoi_path = "cars/PI-2204501-4004DC019E0A484EA143F1F35D50F45F.kml",
    start_date = "2025-10-11",
    end_date = "2025-11-11",
    classification_bands = CLASSIFICATION_BANDS,
    extra_index = EXTRA_BANDS
)

mosaic = mosaic_builder.compute_mosaic()

image_classifier = Classifier(
    image = mosaic,
    classification_bands = CLASSIFICATION_BANDS,
    trees = 100,
    train_pixels = 10000,
    region=mosaic_builder.aoi,
    train_years=[2024],
)

classified, region = image_classifier.classify()

filters = Filtering(
    image = classified,
)

filtered_image = filters.spatial_filter()

filters.export(filtered_image, region)
