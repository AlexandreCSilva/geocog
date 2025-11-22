from engine import GEEManager, Mosaic, Classifier
from consts import S2_BAND

gee = GEEManager()
gee.initialize()

CLASSIFICATION_BANDS = list(S2_BAND.values()) + ["ndvi", "ndwi", "ndbi", "gcvi", "bsi", "glcm"]

if "glcm" in CLASSIFICATION_BANDS:
    CLASSIFICATION_BANDS.remove("glcm")
    
    for band in CLASSIFICATION_BANDS:
        CLASSIFICATION_BANDS.append(f"{band}_contrast")
        CLASSIFICATION_BANDS.append(f"{band}_diss")
        CLASSIFICATION_BANDS.append(f"{band}_ent")
        CLASSIFICATION_BANDS.append(f"{band}_idm")

mosaic_builder = Mosaic(
    aoi_path = "cars/MS-5008305-B903C49807354CB0B28BC9BEED9848D1.kml",
    start_date = "2025-10-28",
    end_date = "2025-11-18",
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