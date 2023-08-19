from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ForecastSerializer


import requests
import pathlib
import logging
logger = logging.getLogger(__name__)



BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

@api_view(['GET'])
def ping(request):

    version = (BASE_DIR / 'VERSION').read_text().strip()
    
    data = {
        "name": "weatherservice",
        "status": "ok",
        "version": version
    }
    
    return Response(data)



def handle_error_response(e):
  logging.error(f'Unexpected error: {e}')
  
  return Response({
    'error': 'Something went wrong', 
    'error_code': 'internal_server_error'},
    status=500)

@api_view(['GET'])  
def forecast(request, city):

  try:

    api_key = settings.OPENWEATHER_API_KEY
    base_url = 'https://api.openweathermap.org/data/2.5/weather'

    at= request.GET.get('at')

    params = {
            'q': city,
            'appid': api_key,
            'units': 'metric', 
        }
    

    response = requests.get(base_url, params=params)
  
  except Exception as e:
    return handle_error_response(e)

  if response.status_code == 404:

    if response.status_code == 404:

        error = response.json()['message']
        
        return Response({
        'error': f"Cannot find city '{city}'", 
        'error_code': 'city_not_found'
        }, status=404)


  elif response.status_code == 200:

    if response.status_code == 200:

        data = response.json()

        clouds = data['weather'][0]['description']

        humidity = f"{data['main']['humidity']}%"

        pressure = f"{round(data['main']['pressure'] / 10)} hPa" 

        temperature = f"{round(data['main']['temp'])}°C"

        forecast_data = {
        "clouds": clouds,
        "humidity": humidity, 
        "pressure": pressure,
        "temperature": temperature
        }

        serializer = ForecastSerializer(forecast_data)
        return Response(serializer.data)

  else:

    return Response({"error": "Error retrieving forecast"}, status=400)
  
  return Response(data)






