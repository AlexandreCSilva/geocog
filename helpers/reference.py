import os
import geemap
import ee
from consts import MAPBIOMAS_LAYERS, COLLECTIONS, LAYER_IDS

def make_reference(year = 2024, region=None):
    base_mask = (
        ee.Image(COLLECTIONS["MAPBIOMAS_COVERAGE"][year])
        .select(f"classification_{year}")
    )
    
    def export_reference(region, reference):
        mapbiomas_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"), "mapbiomas.tif")

        geemap.ee_export_image(
            ee_object=reference,
            filename=mapbiomas_path,
            region=region,
            scale=10,
            file_per_band=False
        )
    
    # Salva o recorte de referencia (opcional)
    if region:
        export_reference(region=region, reference=base_mask)

    def mask_classes(img, class_list):
        mask = img.eq(class_list[0])
        for code in class_list[1:]:
            mask = mask.Or(img.eq(code))
        return mask

    final_mask = ee.Image(0)

    for class_name, class_list in MAPBIOMAS_LAYERS.items():
        class_id = LAYER_IDS[class_name]

        mask = mask_classes(base_mask, class_list)
        final_mask = final_mask.add(mask.multiply(class_id))

    final_mask = final_mask.updateMask(final_mask.gt(0))
    
    return final_mask.rename("class")
