import csv

from django.shortcuts import render
from device.models import *


def device(request):
    # with open('./GP.csv') as f:
    #     csvreader = csv.DictReader(f)
    #     for row in csvreader:
    #         Position.objects.create(**row)
    eq1 = Equipment.objects.get(pk=1)
    tags = Tag.objects.filter(pk=eq1.pk)

    context = {
        'eq1': eq1,
        'tags': tags,
    }

    for i in context:
        print(i)
    return render(request, 'device/device.html', context=context)
