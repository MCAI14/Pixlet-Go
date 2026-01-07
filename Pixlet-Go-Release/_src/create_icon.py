#!/usr/bin/env python3
"""
Convert Pixlet.svg to .ico and associate with .bat files
"""
import os
import subprocess
import sys
import winreg

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_FILE = os.path.join(REPO_DIR, 'Pixlet.svg')
ICO_FILE = os.path.join(REPO_DIR, 'Pixlet.ico')
PNG_FILE = os.path.join(REPO_DIR, 'Pixlet.png')


def svg_to_ico():
    """Convert SVG to ICO using ImageMagick or similar tools."""
    
    # Method 1: Try using Pillow (PIL) if installed
    try:
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            raise ImportError('PIL/Pillow not installed')
        print("Usando Pillow (PIL) para converter SVG para PNG para ICO...")
        
        # Need to use cairosvg or other tool to convert SVG to PNG first
        try:
            try:
                import cairosvg  # type: ignore
            except ImportError:
                raise ImportError('cairosvg not installed')
            print("Convertendo SVG para PNG usando cairosvg...")
            cairosvg.svg2png(url=SVG_FILE, write_to=PNG_FILE, output_width=256, output_height=256)
            
            # Now convert PNG to ICO using Pillow
            img = Image.open(PNG_FILE)
            img.save(ICO_FILE, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"Ícone criado: {ICO_FILE}")
            return True
        except ImportError:
            print("cairosvg nao instalado, tentando ImageMagick...")
            
    except ImportError as e:
        print(f"Pillow nao instalado: {e}")
    
    # Method 2: Try using ImageMagick (convert command)
    try:
        print("Tentando converter com ImageMagick...")
        # SVG -> PNG
        subprocess.run(['convert', SVG_FILE, '-background', 'none', '-density', '128', PNG_FILE], check=True)
        # PNG -> ICO
        subprocess.run(['convert', PNG_FILE, '-define', 'icon:auto-resize=256,128,64,48,32,16', ICO_FILE], check=True)
        print(f"Ícone criado com ImageMagick: {ICO_FILE}")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ImageMagick não disponível")
    
    # Method 3: Try using Inkscape
    try:
        print("Tentando converter com Inkscape...")
        subprocess.run(['inkscape', '--export-type=png', '--export-width=256', '--export-height=256', 
                       f'--export-filename={PNG_FILE}', SVG_FILE], check=True)
        
        # Now need to convert PNG to ICO
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            raise ImportError('Pillow not available for ICO conversion')
        img = Image.open(PNG_FILE)
        img.save(ICO_FILE, format='ICO')
        print(f"Ícone criado com Inkscape: {ICO_FILE}")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Inkscape não disponível")
    
    print("Nenhuma ferramenta de conversão disponível")
    return False


def associate_icon_windows():
    """Associate .bat files with the icon via Windows Registry."""
    try:
        print(f"\nAssociando ícone aos ficheiros .bat...")
        
        # Open registry
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        
        # Path to file type associations
        reg_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.bat\UserChoice'
        
        # Note: Modern Windows has restrictions on modifying these directly
        # We'll try a simpler approach using HKEY_CLASSES_ROOT
        
        try:
            reg_root = winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT)
            
            # Try to set default icon for .bat files
            try:
                key = winreg.OpenKey(reg_root, '.bat\\DefaultIcon', 0, winreg.KEY_WRITE)
            except:
                key = winreg.CreateKey(reg_root, '.bat\\DefaultIcon')
            
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, ICO_FILE)
            winreg.CloseKey(key)
            print(f"Ícone associado em HKEY_CLASSES_ROOT: {ICO_FILE}")
            
        except PermissionError:
            print("Permissão negada para modificar o Registry")
            print("Será necessário executar como Administrador para completar a associação")
            return False
        
        return True
    except Exception as e:
        print(f"Erro ao associar ícone: {e}")
        return False


def main():
    print(f"SVG: {SVG_FILE}")
    print(f"Verificando se existe: {os.path.exists(SVG_FILE)}")
    
    if not os.path.exists(SVG_FILE):
        print("Ficheiro SVG não encontrado!")
        return False
    
    # Step 1: Convert SVG to ICO
    if os.path.exists(ICO_FILE):
        print(f"\nIcone já existe: {ICO_FILE}")
        use_existing = input("Usar o ícone existente? (s/n): ").strip().lower()
        if use_existing != 's':
            svg_to_ico()
    else:
        if not svg_to_ico():
            print("\nNão foi possível converter o SVG para ICO")
            print("Por favor, instale uma das ferramentas:")
            print("  - pip install pillow cairosvg")
            print("  - ImageMagick (convert command)")
            print("  - Inkscape")
            return False
    
    # Step 2: Associate icon with .bat files
    # associate_icon_windows()
    
    print("\nConcluído!")
    print(f"Ícone disponível em: {ICO_FILE}")
    print("\nNota: Para associar o ícone a todos os .bat no Windows,")
    print("é recomendado executar este script como Administrador.")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
