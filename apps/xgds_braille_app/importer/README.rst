

=======================================================
Description of files in this directory
=======================================================

.. _TimestampValidator:

Timestamp Validator
~~~~~~~~~~~~~~~~~~~

The first step of our import process is to validate the timestamps in the incoming data, to make sure it can be imported.
This uses a yaml file registry for describing expected time formats.

+----------------------------------------+-------------------------------------------+---------------------------------+
|Filename                                |Description                                |Tasks                            |
+========================================+===========================================+=================================+
|``validate_timestamps.py``              |Script to analyze files and contents times | **move to xgds_core/importer**  |
|                                        |                                           | **update to specify pattern**   |
|                                        |                                           | **in config file for dirname**  |
+----------------------------------------+-------------------------------------------+---------------------------------+
|``timestamp_validator_config.yaml``     |BRAILLE specific                           | **duplicate and modify for**    |
|                                        |                                           | **SUBSEA**                      |
+----------------------------------------+-------------------------------------------+---------------------------------+
|``ort_timestamp_validator_config.yaml`` |BRAILLE specific                           |                                 |
+----------------------------------------+-------------------------------------------+---------------------------------+
|``run_validate_timestamps.sh``          |Script to run validate timestamps on a     | **move to xgds_core/importer**  |
|                                        |nested directory and print out start and   |                                 |
|                                        |end times to a file                        |                                 |
+----------------------------------------+-------------------------------------------+---------------------------------+
|``link_station_searches.py``            |BRAILLE only, hack to make NamedURLs for   |                                 |
|                                        |science stations based on times            |                                 |
+----------------------------------------+-------------------------------------------+---------------------------------+

.. _ImportHandler:

Import Handler
~~~~~~~~~~~~~~

The Import Handler is found in ../scripts, linked from xgds_core.
It is called as follows:

.. code-block:: bash

./apps/xgds_braille_app/scripts/importHandler.py --username xgds --password ##pwhere## /home/xgds/xgds_braille/apps/xgds_braille_app/importer/ImportHandlerConfig.yaml

The last argument is the configuration file for how it will process other data.  There are 2 such configuration files in this directory:

+----------------------------------+-------------------------------------------+---------------------------------+
|Filename                          |Description                                |Tasks                            |
+==================================+===========================================+=================================+
|``importHandlerConfig.yaml``      |BRAILLE specific, for development docker   | **duplicate and modify for**    |
|                                  |                                           | **SUBSEA**                      |
+----------------------------------+-------------------------------------------+---------------------------------+
|``FieldImportHandlerConfig.yaml`` |BRAILLE specific, for production paths     |                                 |
+----------------------------------+-------------------------------------------+---------------------------------+

.. _PythonImportFiles:

Python Import Files
~~~~~~~~~~~~~~~~~~~

These python import files were called by the import handler, specified in the import handler config yaml file.

+------------------------------+-------------------------------------------+---------------------------------+
|Filename                      |Description                                |Tasks                            |
+==============================+===========================================+=================================+
|``convertNirvssSpectra.py``   |BRAILLE only, process nirvss spectra       |                                 |
+------------------------------+-------------------------------------------+---------------------------------+
|``createBandDepthGeoJSON.py`` |BRAILLE only, build geojson for NIRVSS     |                                 |
+------------------------------+-------------------------------------------+---------------------------------+
|``import_file.py``            |Unused, should be for importing generic    | **Move to xgds_core/importer**  |
|                              |files once we have our geofile model       | Hook up to geofile when ready   |
+------------------------------+-------------------------------------------+---------------------------------+
|``import_image.py``           |Used to import images by an http post      | **Move to xgds_image/importer** |
+------------------------------+-------------------------------------------+---------------------------------+
|``import_map.py``             |Unused, should be for importing geotiff    |Move to xgds_map_server/importer |
|                              |files once we have api to geoserver        | Hook up to api to geoserver     |
+------------------------------+-------------------------------------------+---------------------------------+
|``importDocImage.py``         |BRAILLE only, used to preprocess and       |                                 |
|                              |import DOC images over http                |                                 |
+------------------------------+-------------------------------------------+---------------------------------+
|``importNirvssSpectra.py``    |BRAILLE only, csv loader for NIRVSS        |                                 |
+------------------------------+-------------------------------------------+---------------------------------+
|``PNGInfo.py``                |BRAILLE only, read custom data out of PNG  |                                 |
+------------------------------+-------------------------------------------+---------------------------------+


.. _YamlFiles:

Yaml Files
~~~~~~~~~~

These yaml files are used by the csv and track importer for import, and by the code generator.

+------------------------------+-------------------------------------------+---------------------------------+
|Filename                      |Description                                |Tasks                            |
+==============================+===========================================+=================================+
|``KRex2_Distance.yaml``       |BRAILLE only, wall distance                |                                 |
|                              |example of a simple model with one param   |                                 |
+------------------------------+-------------------------------------------+---------------------------------+
|``KRex2_Environmental.yaml``  |BRAILLE only, environmental sensor 3 param | **Reference for CTD**           |
+------------------------------+-------------------------------------------+---------------------------------+
|``KRex2_LCS.yaml``            |BRAILLE only, LCS sensor multi param       |                                 |
+------------------------------+-------------------------------------------+---------------------------------+
|``KRex2_Light.yaml``          |BRAILLE only, light sensors, stateful      |                                 |
+------------------------------+-------------------------------------------+---------------------------------+
|``KRex2_PastPosition.yaml``   |BRAILLE only, handles positions            |**Reference for track/pos data** |
+------------------------------+-------------------------------------------+---------------------------------+
|``KRex2_Tilt.yaml``           |BRAILLE only, tilt angle, simple stateful  |                                 |
+------------------------------+-------------------------------------------+---------------------------------+

.. o __BEGIN_LICENSE__
.. o  Copyright (c) 2015, United States Government, as represented by the
.. o  Administrator of the National Aeronautics and Space Administration.
.. o  All rights reserved.
.. o
.. o  The xGDS platform is licensed under the Apache License, Version 2.0
.. o  (the "License"); you may not use this file except in compliance with the License.
.. o  You may obtain a copy of the License at
.. o  http://www.apache.org/licenses/LICENSE-2.0.
.. o
.. o  Unless required by applicable law or agreed to in writing, software distributed
.. o  under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
.. o  CONDITIONS OF ANY KIND, either express or implied. See the License for the
.. o  specific language governing permissions and limitations under the License.
.. o __END_LICENSE__
