import ee

# Calcula o mosaico de percentil de uma coleçao para cada banda
def percentile_mosaic(collection, bands, p):
    r = collection.select(bands).reduce(ee.Reducer.percentile([p]))
    out = [r.select(f"{b}_p{p}").rename(f"{b}_p") for b in bands]
    
    return ee.Image.cat(out)

# Pega os mosaicos de percentil e usa os de 25% e 75% para preencher lacunas na mediana (50%)
def combine_percentile(p50, p25, p75):
    def strip(i):
        n = i.bandNames().map(lambda x: ee.String(x).replace("_p",""))
    
        return i.rename(n)
    
    p50s = strip(p50)
    p25s = strip(p25)
    p75s = strip(p75)
    
    return p50s.unmask(p25s).unmask(p75s)

def calculate_percentile(collection, bands):
    count = collection.size().getInfo()

    if count >= 8:
        # Percentil seco
        m25 = percentile_mosaic(collection, bands, 25)
        # Percentil médio
        m50 = percentile_mosaic(collection, bands, 50)
        # Percentil úmido
        m75 = percentile_mosaic(collection, bands, 75)

        mosaic = combine_percentile(m50, m25, m75)
    
    elif count >= 4:
        # Percentil para menos mosaicos
        mosaic = percentile_mosaic(collection, bands, 40)

    else:
        mosaic = collection.median()

    return mosaic
