#!/usr/bin/env python3
"""Test PLY file loading"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from blender_colmap_3dgs.gaussian_splatting import load_ply_gaussian_splats
from pathlib import Path

def test_ply_loading():
    """Test loading PLY file with actual data"""
    
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    print(f"Testing PLY loader with path: {ply_path}")
    
    if not Path(ply_path).exists():
        print(f"❌ PLY file not found: {ply_path}")
        return False
        
    try:
        # Load PLY file
        positions, colors, properties = load_ply_gaussian_splats(ply_path)
        
        print("\n=== PLY Loading Results ===")
        print(f"Loaded {len(positions)} Gaussian splats")
        print(f"Positions shape: {positions.shape}")
        print(f"Colors shape: {colors.shape}")
        
        if positions.shape[0] > 0:
            print(f"\n=== Position Statistics ===")
            print(f"X range: {positions[:, 0].min():.3f} to {positions[:, 0].max():.3f}")
            print(f"Y range: {positions[:, 1].min():.3f} to {positions[:, 1].max():.3f}")
            print(f"Z range: {positions[:, 2].min():.3f} to {positions[:, 2].max():.3f}")
            
        if colors.shape[0] > 0:
            print(f"\n=== Color Statistics ===")
            print(f"Color range: {colors.min():.3f} to {colors.max():.3f}")
            print(f"Sample colors (first 5):")
            for i in range(min(5, len(colors))):
                print(f"  {i+1}: RGB({colors[i, 0]:.3f}, {colors[i, 1]:.3f}, {colors[i, 2]:.3f})")
        
        print(f"\n=== Additional Properties ===")
        for prop_name, prop_values in properties.items():
            if isinstance(prop_values, list) and len(prop_values) > 0:
                print(f"{prop_name}: {len(prop_values)} values")
                if hasattr(prop_values[0], '__len__') and not isinstance(prop_values[0], str):
                    print(f"  Shape per item: {len(prop_values[0])}")
                else:
                    print(f"  Sample values: {prop_values[:3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading PLY file: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_header_reading():
    """Test PLY header reading to understand file structure"""
    
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    print(f"\n=== PLY Header Analysis ===")
    
    try:
        with open(ply_path, 'rb') as f:
            lines = []
            while True:
                line = f.readline().decode('ascii').strip()
                lines.append(line)
                print(f"Header: {line}")
                if line == 'end_header':
                    break
                if len(lines) > 50:  # Safety limit
                    break
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading PLY header: {e}")
        return False

if __name__ == "__main__":
    print("=== PLY File Testing ===")
    
    # First analyze the header structure
    header_success = test_header_reading()
    
    # Then try to load the data
    if header_success:
        load_success = test_ply_loading()
        
        if load_success:
            print("\n✅ PLY loading test completed successfully!")
        else:
            print("\n❌ PLY loading test failed!")
    else:
        print("\n❌ PLY header reading failed!")