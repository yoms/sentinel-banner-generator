from fastkml import kml
from shapely.geometry import Point, Polygon
import shapely.wkt
from datetime import datetime, timedelta, date
import urllib.request
import logging
import os.path
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinel-downloader")
dir_path = os.path.dirname(os.path.realpath(__file__))
granule_kml = os.path.join(dir_path, 'data','S2A_OPER.kml')
base_url = 'https://sentinel-s2-l1c.s3.amazonaws.com/tiles'

def read_zones_from_data_file():
    logger.debug("Read zones from kml data %s", granule_kml)
    with open(granule_kml, 'rb') as kmlfile:
        doc=kmlfile.read()

    k = kml.KML()
    k.from_string(doc)

    file_feature = list(k.features())[0]
    features = list(file_feature.features())
    return list(features[0].features())

def find_zone(zones_features, longitude, latitude):    
    for zone in zones_features:
        zone_geom = shapely.wkt.loads(zone.geometry.to_wkt())
        if Point(longitude, latitude).within(zone_geom) : 
            return zone
            
def get_url_for_zone(zone_name):
    utm_code = zone_name[:2]
    lat_band = zone_name[2]
    square = zone_name[-2:]
    if utm_code[0] == '0':
        utm_code = utm_code[1]    
    return base_url+"/"+utm_code+"/"+lat_band+"/"+square

def product_exist(zone_name, date):
    zone_url = get_url_for_zone(zone_name)
    url_string = zone_url+"/"+str(date.year)+"/"+str(date.month)+"/"+str(date.day)+"/0/preview.jpg"
    logger.debug("Request url : %s "% url_string)
    try:
        urllib.request.urlopen(url_string).read()
        return True
    except urllib.error.HTTPError:
        return False    

            
def download_product_in_zone(zone_name, date, bands = [2,3,4]):
    if not product_exist(zone_name, date):
        return False
    
    zone_url = get_url_for_zone(zone_name)
    def download_band(band_name):
        url_string = zone_url+"/"+str(date.year)+"/"+str(date.month)+"/"+str(date.day)+"/0/"
        url = url_string+"B%02d.jp2"%band
        try:
            logger.info("Download band %s at %s"% (band, url))
            file_name = zone_name+"_"+str(date.year)+"_"+str(date.month)+"_"+str(date.day)+"_"+str(band)
            file_path = os.path.join(tempfile.gettempdir(), file_name)
            logger.info("File path will be %s"% file_path)
            if os.path.isfile(file_path) :
                logger.info("Retrieve band downloaded in cache : %s"% file_path)
            else:
                file_path, headers = urllib.request.urlretrieve(url, file_path)
                logger.info("Band downloaded : %s"% file_path)
            return file_path
        except urllib.error.HTTPError:
            logger.info("Impossible to find requested product")
            return None
            
    products = {}
    
    for band in bands:
        band_name = "B%02d"%band
        products[band] = download_band(band_name)
    return products
            
        
def download_product(longitude, latitude, date, bands = [2,3,4]):
    logger.debug("Download product")
    logger.debug("Longitude : %s"%longitude)
    logger.debug("Latitude : %s"%latitude)
    logger.debug("Date : %s"%date)
    zones_features = read_zones_from_data_file()
    zone = find_zone(zones_features, longitude, latitude)
    logger.debug("Zone find : %s"% zone.name)
    return download_product_in_zone(zone.name, date, bands)
    
def last_image_date_for_lat_lon(latitude, longitude):
    zones_features = read_zones_from_data_file()
    zone = find_zone(zones_features, latitude, longitude)
    date_buffer = date.today()
    while product_exist(zone.name, date_buffer) != True:
        date_buffer = date_buffer - timedelta(days=1)
        logger.debug("Try date time : %s"% date_buffer )
    return date_buffer
    
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
#    zones_features = read_zones_from_data_file()
#    zone = find_zone(zones_features, 1.433333, 43.6)
#    print(zone.name)
#    print(get_url_for_zone(zone.name))
#    download_product_in_zone("31TCJ", datetime(year = 2017, month=10, day=28))
    print(download_product_in_zone("31TCJ", datetime(year = 2017, month=10, day=28)))
    print(last_image_date_for_lat_lon(1.6667, 43.3))
#    print(download_product(1.433333, 43.6, datetime(year = 2017, month=10, day=28)))
    
    
    
#print(len(zones_features))
#print(dir(zones_features[0]))
#print(zones_features[0].name)
#print(zones_features[0].geometry)
#print(dir(zones_features[0].geometry))
#print(zones_features[0].geometry.to_wkt())
#    zone = 
#wkt = zones_features[0].geometry.to_wkt()
#zone = ogr.CreateGeometryFromWkt(wkt)
#print(dir(zone))
