from geemap.basemaps import GoogleMapsTileProvider

style = [
    {"stylers": [{"hue": "#00ffe6"}, {"saturation": -20}]},
    {
        "featureType": "road",
        "elementType": "geometry",
        "stylers": [{"lightness": 100}, {"visibility": "simplified"}],
    },
]

BASEMAP = GoogleMapsTileProvider(
    map_type="roadmap",
    language="pt-Br",
    style=style,
)
