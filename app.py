import mlflow 
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI

# description will apear in the doc
description = """
Welcome to GETAROUND prediction API
Getaround is a site where customers can rent a car. 
You can use the api to estimate the price of your car rental given a number of specifications of the car.
## Preview
* `/preview` here you can see the pricing of the dataset in general
## Estimation
* `/predict` put your car informations to get the price of the rent per day

"""

# tags to identify different endpoints 
tags_metadata = [
    {
        "name": "Preview",
        "description": "Preview of the existing dataset",
    },

    {
        "name": "Estimation",
        "description": "Prediction made with a machine learning model based on Random Forest"
    }
]

#initialising an API object with FastApi class
app = FastAPI(
    title="Get_Around API",
    description=description,
    version="1.0",
    contact={
        "name": "Amina Nasri",
        "url": "https://github.com/SpeedyAmy",
    },
    openapi_tags=tags_metadata
)

class PredictionFeatures(BaseModel):
    model_key: str
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

@app.get("/", tags=["Preview"])
async def index():
    """
    Simply returns preview of the dataset!
    """
    print("/preview called")
    df = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv")

    # Select only n rows
    sample = df.sample(10).iloc[:,1:]
    return sample.to_json(orient='records')


@app.post("/predict", tags=["Estimation"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Prediction for one observation. Endpoint will return a dictionnary like this:
    ```
    {'prediction': value}
    ```
    You need to give this endpoint all columns values as dictionnary, or form data.
    """
    # Read data 
    df = pd.DataFrame(dict(predictionFeatures), index=[0])

    # Log model from mlflow 
    logged_model = 'runs:/8b00b8e04bde401dae69fe09a74c7763/car_rental_predictor'
    

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)
