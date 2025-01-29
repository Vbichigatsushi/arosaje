import os
import glob

# Parcourir tous les répertoires du projet
for root, dirs, files in os.walk('.'):
    if 'migrations' in dirs:
        migration_path = os.path.join(root, 'migrations')

        # Trouver tous les fichiers sauf '__init__.py'
        migration_files = glob.glob(os.path.join(migration_path, '*.py'))
        for file in migration_files:
            if not file.endswith('__init__.py'):
                os.remove(file)
                print(f"Supprimé : {file}")

        # Supprimer les fichiers compilés `.pyc`
        pyc_files = glob.glob(os.path.join(migration_path, '*.pyc'))
        for file in pyc_files:
            os.remove(file)
            print(f"Supprimé : {file}")
