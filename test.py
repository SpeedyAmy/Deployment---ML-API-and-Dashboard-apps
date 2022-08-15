import requests

response = requests.post("https://getaround-price-pred-api.herokuapp.com/predict", json={
  "model_key": "Mercedes",
  "mileage": 181672,
  "engine_power": 105,
  "fuel": "diesel",
  "paint_color": "white",
  "car_type": "hatchback",
  "private_parking_available": True,
  "has_gps": True,
  "has_air_conditioning": False,
  "automatic_car": False,
  "has_getaround_connect": True,
  "has_speed_regulator": False,
  "winter_tires": True
})

print(response.json())