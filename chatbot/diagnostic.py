#!/usr/bin/env python
"""
Script de diagnóstico para verificar el estado de google.generativeai
"""

def check_gemini_installation():
    """Verifica la instalación y disponibilidad de google.generativeai"""
    
    print("=== DIAGNÓSTICO DE GOOGLE GENERATIVE AI ===")
    
    # 1. Verificar si el módulo se puede importar
    try:
        import google.generativeai as genai
        print("✅ google.generativeai se importó correctamente")
    except ImportError as e:
        print(f"❌ Error importando google.generativeai: {e}")
        return False
    
    # 2. Verificar versión
    try:
        version = getattr(genai, '__version__', 'No disponible')
        print(f"📦 Versión: {version}")
    except Exception as e:
        print(f"⚠️ No se pudo obtener la versión: {e}")
    
    # 3. Verificar atributos disponibles
    print("\n🔍 Atributos disponibles:")
    available_attrs = []
    required_attrs = ['configure', 'GenerativeModel']
    
    for attr in dir(genai):
        if not attr.startswith('_'):
            available_attrs.append(attr)
            status = "✅" if attr in required_attrs else "  "
            print(f"{status} {attr}")
    
    # 4. Verificar atributos requeridos
    print("\n📋 Verificación de atributos requeridos:")
    missing_attrs = []
    for attr in required_attrs:
        if hasattr(genai, attr):
            print(f"✅ {attr} - Disponible")
        else:
            print(f"❌ {attr} - NO DISPONIBLE")
            missing_attrs.append(attr)
    
    # 5. Intentar configuración básica
    print("\n🔧 Prueba de configuración:")
    try:
        if hasattr(genai, 'configure'):
            # Usar una API key de prueba (no válida, solo para verificar la función)
            genai.configure(api_key="test_key")
            print("✅ genai.configure() funciona")
        else:
            print("❌ genai.configure() no está disponible")
    except Exception as e:
        print(f"⚠️ Error en genai.configure(): {e}")
    
    # 6. Intentar crear modelo
    print("\n🤖 Prueba de creación de modelo:")
    try:
        if hasattr(genai, 'GenerativeModel'):
            # Intentar crear un modelo (fallará por la API key inválida, pero verificará que la clase existe)
            model = genai.GenerativeModel("gemini-1.5-flash")
            print("✅ GenerativeModel se puede instanciar")
        else:
            print("❌ GenerativeModel no está disponible")
    except Exception as e:
        if "API key" in str(e):
            print("✅ GenerativeModel está disponible (error esperado por API key inválida)")
        else:
            print(f"❌ Error creando GenerativeModel: {e}")
    
    # Resumen
    print("\n" + "="*50)
    if missing_attrs:
        print(f"❌ PROBLEMAS DETECTADOS: Faltan {len(missing_attrs)} atributos requeridos")
        print(f"   Atributos faltantes: {', '.join(missing_attrs)}")
        return False
    else:
        print("✅ TODO OK: Todos los atributos requeridos están disponibles")
        return True

if __name__ == "__main__":
    check_gemini_installation() 