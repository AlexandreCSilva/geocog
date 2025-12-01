from engine import GEEManager, Mosaic, Classifier
from consts import S2_BAND

gee = GEEManager()
gee.initialize()

EXTRA_BANDS = ["ndvi", "ndwi", "nbr"]

CLASSIFICATION_BANDS = list(S2_BAND.values()) + EXTRA_BANDS

TIME_BANDS = ["blue", "red", "green", "nir", "swir1", "swir2", "ndvi", "nbr"]

mosaic_builder = Mosaic(
    aoi_path = "cars/PI-2204501-4004DC019E0A484EA143F1F35D50F45F.kml",
    classification_bands = CLASSIFICATION_BANDS,
    extra_index = EXTRA_BANDS
)

mosaic = mosaic_builder.compute_mosaic()

image_classifier = Classifier(
    image = mosaic,
    classification_bands = CLASSIFICATION_BANDS,
    region=mosaic_builder.aoi,
)

classified, region = image_classifier.classify()

image_classifier.export(classified, region)
