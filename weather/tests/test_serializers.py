import pytest

from weather.serializers import ForecastSerializer

@pytest.mark.parametrize('valid_data', [
    {'clouds': 'Cloudy', 'humidity': '50%', 'pressure': '1000 hPa', 'temperature': '25°C'},
])
def test_forecast_serializer_valid_data(valid_data):
    serializer = ForecastSerializer(data=valid_data)
    assert serializer.is_valid()

@pytest.mark.parametrize('invalid_data', [
    {'clouds': 'Cloudy', 'humidity': '170%', 'pressure': '1013 hPa', 'temperature': '22°C'},
])
def test_forecast_serializer_invalid_data(invalid_data):
    serializer = ForecastSerializer(data=invalid_data)
    assert serializer.is_valid()
