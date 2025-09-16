#!/usr/bin/env python3
"""
Script para corregir el RUT del usuario de prueba.
"""

import os
import sys
from app import create_app, db
from app.models import Usuario
from app.auth_utils import clean_rut

def fix_test_user_rut():
    """Corregir el RUT del usuario de prueba para que coincida con clean_rut."""
    
    # Configurar la aplicación
    app = create_app()
    
    with app.app_context():
        try:
            # Buscar usuario con RUT con guión
            usuario = Usuario.query.filter_by(rut_usuario='11111111-1').first()
            
            if usuario:
                print(f"Usuario encontrado con RUT: '{usuario.rut_usuario}'")
                
                # Actualizar RUT al formato limpio
                rut_limpio = clean_rut('11111111-1')
                usuario.rut_usuario = rut_limpio
                db.session.commit()
                
                print(f"✅ RUT actualizado de '11111111-1' a '{rut_limpio}'")
                
                # Verificar la actualización
                usuario_verificado = Usuario.query.filter_by(rut_usuario=rut_limpio).first()
                if usuario_verificado:
                    print("✅ Verificación exitosa - usuario encontrado con RUT limpio")
                    print(f"RUT final en DB: '{usuario_verificado.rut_usuario}'")
                else:
                    print("❌ Error en la verificación")
                    
            else:
                print("❌ Usuario con RUT '11111111-1' no encontrado")
                
        except Exception as e:
            print(f"❌ Error al corregir RUT: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_test_user_rut()