"""Blender camera animation utilities"""
import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector, Quaternion
from typing import List, Tuple, Optional
from pathlib import Path


def clear_scene():
    """Clear all objects from the current Blender scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_camera_with_animation(poses: List[Tuple[str, np.ndarray, np.ndarray]],
                                frame_start: int = 1,
                                frame_end: Optional[int] = None) -> bpy.types.Object:
    """Create animated camera following COLMAP trajectory"""
    if not poses:
        raise ValueError("No camera poses provided")
        
    if frame_end is None:
        frame_end = len(poses)
    
    # Create camera
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    camera.name = "COLMAP_Camera"
    camera.rotation_mode = 'QUATERNION'
    
    # Set frame range
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    
    # Animate camera
    for i, (image_name, rotation_matrix, translation) in enumerate(poses):
        frame = frame_start + i
        bpy.context.scene.frame_set(frame)
        
        # Convert numpy arrays to Blender Matrix and Quaternion
        mat3 = Matrix(rotation_matrix.tolist())
        camera.location = Vector(translation)
        camera.rotation_quaternion = mat3.to_quaternion()

        # Insert keyframes
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_quaternion", frame=frame)
    
    # Set interpolation to linear for smoother motion
    if camera.animation_data and camera.animation_data.action:
        for fcurve in camera.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'
    
    return camera


def create_point_cloud_mesh(points: np.ndarray,
                           colors: np.ndarray,
                           name: str = "COLMAP_PointCloud",
                           point_radius: float = 0.01,
                           max_points: int = 200000) -> bpy.types.Object:
    """Create a visible point cloud using Geometry Nodes instancing for performance.

    Falls back to simple mesh vertices if GN not available.
    """
    if points is None or len(points) == 0:
        print("No points to create mesh")
        return None

    # Subsample for performance if needed
    if len(points) > max_points:
        import numpy as _np
        idx = _np.random.choice(len(points), max_points, replace=False)
        points = points[idx]
        if len(colors) == len(idx):
            colors = colors[idx]

    # Base mesh with vertices only
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(p) for p in points], [], [])
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Create a small icosphere to instance
    ico_mesh = bpy.data.meshes.new(f"{name}_InstanceMesh")
    ico_bm = bmesh.new()
    bmesh.ops.create_icosphere(ico_bm, subdivisions=1, radius=point_radius)
    ico_bm.to_mesh(ico_mesh)
    ico_bm.free()
    ico_obj = bpy.data.objects.new(f"{name}_Instance", ico_mesh)
    bpy.context.collection.objects.link(ico_obj)
    ico_obj.hide_render = True
    ico_obj.hide_viewport = True

    # Geometry Nodes modifier to instance on points
    try:
        mod = obj.modifiers.new(name="PointInstancer", type='NODES')
        nt = bpy.data.node_groups.new(f"GN_{name}", 'GeometryNodeTree')
        mod.node_group = nt

        # Build node tree
        nodes = nt.nodes
        links = nt.links
        nodes.clear()

        n_input = nodes.new('NodeGroupInput')
        n_input.location = (-300, 0)
        n_output = nodes.new('NodeGroupOutput')
        n_output.location = (400, 0)
        nt.inputs.new('NodeSocketGeometry', 'Geometry')
        nt.outputs.new('NodeSocketGeometry', 'Geometry')

        n_mesh_to_points = nodes.new('GeometryNodeMeshToPoints')
        n_mesh_to_points.location = (-100, 0)
        n_mesh_to_points.inputs['Radius'].default_value = point_radius

        n_obj_info = nodes.new('GeometryNodeObjectInfo')
        n_obj_info.location = (0, -200)
        n_obj_info.inputs['As Instance'].default_value = True
        n_obj_info.inputs['Object'].default_value = ico_obj

        n_instance = nodes.new('GeometryNodeInstanceOnPoints')
        n_instance.location = (200, 0)

        # Links
        links.new(n_input.outputs['Geometry'], n_mesh_to_points.inputs['Mesh'])
        links.new(n_mesh_to_points.outputs['Points'], n_instance.inputs['Points'])
        links.new(n_obj_info.outputs['Geometry'], n_instance.inputs['Instance'])
        links.new(n_instance.outputs['Instances'], n_output.inputs['Geometry'])
    except Exception as e:
        print(f"Geometry Nodes not available, falling back to raw vertices: {e}")

    return obj


def setup_camera_properties(camera: bpy.types.Object,
                           camera_params: dict,
                           width: int,
                           height: int):
    """Setup camera intrinsic properties"""
    if not camera or camera.type != 'CAMERA':
        return
        
    cam_data = camera.data
    
    # Set sensor size and focal length based on COLMAP parameters
    # Default sensor width in mm (approx. full frame). Users can adjust later.
    sensor_width = 36.0
    cam_data.sensor_width = sensor_width
    cam_data.sensor_height = (height / width) * sensor_width

    fx = camera_params.get('fx') or camera_params.get('focal_length')
    fy = camera_params.get('fy') or fx
    cx = camera_params.get('cx')
    cy = camera_params.get('cy')

    if fx:
        cam_data.lens = (fx * sensor_width) / width

    # Principal point offset -> lens shift
    # Blender shift units are in sensor widths, positive right/up.
    if cx is not None and cy is not None:
        cam_data.shift_x = (0.5 * width - cx) / width
        cam_data.shift_y = (cy - 0.5 * height) / width  # note division by width for Blender convention
    
    # Set resolution
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height


def create_image_planes(poses: List[Tuple[str, np.ndarray, np.ndarray]],
                       images_path: str,
                       scale: float = 1.0,
                       camera_params: Optional[dict] = None,
                       forward_offset: float = 0.1) -> List[bpy.types.Object]:
    """Create image planes for each camera position.

    If camera_params include width/height/fx, plane will be sized to match FOV at unit distance
    and placed forward by forward_offset along the camera forward axis.
    """
    image_planes = []
    images_dir = Path(images_path)
    
    for i, (image_name, rotation_matrix, translation) in enumerate(poses):
        image_path = images_dir / image_name
        
        if not image_path.exists():
            print(f"Image not found: {image_path}")
            continue
            
        # Create plane
        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.active_object
        plane.name = f"Image_{i:04d}_{image_name}"
        # Set aspect-correct scale
        img = None
        try:
            img = bpy.data.images.load(str(image_path))
        except Exception as _e:
            print(f"Failed to load image: {image_path} ({_e})")
            bpy.ops.object.delete()
            continue

        iw, ih = img.size[0], img.size[1]
        aspect = iw / ih if ih else 1.0

        fx = camera_params.get('fx') if camera_params else None
        fy = camera_params.get('fy') if camera_params else None
        d = max(1e-3, forward_offset)
        if fx and fy and iw and ih:
            # Default plane in Blender is 2x2 units when scale=(1,1,1)
            target_w = d * (iw / fx)
            target_h = d * (ih / fy)
            plane.scale = (target_w / 2.0, target_h / 2.0, 1.0)
        else:
            width_scale = scale
            height_scale = scale / aspect
            plane.scale = (width_scale, height_scale, 1.0)
        
        # Set position and rotation
        mat = Matrix(rotation_matrix.tolist())
        forward = mat @ Vector((0, 0, -1))  # Blender camera looks along -Z
        plane.location = Vector(translation) + forward * forward_offset
        plane.rotation_euler = mat.to_euler()
        
        # Create material with image texture
        mat = bpy.data.materials.new(name=f"Mat_{image_name}")
        mat.use_nodes = True
        plane.data.materials.append(mat)
        
        # Setup shader nodes
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Add image texture node
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.image = img
        
        # Connect to principled shader
        principled = nodes.get('Principled BSDF')
        if principled:
            links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
        
        image_planes.append(plane)
    
    return image_planes


def set_viewport_shading(shading_type: str = 'MATERIAL'):
    """Set viewport shading mode"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = shading_type
                    break


def setup_scene_for_visualization():
    """Setup scene properties for optimal visualization"""
    scene = bpy.context.scene
    
    # Set frame rate
    scene.render.fps = 24
    
    # Enable motion blur for smooth animation
    scene.render.use_motion_blur = True
    
    # Setup world background
    world = bpy.context.scene.world
    if world.use_nodes:
        bg_node = world.node_tree.nodes.get('Background')
        if bg_node:
            bg_node.inputs['Strength'].default_value = 0.1  # Darker background
    
    # Set viewport shading to material preview
    set_viewport_shading('MATERIAL')


class BlenderCOLMAPIntegration:
    """Main integration class for COLMAP data in Blender"""
    
    def __init__(self):
        self.camera = None
        self.point_cloud = None
        self.image_planes = []
        
    def setup_scene(self, 
                   poses: List[Tuple[str, np.ndarray, np.ndarray]],
                   points: np.ndarray,
                   colors: np.ndarray,
                   images_path: str,
                   camera_params: dict = None,
                   clear_existing: bool = True):
        """Setup complete Blender scene with COLMAP data"""
        
        if clear_existing:
            clear_scene()
        
        # Setup scene properties
        setup_scene_for_visualization()
        
        # Create animated camera
        if poses:
            self.camera = create_camera_with_animation(poses)
            
            # Setup camera properties if available
            if camera_params and 'width' in camera_params and 'height' in camera_params:
                setup_camera_properties(
                    self.camera, 
                    camera_params, 
                    camera_params['width'], 
                    camera_params['height']
                )
        
        # Create point cloud
        if len(points) > 0:
            self.point_cloud = create_point_cloud_mesh(points, colors, "COLMAP_PointCloud")
        
        # Create image planes
        if poses and images_path:
            self.image_planes = create_image_planes(poses, images_path, camera_params=camera_params)
        
        # Set active camera
        if self.camera:
            bpy.context.scene.camera = self.camera
