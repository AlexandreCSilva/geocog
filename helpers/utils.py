import ee
from consts import BANDS_MAP

# Retira nuvens do satélite Sentinel 2
def mask_clouds(img):
    # Verifica se a coleção de imagens do satélite tem a banda QA60
    # Nessa banda tem 2 bits (10 e 11) e neles ficam salvos os pixels de Nuvens e Nubens cirrus
    qa_exists = img.bandNames().contains("BQA")

    def do_mask(i):
        qa = i.select("BQA")
        cloud = qa.bitwiseAnd(1 << 10).eq(0)
        cirrus = qa.bitwiseAnd(1 << 11).eq(0)
        m = cloud.And(cirrus)
        
        return i.updateMask(m)
    
    return ee.Image(ee.Algorithms.If(qa_exists, do_mask(img), img))

def rename_bands(img, font="SENTINEL2"):
    mapper = BANDS_MAP[font]
    
    BANDS = list(mapper.keys())
    BANDS_NAMES = list(mapper.values())
    
    return img.select(BANDS).rename(BANDS_NAMES)
