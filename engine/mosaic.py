import os
import ee
import geemap
import geopandas as gpd
import json
from helpers.indices import add_index
from helpers.visualization import auto_vis_params, generate_thumb
from helpers.utils import rename_bands, mask_clouds
from helpers.calculations import calculate_percentile

class Mosaic:
    def __init__(
        self,
        aoi_path,
        start_date,
        end_date,
        classification_bands,
        extra_index,
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"),
    ):
        self.aoi_path = aoi_path
        self.start_date = start_date
        self.end_date = end_date
        self.classification_bands = classification_bands
        self.extra_index = extra_index
        self.output_dir = output_dir

        os.makedirs(output_dir, exist_ok=True)

        self.aoi = self.load_aoi()

    def load_aoi(self):
        gdf = gpd.read_file(self.aoi_path, driver="KML")
        geom = json.loads(gdf.to_json())["features"][0]["geometry"]
        return ee.Geometry(geom).buffer(2000)

    def build_collection(self, start=None, end=None):
        start = start if start else self.start_date
        end = end if end else self.end_date

        col = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterDate(start, end)
              .filterBounds(self.aoi)
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
              .map(rename_bands)
              .map(mask_clouds)
              .map( lambda img: add_index(img, self.extra_index))
        )
        
        return col

    def compute_mosaic(self):
        collection = self.build_collection()
        
        mosaic = calculate_percentile(
            collection,
            bands=self.classification_bands,
        )

        return mosaic

    def export_mosaic(self, mosaic):
        bbox = self.aoi.bounds()
        grid = bbox.coveringGrid('EPSG:4326', 10000)

        for i, f in enumerate(grid.toList(grid.size()).getInfo()):
            tile = ee.Feature(f).geometry()
            raw_path = os.path.join(self.output_dir, f"mosaic1_{i}.tif")

            image = mosaic.select("red", "green", "blue")
            image_8bit = image.multiply(255).divide(3000).clamp(0, 255).uint8()

            geemap.ee_export_image(
                ee_object=image_8bit.visualize(
                    bands=["red", "green", "blue"],
                    min=0,
                    max=255,
                ),
                filename=raw_path,
                region=tile,
                scale=10,
                file_per_band=False
            )

        return raw_path

    def export_thumbs(self, collection):
        size = collection.size().getInfo()
        imgs = collection.sort("system:time_start").toList(size)
        bbox = self.aoi.bounds()

        for i in range(size):
            generate_thumb(ee.Image(imgs.get(i)), self.vizualization_bands, bbox, i)
