import ee

# Calcula o mosaico de percentil de uma coleçao para cada banda
def percentile_mosaic(collection, bands, p):
    r = collection.select(bands).reduce(ee.Reducer.percentile([p]))
    out = [r.select(f"{b}_p{p}").rename(f"{b}") for b in bands]
    
    return ee.Image.cat(out)

# Pega os mosaicos de percentil e usa os de 20% e 80% para preencher lacunas na mediana (50%)
def combine_percentile(p50, p20, p80):
    def strip(i):
        n = i.bandNames().map(
            lambda x: ee.String(x).replace('_p[0-9]+', '', 'g')
        )
        return i.rename(n)
        
    p50s = strip(p50)
    p20s = strip(p20)
    p80s = strip(p80)
    
    return p50s.unmask(p20s).unmask(p80s)

def calculate_percentile(collection, bands):
    count = collection.size().getInfo()

    if count >= 8:
        # Percentil seco
        m20 = percentile_mosaic(collection, bands, 20)
        # Percentil médio
        m50 = percentile_mosaic(collection, bands, 50)
        # Percentil úmido
        m80 = percentile_mosaic(collection, bands, 80)

        mosaic = combine_percentile(m50, m20, m80)
    
    elif count >= 4:
        # Percentil para poucos mosaicos
        mosaic = percentile_mosaic(collection, bands, 40)

    else:
        mosaic = collection.median()

    return mosaic
