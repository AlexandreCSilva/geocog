from engine import GEEManager, Mosaic, Classifier
from consts import S2_BAND

gee = GEEManager()
gee.initialize()

CLASSIFICATION_BANDS = list(S2_BAND.values()) + ["ndvi", "ndwi"]

mosaic_builder = Mosaic(
    aoi_path = "cars/SP-3536901-59066243765040219D013B8B8A6538BC.kml",
    start_date = "2025-08-01",
    end_date = "2025-10-30",
    classification_bands = CLASSIFICATION_BANDS,
)

mosaic, collection = mosaic_builder.compute_mosaic()

# só para vizualização do mosaico (opcional)
#mosaic_builder.export_mosaic(mosaic)
#mosaic_builder.export_visual(mosaic)
#mosaic_builder.export_thumbs(collection)

image_classifier = Classifier(
    image = mosaic,
    classification_bands = CLASSIFICATION_BANDS,
    trees = 100,
    train_pixels = 10000,
    region=mosaic_builder.aoi
)

first_classified, region = image_classifier.classify()

image_classifier.reference = first_classified.rename("class")

classified, _region = image_classifier.classify()

# só para vizualização do mosaico (opcional)
image_classifier.export(classified, region)