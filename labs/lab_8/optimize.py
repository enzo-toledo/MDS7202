import os
import pickle

import mlflow
import optuna
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# Repetimos todo para que funcione el .py bien:
df = pd.read_csv("water_potability.csv")
df.fillna(df.median(), inplace=True)

X = df.drop("Potability", axis=1)
y = df["Potability"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def get_best_model(experiment_id):
    runs = mlflow.search_runs(experiment_id)
    best_model_id = runs.sort_values("metrics.valid_f1")["run_id"].iloc[0]
    best_model = mlflow.sklearn.load_model("runs:/" + best_model_id + "/model")
    return best_model


def optimize_model():
    # Crear experimento:
    experiment_name = "XGBoost_Potabilidad_Agua"

    # Evitar error por si existe:
    existing = mlflow.get_experiment_by_name(experiment_name)
    if existing is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = existing.experiment_id

    # Definir función para trials con Optuna (como en lab_7 pero con XGBoost y MLflow)
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 300),
            "max_depth": trial.suggest_int("max_depth", 2, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        }

        # Nombre de run interpretable, usando el learning_rate como referencia
        run_name = f"XGBoost con lr {round(params['learning_rate'], 3)}"

        # Cada trial es un run dentro del experimento:
        with mlflow.start_run(experiment_id=experiment_id, run_name=run_name):
            model = XGBClassifier(**params, eval_metric="logloss", random_state=42)
            model.fit(X_train, y_train)

            # Predecir sobre test y calcular f1
            preds = model.predict(X_test)
            valid_f1 = f1_score(y_test, preds, average="macro")  # mejor ante desbalanceo el macro.

            # Registrar manualmente parametros, metrica y modelo
            mlflow.log_params(params)
            mlflow.log_metric("valid_f1", valid_f1)
            mlflow.sklearn.log_model(model, "model")

        return valid_f1

    # Crear el estudio y optimizar (maximizar f1), al menos 10 iteraciones
    study = optuna.create_study(
        direction="maximize", study_name="XGBoost-Potabilidad", sampler=optuna.samplers.TPESampler(seed=42)
    )
    study.optimize(objective, n_trials=15)

    # Recuperar el mejor modelo registrado en MLflow
    best_model = get_best_model(experiment_id)

    # 5. Guardar en models/ el mejor modelo obtenido:
    os.makedirs("models", exist_ok=True)
    with open("models/best_model.pkl", "wb") as f:
        pickle.dump(best_model, f)

    print("Mejor f1 obtenido:", study.best_value)
    print("Mejores hiperparametros:", study.best_params)

    # Guardar versiones de librerías:
    #!uv pip freeze > requirements.txt mover.

    return best_model


if __name__ == "__main__":
    optimize_model()
