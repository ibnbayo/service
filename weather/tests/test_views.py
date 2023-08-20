import pytest
from django.test import RequestFactory
from django.urls import reverse
from weather.views import ping, forecast

@pytest.fixture
def mock_requests_get(mocker):
    mock = mocker.patch('requests.get')
    mock.return_value.status_code = 200
    return mock

class TestWeatherViews:

    @pytest.fixture
    def factory(self):
        return RequestFactory()

    @pytest.mark.parametrize('city', ['london', 'paris'])
    def test_forecast_success(self, mock_requests_get, factory, city):
        request = factory.get(f'/forecast/{city}')
        response = forecast(request, city)

        assert response.status_code == 200
        assert 'humidity' in response.data

    def test_forecast_not_found(self, mock_requests_get, factory):
        request = factory.get('/forecast/invalidcity')

        response = forecast(request, 'invalidcity')

        mock_requests_get.return_value.status_code = 404

        response = forecast(request, 'invalidcity')

        assert response.status_code == 404
        assert response.data['error_code'] == 'city_not_found'

    def test_forecast_error(self, mock_requests_get, factory):
        request = factory.get('/forecast/london')

        mock_requests_get.return_value.status_code = 500

        response = forecast(request, 'london')

        assert response.status_code == 500
        assert response.data['error_code'] == 'external_api_error'  # Updated error code

    def test_ping(self, mocker, factory):
        mocker.patch(
            'pathlib.Path.read_text',
            return_value='1.0.0'
        )

        request = factory.get('/ping/')
        response = ping(request)

        assert response.status_code == 200

        expected = {
            "name": "weatherservice",
            "status": "ok",
            "version": "1.0.0"
        }

        assert response.data == expected



