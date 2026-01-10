#!/bin/bash
./git.sh;
python generate_markdown.py;
python generate_dataset.py;
python upload_to_hub.py dataset;
