import bcrypt
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def hash_password(password):
    """
    Genera un hash bcrypt seguro para la contraseña proporcionada.
    Usa un salt aleatorio para mayor seguridad.
    """
    if not password or len(password) < 4:
        print("Error: La contraseña debe tener al menos 4 caracteres")
        return None

    try:
        # Genera un salt y hashea la contraseña
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Error al hashear la contraseña: {e}")
        return None

def generate_secure_password():
    """
    Genera una contraseña segura aleatoria (opcional)
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password

def main():
    print("=== Generador de Hash de Contraseñas ===")
    print("Este script genera hashes seguros para contraseñas usando bcrypt")
    print()

    if len(sys.argv) > 1:
        password = sys.argv[1]
        print(f"Procesando contraseña proporcionada...")
    else:
        print("Opciones:")
        print("1. Ingresar contraseña manualmente")
        print("2. Generar contraseña segura aleatoria")
        choice = input("Selecciona una opción (1 o 2): ").strip()

        if choice == "2":
            password = generate_secure_password()
            print(f"Contraseña generada: {password}")
        else:
            password = input("Ingresa la contraseña a hashear: ")

    if not password:
        print("Error: No se proporcionó contraseña")
        return

    hashed_password = hash_password(password)

    if hashed_password:
        print("\n" + "="*50)
        print("HASH GENERADO EXITOSAMENTE:")
        print("="*50)
        print(f"Contraseña original: {password}")
        print(f"Hash bcrypt: {hashed_password}")
        print("="*50)
        print("\n📝 Usa este hash para insertar en tu tabla 'usuarios'")
        print("Ejemplo SQL:")
        print(f"INSERT INTO usuarios (rut_usr, passwd_usr, ...) VALUES ('12345678-9', '{hashed_password}', ...);")
        print("\n⚠️  IMPORTANTE: Guarda la contraseña original en un lugar seguro")
        print("   El hash no se puede revertir!")

if __name__ == "__main__":
    main()