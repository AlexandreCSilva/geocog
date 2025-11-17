import os
import ee
import geemap

thumbs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/thumbs")
os.makedirs(thumbs_dir, exist_ok=True)

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

def generate_thumb(img, bands, region, name):
    min, max = auto_vis_params(img, bands, region)

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
