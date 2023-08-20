Weather service
===============

## Overview

This is an HTTP weather service that provides information on weather. It uses the [openweathermap](https://www.openweathermap.org) API as a data source. The API requires an API key that can be obtained for free after [signing up](https://home.openweathermap.org/users/sign_up).
Live link: [Weather Service](https://weatherapi-nuvrkturzq-nw.a.run.app)


Getting it running
------------------

## Getting it running

### Running via terminal

# 1. Install Required Packages
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```
# 2. Install pipenv
`pip3 install pipenv`

# 3. Clone the Repository
git clone https://github.com/ibnbayo/service
cd <project_folder>

# 4. Install Dependencies with pipenv
`pipenv install`

# 5. Activate Virtual Environment
`pipenv shell`

# 6. Create a .env File
Copy the .env.example file to .env and add your OpenWeatherMap API key and set secret to any value
`cp .env.example .env`

# 7. Run Migrations
`python manage.py migrate`

# 8. Run the Development Server
`python manage.py runserver`

### Running with Docker

# 1. Install Docker
```bash
sudo apt update
sudo apt install docker.io
```

# 2. Clone the Repository
git clone https://github.com/ibnbayo/service
cd <project_folder>

# 3. Build the Docker Image
`docker build -t weatherapi .`

# 4. # Copy the .env.example file to .env
`cp .env.example .env`

# 5. Set your OpenWeatherMap API key and secret in .env

# 6. Run the Docker Container
docker run -d -p 8080:8080 --env-file .env weatherapi



The Service
-----------

The following calls can be made against this web service using 
[curl](https://curl.haxx.se/)

### `/ping`

This is a simple health check that we can use to determine that the service is
running, and provides information about the application. The `"version"`
attribute matches the version number in the `VERSION`
file.

```bash
$ curl -si http://localhost:8080/ping/

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
{
  "name": "weatherservice",
  "status": "ok",
  "version": "1.0.0"
}
```

### `/forecast/<city>`

This endpoint allows a user to request a breakdown of the current weather for
a specific city. The response includes a description of the cloud cover,
the humidity as a percentage, the pressure in hecto Pascals (hPa), and
temperature in Celsius.

For example fetching the weather data for London looks like this:

```bash
$ curl -si http://localhost:8080/forecast/london/

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
{
    "clouds": "broken clouds",
    "humidity": "66.6%",
    "pressure": "1027.51 hPa",
    "temperature": "14.4C"
}
```

Authentication
--------------

The `/forecast/<city>` and `/ping` endpoints are secured with Basic Authentication. Use user `admin` and password `secret` to access.

Deployment
--------------

The service is deployed to Google Cloud Run. 

Testing
-----------



To Do
-----------

The `/forecast/<city>` endpoint should also take an `at` query string parameter that will
return the weather forecast for a specific date or datetime. The `at`
parameter should accept both date and datetime stamps in the [ISO
8601](https://en.wikipedia.org/wiki/ISO_8601) format. The service should
respect time zone offsets.

```bash
$ curl -si http://localhost:8080/forecast/london/?at=2018-10-14T14:34:40+0100

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
{
    "clouds": "sunny",
    "humidity": "12.34%",
    "pressure": "1000.51 hPa",
    "temperature": "34.4C"
}

$ curl -si http://localhost:8080/forecast/london/?at=2018-10-14

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
{
    "clouds": "overcast",
    "humidity": "20.6%",
    "pressure": "1014.51 hPa",
    "temperature": "28.0C"
}
```

### Errors

When no data is found or the endpoint is invalid the service responds
with `404` status code and a message:

```bash
$ curl -si http://localhost:8080/forecast/midgar/

HTTP/1.1 404 Not Found
Content-Type: application/json; charset=utf-8
{
    "error": "Cannot find city 'midgar'",
    "error_code": "city_not_found"
}
```

Similarly invalid requests return a `400` status code:

```bash
$ curl -si http://localhost:8080/forecast/london/?at=1938-12-25

HTTP/1.1 400 Bad Request
Content-Type: application/json; charset=utf-8
{
    "error": "Date is in the past",
    "error_code": "invalid date"
}
```

If anything else goes wrong the service returns a response with a `500` status code
and a message that doesn't leak any information about the service internals:

```bash
$ curl -si http://localhost:8080/forecast/london

HTTP/1.1 500 Internal Server Error
Content-Type: application/json; charset=utf-8
{
    "error": "Something went wrong",
    "error_code": "internal_server_error"
}
```

## Error Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 404         | City not found or invalid endpoint     |
| 500         | Internal server error, no details leaked |



