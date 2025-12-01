import os
import ee
import geemap
from helpers.reference import make_reference
from helpers.visualization import apply_colormap

class Classifier:
    def __init__(
        self,
        image,
        region,
        classification_bands,
        trees=100,
        train_pixels=5000,
        train_years=[2024],
        reference=None,
        grid_size=8000,
        output_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/classifications"),
    ):
        self.image = image
        self.classification_bands = classification_bands
        self.trees = trees
        self.train_pixels = train_pixels
        self.output_dir = output_dir
        self.region = region
        self.reference = reference
        self.train_years = train_years
        self.grid_size = grid_size

        os.makedirs(output_dir, exist_ok=True)

    def classify(self):
        if not self.reference:
            self.reference = make_reference(years=self.train_years)

        img_ref = self.image.addBands(self.reference)

        samples_fc = ee.FeatureCollection([])

        for year in self.train_years:
            class_band = f"class_{year}"

            samples = (
                img_ref
                .stratifiedSample(
                    numPoints=self.train_pixels,
                    classBand=class_band,
                    region=self.region,
                    scale=10,
                    geometries=False,
                )
                .map(lambda f: f.set("class", f.get(class_band)))
            )

            samples_fc = samples_fc.merge(samples)

        classifier = ee.Classifier.smileRandomForest(self.trees).train(
            samples_fc, "class", self.classification_bands
        )

        classified = self.image.classify(classifier)

        return classified, self.region

    def export(self, classified, region):
        grid = region.coveringGrid('EPSG:4326', self.grid_size)

        for i, f in enumerate(grid.toList(grid.size()).getInfo()):
            tile = ee.Feature(f).geometry()
            out_path = os.path.join(self.output_dir, f"classification_{i}.tif")

            geemap.ee_export_image(
                ee_object=classified,
                filename=out_path,
                region=tile,
                scale=10,
                file_per_band=False,
            )

            apply_colormap(out_path)
        
    def log_precision(self, samples, classifier):
        samples_random = samples.randomColumn('rand', 42)

        train = samples_random.filter(ee.Filter.lte('rand', 0.7))
        test  = samples_random.filter(ee.Filter.gt('rand', 0.7))

        trained_classifier = classifier.train(
            features=train,
            classProperty='class',
            inputProperties=self.classification_bands,
        )

        classified = test.classify(trained_classifier)

        confusion_matrix = classified.errorMatrix('class', 'classification')

        matrix = confusion_matrix.getInfo()
        accuracy = confusion_matrix.accuracy().getInfo()
        kappa = confusion_matrix.kappa().getInfo()

        print("\n======= CONFUSION MATRIX =======")
        for row in matrix:
            print(row)

        print("\n======= METRICS =======")
        print(f"Overall Accuracy: {accuracy:.4f}")
        print(f"Kappa: {kappa:.4f}")

    