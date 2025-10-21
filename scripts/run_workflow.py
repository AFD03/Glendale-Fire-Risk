#!/usr/bin/env python3
"""
Master Workflow Script
======================

This script runs all GIS processing steps in the correct order.

Usage:
    python run_workflow.py [--skip-clip] [--skip-terrain] [--skip-risk]

Options:
    --skip-clip     Skip clipping and reprojection step
    --skip-terrain  Skip terrain analysis (slope/aspect) step
    --skip-risk     Skip risk model building step

Author: Glendale Fire Risk Team
"""

import sys
import subprocess
from pathlib import Path
import argparse


def run_script(script_name, description):
    """
    Run a Python script and report results.
    
    Args:
        script_name: Name of the script file
        description: Description of what the script does
        
    Returns:
        bool: True if successful, False otherwise
    """
    script_path = Path(__file__).parent / script_name
    
    print("\n" + "="*60)
    print(f"  {description.upper()}")
    print("="*60)
    print(f"Running: {script_name}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False
        )
        print(f"\n✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ Error running {script_name}: {e}")
        return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Run the complete GIS processing workflow'
    )
    parser.add_argument(
        '--skip-clip',
        action='store_true',
        help='Skip clipping and reprojection step'
    )
    parser.add_argument(
        '--skip-terrain',
        action='store_true',
        help='Skip terrain analysis (slope/aspect) step'
    )
    parser.add_argument(
        '--skip-risk',
        action='store_true',
        help='Skip risk model building step'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  GLENDALE FIRE RISK - COMPLETE WORKFLOW")
    print("="*60)
    print("\nThis script will run all GIS processing steps:")
    print("  1. Clip and reproject data to Glendale boundary")
    print("  2. Derive slope and aspect from DEM")
    print("  3. Build fire risk model with weighted overlay")
    
    if args.skip_clip or args.skip_terrain or args.skip_risk:
        print("\nSkipping steps:")
        if args.skip_clip:
            print("  - Clipping and reprojection")
        if args.skip_terrain:
            print("  - Terrain analysis")
        if args.skip_risk:
            print("  - Risk model building")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    success_count = 0
    total_steps = 3
    
    # Step 1: Clip and reproject
    if not args.skip_clip:
        if run_script("clip_and_reproject.py", "Step 1: Clip and Reproject Data"):
            success_count += 1
        else:
            print("\n⚠️  Step 1 failed. Cannot continue to next steps.")
            return 1
    else:
        print("\n⏭️  Skipping Step 1: Clip and Reproject Data")
    
    # Step 2: Derive terrain
    if not args.skip_terrain:
        if run_script("derive_terrain.py", "Step 2: Derive Terrain Products"):
            success_count += 1
        else:
            print("\n⚠️  Step 2 failed. Cannot continue to next steps.")
            return 1
    else:
        print("\n⏭️  Skipping Step 2: Derive Terrain Products")
    
    # Step 3: Build risk model
    if not args.skip_risk:
        if run_script("build_risk_model.py", "Step 3: Build Fire Risk Model"):
            success_count += 1
        else:
            print("\n⚠️  Step 3 failed.")
            return 1
    else:
        print("\n⏭️  Skipping Step 3: Build Fire Risk Model")
    
    # Final summary
    print("\n" + "="*60)
    print("  WORKFLOW COMPLETE")
    print("="*60)
    print(f"\nCompleted {success_count}/{total_steps} steps successfully!")
    
    if success_count == total_steps:
        print("\n✓ All processing complete!")
        print("\nNext steps:")
        print("  1. Open qgis_project/glendale_fire_risk.qgz in QGIS")
        print("  2. Load the risk layers from data_processed/raster/")
        print("  3. Style and visualize the fire risk map")
        print("  4. Begin building the Dash web application")
    else:
        print("\n⚠️  Some steps were skipped or failed.")
        print("Review the output above for details.")
    
    return 0 if success_count == total_steps else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow cancelled by user.")
        sys.exit(1)
