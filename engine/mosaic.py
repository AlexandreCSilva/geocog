import os
import ee
import geemap
import geopandas as gpd
import json
from helpers.indices import add_ndvi, add_ndwi
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
        vizualization_bands = ["swir1","nir","red"],
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"),
    ):
        self.aoi_path = aoi_path
        self.start_date = start_date
        self.end_date = end_date
        self.vizualization_bands = vizualization_bands
        self.classification_bands = classification_bands
        self.output_dir = output_dir

        os.makedirs(output_dir, exist_ok=True)

        self.aoi = self.load_aoi()

    def load_aoi(self):
        gdf = gpd.read_file(self.aoi_path, driver="KML")
        geom = json.loads(gdf.to_json())["features"][0]["geometry"]
        return ee.Geometry(geom).buffer(2000)

    def build_collection(self):
        col = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterDate(self.start_date, self.end_date)
              .filterBounds(self.aoi)
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
              .map(rename_bands)
              .map(mask_clouds)
              .map(add_ndvi)
              .map(add_ndwi)
        )
        
        return col

    def compute_mosaic(self):
        collection = self.build_collection()
        mosaic = calculate_percentile(
            collection,
            bands=self.classification_bands,
        )
        
        return mosaic, collection

    def export_mosaic(self, mosaic):
        raw_path = os.path.join(self.output_dir, "mosaic.tif")
        bbox = self.aoi.bounds()

        geemap.ee_export_image(
            ee_object=mosaic.select(self.classification_bands),
            filename=raw_path,
            region=bbox,
            scale=10,
            file_per_band=False
        )

        return raw_path

    def export_visual(self, mosaic):
        bbox = self.aoi.bounds()
        mn, mx = auto_vis_params(mosaic, self.vizualization_bands, bbox)

        vis = mosaic.visualize(
            bands=self.vizualization_bands,
            min=mn,
            max=mx
        )

        out = os.path.join(self.output_dir, "mosaic_visual.tif")

        geemap.ee_export_image(
            ee_object=vis,
            filename=out,
            region=bbox,
            scale=10,
            file_per_band=False
        )
        return out

    def export_thumbs(self, collection):
        size = collection.size().getInfo()
        imgs = collection.sort("system:time_start").toList(size)
        bbox = self.aoi.bounds()

        for i in range(size):
            generate_thumb(ee.Image(imgs.get(i)), self.vizualization_bands, bbox, i)
