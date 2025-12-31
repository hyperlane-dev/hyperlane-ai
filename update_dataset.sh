#!/bin/bash
python generate_markdown.py;
python generate_dataset.py;
python upload_to_hub.py dataset;
gtl acp;
