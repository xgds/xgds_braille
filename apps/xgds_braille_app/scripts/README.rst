
Steps for data import:

1. Run the data validator:
cd apps/xgds_braille_app/importer
./validate_timestamps.py -m -c timestamp_validator_config.yaml  <path to data you want to analyze>

2. Run the import handler:
./apps/xgds_braille_app/scripts/importHandler.py --username xgds --password ##pwhere## /home/xgds/xgds_braille/apps/xgds_braille_app/importer/ImportHandlerConfig.yaml

3. import geotiff
manually add the geotiff to geoserver in workspace braille, with name layerName
https://braille-field.xgds.org/geoserver/web/wicket/page?6
publish the store
Update transparent color to black
Update tile size to 256, 256
add EPSG:3857 to tile caching

4. add geotiff layer to xGDS
https://braille-field.xgds.org/xgds_map_server/addWMS/
wmsUrl: https://localhost/geoserver/braille/wms
layers: braile:layerName

