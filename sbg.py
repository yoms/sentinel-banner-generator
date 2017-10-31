import banner_generator
import sentinel_downloader
import uuid
import tempfile
import os.path
from datetime import datetime
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinel-banner-generator")



def configure_logger(verbose):
    logger.setLevel(logging.INFO)
    banner_generator.logger.setLevel(logging.INFO)
    sentinel_downloader.logger.setLevel(logging.INFO)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        banner_generator.logger.setLevel(logging.DEBUG)
        sentinel_downloader.logger.setLevel(logging.DEBUG)


if __name__ == '__main__':

    # --size_x 1400 --size_y 800 1.6667 43.3 /tmp/banner.png
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", help="Banner width in pixels", default=1400,type=int)
    parser.add_argument("--height", help="Banner height in pixels", default=800,type=int)
    parser.add_argument("--date", help="Image acquisition date")
    parser.add_argument("--verbose", help="run the script in verbose", action="store_true")
    parser.add_argument("latitude", help="Latitude", type=float)
    parser.add_argument("longitude", help="longitude", type=float)
    parser.add_argument("output", help="Banner file result in output")
    args = parser.parse_args()

    tiff_file = os.path.join(tempfile.gettempdir(), 'merge.tiff')
    big_png_file = os.path.join(tempfile.gettempdir(), 'big_png.png')
    banner_file = args.output
    
    lat = args.latitude
    lon = args.longitude
    
    banner_size_x = args.width
    banner_size_y = args.height
    
    configure_logger(args.verbose)
        
    if args.date == None:
        date = sentinel_downloader.last_image_date_for_lat_lon(lat, lon)
    else:
        date = datetime.strptime( args.date ,"%Y-%m-%d" )
    
    logger.info("Launch banner generation with given parameters : ")
    logger.info("Banner file : %s"% banner_file)
    logger.info("Latitude : %s"% lat)
    logger.info("Longitude : %s"% lon)
    logger.info("Banner width : %s"% banner_size_x)
    logger.info("Banner height : %s"% banner_size_y)
    logger.info("Acquisition date : %s"% date.strftime("%Y-%m-%d"))
    
    bands = sentinel_downloader.download_product(lat, lon, date)
    banner_generator.create_raster_from_band(bands['B4'], bands['B3'], bands['B2'],tiff_file)
    x, y = banner_generator.get_x_y_for_lon_lat(tiff_file, lat, lon)
    banner_generator.create_png_from_raster(tiff_file, big_png_file)
    banner_generator.extract_banner(big_png_file, x, y,banner_size_x, banner_size_y, banner_file)
    
    
    
    
