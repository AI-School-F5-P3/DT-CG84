import pandas as pd
import optuna
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Cargamos los datos desde los archivos CSV (Loading data from CSV files)
customer_profiles = pd.read_csv('csv/customer_profiles.csv')
product_affinity = pd.read_csv('csv/product_affinity.csv')
product_interactions = pd.read_csv('csv/product_interactions.csv')

# Unimos los datos de clientes con sus afinidades a productos
# (Merging customer data with their product affinities)
merged_data = pd.merge(
    customer_profiles, 
    product_affinity, 
    on="customer_id"
)

# Convertimos las categorías de texto a números para que el modelo las entienda
# (Converting text categories to numbers so the model can understand them)
encoder = LabelEncoder()
for col in ['gender', 'location', 'preferred_category', 'product_id']:
    if col in merged_data.columns:
        merged_data[col] = encoder.fit_transform(merged_data[col])

# Seleccionamos las características que usaremos para predecir
# (Selecting features we'll use for prediction)
features = [
    "age", "gender", "income", "location", "purchase_frequency", 
    "avg_order_value", "preferred_category", "clv",
    "ingredients", "quality", "brand_loyalty", "discount_sensitivity",
    "product_id"
]

X = merged_data[features]
y = merged_data["affinity_score"]  # Usamos el score de afinidad directamente como target

# Dividimos los datos en conjunto de entrenamiento y prueba
# (Splitting data into training and test sets)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

def objetivo_optuna(trial):
    """
    Esta función prueba diferentes combinaciones de hiperparámetros para encontrar la mejor
    (This function tests different hyperparameter combinations to find the best one)
    """
    param = {
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
        'objective': 'reg:logistic'  # Para asegurar predicciones entre 0 y 1
    }
    
    # Creamos el modelo con los parámetros sugeridos
    # (Creating model with suggested parameters)
    model = XGBRegressor(**param, random_state=42)
    
    # Evaluamos el modelo usando validación cruzada con R²
    # (Evaluating model using cross-validation with R²)
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    
    return scores.mean()

# Creamos el estudio de Optuna para encontrar los mejores hiperparámetros
# (Creating Optuna study to find best hyperparameters)
study = optuna.create_study(direction="maximize")
study.optimize(objetivo_optuna, n_trials=50)

print("\nMejores hiperparámetros encontrados (Best hyperparameters found):")
print(study.best_params)

# Entrenamos el modelo final con los mejores hiperparámetros
# (Training final model with best hyperparameters)
best_params = study.best_params
best_params['objective'] = 'reg:logistic'  # Aseguramos que se mantenga la función objetivo
modelo_final = XGBRegressor(**best_params, random_state=42)
modelo_final.fit(X_train, y_train)

# Evaluamos el rendimiento del modelo
# (Evaluating model performance)
predicciones = modelo_final.predict(X_test)
mse = mean_squared_error(y_test, predicciones)
r2 = r2_score(y_test, predicciones)

print("\nMétricas de Evaluación (Evaluation Metrics):")
print(f"Error Cuadrático Medio (MSE): {mse:.4f}")
print(f"R² Score: {r2:.4f}")

# Importancia de características (Feature importance)
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': modelo_final.feature_importances_
})
print("\nImportancia de Características (Feature Importance):")
print(feature_importance.sort_values('importance', ascending=False))

def predecir_probabilidad_compra(datos_cliente):
    """
    Predice la probabilidad de que un cliente compre (valor entre 0 y 1)
    (Predicts the probability of a customer making a purchase - value between 0 and 1)
    
    Args:
        datos_cliente (DataFrame): DataFrame con las características del cliente
        
    Returns:
        float: Probabilidad de compra entre 0 y 1
    """
    if not all(feature in datos_cliente.columns for feature in features):
        raise ValueError(f"El DataFrame debe contener todas las características: {features}")
    
    return modelo_final.predict(datos_cliente[features])

# Ejemplo de uso (Usage example):
# nuevo_cliente = pd.DataFrame([{...}])  # Crear DataFrame con las características necesarias
# probabilidad = predecir_probabilidad_compra(nuevo_cliente)