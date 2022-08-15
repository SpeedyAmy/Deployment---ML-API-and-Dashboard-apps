docker run -it \
-v "$(pwd):/home/app" \
-p 4000:4000 \
-e PORT=4000 \
-e MLFLOW_TRACKING_URI="https://mlflow-car-rental-predictor.herokuapp.com/" \
-e AWS_ACCESS_KEY_ID="THIS_IS_SECRET" \
-e AWS_SECRET_ACCESS_KEY="THIS_IS_SECRET" \
-e ARTIFACT_ROOT="THIS_IS_SECRET" \
getaround-api