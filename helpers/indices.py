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
            # Diferença vegetal
            # - Vegetação densa → valores altos
            # - Agricultura rasa → valores médios
            # - Solo exporto → valores baixos
            # - Urbano → 0
            case "ndvi":
                return img.expression("(NIR - RED) / (NIR + RED)", bands).rename("ndvi")

            # Diferença hídrica
            # - Água pura → valores muito altos
            # - Áreas irrigadas → valores altos
            # - Vegetação seca → valores baixos
            case "ndwi":
                return img.expression("(NIR - SWIR1) / (NIR + SWIR1)", bands).rename("ndwi")

            # Diferença de construções
            # - Construções, galpões, telhas → valores altos
            # - Vegetação → valores baixo
            # - Água → valores negativo
            case "ndbi":
                return img.expression("(SWIR1 - NIR) / (SWIR1 + NIR)", bands).rename("ndbi")

            # Índice de clorofila
            # ajuda a separar agricultura de pastagem
            case "gcvi":
                return img.expression("(NIR / GREEN) - 1", bands).rename("gcvi")

            # Textura espacial da imagem
            case "glcm":
                texture_indexes = ["nir", "swir1", "ndvi", "ndbi", "bsi"]

                glcm_list = []

                for idx in texture_indexes:
                    glcm_list.append(compute_glcm(idx))

                if len(glcm_list) > 0:
                    glcm = glcm_list[0]
                    
                    for band in glcm_list[1:]:
                        glcm = glcm.addBands(band)
                    
                    return glcm

            # índice de solo exposto
            case "bsi":
                return img.expression("((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))", bands).rename("bsi")

        raise ValueError(f"Não foi possível calcular o índice: {index}.")
    
    def compute_glcm(band):
        glcm = img.select(band).multiply(100).toInt().glcmTexture(size=3)

        return glcm.select([
            f"{band}_contrast",
            f"{band}_diss",
            f"{band}_ent",
            f"{band}_idm",
        ])

    for idx in index_list:
        img = img.addBands(compute(idx))

    return img
