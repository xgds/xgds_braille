
Steps for data import:

1. import track
./xgds_braille//apps/geocamTrack/importer/trackImportRunner.py -c ./xgds_braille/apps/xgds_braille_app/importer/KRex2_PastPosition.yaml -i TRACK_DATA_FILENAME -o 10T

2. import geotiff
manually add the geotiff to geoserver in workspace braille, with name layerName
https://localhost/geoserver/web/wicket/page?6
publish the store
Update transparent color to black
Update tile size to 256, 256
add EPSG:3857 to tile caching

3. add geotiff layer to xGDS
https://localhost/xgds_map_server/addWMS/
wmsUrl: https://localhost/geoserver/braille/wms
layers: braile:layerName

4. Import other scalar data
* environmental: ./apps/xgds_core/importer/csvImportRunner.py -c ./apps/xgds_braille_app/importer/KRex2_Environmental.yaml -i path_to_environmental.tsv
* wall distance: ./apps/xgds_core/importer/csvImportRunner.py -c ./apps/xgds_braille_app/importer/KRex2_EDistance.yaml -i path_to_distances.txt
* rover state:  TODO

5. Import NIRVSS data
* short wavelength NIRVSS:
* long wavelength NIRVSS:
* LCS:

6. Import photos
* DSLR (x2):
* NIRVSS DOC:
* NAVCAM (x2):
* RGB-D Camera:
