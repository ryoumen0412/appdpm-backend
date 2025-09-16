#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en la base de datos.
"""

import os
import sys
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

def create_test_user():
    """Crear un usuario de prueba para validar la API."""
    
    # Configurar la aplicación
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si ya existe un usuario de prueba
            existing_user = Usuario.query.filter_by(rut_usuario='11111111-1').first()
            
            if existing_user:
                print("❗ Usuario de prueba ya existe!")
                print(f"   RUT: {existing_user.rut_usuario}")
                print(f"   Usuario: {existing_user.user_usuario}")
                print(f"   Nivel: {existing_user.nivel_usuario}")
                return
            
            # Crear nuevo usuario de prueba
            test_user = Usuario(
                rut_usuario='11111111-1',
                user_usuario='admin_test',
                passwd_usuario=generate_password_hash('test123'),
                nivel_usuario=3  # Nivel administrativo
            )
            
            # Guardar en base de datos
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Usuario de prueba creado exitosamente!")
            print("="*50)
            print("CREDENCIALES DE PRUEBA:")
            print("="*50)
            print(f"RUT: 11111111-1")
            print(f"Contraseña: test123")
            print(f"Nivel: 3 (Administrador)")
            print("="*50)
            print("\n🔧 Usa estas credenciales para probar la API")
            
        except Exception as e:
            print(f"❌ Error al crear usuario de prueba: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_user()