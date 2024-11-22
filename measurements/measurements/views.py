from .models import Measurement
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import requests
import json

def check_variable(data):
    r = requests.get(settings.PATH_VAR, headers={"Accept":"application/json"})
    variables = r.json()
    for variable in variables:
        if data["variable"] == variable["id"]:
            return True
    return False

def get_place_id(data):
    """
    Modificar la función para buscar el lugar por código en lugar de nombre.
    """
    r = requests.get(settings.PATH_PLACES, headers={"Accept": "application/json"})
    places = r.json()
    for place in places:
        if data["place"] == place["code"]:
            return place["id"]
    return -1


def MeasurementList(request):
    queryset = Measurement.objects.all()
    context = list(queryset.values('id', 'variable', 'value', 'unit', 'place', 'dateTime'))
    return JsonResponse(context, safe=False)

def MeasurementCreate(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data_json = json.loads(data)
        place_id = get_place_id(data_json)
        if check_variable(data_json) and place_id != -1:
            measurement = Measurement()
            measurement.variable = data_json['variable']
            measurement.value = data_json['value']
            measurement.unit = data_json['unit']
            measurement.place = place_id
            measurement.save()
            return HttpResponse("successfully created measurement")
        else:
            return HttpResponse("unsuccessfully created measurement. Variable or place does not exist")

def MeasurementsCreate(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data_json = json.loads(data)
        measurement_list = []
        for measurement in data_json:
                    try:
                         
                        place_id = get_place_id(measurement)
                        
                    except:
                        place_id = 1
                    if check_variable(measurement) == True and place_id != -1:
                        db_measurement = Measurement()
                        db_measurement.variable = measurement['variable']
                        db_measurement.value = measurement['value']
                        db_measurement.unit = measurement['unit']
                        db_measurement.place = place_id
                        measurement_list.append(db_measurement)
                    else:
                        return HttpResponse("unsuccessfully created measurement. Variable or place does not exist")
        
        Measurement.objects.bulk_create(measurement_list)
        return HttpResponse("successfully created measurements")