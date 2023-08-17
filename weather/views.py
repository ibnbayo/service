from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ForecastSerializer
import requests
import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent 

@api_view(['GET'])
def ping(request):

    version = (BASE_DIR / 'VERSION').read_text().strip()
    
    data = {
        "name": "weatherservice",
        "status": "ok",
        "version": version
    }
    
    return Response(data)


@api_view(['GET'])
def forecast(request, city):

  api_key = settings.OPENWEATHER_API_KEY

  url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"

  response = requests.get(url)

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

    # return Response(forecast_data)

  else:
    return Response({"error": "Error retrieving forecast"}, status=400)

