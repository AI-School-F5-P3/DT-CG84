import pandas as pd
import numpy as np
from faker import Faker
import os

def create_customer_profiles(n_customers):
    fake = Faker()
    
    # Comunidades autonomas de España
    locations = [
        "Madrid", "Cataluña", "Andalucia", "Comunidad Valenciana", "Galicia",
        "Castilla y León", "Euskadi", "Castilla-La Mancha",
        "Islas Canarias", "Murcia", "Aragón", "Extremadura",
        "Islas Baleares", "Asturias", "Navarra", "Cantabria",
        "La Rioja", "Ceuta", "Melilla"
    ]

    # Probabilidades de que un cliente sea de una comunidad autonoma en función de datos de INE
    probabilities = [
        0.140, 0.160, 0.180, 0.110, 0.057,
        0.050, 0.047, 0.043,
        0.045, 0.032, 0.028, 0.022,
        0.025, 0.021, 0.014, 0.012,
        0.007, 0.0035, 0.0035
    ]

    customer_profiles = pd.DataFrame({
        "customer_id": np.arange(1, n_customers+1), 
        "age": np.clip(np.random.normal(40, 10, n_customers).astype(int), 18, 80), # Edad entre 18 y 80 años
        "gender": np.random.choice(["Male", "Female", "Other"], n_customers, p=[0.48, 0.48, 0.04]), # Genero
        "income": np.random.lognormal(mean=10.5, sigma=0.4, size=n_customers).astype(int), # Ingresos anuales, sesgo a salarios medios-bajos
        "location": np.random.choice(locations, n_customers, p=probabilities), # Comunidad autonoma
        "purchase_frequency": np.random.gamma(shape=2, scale=0.5, size=n_customers), # Frecuencia de compra
        "avg_order_value": np.random.lognormal(mean=4, sigma=0.5, size=n_customers), # Valor medio de compra
        "preferred_category": np.random.choice(
            ["Food", "Beverages", "Personal Hygiene", "Snacks", "Household Cleaning"], # Categorias de productos preferidas asumiendo fast-consuming products
            n_customers
        ),
        "brand_loyalty": np.random.beta(a=2, b=2, size=n_customers), # Lealtad a la marca
        "discount_sensitivity": np.random.beta(a=1.5, b=3, size=n_customers), # Sensibilidad al descuento, interés en promociones
    })

    customer_profiles["clv"] = (
        customer_profiles["income"] * 0.001 +
        customer_profiles["purchase_frequency"] * customer_profiles["avg_order_value"]
    ) #  Customer Lifetime Value (CLV) net profit from a customer expected to generate over the entire future relationship with the business
    
    return customer_profiles

def create_product_interactions(n_interactions, customer_profiles):
    products = ["P-FOOD-001", "P-BEVERAGE-002", "P-HYGIENE-003", "P-SNACKS-004", "P-CLEANING-005"]
    categories = ["Food", "Beverages", "Personal Hygiene", "Snacks", "Household Cleaning"]

    product_interactions = pd.DataFrame({
        "interaction_id": np.arange(1, n_interactions+1),
        "customer_id": np.random.choice(customer_profiles["customer_id"], n_interactions),
        "product_id": np.random.choice(products, n_interactions),
        "event_type": np.random.choice(
            ["click", "view", "cart_add", "purchase"], 
            n_interactions, 
            p=[0.5, 0.3, 0.15, 0.05]
        ), # Eventos de interacción con el producto
        "timestamp": pd.date_range(start="2023-01-01", periods=n_interactions, freq="min"),
        "time_spent": np.random.exponential(scale=30, size=n_interactions),
    })
    
    return product_interactions

def calculate_product_affinity(product_interactions): # Afinidad del cliente por un producto, preferencias
    return (
        product_interactions
        .groupby(["customer_id", "product_id"])
        .agg(
            affinity_score=("event_type", lambda x: (x == "purchase").mean() * 0.7 + (x == "cart_add").mean() * 0.3),
            last_interaction=("timestamp", "max")
        )
        .reset_index()
    )

def export_to_csv(customer_profiles, product_interactions, product_affinity):
    # Exportacion a csv para uso local
    if not os.path.exists('csv'):
        os.makedirs('csv')
    
    customer_profiles.to_csv('csv/customer_profiles.csv', index=False)
    product_interactions.to_csv('csv/product_interactions.csv', index=False)
    product_affinity.to_csv('csv/product_affinity.csv', index=False)

def main():
    n_customers = 100000
    n_interactions = 5000000
    
    customer_profiles = create_customer_profiles(n_customers)
    product_interactions = create_product_interactions(n_interactions, customer_profiles)
    product_affinity = calculate_product_affinity(product_interactions)
    
    export_to_csv(customer_profiles, product_interactions, product_affinity)

if __name__ == "__main__":
    main()