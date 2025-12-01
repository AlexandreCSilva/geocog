import ee

def add_index(img, index_list):
    red   = img.select("red")
    green = img.select("green")
    nir   = img.select("nir")

    extra_bands = []

    if "ndvi" in index_list:
        extra_bands.append(img.normalizedDifference(["nir","red"]).rename("ndvi"))

    if "ndwi" in index_list:
        extra_bands.append(img.normalizedDifference(["nir","swir1"]).rename("ndwi"))

    if "ndmi" in index_list:
        extra_bands.append(img.normalizedDifference(["nir", "swir1"]).rename("ndmi"))

    if "mndwi" in index_list:
        extra_bands.append(img.normalizedDifference(["green", "swir1"]).rename("mndwi"))

    if "swir_ratio" in index_list:
        extra_bands.append(img.select("swir1").divide(img.select("swir2")).rename("swir_ratio"))

    if "fmr" in index_list:
        extra_bands.append(img.select("swir1").subtract(img.select("nir")).rename("fmr"))

    if "nbr" in index_list:
        extra_bands.append(img.normalizedDifference(["nir","swir2"]).rename("nbr"))

    if "nbr2" in index_list:
        extra_bands.append(img.normalizedDifference(["swir1","swir2"]).rename("nbr2"))

    if "gcvi" in index_list:
        extra_bands.append((nir.divide(green).subtract(1)).rename("gcvi"))

    if "evi2" in index_list:
        extra_bands.append(
            (nir.subtract(red)
            .multiply(2.5)
            .divide(nir.add(red.multiply(2.4)).add(1))
            ).rename("evi2")
        )

    if "savi" in index_list:
        extra_bands.append(
            (nir.subtract(red))
            .multiply(1.5)
            .divide(nir.add(red).add(0.5))
            .rename("savi")
        )

    if len(extra_bands) > 0:
        img = img.addBands(ee.Image.cat(extra_bands))

    return img
