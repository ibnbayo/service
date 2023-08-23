from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ForecastSerializer
from datetime import datetime
import datetime
import re

import time

import dateutil.parser as parser

import urllib.parse
from urllib.parse import urlparse


import requests
import logging
import pathlib

logger = logging.getLogger(__name__)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ping(request):
    """
    Endpoint to check service health and version.
    """
    version = (BASE_DIR / 'VERSION').read_text().strip()
    data = {
        "name": "weatherservice",
        "status": "ok",
        "version": version
    }
    return Response(data)

def handle_error_response():
    """
    Handle unexpected errors and return a consistent error response.
    """
    logging.error('An unexpected error occurred')
    return Response({
        'error': 'Something went wrong', 
        'error_code': 'internal_server_error'
    }, status=500)

def process_forecast_data(data):
    """
    Process the raw API response to extract relevant forecast data.
    """
    clouds = data['weather'][0]['description']
    humidity = f"{data['main']['humidity']}%"
    pressure = f"{round(data['main']['pressure'] / 10)} hPa" 
    temperature = f"{round(data['main']['temp'])}°C"

    return {
        "clouds": clouds,
        "humidity": humidity, 
        "pressure": pressure,
        "temperature": temperature
    }



def validate_and_convert_datetime(raw_datetime):

  try:
    datetime_obj = parser.isoparse(raw_datetime)

  except ValueError:
    return {"error": "Invalid ISO date/time format"}, 400

  if datetime_obj < datetime.now():
    return {"error": "Datetime is in the past"}, 400
  
  timestamp = datetime_obj.timestamp()

  return timestamp



#error handling bing
@api_view(['GET'])  
def forecast(request, location):

  url = request.build_absolute_uri()
  parsed = urlparse(url)

  query = urllib.parse.parse_qs(parsed.query)

  if 'at' in query:
    old_raw_datetime = query['at'][0]
    raw_datetime = re.sub(r'\+\d{4}$', '', old_raw_datetime)

    try:
      parsed_datetime = parser.isoparse(raw_datetime) 
    except ValueError:
      return Response({
        'error': 'Invalid date and time format',
        'error_code': 'invalid_date_time'
      }, status=400)

    local_datetime = parsed_datetime.astimezone(datetime.timezone.utc)
    datetimev = int(time.mktime(local_datetime.timetuple())) 

    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={settings.OPENWEATHER_API_KEY}"
    

    try:
      geo_data = requests.get(geo_url).json()
    except requests.exceptions.RequestException as e:
      return handle_error_response()

    if not geo_data or 'lat' not in geo_data[0] or 'lon' not in geo_data[0]:
      return Response({
        'error': f"Cannot find city '{location}'",
        'error_code': 'city_not_found'
      }, status=404)

    lat = geo_data[0]['lat']
    lon = geo_data[0]['lon']

    weather_url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={datetimev}&appid={settings.OPENWEATHER_API_KEY}"
    
    try:
      weather_data = requests.get(weather_url).json()
    except requests.exceptions.RequestException as e:
      return handle_error_response()

    if not weather_data or 'data' not in weather_data or len(weather_data['data']) == 0:
      return Response({
        'error': f"Something went wrong",
        'error_code': 'internal_server_error'
      }, status=500)

    weather = weather_data['data'][0]

  else:


    try:
        api_key = settings.OPENWEATHER_API_KEY
        base_url = 'https://api.openweathermap.org/data/2.5/weather'
        

        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric', 
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 404:
            error = response.json()['message']
            return Response({
                'error': f"Cannot find city '{location}'", 
                'error_code': 'city_not_found'
            }, status=404)
        
        elif response.status_code == 400:
            return Response({
                'error': 'Date is in the past', 
                'error_code': 'invalid_date'
            }, status=400)

        elif response.status_code == 200:
            data = response.json()
            forecast_data = process_forecast_data(data)
            serializer = ForecastSerializer(forecast_data)
            return Response(serializer.data)

        else:
            return handle_error_response()

    except Exception as e:
        return handle_error_response()


  clouds = weather['weather'][0]['description']
  humidity = str(weather['humidity']) + '%'
  pressure = str(weather['pressure']) + ' hPa'  
  temperature = str(round(weather['temp'])) + '°C'

  forecast = {
  'clouds': clouds,
  'humidity': humidity,
  'pressure': pressure,
  'temperature': temperature   
  }

  serializer = ForecastSerializer(forecast)  

  return Response(serializer.data)
