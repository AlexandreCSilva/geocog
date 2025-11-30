import os
import geemap
import ee
from consts import MAPBIOMAS_LAYERS, COLLECTIONS, LAYER_IDS

def make_reference(years=range(2018, 2024), region=None):
    def export_reference(region, reference, year):
        mapbiomas_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"), f"mapbiomas_{year}.tif")

        geemap.ee_export_image(
            ee_object=reference,
            filename=mapbiomas_path,
            region=region,
            scale=10,
            file_per_band=False
        )
    
    def mask_classes(img, class_list):
        mask = img.eq(class_list[0])
        for code in class_list[1:]:
            mask = mask.Or(img.eq(code))
        return mask

    ref_bands = []

    for year in years:
        base_mask = (
            ee.Image(COLLECTIONS["MAPBIOMAS_COVERAGE"][2024])
            .select(f"classification_{year}")
        )
        
        final_mask = ee.Image(0)
        
        for class_name, class_list in MAPBIOMAS_LAYERS.items():
            class_id = LAYER_IDS[class_name]
            class_mask = mask_classes(base_mask, class_list)
            final_mask = final_mask.add(class_mask.multiply(class_id))

        final_mask = final_mask.updateMask(final_mask.gt(0))
        final_mask = final_mask.rename(f"class_{year}")

        ref_bands.append(final_mask)

        # Salva o recorte de referencia (opcional)
        if region:
            export_reference(region, base_mask, year)

    reference = ref_bands[0]
    for band in ref_bands[1:]:
        reference = reference.addBands(band)
    
    return reference
