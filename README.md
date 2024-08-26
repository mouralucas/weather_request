# Project to fetch weather data for cities

This code was developed using FastAPI because it is a simple framework to build async requests, 
and it's easy to handle the data.



## Running the project in Linux

Export the environment variable for the Open Weather API and then run docker commands. 
This commands must be executed in the same terminal

```bash
export open_weather_api_key=[your_api_key]
```

To run the project just build the docker in the root folder. 

```bash
docker compose build
```

```bash
docker compose up
```

After this commands the server will be running in 

```
http://0.0.0.0:8000 
```

There are two endpoints:
### POST /weather
Required param: user_id

This endpoint triggers the weather fetch to Open Weather api, using the list of cities. 

It will run in the background. To complete all cities it may take a few minutes 
(only 60 requests are allowed per minute).

While it runs, the user can check the percentage of completion using the GET endpoint

### GET /weather
Required query param: user_id

This will return the completion percentage for the user

## Testing

Create the virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies
```bash
pip3 install -r requirements.txt
```

Run the pytest

```bash
pytest
```

It may take some time due to request restriction per period!