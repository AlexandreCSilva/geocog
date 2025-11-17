from engine import GEEManager, Mosaic, Classifier
from consts import S2_BAND

gee = GEEManager()
gee.initialize()

CLASSIFICATION_BANDS = list(S2_BAND.values()) + ["ndvi", "ndwi"]

mosaic_builder = Mosaic(
    aoi_path = "cars/MS-5008305-B903C49807354CB0B28BC9BEED9848D1.kml",
    start_date = "2025-08-01",
    end_date = "2025-09-30",
    classification_bands = CLASSIFICATION_BANDS,
)

mosaic, collection = mosaic_builder.compute_mosaic()

# só para vizualização do mosaico (opcional)
mosaic_builder.export_mosaic(mosaic)
mosaic_builder.export_visual(mosaic)
mosaic_builder.export_thumbs(collection)

image_classifier = Classifier(
    image = mosaic,
    classification_bands = CLASSIFICATION_BANDS,
    trees = 100,
    train_pixels = 10000,
    region=mosaic_builder.aoi
)

classified, region = image_classifier.classify()

# só para vizualização do mosaico (opcional)
image_classifier.export(classified, region)