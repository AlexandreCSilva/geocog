import os
import ee
import geemap
import geopandas as gpd
import json
from datetime import date, timedelta
from helpers.indices import add_index
from helpers.utils import rename_bands, mask_clouds
from helpers.calculations import calculate_percentile
from helpers.region import get_season_months, get_climate_zone

class Mosaic:
    def __init__(
        self,
        aoi_path,
        classification_bands,
        extra_index = [],
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/mosaics"),
    ):
        self.aoi_path = aoi_path
        self.classification_bands = classification_bands
        self.extra_index = extra_index
        self.output_dir = output_dir

        os.makedirs(output_dir, exist_ok=True)

        self.aoi = self.load_aoi()

    def load_aoi(self):
        gdf = gpd.read_file(self.aoi_path, driver="KML")
        geom = json.loads(gdf.to_json())["features"][0]["geometry"]

        aoi = ee.Geometry(geom)

        area_m2 = aoi.area().getInfo()
        area_km2 = area_m2 / 1e6

        if area_km2 < 5:
            aoi = aoi.buffer(2000)

        return aoi

    def filter_by_months(self, collection, months):
        months = ee.List(months)
        col = collection.filter(ee.Filter.inList("month", months))

        def non_empty():
            return col

        def empty():
            const = ee.Image.constant(0)

            empty_img = ee.Image.cat([
                const.rename(b) for b in self.classification_bands
            ])

            return ee.ImageCollection([empty_img])

        return ee.Algorithms.If(col.size().eq(0), empty(), non_empty())

    def build_collection(self, start, end):
        col = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(self.aoi)
              .filterDate(start, end)
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
              .map(rename_bands)
              .map(mask_clouds)
              .map(lambda img: add_index(img, self.extra_index))
              .map(lambda img: img.set("month", ee.Date(img.get("system:time_start")).get("month")))
        )
        
        return col

    def compute_mosaic(self):
        start = "2025-01-01"
        end = date.today().strftime("%Y-%m-%d")

        collection = self.build_collection(start, end)

        collection = collection.filter(
            ee.Filter.listContains("system:band_names", "nbr")
        )

        climate_code = get_climate_zone(self.aoi)
        seasons = get_season_months(climate_code)

        wet_months = seasons["wet"]
        dry_months = seasons["dry"]

        wet = self.filter_by_months(collection, wet_months)
        dry = self.filter_by_months(collection, dry_months)

        wet = ee.ImageCollection(wet)
        dry = ee.ImageCollection(dry)

        ndvi_wet = wet.select("ndvi").median()
        ndvi_dry = dry.select("ndvi").median()

        nbr_wet  = wet.select("nbr").median()
        nbr_dry  = dry.select("nbr").median()

        ndvi_diff = ndvi_dry.subtract(ndvi_wet).rename("ndvi_diff")
        nbr_diff  = nbr_dry.subtract(nbr_wet).rename("nbr_diff")

        ndvi_max = collection.select("ndvi").reduce(ee.Reducer.max()).rename("ndvi_max")
        ndvi_min = collection.select("ndvi").reduce(ee.Reducer.min()).rename("ndvi_min")
        ndvi_amp = ndvi_max.subtract(ndvi_min).rename("ndvi_amp")

        ndvi_var = collection.select("ndvi").reduce(ee.Reducer.variance()).rename("ndvi_var")
        nbr_var  = collection.select("nbr").reduce(ee.Reducer.variance()).rename("nbr_var")

        wet_img = wet.median().rename([b + "_wet" for b in self.classification_bands])
        dry_img = dry.median().rename([b + "_dry" for b in self.classification_bands])

        base_mosaic = calculate_percentile(
            collection,
            bands=self.classification_bands,
        )

        out = (
            base_mosaic
            .addBands(wet_img)
            .addBands(dry_img)
            .addBands(ndvi_diff)
            .addBands(nbr_diff)
            .addBands(ndvi_max)
            .addBands(ndvi_min)
            .addBands(ndvi_amp)
            .addBands(ndvi_var)
            .addBands(nbr_var)
        )

        return out

    def export_mosaic(self, mosaic):
        bbox = self.aoi.bounds()
        grid = bbox.coveringGrid('EPSG:4326', 10000)

        for i, f in enumerate(grid.toList(grid.size()).getInfo()):
            tile = ee.Feature(f).geometry()
            raw_path = os.path.join(self.output_dir, f"mosaic_{i}.tif")

            image = mosaic.select("red_dry", "green_dry", "blue_dry")
            image_8bit = image.multiply(255).divide(3000).clamp(0, 255).uint8()

            geemap.ee_export_image(
                ee_object=image_8bit.visualize(
                    bands=["red_dry", "green_dry", "blue_dry"],
                    min=0,
                    max=255,
                ),
                filename=raw_path,
                region=tile,
                scale=10,
                file_per_band=False
            )

        return raw_path

    # Talvez tirar isso porque exportar as thumbs em grid pode pesar muito
    # Atualizar para apply colormap
    def auto_vis_params(img, bands, region):
        stats = img.select(bands).reduceRegion(
            reducer=ee.Reducer.percentile([2, 98]),
            geometry=region,
            scale=10,
            maxPixels=1e9
        ).getInfo()

        min = []
        max = []

        for b in bands:
            min.append(stats[b + "_p2"])
            max.append(stats[b + "_p98"])

        return min, max

    # Atualizar par ao modelo de grid como de filtering
    def export_thumb(img, bands, region, name):
        min, max = self.auto_vis_params(img, bands, region)

        thumb = img.visualize(
            bands,
            min=min,
            max=max,
        )

        thumb_path = os.path.join(thumbs_dir, f"thumb_{name}.tif")

        geemap.ee_export_image(
            ee_object=thumb,
            filename=thumb_path,
            region=region,
            scale=10,
            file_per_band=False
        )

    def export_thumbs(self, collection):
        size = collection.size().getInfo()
        imgs = collection.sort("system:time_start").toList(size)
        bbox = self.aoi.bounds()

        for i in range(size):
            self.export_thumb(ee.Image(imgs.get(i)), self.vizualization_bands, bbox, i)
