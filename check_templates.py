import os
import re

def check_template_blocks(file_path):
    """Verifica que todos los bloques Jinja2 estén correctamente cerrados"""
    
    print(f"\n🔍 Verificando: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar bloques que necesitan cerrarse
        block_pattern = r'{%\s*block\s+(\w+)\s*%}'
        endblock_pattern = r'{%\s*endblock\s*%}'
        
        blocks = re.findall(block_pattern, content)
        endblocks = re.findall(endblock_pattern, content)
        
        print(f"📋 Bloques encontrados: {blocks}")
        print(f"📋 Endblocks encontrados: {len(endblocks)}")
        
        if len(blocks) != len(endblocks):
            print(f"❌ ERROR: {len(blocks)} bloques pero {len(endblocks)} endblocks")
            return False
        
        # Verificar extends
        extends_pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
        extends = re.findall(extends_pattern, content)
        
        if extends:
            print(f"📋 Extiende de: {extends[0]}")
        
        print("✅ Plantilla válida")
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False

def main():
    """Verifica todas las plantillas"""
    
    print("🔧 Verificador de Plantillas Jinja2")
    print("=" * 50)
    
    templates_dir = "templates"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Directorio {templates_dir} no encontrado")
        return
    
    template_files = [
        "base.html",
        "login.html", 
        "superadmin.html",
        "dashboard.html", # Añadido para verificación
        "empleado.html",  # Añadido para verificación
        "credit-detail-modal.html" # Añadido para verificación
    ]
    
    all_valid = True
    
    for template_file in template_files:
        file_path = os.path.join(templates_dir, template_file)
        is_valid = check_template_blocks(file_path)
        if not is_valid:
            all_valid = False
    
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ Todas las plantillas son válidas")
    else:
        print("❌ Hay errores en las plantillas")
    
    print("\n🚀 Para probar:")
    print("python app.py") # Ahora se recomienda usar app.py para probar todas las plantillas

if __name__ == '__main__':
    main()
