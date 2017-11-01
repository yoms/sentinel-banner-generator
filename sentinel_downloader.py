from fastkml import kml
from shapely.geometry import Point, Polygon
import shapely.wkt
from datetime import datetime, timedelta, date
import urllib.request
import logging
import os.path

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

def download_product_in_zone(zone_name, date):
    if not product_exist(zone_name, date):
        return False
    
    zone_url = get_url_for_zone(zone_name)
    url_string = zone_url+"/"+str(date.year)+"/"+str(date.month)+"/"+str(date.day)+"/0/"
    b2_url = url_string+"B02.jp2"
    b3_url = url_string+"B03.jp2"
    b4_url = url_string+"B04.jp2"
    try:
        logger.info("Download B2")
        b2_file_name, b2_headers = urllib.request.urlretrieve(b2_url)
        logger.info("B2 downloaded : %s"% b2_file_name)
        logger.info("Download B3")
        b3_file_name, b3_headers = urllib.request.urlretrieve(b3_url)
        logger.info("B3 downloaded : %s"% b3_file_name)
        logger.info("Download B4")
        b4_file_name, b4_headers = urllib.request.urlretrieve(b4_url)
        logger.info("B4 downloaded : %s"% b4_file_name)
        return {"B2": b2_file_name, "B3": b3_file_name, "B4": b4_file_name}
    except urllib.error.HTTPError:
        logger.info("Impossible to find requested product")
        return False
            
        
def download_product(longitude, latitude, date):
    logger.debug("Download product")
    logger.debug("Longitude : %s"%longitude)
    logger.debug("Latitude : %s"%latitude)
    logger.debug("Date : %s"%date)
    zones_features = read_zones_from_data_file()
    zone = find_zone(zones_features, longitude, latitude)
    logger.debug("Zone find : %s"% zone.name)
    return download_product_in_zone(zone.name, date)
    
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
