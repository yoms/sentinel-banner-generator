from osgeo import gdal, osr, ogr
import numpy as np
import scipy.misc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("banner-generator")

def create_raster_from_band( red, green, blue, output_file):
    logger.debug("Create big raster in output_file : %s"%output_file)
    red_ds = gdal.Open(red)
    nx = red_ds.GetRasterBand(1).XSize
    ny = red_ds.GetRasterBand(1).YSize
    
    dst_ds = gdal.GetDriverByName('GTiff').Create(output_file, ny, nx, 3, gdal.GDT_UInt16)

    dst_ds.SetGeoTransform(red_ds.GetGeoTransform())
    dst_ds.SetProjection(red_ds.GetProjection())
    
    def write_band(band, index_band):
        logger.debug("Write band : %s"%index_band)
        band_ds = gdal.Open(band)
        array = band_ds.GetRasterBand(1).ReadAsArray()
        dst_ds.GetRasterBand(index_band).WriteArray(array)
            
    write_band(red, 1)
    write_band(blue, 2)
    write_band(green, 3)
    
    dst_ds.FlushCache()
    
    dst_ds = None
    logger.debug("Big raster is write in output_file : %s"%output_file)

def create_png_from_raster(raster_file, output_file, blue_clip=(0.,2500.), red_clip=(0.,2500.), green_clip=(0.,2500.)):
    logger.debug("Create big png in output_file : %s"%output_file)
    raster_ds = gdal.Open(raster_file)
    bytes_max = 255.  
    
    if blue_clip[0] > blue_clip[1] : 
        logger.error("Maximum clip value should be higther than the Minimum clip value")
        return False
    if red_clip[0] > red_clip[1] : 
        logger.error("Maximum clip value should be higther than the Minimum clip value")
        return False
    if green_clip[0] > green_clip[1] : 
        logger.error("Maximum clip value should be higther than the Minimum clip value") 
        return False
    
    def clip_array(band_index, clip):
        array = np.array(raster_ds.GetRasterBand(band_index).ReadAsArray())
        array = np.clip(array, clip[0], clip[1])
        array = array - clip[0]
        array = (np.float32(array)*bytes_max)/(clip[1]-clip[0])
        array = array.astype(int)
        return array
    
    logger.debug("Prepare red color, clip raw value at %s, %s"%red_clip)    
    red_array = clip_array(1, red_clip)
    logger.debug("Prepare green color, clip raw value at %s, %s"%green_clip)
    green_array = clip_array(2, green_clip)
    logger.debug("Prepare blue color, clip raw value at %s, %s"%blue_clip)
    blue_array = clip_array(3, blue_clip)
    
    rgb = np.zeros((len(red_array), len(red_array[0]), 3), dtype=np.uint8)
    rgb[..., 0] = red_array
    rgb[..., 1] = green_array
    rgb[..., 2] = blue_array
    logger.debug("Writing png file in %s"%output_file)
    scipy.misc.imsave(output_file, rgb)
    return True
    
def get_x_y_for_lon_lat(raster_file, lon, lat):
    logger.debug("Compute x and y from lon lat")
    logger.debug("Longitude : %s"%lon)
    logger.debug("Latitude : %s"%lat)
    sref = osr.SpatialReference()
    sref.ImportFromEPSG(4326)
   
    # create a geometry from coordinates
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)

    raster_ds = gdal.Open(raster_file)
    dref = osr.SpatialReference()
    dref.ImportFromWkt(raster_ds.GetProjection())
    ct = osr.CoordinateTransformation(sref,dref)
    point.Transform(ct)
    point_x = point.GetX()
    point_y = point.GetY()
    logger.debug("Point value in raster proj")
    logger.debug("Point x : %s"%point_x)
    logger.debug("Point y : %s"%point_y)
    ulx, xres, xskew, uly, yskew, yres  = raster_ds.GetGeoTransform()
    
    logger.debug("Upper left coordinate in proj")
    logger.debug("Point x : %s"%ulx)
    logger.debug("Point x : %s"%uly)
    lrx = ulx + (raster_ds.RasterXSize * xres)
    lry = uly + (raster_ds.RasterYSize * yres)
    logger.debug("Lower rigth coordinate in proj")
    logger.debug("Point x : %s"%lrx)
    logger.debug("Point x : %s"%lry)
    
    logger.debug("Raster resolution")
    logger.debug("Res on X : %s"%xres)
    logger.debug("Res on Y : %s"%yres)
    point_x = (point_x- ulx)/xres
    point_y = (point_y- uly)/yres

    return (int(point_x), int(point_y) )

def extract_banner(img_path, x, y, size_x, size_y, out_path):
    logger.debug("Extract banner")
    y_min = int(y-size_y/2)
    y_max = y_min+size_y
    
    x_min = int(x-size_x/2)
    x_max = x_min+size_x
    logger.debug("Extract data from table")
    logger.debug("Min x : %s"%x_min)
    logger.debug("Max x : %s"%x_max)
    logger.debug("Min y : %s"%y_min)
    logger.debug("Max y : %s"%y_max)
    img = scipy.misc.imread(img_path)
    
    y_min = max(0, min(y_min, len(img)))
    y_max = max(0, min(y_max, len(img)))
    x_min = max(0, min(x_min, len(img[0])))
    x_max = max(0, min(x_max, len(img[0])))
    
    logger.debug("After clamp")
    logger.debug("Min x : %s"%x_min)
    logger.debug("Max x : %s"%x_max)
    logger.debug("Min y : %s"%y_min)
    logger.debug("Max y : %s"%y_max)
    
    logger.debug("Image y: %s"%len(img))
    logger.debug("Image x: %s"%len(img[0]))
    
    if y_max == y_min:
        logger.error("After clamp, image size is Null")
        return False
    if x_max == x_min:
        logger.error("After clamp, image size is Null")
        return False
    rgb = np.zeros((y_max-y_min, x_max-x_min, 3), dtype=np.uint8)
    rgb[..., 0] = img[y_min:y_max,x_min:x_max, 0]
    rgb[..., 1] = img[y_min:y_max,x_min:x_max, 1]
    rgb[..., 2] = img[y_min:y_max,x_min:x_max, 2]
    logger.debug("Write banner in output file %s", out_path)
    scipy.misc.imsave(out_path, rgb)
    return True

if __name__ == '__main__':

    logger.setLevel(logging.DEBUG)
    tiff_file = "/tmp/out.tiff"
    big_png_file = "/tmp/out_big.png"
    banner_file = "/tmp/out.png"
#    create_raster_from_band( '/tmp/tmp0_if50g9','/tmp/tmpz61ja8cq','/tmp/tmp7dl287r9', tiff_file)
#    x, y = get_x_y_for_lon_lat(tiff_file, 1.433333, 43.6)
#    create_png_from_raster(tiff_file, big_png_file, red_clip=(250., 2500.), blue_clip=(250., 2500.), green_clip=(250., 2500.))
#    extract_banner(big_png_file, x, y,1400, 800, banner_file)
    extract_banner(big_png_file, 0, 0,1400, 800, banner_file)
    extract_banner(big_png_file, 10980, 10980,1400, 800, banner_file)
    extract_banner(big_png_file, 20980, 20980,1400, 800, banner_file)

