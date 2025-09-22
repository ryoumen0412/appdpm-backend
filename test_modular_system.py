#!/usr/bin/env python3
"""
Script de verificación completa del sistema modular
Prueba el flujo de autenticación y todos los endpoints principales
"""

import requests
import json
import sys
from datetime import datetime

# Configuración base
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_server_health():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return True, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_auth_system():
    """Probar el sistema de autenticación completo"""
    print_separator("MÓDULO AUTH - SISTEMA DE AUTENTICACIÓN")
    
    # Test 1: Login con credenciales válidas
    login_data = {
        "rut_usuario": "111111111",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'token' in data['data']:
                token = data['data']['token']
                print_test_result("Login exitoso", True, f"Token obtenido: {token[:20]}...")
                return token
            else:
                print_test_result("Login - Token no encontrado", False, data)
                return None
        else:
            print_test_result("Login falló", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_test_result("Login - Error de conexión", False, str(e))
        return None

def test_authenticated_endpoints(token):
    """Probar endpoints que requieren autenticación"""
    if not token:
        print("❌ No hay token disponible para pruebas autenticadas")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints de cada módulo
    endpoints_to_test = [
        ("AUTH - Profile", "GET", "/auth/profile"),
        ("USUARIOS - Lista", "GET", "/usuarios"),
        ("CENTROS - Lista", "GET", "/centros"),
        ("ACTIVIDADES - Lista", "GET", "/actividades"),
        ("TALLERES - Lista", "GET", "/actividades/talleres"),
        ("SERVICIOS - Lista", "GET", "/servicios"),
        ("MANTENCIONES - Lista", "GET", "/mantenciones"),
        ("TRABAJADORES APOYO - Lista", "GET", "/trabajadores-apoyo"),
        ("PERSONAS A CARGO - Lista", "GET", "/personas-a-cargo"),
        ("PERSONAS MAYORES - Lista", "GET", "/personas-mayores"),
    ]
    
    print_separator("ENDPOINTS AUTENTICADOS")
    
    successful_requests = 0
    total_requests = len(endpoints_to_test)
    
    for name, method, endpoint in endpoints_to_test:
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if isinstance(data, dict) and ('data' in data or 'message' in data):
                        print_test_result(name, True, f"Status: {response.status_code}")
                        successful_requests += 1
                    else:
                        print_test_result(name, True, f"Status: {response.status_code}, Data type: {type(data)}")
                        successful_requests += 1
                except:
                    print_test_result(name, True, f"Status: {response.status_code} (Non-JSON response)")
                    successful_requests += 1
            elif response.status_code == 401:
                print_test_result(name, False, "Token inválido o expirado")
            elif response.status_code == 403:
                print_test_result(name, False, "Sin permisos suficientes")
            elif response.status_code == 404:
                print_test_result(name, False, "Endpoint no encontrado")
            else:
                print_test_result(name, False, f"Status: {response.status_code}")
                
        except Exception as e:
            print_test_result(name, False, f"Error: {str(e)}")
    
    return successful_requests, total_requests

def test_unauthenticated_access():
    """Verificar que los endpoints protegidos rechacen acceso sin autenticación"""
    print_separator("VERIFICACIÓN DE PROTECCIÓN DE ENDPOINTS")
    
    protected_endpoints = [
        "/usuarios",
        "/centros", 
        "/actividades",
        "/servicios"
    ]
    
    protected_correctly = 0
    
    for endpoint in protected_endpoints:
        try:
            url = f"{API_BASE}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 401:
                print_test_result(f"Protección {endpoint}", True, "Acceso denegado correctamente")
                protected_correctly += 1
            else:
                print_test_result(f"Protección {endpoint}", False, f"Status: {response.status_code} (esperado 401)")
                
        except Exception as e:
            print_test_result(f"Protección {endpoint}", False, f"Error: {str(e)}")
    
    return protected_correctly, len(protected_endpoints)

def test_blueprint_registration():
    """Verificar que todos los blueprints estén registrados"""
    print_separator("VERIFICACIÓN DE BLUEPRINTS")
    
    # Intentar acceder a endpoints base de cada módulo
    blueprint_endpoints = [
        ("Auth Blueprint", "/auth/login"),
        ("Usuarios Blueprint", "/usuarios"),
        ("Centros Blueprint", "/centros"),
        ("Actividades Blueprint", "/actividades"),
        ("Servicios Blueprint", "/servicios"),
        ("Personas Blueprint", "/personas-a-cargo"),
    ]
    
    registered_blueprints = 0
    
    for name, endpoint in blueprint_endpoints:
        try:
            url = f"{API_BASE}{endpoint}"
            response = requests.get(url, timeout=10)
            
            # Un blueprint registrado debería responder (aunque sea con 401/405)
            if response.status_code != 404:
                print_test_result(name, True, f"Blueprint registrado (Status: {response.status_code})")
                registered_blueprints += 1
            else:
                print_test_result(name, False, "Blueprint no encontrado (404)")
                
        except Exception as e:
            print_test_result(name, False, f"Error: {str(e)}")
    
    return registered_blueprints, len(blueprint_endpoints)

def main():
    print_separator("VERIFICACIÓN COMPLETA DEL SISTEMA MODULAR")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    
    # Test 1: Verificar que el servidor esté funcionando
    print_separator("CONECTIVIDAD DEL SERVIDOR")
    server_ok, server_details = test_server_health()
    print_test_result("Servidor funcionando", server_ok, server_details)
    
    if not server_ok:
        print("\n❌ El servidor no está funcionando. Inicialo con: python run.py")
        sys.exit(1)
    
    # Test 2: Verificar registro de blueprints
    registered, total_blueprints = test_blueprint_registration()
    
    # Test 3: Verificar protección de endpoints
    protected, total_protected = test_unauthenticated_access()
    
    # Test 4: Probar sistema de autenticación
    token = test_auth_system()
    
    # Test 5: Probar endpoints autenticados
    if token:
        successful, total_authenticated = test_authenticated_endpoints(token)
    else:
        successful = 0
        total_authenticated = 10
        print("\n❌ No se pudo obtener token, saltando pruebas autenticadas")
    
    # Resumen final
    print_separator("RESUMEN DE RESULTADOS")
    print(f"🖥️  Servidor funcionando: {'✅' if server_ok else '❌'}")
    print(f"🔧 Blueprints registrados: {registered}/{total_blueprints}")
    print(f"🔒 Endpoints protegidos: {protected}/{total_protected}")
    print(f"🔑 Sistema de autenticación: {'✅' if token else '❌'}")
    print(f"📡 Endpoints autenticados: {successful}/{total_authenticated}")
    
    total_tests = 1 + total_blueprints + total_protected + 1 + total_authenticated
    passed_tests = (1 if server_ok else 0) + registered + protected + (1 if token else 0) + successful
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 RESULTADO GENERAL: {passed_tests}/{total_tests} pruebas exitosas ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 ¡Sistema modular funcionando correctamente!")
        return True
    elif success_rate >= 60:
        print("⚠️  Sistema funcionando con algunos problemas menores")
        return True
    else:
        print("❌ Sistema tiene problemas importantes que necesitan atención")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)