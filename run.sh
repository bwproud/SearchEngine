#!/bin/bash
#python index.py -i ./dataset/dataset.csv -d dictionary.txt -p postings.txt
#python index.py -i ./dataset/dataset.csv -d dictionary.txt -p postings.txt
python search.py -d dictionary.txt -p postings.txt -q queries.txt -o output.txt
