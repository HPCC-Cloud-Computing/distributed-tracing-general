# coding=utf-8
from difflib import SequenceMatcher
import unicodecsv as csv

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
def loadCSV():
	csvFile = open("monan.csv", "r")
	csvreader = csv.reader(csvFile, encoding='utf-8')
	results = []
	for row in csvreader:
		monan = {'name' : row[0], 'location' : row[1], 'type' : row[2], 'description' : row[3]}
		results.append(monan)
	return results