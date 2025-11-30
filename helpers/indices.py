import ee

def add_index(img, index_list):
    bands = {
        "RED": img.select("red"),
        "GREEN": img.select("green"),
        "BLUE": img.select("blue"),
        "SWIR1": img.select("swir1"),
        "SWIR2": img.select("swir2"),
        "NIR": img.select("nir"),
    }

    def compute(index):
        match index:
            case "ndvi":
                return img.normalizedDifference(['nir','red']).rename('ndvi')

            case "ndwi":
                return img.normalizedDifference(['nir','swir1']).rename('ndwi')

            case "nbr":
                return img.normalizedDifference(['nir','swir2']).rename('nbr')

            case "ndbi":
                return img.normalizedDifference(['swir1','nir']).rename("ndbi")
            
            case "gndvi":
                return img.normalizedDifference(['nir','green']).rename("gndvi")
            
            case "gcvi":
                return img.expression("(NIR / GREEN) - 1", bands).rename("gcvi")

            case "bsi":
                return img.expression("((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))", bands).rename("bsi")

            case "evi2":
                return img.expression("2.5 * (NIR - RED) / (NIR + 2.4 * RED + 1)", bands).rename("evi2")
            
            case "savi":
                return img.expression("((NIR - RED) / (NIR + RED + 0.5)) * 1.5", bands).rename("savi")

        raise ValueError(f"Não foi possível calcular o índice: {index}.")
    
    for idx in index_list:
        img = img.addBands(compute(idx))

    return img

"""
def period_mosaic_stats(col, bands, reducer_list=['median','min','max','stdDev']):
    reducers = {
        'median': ee.Reducer.median(),
        'min': ee.Reducer.min(),
        'max': ee.Reducer.max(),
        'mean': ee.Reducer.mean(),
        'stdDev': ee.Reducer.stdDev()
    }

    out_bands = []

    for stat in reducer_list:
        r = reducers.get(stat)
        if r is None:
            continue
        reduced = col.select(bands).reduce(r)

        for b in bands:
            src_name = f"{b}_{stat}" if stat != 'median' else f"{b}_median"
            out_bands.append(reduced.select([b]).rename(f"{b}_{stat}"))

    if len(out_bands) == 0:
        return None

    return ee.Image.cat(out_bands)

def build_dry_wet_index_stack(aoi, wet_col, dry_col, bands, stats=['median','min','max','stdDev']):
    wet_stats_img = period_mosaic_stats(wet_col, bands, reducer_list=stats)
    dry_stats_img = period_mosaic_stats(dry_col, bands, reducer_list=stats)

    # prefix bands
    def prefix(img, prefix_str):
        names = img.bandNames()
        new_names = names.map(lambda n: ee.String(prefix_str).cat('_').cat(ee.String(n)))
        return img.rename(new_names)

    wet_pref = prefix(wet_stats_img, 'wet')
    dry_pref = prefix(dry_stats_img, 'dry')

    combined = ee.Image.cat([wet_pref, dry_pref])
    return combined
"""