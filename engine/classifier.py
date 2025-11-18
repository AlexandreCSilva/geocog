import os
import ee
import geemap
from helpers.reference import make_reference

class Classifier:
    def __init__(
            self,
            classification_bands,
            trees,
            train_pixels,
            image,
            region,
            reference = None,
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"),
        ):
        self.image = image
        self.classification_bands = classification_bands
        self.trees = trees
        self.train_pixels = train_pixels
        self.output_dir = output_dir
        self.region = region
        self.reference = reference

        os.makedirs(output_dir, exist_ok=True)

    def classify(self):
        if not self.reference:
            self.reference = make_reference()
        
        train = self.image.select(self.classification_bands).addBands(self.reference)

        samples = train.sample(
            region=self.region,
            scale=10,
            numPixels=self.train_pixels,
            seed=23,
            tileScale=4
        )

        samples = samples.filter(ee.Filter.neq("class", 0))
        
        classification = ee.Classifier.smileRandomForest(self.trees).train(
            samples, "class", self.classification_bands
        )

        # Logs de precisão da classificação (opcional)
        #self.log_precision(samples, classifier=classification)

        return self.image.classify(classification), self.region

    def export(self, classified, region):
        out_path = os.path.join(self.output_dir, "classification.tif")

        geemap.ee_export_image(
            ee_object=classified,
            filename=out_path,
            region=region,
            scale=10,
            file_per_band=False,
        )

        return out_path
    
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

    