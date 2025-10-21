#!/usr/bin/env python3
"""
Script Validation Test
======================

This script validates the syntax and structure of the GIS processing scripts
without requiring GDAL/rasterio to be installed.

Usage:
    python test_scripts.py

Author: Glendale Fire Risk Team
"""

import ast
import sys
from pathlib import Path

# Script paths
SCRIPT_DIR = Path(__file__).parent
SCRIPTS = [
    SCRIPT_DIR / "clip_and_reproject.py",
    SCRIPT_DIR / "derive_terrain.py",
    SCRIPT_DIR / "build_risk_model.py"
]


def validate_python_syntax(script_path):
    """
    Validate that a Python script has correct syntax.
    
    Args:
        script_path: Path to the Python script
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(script_path, 'r') as f:
            code = f.read()
        
        # Parse the code to check for syntax errors
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"


def check_script_structure(script_path):
    """
    Check that script has expected structure (main function, etc.)
    
    Args:
        script_path: Path to the Python script
        
    Returns:
        dict: Structure information
    """
    with open(script_path, 'r') as f:
        code = f.read()
    
    tree = ast.parse(code)
    
    info = {
        'has_main': False,
        'has_docstring': ast.get_docstring(tree) is not None,
        'imports': [],
        'functions': []
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            info['functions'].append(node.name)
            if node.name == 'main':
                info['has_main'] = True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                info['imports'].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            info['imports'].append(f"{node.module}")
    
    return info


def main():
    """Run validation tests."""
    print("="*60)
    print("  GIS SCRIPT VALIDATION TEST")
    print("="*60)
    
    all_valid = True
    
    for script_path in SCRIPTS:
        print(f"\n📄 Testing {script_path.name}...")
        
        if not script_path.exists():
            print(f"  ✗ Script not found!")
            all_valid = False
            continue
        
        # Test syntax
        is_valid, error = validate_python_syntax(script_path)
        if is_valid:
            print("  ✓ Syntax is valid")
        else:
            print(f"  ✗ Syntax error: {error}")
            all_valid = False
            continue
        
        # Check structure
        structure = check_script_structure(script_path)
        
        if structure['has_docstring']:
            print("  ✓ Has module docstring")
        else:
            print("  ⚠ Missing module docstring")
        
        if structure['has_main']:
            print("  ✓ Has main() function")
        else:
            print("  ⚠ No main() function")
        
        print(f"  ℹ Functions: {', '.join(structure['functions'][:5])}")
        
        # Check for expected imports
        expected_imports = {
            'clip_and_reproject.py': ['geopandas', 'rasterio'],
            'derive_terrain.py': ['numpy', 'rasterio', 'scipy'],
            'build_risk_model.py': ['numpy', 'rasterio', 'geopandas']
        }
        
        script_name = script_path.name
        if script_name in expected_imports:
            has_all = all(
                any(imp in structure['imports'] for imp in [expected])
                for expected in expected_imports[script_name]
            )
            if has_all:
                print(f"  ✓ Has expected imports")
            else:
                print(f"  ⚠ May be missing some expected imports")
    
    print("\n" + "="*60)
    if all_valid:
        print("  ✓ ALL SCRIPTS VALIDATED SUCCESSFULLY")
    else:
        print("  ✗ SOME SCRIPTS HAVE ISSUES")
    print("="*60)
    
    # Print next steps
    print("\nNext Steps:")
    print("1. Install dependencies: pip install -r ../requirements.txt")
    print("2. Download DEM data (see data_download_notes.md)")
    print("3. Run scripts in order:")
    print("   - python clip_and_reproject.py")
    print("   - python derive_terrain.py")
    print("   - python build_risk_model.py")
    
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
