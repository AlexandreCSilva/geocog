import ee
from consts import MAPBIOMAS_LAYERS, COLLECTIONS

CLASS_IDS = {
    "forest": 1,
    "pasture": 2,
    "agriculture": 3,
}

def make_reference():
    base_mask = (
        ee.Image(COLLECTIONS["MAPBIOMAS_COVERAGE"])
        .select("classification_2024")
    )

    def mask_classes(img, class_list):
        mask = img.eq(class_list[0])
        for code in class_list[1:]:
            mask = mask.Or(img.eq(code))
        return mask

    final_mask = ee.Image(0)

    for class_name, class_list in MAPBIOMAS_LAYERS.items():
        class_id = CLASS_IDS[class_name]

        mask = mask_classes(base_mask, class_list)
        final_mask = final_mask.add(mask.multiply(class_id))

    final_mask = final_mask.updateMask(final_mask.gt(0))

    return final_mask.rename("class")
