import os
import ee
import geemap
from consts import LAYER_IDS

class Filtering:
    def __init__(
        self,
        image,
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"),
    ):
        self.image = image
        self.output_dir = output_dir

    def majority_filter(self, img, param):
        param = ee.Dictionary(param)
        max_size = ee.Number(param.get("maxSize"))
        class_value = ee.Number(param.get("classValue"))

        # Pega uma mascara da classe
        class_mask = img.eq(class_value)

        # Conecta os pixeis em grupos os contanda
        connected = class_mask.mask(class_mask).connectedPixelCount(
            max_size, eightConnected=True
        )

        # Regiões menores que o tamanho maximo (ruído)
        small_regions = connected.lt(max_size)

        # Para cada uma das regiês menores pega a a vizinhança 3x3
        neighborhood = (
            img.neighborhoodToBands(ee.Kernel.square(1))
            .mask(small_regions)
        )

        # Pega o valor mais comum da vizinhança
        majority = neighborhood.reduce(ee.Reducer.mode())

        # Substitui o ruído pelo valor comum
        return img.where(small_regions, majority).byte()

    def spatial_filter(self):
        max_size = 7
        params = []
        
        for layer in LAYER_IDS.keys():
            params.append({"classValue": LAYER_IDS[layer], "maxSize": max_size})

        result = ee.List(params).iterate(
            lambda param, img: self.majority_filter(ee.Image(img), param),
            self.image
        )

        return ee.Image(result)

    def export(self, filtered, region):
        out_path = os.path.join(self.output_dir, "filtered.tif")

        geemap.ee_export_image(
            ee_object=filtered,
            filename=out_path,
            region=region,
            scale=10,
            file_per_band=False,
        )

        return out_path