import os
import time
import rasterio

def apply_colormap(path):
    while not os.path.exists(path):
        time.sleep(1)
    
    colormap = {
        1: (35, 197, 0),     # verde
        2: (255, 252, 0),    # amarelo
        3: (255, 134, 0),    # laranja
        4: (75, 165, 230),   # azul
    }

    with rasterio.open(path, "r+") as dst:
        dst.write_colormap(1, colormap)