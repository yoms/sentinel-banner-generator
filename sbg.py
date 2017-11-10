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

def coma_string_to_list(bands):
    try:
        bands_str = bands.split(',')
        list_returned  = []
        for band_str in bands_str:
            list_returned.append(int(band_str))
        return list_returned
    except ValueError:
        logger.error("Impossible to parse band strings %s"%bands)
        return None
        
    
if __name__ == '__main__':
    # --size_x 1400 --size_y 800 1.6667 43.3 /tmp/banner.png
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", help="Banner width in pixels", default=1400,type=int)
    parser.add_argument("--height", help="Banner height in pixels", default=800,type=int)
    parser.add_argument("--date", help="Image acquisition date")
    parser.add_argument("--verbose", help="run the script in verbose", action="store_true")
    parser.add_argument('--bands', help='Bands used for build the banner (RGB), format : 4,3,2', default='4,3,2')
    parser.add_argument('--red_clip', help='Values used to clip band data ex: 250,2500', default='0,2500')
    parser.add_argument('--green_clip', help='Values used to clip band data ex: 250,2500', default='0,2500')
    parser.add_argument('--blue_clip', help='Values used to clip band data ex: 250,2500', default='0,2500')

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
    
    bands_indexes = coma_string_to_list(args.bands)
    if len(bands_indexes) != 3:
        logger.error("The number of bands used to build banners should be 3")
        exit(1)
        
    red_clip = coma_string_to_list(args.red_clip)
    green_clip = coma_string_to_list(args.green_clip)
    blue_clip = coma_string_to_list(args.blue_clip)
    
    red_clip_tuple = (float(red_clip[0]), float(red_clip[1]))
    blue_clip_tuple = (float(blue_clip[0]), float(blue_clip[1]))
    green_clip_tuple = (float(green_clip[0]), float(green_clip[1]))
    
    if len(red_clip) != 2:
        logger.error("Clip value should contain a min and a max")
        exit(1)
    if len(green_clip) != 2:
        logger.error("Clip value should contain a min and a max")
        exit(1)
    if len(blue_clip) != 2:
        logger.error("Clip value should contain a min and a max")
        exit(1)
    
    if blue_clip[0] > blue_clip[1] : 
        logger.error("Maximum clip value should be higther than the Minimum clip value")
        exit(1)
    if red_clip[0] > red_clip[1] : 
        logger.error("Maximum clip value should be higther than the Minimum clip value")
        exit(1)
    if green_clip[0] > green_clip[1] : 
        logger.error("Maximum clip value should be higther than the Minimum clip value") 
        exit(1)
        
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
    logger.info("Band downloaded : %s"%bands_indexes )
    logger.info("Red band   : %s"%bands_indexes[0] )
    logger.info("Green Band : %s"%bands_indexes[1] )
    logger.info("Blue Band  : %s"%bands_indexes[2] )
    
    logger.info("Red clip   : %s"%red_clip )
    logger.info("Green clip : %s"%green_clip )
    logger.info("Blue clip  : %s"%blue_clip )
    
    bands = sentinel_downloader.download_product(lat, lon, date, bands_indexes)
    banner_generator.create_raster_from_band(bands[bands_indexes[0]], bands[bands_indexes[1]], bands[bands_indexes[2]],tiff_file)
    x, y = banner_generator.get_x_y_for_lon_lat(tiff_file, lat, lon)
    png_created = banner_generator.create_png_from_raster(tiff_file, big_png_file,red_clip=red_clip_tuple, blue_clip=blue_clip_tuple, green_clip=green_clip_tuple)
    if png_created:
        banner_generator.extract_banner(big_png_file, x, y,banner_size_x, banner_size_y, banner_file)
    
    
    
    
