from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime

app = Flask(__name__)
# Habilitamos CORS para permitir peticiones desde el frontend
CORS(app)

# Simulamos una base de datos con pandas (en producción usarías una DB real)
def load_synthetic_data():
    # Ejemplo de estructura de datos sintéticos
    data = {
        'id': range(1, 1001),
        'edad': pd.np.random.randint(18, 80, 1000),
        'nivel_consumo': pd.np.random.choice(['bajo', 'medio', 'alto'], 1000),
        'region': pd.np.random.choice(['Madrid', 'Cataluña', 'Andalucía', 'Valencia'], 1000),
        'gasto_mensual': pd.np.random.normal(1000, 300, 1000),
        'ultima_compra': pd.date_range(start='2024-01-01', periods=1000).tolist()
    }
    return pd.DataFrame(data)

# Cargamos los datos
df = load_synthetic_data()

@app.route('/api/consumidores', methods=['GET'])
def get_consumers():
    """Endpoint para obtener lista de consumidores con filtros opcionales"""
    try:
        # Parámetros de consulta opcionales
        region = request.args.get('region')
        nivel_consumo = request.args.get('nivel_consumo')
        
        # Aplicamos filtros si existen
        filtered_df = df.copy()
        if region:
            filtered_df = filtered_df[filtered_df['region'] == region]
        if nivel_consumo:
            filtered_df = filtered_df[filtered_df['nivel_consumo'] == nivel_consumo]
        
        # Convertimos a formato JSON
        return jsonify({
            'status': 'success',
            'data': filtered_df.to_dict('records'),
            'total': len(filtered_df)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/consumidores/<int:consumer_id>', methods=['GET'])
def get_consumer(consumer_id):
    """Endpoint para obtener detalles de un consumidor específico"""
    try:
        consumer = df[df['id'] == consumer_id]
        if len(consumer) == 0:
            return jsonify({'status': 'error', 'message': 'Consumidor no encontrado'}), 404
        
        return jsonify({
            'status': 'success',
            'data': consumer.iloc[0].to_dict()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analytics/consumo-por-region', methods=['GET'])
def consumption_by_region():
    """Endpoint para análisis de consumo por región"""
    try:
        analysis = df.groupby('region').agg({
            'gasto_mensual': ['mean', 'min', 'max', 'count']
        }).round(2)
        
        return jsonify({
            'status': 'success',
            'data': analysis.to_dict()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)