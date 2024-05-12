from pyproj import Transformer
from affine import Affine

# Transform from coordinate system ISN93 to WGS84 (X/Y -> lon/lat)
def transformISN93ToWGS84(X, Y):
    transformer = Transformer.from_crs(3057, 4326, always_xy=True)
    return transformer.transform(X, Y)

# Transform from coordinate system WGS84 to ISN93 (lon/lat -> X/Y)
def transformWGS84ToISN93(lon, lat):
    """
    Transform from coordinate system WGS84 to ISN93 (lon/lat -> X/Y)

    :param lon: longitudional coordinates
    :param lat: latitudinal coordinates
    :return: the X/Y values corresponding to lon/lat in the new reference system
    """
    transformer = Transformer.from_crs(4326, 3057, always_xy = True)
    return transformer.transform(lon, lat)

def getVedurLonLatInISN93(lon: float, lat: float):
    transformer = Transformer.from_crs(4326, 3057, always_xy = True)
    return transformer.transform(-lon, lat)