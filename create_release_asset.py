import os
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP_NAME = os.path.join(ROOT, 'pixlet-installer.zip')

files_to_include = [
    'installer.py',
    'requirements.txt',
    'README.md'
]

def main():
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)
    with zipfile.ZipFile(ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for fname in files_to_include:
            path = os.path.join(ROOT, fname)
            if os.path.exists(path):
                z.write(path, arcname=os.path.basename(path))
    print('Created', ZIP_NAME)

if __name__ == '__main__':
    main()
