#!/usr/bin/env python3
"""
Script para verificar el usuario de prueba en la base de datos.
"""

import os
import sys
from app import create_app, db
from app.models import Usuario
from app.auth_utils import clean_rut

def check_test_user():
    """Verificar el usuario de prueba en la base de datos."""
    
    # Configurar la aplicación
    app = create_app()
    
    with app.app_context():
        try:
            # Buscar usuario con RUT limpio
            rut_limpio = clean_rut('11111111-1')
            print(f"Buscando usuario con RUT limpio: '{rut_limpio}'")
            
            usuario = Usuario.query.filter_by(rut_usuario=rut_limpio).first()
            
            if usuario:
                print("✅ Usuario encontrado en la base de datos!")
                print("="*50)
                print(f"ID: {usuario.id_usuario}")
                print(f"RUT almacenado: '{usuario.rut_usuario}'")
                print(f"Usuario: {usuario.user_usuario}")
                print(f"Hash contraseña: {usuario.passwd_usuario[:50]}...")
                print(f"Nivel: {usuario.nivel_usuario}")
                
                # Probar verificación de contraseña
                password_ok = usuario.check_password('test123')
                print(f"Verificación contraseña 'test123': {password_ok}")
                
            else:
                print("❌ Usuario NO encontrado en la base de datos!")
                print("\nBuscando todos los usuarios...")
                todos_usuarios = Usuario.query.all()
                print(f"Total usuarios en DB: {len(todos_usuarios)}")
                for u in todos_usuarios:
                    print(f"  - ID: {u.id_usuario}, RUT: '{u.rut_usuario}', Usuario: {u.user_usuario}")
                
        except Exception as e:
            print(f"❌ Error al verificar usuario: {e}")

if __name__ == "__main__":
    check_test_user()