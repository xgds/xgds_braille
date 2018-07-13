#!/bin/bash

read -p "About to DELETE the braille-file-store DB and create an empty one. Are you sure (yes or no)? " -r
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]
then
    # delete current database
    curl -X DELETE http://127.0.0.1:5984/braille-data-store
    # create new empty one
    curl -X PUT http://127.0.0.1:5984/braille-data-store
    # install design (query) documents
    curl -X PUT http://127.0.0.1:5984/braille-file-store/"id" -d @./couchViews.js
fi
