# Deploy and API and Dashboard to analyse rental delays and estimate pricing of cars rentals on Getaround

## Details for certification purpose
* email : amina.nasri@gmail.com
* video link : https://share.vidyard.com/watch/V3hUD7Mu7TCGhGDRMXZ4oM?

## Project goals and deliverables
* The project repo is accessible via https://github.com/SpeedyAmy/Deployment---ML-API-and-Dashboard-apps
* A dashboard in production accessible via https://getaround-dashboard-an.herokuapp.com/
* An API with a predict endpoint to estimate a car rental pricing
* The API documentation is accesisble via  https://get-around-api2.herokuapp.com/docs
* The MLflow tracking models server via https://mlflow-car-rental-predictor.herokuapp.com/#/experiments/2

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Data

There are two files you need to download:

* "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx 👈 For Data Analysis purpose
* https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv 👈 For Machine Learning purpose

### Prerequisites

The source code is written in Python 3
The python packages can be installed with pip : pip3 install or !pip install if in jupyter notebook
All libraries needed are specified in requitements.txt file


### Installing

You will need to check the libraries to be imported in the requirements file in the repo.
You need to install MLFLOW locally if you want to run the packaged project

## Deployment

- If you want to deploy this repo, you need to get clone it and type on CLI MLFLOW run . 
- Otherwise, you need to have your own MLFLOW tracking URI ready and your AWS credentials and and S3 bucket and database SQL ready in order to run the training part.
- Before running container, export environement variables from secrets.sh or give their values with CLI 

* Dashboard with STREAMLIT (dashboard directory)
- Build docker image:
docker build . -t YOUR_IMAGE_NAME
- RUN localy dashboard (access through browser via localhost:4000/docs)
docker run -it -v "%cd%:/home/app" -e PORT=80 -p 4000:80 you-image-name python app.py

* MACHINE LEARNING with MLFLOW (ml directory)
- Build docker image:
docker build . -t YOUR_IMAGE_NAME
- RUN localy mlflow tracking
docker run -it -v "$(pwd):/home/app" -e AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY" -e BACKEND_STORE_URI="YOUR_BACKEND_STORE_URI" -e ARTIFACT_ROOT="YOUR_S3_BUCKET" -e MLFLOW_TRACKING_URI="YOUR_MLFLOW_HEROKU_SERVER_URI" YOUR_IMAGE_NAME python train.py

* API with FASTAPI (root directory)
- Build build docker image:
docker build . -t YOUR_IMAGE_NAME
- Run locally the api 
docker run -it -v "$(pwd):/home/app" -e AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY" -e BACKEND_STORE_URI="YOUR_BACKEND_STORE_URI" -e ARTIFACT_ROOT="YOUR_S3_BUCKET" -e MLFLOW_TRACKING_URI="YOUR_MLFLOW_HEROKU_SERVER_URI" YOUR_IMAGE_NAME python app.py

* Create app and deploy it with Heroku
1-heroku container:login
2-heroku create YOUR_APP_NAME
3-heroku container:push web -a YOUR_APP_NAME
4-heroku container:release web -a YOUR_APP_NAME
5-heroku open -a YOUR_APP_NAME


## Built With
* source code in Python3. Every repo has its own Dockerfile, script.py and requirements.txt

## Authors

**Amina Nasri** - [SpeedyAmy](https://github.com/SpeedyAmy)
I got help from my co students during the fullstack
