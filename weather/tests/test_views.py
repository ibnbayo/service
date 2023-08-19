import pytest
from django.test import RequestFactory
from weather.views import ping, forecast

@pytest.fixture
def mock_requests_get(mocker):
    mock = mocker.patch('requests.get')
    mock.return_value.status_code = 200
    return mock

def test_ping(mocker):
  mocker.patch(
    'pathlib.Path.read_text', 
    return_value='1.0.0'
  )

  factory = RequestFactory()
  
  request = factory.get('/ping/')
  response = ping(request)

  assert response.status_code == 200
  
  expected = {
    "name": "weatherservice",
    "status": "ok", 
    "version": "1.0.0"
  }

  assert response.data == expected

def test_forecast_success(mock_requests_get):
    factory = RequestFactory()
    request = factory.get('/forecast/london')

    response = forecast(request, 'london')
  
    assert response.status_code == 200
    assert 'humidity' in response.data

def test_forecast_not_found(mock_requests_get):

    factory = RequestFactory()
    request = factory.get('/forecast/invalidcity')
    
    response = forecast(request, 'invalidcity')

    mock_requests_get.return_value.status_code = 404
  
    response = forecast(request, 'invalidcity')

    assert response.status_code == 404
    assert response.data['error_code'] == 'city_not_found'

def test_forecast_error(mock_requests_get):

    factory = RequestFactory()
    request = factory.get('/forecast/london')

    mock_requests_get.return_value.status_code = 500

    response = forecast(request, 'london')

    assert response.status_code == 500
    assert response.data['error_code'] == 'internal_server_error'