import logging
import pathlib
from datetime import datetime, timezone

import dateutil.parser as parser
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ForecastSerializer

logger = logging.getLogger(__name__)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
VERSION_FILE = BASE_DIR / 'VERSION'
OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY
OPENWEATHER_GEO_URL = 'http://api.openweathermap.org/geo/1.0/direct'
OPENWEATHER_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
OPENWEATHER_TIMEMACHINE_URL = 'https://api.openweathermap.org/data/3.0/onecall/timemachine'

HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ping(request):
    """
    Endpoint to check service health and version.
    """
    version = VERSION_FILE.read_text().strip()
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
    logger.error('An unexpected error occurred')
    return Response({
        'error': 'Something went wrong', 
        'error_code': 'internal_server_error'
    }, status=HTTP_STATUS_INTERNAL_SERVER_ERROR)

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
    """
    Validate and convert a raw datetime string to a timestamp.
    Return a tuple of (timestamp, error) where error is None if valid.
    """
    try:
        datetime_obj = parser.isoparse(raw_datetime)
    except ValueError:
        return None, {"error": "Invalid ISO date/time format"}

    if datetime_obj < datetime.now():
        return None, {"error": "Datetime is in the past"}
  
    timestamp = datetime_obj.timestamp()
    return timestamp, None

def get_location_coordinates(location):
    """
    Get the latitude and longitude of a location using the OpenWeather API.
    Return a tuple of (lat, lon, error) where error is None if found.
    """
    geo_url = f"{OPENWEATHER_GEO_URL}?q={location}&limit=1&appid={OPENWEATHER_API_KEY}"
    
    try:
        geo_data = requests.get(geo_url).json()
    except requests.exceptions.RequestException as e:
        return None, None, handle_error_response()

    if not geo_data or 'lat' not in geo_data[0] or 'lon' not in geo_data[0]:
        return None, None, Response({
            'error': f"Cannot find city '{location}'",
            'error_code': 'city_not_found'
        }, status=HTTP_STATUS_NOT_FOUND)

    lat = geo_data[0]['lat']
    lon = geo_data[0]['lon']
    
    return lat, lon, None

def get_current_weather(lat, lon):
    """
    Get the current weather data for a given latitude and longitude using the OpenWeather API.
    Return a tuple of (weather, error) where error is None if successful.
    """
    
    weather_url = f"{OPENWEATHER_WEATHER_URL}?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
    
    try:
        weather_data = requests.get(weather_url).json()
        
        if weather_data['cod'] != HTTP_STATUS_OK:
            return None, Response({
                'error': weather_data['message'],
                'error_code': weather_data['cod']
            }, status=weather_data['cod'])
        
        weather = process_forecast_data(weather_data)
        return weather, None
    except requests.exceptions.RequestException as e:
        return None, handle_error_response()

def get_past_weather(lat, lon, timestamp):
    """
    Get the past weather data for a given latitude, longitude, and timestamp using the OpenWeather API.
    Return a tuple of (weather, error) where error is None if successful.
    """
    
    weather_url = f"{OPENWEATHER_TIMEMACHINE_URL}?lat={lat}&lon={lon}&dt={timestamp}&units=metric&appid={OPENWEATHER_API_KEY}"
    
    try:
        weather_data = requests.get(weather_url).json()
        
        # Check if the response has data
        if not weather_data or 'data' not in weather_data or len(weather_data['data']) == 0:
            return None, Response({
                'error': 'Something went wrong',
                'error_code': 'internal_server_error'
            }, status=HTTP_STATUS_INTERNAL_SERVER_ERROR)

        weather = process_forecast_data(weather_data['data'][0])
        return weather, None
    except requests.exceptions.RequestException as e:
        return None, handle_error_response()

@api_view(['GET'])  
def forecast(request, location):
    """
    Endpoint to get the forecast data for a given location and optional datetime.
    """
    
    query = request.GET
    
    # Validate and convert the datetime parameter if present
    if 'at' in query:
        raw_datetime = query['at']
        # Use a different name for the local variable
        local_timestamp, error = validate_and_convert_datetime(raw_datetime)
        
        if error is not None:
            return Response(error, status=HTTP_STATUS_BAD_REQUEST)

    lat, lon, error = get_location_coordinates(location)

    if error is not None:
        return error
    
    # Get the weather data for the coordinates and optional timestamp using the OpenWeather API
    if 'at' in query:
        weather, error = get_past_weather(lat, lon, local_timestamp)
    else:
        weather, error = get_current_weather(lat, lon)
    
    if error is not None:
        return error
    
    return Response(weather, status=HTTP_STATUS_OK)
