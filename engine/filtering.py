import os
import time
import ee
import geemap
import rasterio
from rasterio.plot import reshape_as_raster
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
        max_size = 20
        params = []
        
        for layer in LAYER_IDS.keys():
            params.append({"classValue": LAYER_IDS[layer], "maxSize": max_size})

        result = ee.List(params).iterate(
            lambda param, img: self.majority_filter(ee.Image(img), param),
            self.image
        )

        return ee.Image(result)

    def apply_qgis_colormap(self, path):
        colormap = {
            1: (35, 197, 0),     # verde
            2: (255, 252, 0),    # amarelo
            3: (255, 134, 0),    # laranja
            #4: (255, 0, 0),      # vermelho
        }

        with rasterio.open(path, "r+") as dst:
            dst.write_colormap(1, colormap)
    
    def export(self, filtered, region):
        grid = region.coveringGrid('EPSG:4326', 8000)

        for i, f in enumerate(grid.toList(grid.size()).getInfo()):
            tile = ee.Feature(f).geometry()
            out_path = os.path.join(self.output_dir, f"filtered_{i}.tif")
            
            geemap.ee_export_image(
                ee_object=filtered.select(["classification"]).uint8(),
                filename=out_path,
                region=tile,
                scale=10,
                file_per_band=False,
            )

            """
            task = ee.batch.Export.image.toDrive(
                image=filtered.select(["classification"]).uint8(),
                description=f"filtered_{i}.tif",
                folder="gee_exports",
                region=tile,
                scale=10,
                maxPixels=1e13,
            )

            print(f"Starting export tile {i}/{n-1}")
            task.start()
            """
            
            while not os.path.exists(out_path): 
                time.sleep(2)

            self.apply_qgis_colormap(out_path)
