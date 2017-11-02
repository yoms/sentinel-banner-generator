![alt text](https://github.com/yoms/sentinel-banner-generator/raw/master/exemple/toulouse.png)
# sentinel-banner-generator
Generate a banner from Sentinel2 images.

## Caution
Unzip ./data/S2A_OPER.kml.zip before use

If the result is dark, be sure your request lat/lon and sizes are in the product, because due to granule generation maybe you are trying to generate a banner from a no data part of the product.

Exemple : 

![alt text](https://sentinel-s2-l1c.s3.amazonaws.com/tiles/30/T/YN/2017/10/31/0/preview.jpg)

One day maybe i will handle this case, but it seems that i have a life out of my computer.
## command line
Generate banner from the last sentinel2 product at the given position:
```
python3 sbg.py 1.433333 43.600000 /tmp/banner_new.png
```

Generate banner with a specific height and width:
```
python3 sbg.py --height 396 --width 1584  1.433333 43.600000 /tmp/banner_new.png
```

Generate banner from the sentinel2 product at the given position and the given date:
```
python3 sbg.py --date 2017-10-28 1.433333 43.600000 /tmp/banner_new.png
```

Launch in verbose (Mainly because you love my english, baguette du fromage)
```
python3 sbg.py --verbose 1.433333 43.600000 /tmp/banner_new.png
```

If you prefer use docker you can try this way:
```
docker run -v /tmp/out:/data --rm yoms/sentinel-banner-generator 1.433333 43.6 --date 2017-10-28 /data/banner.png
```
## how?
* The script use the S2A_OPER_GIP_TILPAR_20150622T000000_21000101T000000_ZZ_0007.kml provide by the esa to locate the right zone for the given position.
* Then the script download the bands 5,4,3 from http://sentinel-s2-l1c.s3-website.eu-central-1.amazonaws.com/#tiles/.
* After that we merge the differents bands in one GTiff, and from this one we compute a big png.
* At the and the script clip the big png.

## Why?
* The script: why not, create another useless script on github
* Create a GTiff and not compute the banner from the downloaded band: because i dont have the time to optimise this part for now.
* My python is dirty: Not used to be a python guy.

## TODO
- [ ] Add the possibility to compose the banner from others band
- [ ] Handle lat lon on the border of an product
