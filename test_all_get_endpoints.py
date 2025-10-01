#!/usr/bin/env python3
"""
Script de Testing Completo para Endpoints GET
==============================================

Testa todos los endpoints GET disponibles en la API DPM.
Utiliza autenticación JWT con el usuario 11111111-1 / test123.

Uso:
    python test_all_get_endpoints.py

Requiere:
    - Servidor Flask corriendo en localhost:5000
    - Usuario de prueba: RUT 11111111-1, password test123
    - requests library: pip install requests
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configuración
BASE_URL = "http://100.126.196.33:5000"
TEST_USER = {
    "rut_usuario": "11111111-1",
    "password": "test1234"
}

class Colors:
    """Colores para output en consola"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class APITester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.results = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
    def log(self, message: str, color: str = Colors.WHITE):
        """Log con timestamp y color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.CYAN}[{timestamp}]{Colors.RESET} {color}{message}{Colors.RESET}")
    
    def authenticate(self) -> bool:
        """Autenticar y obtener token JWT"""
        self.log("Iniciando autenticación...", Colors.YELLOW)
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json=TEST_USER,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'token' in data['data']:
                    self.token = data['data']['token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    self.log(f"Autenticación exitosa para usuario {TEST_USER['rut_usuario']}", Colors.GREEN)
                    return True
                else:
                    self.log("❌Respuesta de login no contiene token", Colors.RED)
                    return False
            else:
                self.log(f"❌Error de autenticación: {response.status_code} - {response.text}", Colors.RED)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌Error de conexión durante autenticación: {e}", Colors.RED)
            return False
    
    def test_endpoint(self, method: str, endpoint: str, description: str, 
                     expected_status: int = 200, params: dict = None) -> bool:
        """
        Testear un endpoint específico
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: URL endpoint
            description: Descripción del test
            expected_status: Status code esperado
            params: Query parameters
        """
        self.results['total'] += 1
        
        try:
            url = f"{BASE_URL}{endpoint}"
            self.log(f"{description}")
            print(f"    {Colors.BLUE}→ {method} {endpoint}{Colors.RESET}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=10
            )
            
            # Evaluar resultado
            success = response.status_code == expected_status
            
            if success:
                self.results['successful'] += 1
                status_color = Colors.GREEN
                status_icon = "✅"
                
                # Mostrar información adicional para respuestas exitosas
                try:
                    data = response.json()
                    if 'data' in data:
                        if isinstance(data['data'], dict) and 'items' in data['data']:
                            # Respuesta paginada
                            item_count = len(data['data']['items'])
                            pagination = data['data'].get('pagination', {})
                            total = pagination.get('total', 'N/A')
                            print(f"    {Colors.CYAN}Items: {item_count}, Total: {total}{Colors.RESET}")
                        elif isinstance(data['data'], list):
                            # Lista directa
                            print(f"    {Colors.CYAN}Items: {len(data['data'])}{Colors.RESET}")
                        elif isinstance(data['data'], dict):
                            # Objeto único
                            print(f"    {Colors.CYAN}Objeto único obtenido{Colors.RESET}")
                except:
                    pass
                    
            else:
                self.results['failed'] += 1
                status_color = Colors.RED
                status_icon = "❌"
                
                error_info = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_info += f", Error: {error_data['error']}"
                except:
                    error_info += f", Text: {response.text[:100]}"
                
                self.results['errors'].append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': response.status_code,
                    'error': error_info
                })
            
            print(f"    {status_color}{status_icon} {response.status_code} - {response.reason}{Colors.RESET}")
            
            return success
            
        except requests.exceptions.Timeout:
            self.log(f"    Timeout en {endpoint}", Colors.YELLOW)
            self.results['failed'] += 1
            return False
            
        except requests.exceptions.RequestException as e:
            self.log(f"    Error de conexión: {e}", Colors.RED)
            self.results['failed'] += 1
            return False
    
    def run_tests(self):
        """Ejecutar todos los tests de endpoints GET"""
        
        self.log("Iniciando testing de endpoints GET", Colors.BOLD + Colors.CYAN)
        self.log(f"Servidor: {BASE_URL}", Colors.WHITE)
        
        # Verificar conectividad
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"Servidor saludable: {health_data.get('status', 'unknown')}", Colors.GREEN)
            else:
                self.log("Servidor responde pero health check falló", Colors.YELLOW)
        except:
            self.log("No se puede conectar al servidor", Colors.RED)
            return
        
        # Autenticar
        if not self.authenticate():
            self.log("No se puede continuar sin autenticación", Colors.RED)
            return
        
        print()
        self.log("Ejecutando tests de endpoints GET...", Colors.BOLD + Colors.YELLOW)
        print()
        
        # === ENDPOINTS PÚBLICOS ===
        self.log("ENDPOINTS PÚBLICOS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/health", "Health Check")
        
        print()
        
        # === AUTH ENDPOINTS ===
        self.log("AUTH ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/auth/profile", "Obtener perfil de usuario")
        
        print()
        
        # === USUARIOS ENDPOINTS ===
        self.log("USUARIOS ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/usuarios/", "Listar usuarios")
        self.test_endpoint("GET", "/api/usuarios/", "Listar usuarios con paginación", params={'page': 1, 'per_page': 5})
        self.test_endpoint("GET", "/api/usuarios/1", "Obtener usuario por ID")
        self.test_endpoint("GET", "/api/usuarios/stats", "Estadísticas de usuarios")
        
        print()
        
        # === PERSONAS MAYORES ENDPOINTS ===
        self.log("PERSONAS MAYORES ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/personas-mayores", "Listar personas mayores")
        self.test_endpoint("GET", "/api/personas-mayores", "Listar con filtros", params={'page': 1, 'per_page': 5})
        # Note: No testeamos RUT específico porque no sabemos si existe
        
        print()
        
        # === PERSONAS A CARGO ENDPOINTS ===
        self.log("PERSONAS A CARGO ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/personas-a-cargo", "Listar personas a cargo")
        self.test_endpoint("GET", "/api/personas-a-cargo", "Listar con paginación", params={'page': 1, 'per_page': 3})
        
        print()
        
        # === CENTROS ENDPOINTS ===
        self.log("CENTROS COMUNITARIOS ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/centros/", "Listar centros comunitarios")
        self.test_endpoint("GET", "/api/centros/", "Listar con filtros", params={'nombre': 'centro'})
        self.test_endpoint("GET", "/api/centros/1", "Obtener centro por ID")
        
        print()
        
        # === ACTIVIDADES ENDPOINTS ===
        self.log("ACTIVIDADES ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/actividades/", "Listar actividades")
        self.test_endpoint("GET", "/api/actividades/", "Listar con filtros", params={'page': 1})
        self.test_endpoint("GET", "/api/actividades/1", "Obtener actividad por ID")
        
        print()
        
        # === TALLERES ENDPOINTS ===
        self.log("TALLERES ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/actividades/talleres", "Listar talleres")
        self.test_endpoint("GET", "/api/actividades/talleres/1", "Obtener taller por ID")
        
        print()
        
        # === SERVICIOS ENDPOINTS ===
        self.log("SERVICIOS ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/servicios/", "Listar servicios")
        self.test_endpoint("GET", "/api/servicios/1", "Obtener servicio por ID")
        self.test_endpoint("GET", "/api/servicios/mantenciones", "Listar mantenciones")
        self.test_endpoint("GET", "/api/servicios/mantenciones/1", "Obtener mantención por ID")
        self.test_endpoint("GET", "/api/servicios/trabajadores-apoyo", "Listar trabajadores de apoyo")
        self.test_endpoint("GET", "/api/servicios/trabajadores-apoyo/99999999-9", "Obtener trabajador por RUT")
        
        print()
        
        # === MANTENCIONES ENDPOINTS ===
        self.log("MANTENCIONES ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/mantenciones/", "Listar mantenciones")
        self.test_endpoint("GET", "/api/mantenciones/1", "Obtener mantención por ID")
        self.test_endpoint("GET", "/api/mantenciones/centro/1", "Mantenciones por centro")
        
        print()
        
        # === TRABAJADORES ENDPOINTS ===
        self.log("TRABAJADORES DE APOYO ENDPOINTS", Colors.BOLD + Colors.WHITE)
        self.test_endpoint("GET", "/api/trabajadores-apoyo/", "Listar trabajadores")
        self.test_endpoint("GET", "/api/trabajadores-apoyo/centro/1", "Trabajadores por centro")
        
        print()
        
        # === RESUMEN FINAL ===
        self.show_summary()
    
    def show_summary(self):
        """Mostrar resumen de resultados"""
        print("=" * 60)
        self.log("RESUMEN DE TESTING", Colors.BOLD + Colors.CYAN)
        print()
        
        total = self.results['total']
        successful = self.results['successful']
        failed = self.results['failed']
        success_rate = (successful / total * 100) if total > 0 else 0
        
        self.log(f"Total de tests: {total}", Colors.WHITE)
        self.log(f"Exitosos: {successful}", Colors.GREEN)
        self.log(f"Fallidos: {failed}", Colors.RED)
        self.log(f"Tasa de éxito: {success_rate:.1f}%", 
                Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 60 else Colors.RED)
        
        # Mostrar errores si los hay
        if self.results['errors']:
            print()
            self.log("ERRORES ENCONTRADOS:", Colors.RED + Colors.BOLD)
            for error in self.results['errors']:
                print(f"  • {error['method']} {error['endpoint']}")
                print(f"    {Colors.RED}→ {error['error']}{Colors.RESET}")
        
        print()
        if success_rate >= 80:
            self.log("Testing completado exitosamente!", Colors.GREEN + Colors.BOLD)
        elif success_rate >= 60:
            self.log("Testing completado con advertencias", Colors.YELLOW + Colors.BOLD)
        else:
            self.log("Testing completado con errores significativos", Colors.RED + Colors.BOLD)
        
        print("=" * 60)

def main():
    """Función principal"""
    print(f"{Colors.BOLD}{Colors.CYAN}API DPM - Test de Endpoints GET{Colors.RESET}")
    print(f"Versión: 2.1.0 | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tester = APITester()
    
    try:
        tester.run_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW} Testing interrumpido por el usuario{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado durante testing: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()