#!/usr/bin/env python3
"""
COLMAP and 3D Gaussian Splatting Integration for Blender

This script automatically loads COLMAP reconstruction data and Gaussian splatting PLY files
into Blender, creating an animated camera following the COLMAP trajectory and displaying
both the sparse point cloud and dense Gaussian splats.

Usage:
    python main.py [--colmap-path PATH] [--ply-path PATH] [--images-path PATH]
"""

import argparse
import sys
from pathlib import Path

try:
    import bpy
    BLENDER_AVAILABLE = True
except ImportError:
    print("Warning: Blender Python API not available. Make sure you're running this in Blender.")
    BLENDER_AVAILABLE = False

from blender_colmap_3dgs.colmap_parser import COLMAPLoader
from blender_colmap_3dgs.blender_animation import BlenderCOLMAPIntegration
from blender_colmap_3dgs.gaussian_splatting import GaussianSplattingIntegration


def main(colmap_path: str, ply_path: str, images_path: str = None, use_kiri: bool = True):
    """Main integration function"""
    
    if not BLENDER_AVAILABLE:
        print("Error: This script must be run within Blender Python environment")
        return False
    
    print("=== COLMAP and 3D Gaussian Splatting Integration ===")
    print(f"COLMAP path: {colmap_path}")
    print(f"PLY path: {ply_path}")
    print(f"Images path: {images_path}")
    
    # Validate paths
    colmap_path = Path(colmap_path)
    ply_path = Path(ply_path)
    
    if not colmap_path.exists():
        print(f"Error: COLMAP path does not exist: {colmap_path}")
        return False
    
    if not ply_path.exists():
        print(f"Error: PLY path does not exist: {ply_path}")
        return False
    
    if images_path:
        images_path = Path(images_path)
        if not images_path.exists():
            print(f"Warning: Images path does not exist: {images_path}")
            images_path = None
    
    try:
        # Step 1: Load COLMAP data
        print("\n1. Loading COLMAP reconstruction data...")
        colmap_loader = COLMAPLoader(str(colmap_path))
        colmap_loader.load_reconstruction()
        
        if not colmap_loader.images:
            print("Error: No images found in COLMAP reconstruction")
            return False
        
        print(f"   - Loaded {len(colmap_loader.cameras)} cameras")
        print(f"   - Loaded {len(colmap_loader.images)} images")
        print(f"   - Loaded {len(colmap_loader.points3d)} 3D points")
        
        # Get camera poses and point cloud
        camera_poses = colmap_loader.get_camera_poses_for_blender(sort='id')
        colmap_points, colmap_colors = colmap_loader.get_point_cloud()
        
        # Get camera parameters for the first camera
        camera_params = {}
        if colmap_loader.cameras:
            first_camera = list(colmap_loader.cameras.values())[0]
            fx = None
            fy = None
            cx = None
            cy = None
            if first_camera.model == 'SIMPLE_PINHOLE' and len(first_camera.params) >= 3:
                fx = first_camera.params[0]
                fy = fx
                cx = first_camera.params[1]
                cy = first_camera.params[2]
            elif first_camera.model in ('PINHOLE', 'OPENCV', 'OPENCV_FISHEYE', 'FULL_OPENCV') and len(first_camera.params) >= 4:
                fx = first_camera.params[0]
                fy = first_camera.params[1]
                cx = first_camera.params[2]
                cy = first_camera.params[3]
            else:
                if len(first_camera.params) > 0:
                    fx = first_camera.params[0]
                    fy = fx
            camera_params = {
                'width': first_camera.width,
                'height': first_camera.height,
                'fx': fx,
                'fy': fy,
                'cx': cx,
                'cy': cy,
                'model': first_camera.model,
            }
        
        # Step 2: Load Gaussian Splats
        print("\n2. Loading 3D Gaussian Splats...")
        gs_integration = GaussianSplattingIntegration()
        
        if gs_integration.load_gaussian_splats(str(ply_path), use_kiri=use_kiri):
            print("   - Successfully loaded Gaussian splats")
            
            # Align splats with COLMAP point cloud
            if len(colmap_points) > 0:
                print("   - Aligning splats with COLMAP point cloud...")
                gs_integration.align_with_colmap(colmap_points)
        else:
            print("   - Failed to load Gaussian splats")
        
        # Step 3: Setup Blender scene
        print("\n3. Setting up Blender scene...")
        blender_integration = BlenderCOLMAPIntegration()
        
        blender_integration.setup_scene(
            poses=camera_poses,
            points=colmap_points,
            colors=colmap_colors,
            images_path=str(images_path) if images_path else "",
            camera_params=camera_params,
            clear_existing=True
        )
        
        # Setup Gaussian splat visualization
        gs_integration.setup_visualization()
        
        print("   - Created animated camera with", len(camera_poses), "keyframes")
        if len(colmap_points) > 0:
            print("   - Created COLMAP point cloud with", len(colmap_points), "points")
        if blender_integration.image_planes:
            print("   - Created", len(blender_integration.image_planes), "image planes")
        
        # Step 4: Final scene setup
        print("\n4. Finalizing scene setup...")
        
        # Set playback range
        if camera_poses:
            bpy.context.scene.frame_start = 1
            bpy.context.scene.frame_end = len(camera_poses)
            bpy.context.scene.frame_current = 1
        
        # Set viewport to camera view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        break
                break
        
        print("\n=== Integration Complete! ===")
        print("Scene is ready for visualization:")
        print("- Press SPACEBAR to play camera animation")
        print("- Use NUM0 to switch to camera view")
        print("- Use NUM7/NUM1/NUM3 for top/front/side views")
        
        return True
        
    except Exception as e:
        print(f"Error during integration: {e}")
        import traceback
        traceback.print_exc()
        return False


def setup_example_paths():
    """Setup example paths for testing"""
    # These are placeholder paths - user should modify them
    example_paths = {
        'colmap_path': '/tmp/colmap_workspace',  # Contains sparse/0/ folder with .bin files
        'ply_path': '/tmp/splats.ply',           # Gaussian splats PLY file
        'images_path': '/tmp/images'             # Original images folder
    }
    
    return example_paths


def _parse_blender_cli_args(argv):
    """Parse arguments when running inside Blender. Blender forwards args after `--`."""
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='COLMAP and 3D Gaussian Splatting Integration (Blender)')
    parser.add_argument('--colmap-path', required=True, help='Path to COLMAP workspace or sparse folder')
    parser.add_argument('--ply-path', required=True, help='Path to Gaussian splats PLY file')
    parser.add_argument('--images-path', default=None, help='Path to original images folder (optional)')
    parser.add_argument('--no-kiri', action='store_true', help='Disable KIRI 3DGS Engine integration')
    return parser.parse_args(argv) if argv else None


def run_blender_script():
    """Run the integration when executed as Blender script.

    Supports two modes:
    - With CLI args: blender --python main.py -- --colmap-path ... --ply-path ... [--images-path ...] [--no-kiri]
    - Without CLI args: prints guidance and example paths.
    """
    if not BLENDER_AVAILABLE:
        print("This script must be run within Blender")
        return

    args = _parse_blender_cli_args(sys.argv)
    if args:
        print("=== Running COLMAP + 3DGS Integration (CLI) ===")
        return main(
            colmap_path=args.colmap_path,
            ply_path=args.ply_path,
            images_path=args.images_path,
            use_kiri=not args.no_kiri,
        )

    # Fallback: show example guidance when no args provided
    example_paths = setup_example_paths()
    print("=== Running COLMAP + 3DGS Integration (Guide) ===")
    print("No CLI args detected. Either pass args after `--` or edit final_example.py.")
    print("Current example paths:")
    for key, path in example_paths.items():
        print(f"  {key}: {path}")
    print("\nTo run with your data:")
    print("  blender --python main.py -- --colmap-path /path/to/colmap --ply-path /path/to/splat.ply --images-path /path/to/images")


if __name__ == "__main__":
    if BLENDER_AVAILABLE:
        # Running inside Blender
        run_blender_script()
    else:
        # Running from command line (for development/testing)
        parser = argparse.ArgumentParser(description='COLMAP and 3D Gaussian Splatting Integration')
        parser.add_argument('--colmap-path', required=True, 
                          help='Path to COLMAP workspace (containing sparse/0/ folder)')
        parser.add_argument('--ply-path', required=True,
                          help='Path to Gaussian splats PLY file')
        parser.add_argument('--images-path', 
                          help='Path to original images folder')
        parser.add_argument('--no-kiri', action='store_true',
                          help='Disable KIRI 3DGS Engine integration')
        
        args = parser.parse_args()
        
        print("Note: To run this integration, execute this script within Blender:")
        print(f"blender --python {__file__}")
        print("\nOr open Blender and run the script in the Text Editor")
        
        print(f"\nProvided arguments:")
        print(f"  COLMAP path: {args.colmap_path}")
        print(f"  PLY path: {args.ply_path}")
        print(f"  Images path: {args.images_path}")
        print(f"  Use KIRI: {not args.no_kiri}")
