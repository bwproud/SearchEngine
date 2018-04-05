#!/bin/bash
#python index.py -i ./dataset/dataset.csv -d dictionary.txt -p postings.txt
#python index.py -i ./dataset/dataset.csv -d dictionary.txt -p postings.txt

pyrun="py -2"

if ! type "py" &> /dev/null; then
  pyrun="python"
fi

$pyrun search.py -d dictionary.txt -p postings.txt -q query.txt -o output.txt
