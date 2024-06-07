import csv

from models import GP

with open('./GP.csv') as f:
    csvreader = csv.DictReader(f)
    for row in csvreader:
        GP.objects.create(*row)
