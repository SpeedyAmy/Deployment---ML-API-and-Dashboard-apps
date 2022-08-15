import argparse
import pandas as pd
import time
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import  StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline


if __name__ == "__main__":

    ### MLFLOW Experiment setup
    experiment_name="car_rental_predictor1"
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    client = mlflow.tracking.MlflowClient()
    run = client.create_run(experiment.experiment_id)

    print("training model...")
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog(log_models=False) # We won't log models right away

    # Parse arguments given in shell script
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_estimators")
    parser.add_argument("--min_samples_split")
    args = parser.parse_args()

    # Import dataset
    df =  pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv")
    # dropping useless column
    df = df.drop("Unnamed: 0", axis=1)

    # X, y split 
    target_col_name = "rental_price_per_day"
    X = df.loc[:, df.columns != target_col_name]
    y = df.loc[:, target_col_name]

    # Train / test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state=42)

    # Preprocessing 
    #there are no missing values in the dataset. We only need to standardize NF and One hot Encode CF
    numerical_features = ["mileage", "engine_power"]
    categorical_features = ["model_key", "fuel", "paint_color", "car_type", "private_parking_available", "has_gps", "has_air_conditioning", "automatic_car", "has_getaround_connect", "has_speed_regulator", "winter_tires"]
    #Create pipeline for numeric features
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    #Create pipeline for categorical features
    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(drop='first')) # first column will be dropped to avoid creating correlations between features
        ])

    #Use ColumnTranformer to make a preprocessor object
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # Pipeline 
    n_estimators = int(args.n_estimators)
    min_samples_split=int(args.min_samples_split)

    model = Pipeline(steps=[
        ("Preprocessing", preprocessor),
        ("Regressor",RandomForestClassifier(n_estimators=n_estimators, min_samples_split=min_samples_split))
    ], verbose=True)


    # Log experiment to MLFlow
    with mlflow.start_run(run_id = run.info.run_id) as run:
        model.fit(X_train, y_train)
        predictions = model.predict(X_train)

        # Log model seperately to have more flexibility on setup 
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="car_rental_predictor",
            registered_model_name="car_rental_predictor_RF",
            signature=infer_signature(X_train, predictions)
        )
        
    print("...Done!")
    print(f"---Total training time: {time.time()-start_time}")