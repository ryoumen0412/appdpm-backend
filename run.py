"""
Application Entry Point

"""

from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("Tablas de base de datos creadas/verificadas exitosamente")

if __name__ == '__main__':
    print("Iniciando servidor Flask para Sistema DPM...")
    print("Servidor disponible en: http://localhost:5000")
    print("API disponible en: http://localhost:5000/api/health")
    print("Modo debug: ACTIVADO")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


