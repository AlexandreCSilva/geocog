def add_ndvi(img):
    ndvi = img.normalizedDifference(["nir","red"]).rename("ndvi")
    return img.addBands(ndvi)

def add_ndwi(img):
    ndwi = img.normalizedDifference(["nir","swir1"]).rename("ndwi")
    return img.addBands(ndwi)
