"""3D Gaussian Splatting integration with Blender and KIRI Engine"""
try:
    import bpy  # type: ignore
    BLENDER_AVAILABLE = True
except Exception:
    bpy = None  # type: ignore
    BLENDER_AVAILABLE = False

import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
import struct


def load_ply_gaussian_splats(ply_path: str) -> Tuple[np.ndarray, np.ndarray, dict]:
    """Load 3D Gaussian Splats from PLY file
    
    Returns:
        positions: (N, 3) array of 3D positions
        colors: (N, 3) array of RGB colors [0, 1]
        properties: dict of additional properties (opacity, scale, rotation, etc.)
    """
    positions = []
    colors = []
    properties = {}
    
    with open(ply_path, 'rb') as f:
        # Read PLY header
        line = f.readline().decode('ascii').strip()
        if line != 'ply':
            raise ValueError("Invalid PLY file")
        
        vertex_count = 0
        properties_list = []
        in_header = True
        format_binary = False
        is_little_endian = True
        
        while in_header:
            line = f.readline().decode('ascii').strip()
            
            if line.startswith('format'):
                fmt = line.split()[1]
                if 'binary' in fmt:
                    format_binary = True
                is_little_endian = 'little' in fmt
            elif line.startswith('element vertex'):
                vertex_count = int(line.split()[-1])
            elif line.startswith('property'):
                parts = line.split()
                prop_type = parts[1]
                prop_name = parts[2]
                properties_list.append((prop_type, prop_name))
            elif line == 'end_header':
                in_header = False
        
        print(f"Loading {vertex_count} vertices in {'binary' if format_binary else 'ASCII'} format")
        print(f"Properties: {[name for _, name in properties_list]}")
        
        # Initialize properties dict
        for _, prop_name in properties_list:
            if prop_name not in ['x', 'y', 'z']:
                properties[prop_name] = []
        
        # Map PLY types to struct formats
        def read_value(ply_type: str):
            if ply_type in ('float', 'float32'):
                return struct.unpack(('<' if is_little_endian else '>') + 'f', f.read(4))[0]
            if ply_type in ('double', 'float64'):
                return struct.unpack(('<' if is_little_endian else '>') + 'd', f.read(8))[0]
            if ply_type in ('uchar', 'uint8'):
                return struct.unpack('B', f.read(1))[0]
            if ply_type in ('char', 'int8'):
                return struct.unpack('b', f.read(1))[0]
            if ply_type in ('ushort', 'uint16'):
                return struct.unpack(('<' if is_little_endian else '>') + 'H', f.read(2))[0]
            if ply_type in ('short', 'int16'):
                return struct.unpack(('<' if is_little_endian else '>') + 'h', f.read(2))[0]
            if ply_type in ('uint', 'uint32'):
                return struct.unpack(('<' if is_little_endian else '>') + 'I', f.read(4))[0]
            if ply_type in ('int', 'int32'):
                return struct.unpack(('<' if is_little_endian else '>') + 'i', f.read(4))[0]
            # Default to float
            return struct.unpack(('<' if is_little_endian else '>') + 'f', f.read(4))[0]

        # Read vertex data
        for i in range(vertex_count):
            if format_binary:
                data: List[float] = []
                for prop_type, _prop_name in properties_list:
                    data.append(read_value(prop_type))
            else:
                # ASCII format
                line = f.readline().decode('ascii').strip()
                tokens = line.split()
                data = []
                for (prop_type, _prop_name), tok in zip(properties_list, tokens):
                    if prop_type in ('uchar', 'uint8', 'char', 'int8', 'ushort', 'uint16', 'short', 'int16', 'uint', 'uint32', 'int', 'int32'):
                        data.append(float(int(tok)))
                    else:
                        data.append(float(tok))
            
            # Extract position (x, y, z)
            pos = data[:3]
            positions.append(pos)
            
            # Process properties by name
            prop_idx = 0
            for prop_type, prop_name in properties_list:
                if prop_name in ['x', 'y', 'z']:
                    prop_idx += 1
                    continue
                    
                if prop_name not in properties:
                    properties[prop_name] = []
                    
                properties[prop_name].append(data[prop_idx])
                prop_idx += 1
        
        # Convert spherical harmonics to RGB colors for Nerfstudio format
        if 'f_dc_0' in properties and 'f_dc_1' in properties and 'f_dc_2' in properties:
            print("Converting spherical harmonics coefficients to RGB colors...")
            # f_dc coefficients are the 0th order SH coefficients
            # Improved SH to RGB conversion for better visibility
            
            for i in range(len(positions)):
                # Extract DC components (0th order spherical harmonics)
                sh_r = properties['f_dc_0'][i] 
                sh_g = properties['f_dc_1'][i]
                sh_b = properties['f_dc_2'][i]
                
                # Enhanced SH to RGB conversion with better color mapping
                # Using sigmoid activation for better color range
                import math
                def sigmoid(x):
                    return 1.0 / (1.0 + math.exp(-x))
                
                # Apply sigmoid to get better color distribution
                rgb_r = sigmoid(sh_r)
                rgb_g = sigmoid(sh_g) 
                rgb_b = sigmoid(sh_b)
                
                # Alternative: Linear mapping with offset
                # rgb_r = max(0, min(1, sh_r * 0.5 + 0.5))
                # rgb_g = max(0, min(1, sh_g * 0.5 + 0.5))
                # rgb_b = max(0, min(1, sh_b * 0.5 + 0.5))
                
                colors.append([rgb_r, rgb_g, rgb_b])
        else:
            # Fallback to default colors if no SH coefficients found
            print("No spherical harmonics found, using default gray colors")
            colors = [[0.5, 0.5, 0.5] for _ in range(len(positions))]
    
    # Convert lists to numpy arrays
    positions = np.array(positions)
    colors = np.array(colors)
    
    # Convert relevant properties to numpy arrays
    for key in ['opacity', 'scale_0', 'scale_1', 'scale_2', 'rot_0', 'rot_1', 'rot_2', 'rot_3']:
        if key in properties:
            properties[key] = np.array(properties[key])
    
    # Group scale and rotation if they exist
    if all(k in properties for k in ['scale_0', 'scale_1', 'scale_2']):
        properties['scale'] = np.column_stack([
            properties['scale_0'], 
            properties['scale_1'], 
            properties['scale_2']
        ])
    
    if all(k in properties for k in ['rot_0', 'rot_1', 'rot_2', 'rot_3']):
        properties['rotation'] = np.column_stack([
            properties['rot_0'],
            properties['rot_1'], 
            properties['rot_2'],
            properties['rot_3']
        ])
    
    print(f"Loaded {len(positions)} Gaussian splats with {len(colors)} colors")
    
    return positions, colors, properties


def import_gaussian_splats_with_kiri(ply_path: str) -> Optional[bpy.types.Object]:
    """Import Gaussian Splats using KIRI 3DGS Engine addon"""
    if not BLENDER_AVAILABLE:
        print("KIRI import requires Blender. Blender Python API not available.")
        return None
    try:
        # Check if KIRI addon seems present
        addons = bpy.context.preferences.addons.keys()
        if not any('kiri' in key.lower() for key in addons):
            print("KIRI 3DGS Engine addon not found. Please install and enable it.")
            return None

        # Try known operator variants
        tried = []
        op_paths = [
            ('kiri', 'import_gaussian_splats'),
            ('import_scene', 'kiri_gaussian_splats'),
            ('kiri_3dgs', 'import_gaussian_splats'),
        ]
        for mod_name, op_name in op_paths:
            mod = getattr(bpy.ops, mod_name, None)
            if mod and hasattr(mod, op_name):
                tried.append(f"bpy.ops.{mod_name}.{op_name}")
                try:
                    getattr(mod, op_name)(filepath=ply_path)
                    return bpy.context.active_object
                except Exception as e:
                    print(f"Tried {mod_name}.{op_name} failed: {e}")
        print("KIRI import operator not found among:", tried)
        print("Falling back to manual import.")
        return None
            
    except Exception as e:
        print(f"Failed to import with KIRI: {e}")
        return None


def create_gaussian_splat_points(positions: np.ndarray,
                                colors: np.ndarray,
                                properties: dict = None,
                                name: str = "GaussianSplats",
                                point_radius: float = 0.01,
                                max_points: int = 200000) -> bpy.types.Object:
    """Create an instanced representation of Gaussian splats using Geometry Nodes.

    Note: This is a visualization fallback and not true 3DGS rendering.
    """
    if not BLENDER_AVAILABLE:
        print("Cannot create splat points: Blender Python API not available.")
        return None
    if len(positions) == 0:
        print("No positions to create splat points")
        return None

    print(f"🔨 Creating 3DGS point cloud with {len(positions)} splats...")

    # Subsample for performance
    if len(positions) > max_points:
        print(f"   📊 Subsampling from {len(positions)} to {max_points} points for performance")
        indices = np.random.choice(len(positions), max_points, replace=False)
        positions = positions[indices]
        colors = colors[indices] if len(colors) == len(indices) else colors
        if properties:
            for key, values in properties.items():
                if isinstance(values, np.ndarray) and len(values) == len(indices):
                    properties[key] = values[indices]

    # Base mesh with vertices only
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(p) for p in positions], [], [])
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Instance object
    sphere_mesh = bpy.data.meshes.new(f"{name}_InstanceMesh")
    import bmesh as _bmesh
    bm = _bmesh.new()
    _bmesh.ops.create_icosphere(bm, subdivisions=1, radius=point_radius)
    bm.to_mesh(sphere_mesh)
    bm.free()
    sphere_obj = bpy.data.objects.new(f"{name}_Instance", sphere_mesh)
    bpy.context.collection.objects.link(sphere_obj)
    sphere_obj.hide_render = True
    sphere_obj.hide_viewport = True

    # Geometry Nodes for instancing
    try:
        mod = obj.modifiers.new(name="SplatInstancer", type='NODES')
        nt = bpy.data.node_groups.new(f"GN_{name}", 'GeometryNodeTree')
        mod.node_group = nt
        nodes = nt.nodes
        links = nt.links
        nodes.clear()

        n_input = nodes.new('NodeGroupInput')
        n_output = nodes.new('NodeGroupOutput')
        nt.inputs.new('NodeSocketGeometry', 'Geometry')
        nt.outputs.new('NodeSocketGeometry', 'Geometry')

        n_mesh_to_points = nodes.new('GeometryNodeMeshToPoints')
        n_mesh_to_points.inputs['Radius'].default_value = point_radius

        n_obj_info = nodes.new('GeometryNodeObjectInfo')
        n_obj_info.inputs['As Instance'].default_value = True
        n_obj_info.inputs['Object'].default_value = sphere_obj

        n_instance = nodes.new('GeometryNodeInstanceOnPoints')

        # Link
        links.new(n_input.outputs['Geometry'], n_mesh_to_points.inputs['Mesh'])
        links.new(n_mesh_to_points.outputs['Points'], n_instance.inputs['Points'])
        links.new(n_obj_info.outputs['Geometry'], n_instance.inputs['Instance'])
        links.new(n_instance.outputs['Instances'], n_output.inputs['Geometry'])
    except Exception as e:
        print(f"Failed to create Geometry Nodes for splats: {e}")

    # Material (optional for emission look)
    create_splat_material(obj, name)

    # Custom props for debug/inspection
    if properties:
        for prop_name, prop_values in properties.items():
            if isinstance(prop_values, np.ndarray):
                obj[f"splat_{prop_name}"] = prop_values[:10].tolist()  # sample preview

    print(f"   ✅ 3DGS point cloud '{name}' created (instanced)")
    return obj


def create_splat_material(obj: bpy.types.Object, name: str):
    """Create material optimized for Gaussian splat visualization"""
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    obj.data.materials.append(mat)
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create enhanced shader node setup for better 3DGS visualization
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    mix_node = nodes.new(type='ShaderNodeMixShader')
    
    # Emission shader for bright areas
    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.inputs['Strength'].default_value = 2.0
    
    # Principled BSDF for realistic lighting
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.inputs['Roughness'].default_value = 0.0
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Alpha'].default_value = 0.8
    
    # Vertex color attribute
    attr_node = nodes.new(type='ShaderNodeAttribute')
    attr_node.attribute_name = 'SplatColor'
    
    # ColorRamp for enhancing color visibility
    colorramp_node = nodes.new(type='ShaderNodeValToRGB')
    colorramp = colorramp_node.color_ramp
    colorramp.elements[0].position = 0.0
    colorramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)  # Black
    colorramp.elements[1].position = 1.0
    colorramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # White
    
    # Math node for brightness control
    brightness_node = nodes.new(type='ShaderNodeMath')
    brightness_node.operation = 'MULTIPLY'
    brightness_node.inputs[1].default_value = 1.5  # Brightness multiplier
    
    # RGB curves for color enhancement
    curves_node = nodes.new(type='ShaderNodeRGBCurve')
    
    # Link nodes for enhanced visualization
    links.new(attr_node.outputs['Color'], curves_node.inputs['Color'])
    links.new(curves_node.outputs['Color'], principled_node.inputs['Base Color'])
    links.new(curves_node.outputs['Color'], emission_node.inputs['Color'])
    
    # Mix emission and principled shaders
    links.new(emission_node.outputs['Emission'], mix_node.inputs[1])
    links.new(principled_node.outputs['BSDF'], mix_node.inputs[2])
    mix_node.inputs['Fac'].default_value = 0.3  # Mix ratio
    
    links.new(mix_node.outputs['Shader'], output_node.inputs['Surface'])
    
    # Set material properties for better visibility
    mat.use_backface_culling = False
    mat.blend_method = 'BLEND'  # Enable transparency
    mat.use_screen_refraction = True
    
    return mat


def setup_splat_visualization_settings():
    """Setup Blender settings for optimal Gaussian splat visualization"""
    print("🎨 Setting up enhanced 3DGS visualization...")
    
    # Set viewport display settings (feature-gated for Blender versions)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Use material preview for better 3DGS rendering
                    if hasattr(space, 'shading') and hasattr(space.shading, 'type'):
                        space.shading.type = 'MATERIAL'
                    # Prefer vertex color display if available
                    if hasattr(space.shading, 'color_type'):
                        try:
                            space.shading.color_type = 'VERTEX'
                        except Exception:
                            pass
                    if hasattr(space.shading, 'studio_light'):
                        try:
                            space.shading.studio_light = 'forest.exr'
                        except Exception:
                            pass
                    if hasattr(space.shading, 'studiolight_intensity'):
                        space.shading.studiolight_intensity = 1.5
                    if hasattr(space.shading, 'studiolight_background_alpha'):
                        space.shading.studiolight_background_alpha = 0.2
                    if hasattr(space, 'overlay'):
                        space.overlay.show_wireframes = False
                        space.overlay.show_face_orientation = False
                    print("   ✅ Viewport shading configured")
                    break
    
    # Set render engine for better results (support both old and new Blender versions)
    try:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        print("   ✅ Using EEVEE Next (Blender 4.0+)")
        
        # Configure EEVEE Next
        if hasattr(bpy.context.scene, 'eevee'):
            eevee = bpy.context.scene.eevee
            if hasattr(eevee, 'use_bloom'):
                eevee.use_bloom = True
                eevee.bloom_intensity = 0.8
                eevee.bloom_radius = 6.0
    except:
        try:
            bpy.context.scene.render.engine = 'EEVEE'
            print("   ✅ Using EEVEE (Blender 3.x)")
            
            # Configure legacy EEVEE
            eevee = bpy.context.scene.eevee
            eevee.use_bloom = True
            eevee.bloom_intensity = 0.8
            eevee.bloom_radius = 6.0
            eevee.use_volumetric_lights = False
            eevee.volumetric_tile_size = '2'
        except:
            # Fallback to Cycles
            bpy.context.scene.render.engine = 'CYCLES'
            print("   ✅ Fallback to Cycles render engine")
    
    # Set world background
    world = bpy.context.scene.world
    if world and world.use_nodes:
        bg_node = world.node_tree.nodes.get('Background')
        if bg_node:
            bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)  # Dark background
            bg_node.inputs['Strength'].default_value = 0.3
            print("   ✅ Dark background for better 3DGS visibility")
    
    print("   ✅ EEVEE render engine with bloom effects")
    
    # Set better viewport clipping for large scenes
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 1000.0  # Extend far clipping
                    space.clip_start = 0.01   # Closer near clipping
                    break


def align_gaussian_splats_with_colmap(splat_obj: bpy.types.Object,
                                     colmap_positions: np.ndarray,
                                     splat_positions: np.ndarray) -> bpy.types.Object:
    """Align Gaussian splats with COLMAP point cloud using improved alignment"""
    if splat_obj is None or len(colmap_positions) == 0 or len(splat_positions) == 0:
        return splat_obj
    
    print("🔄 Aligning Gaussian splats with COLMAP point cloud...")
    
    # Convert splat positions to Blender coordinate system (same as COLMAP)
    # Nerfstudio uses different coordinates than COLMAP
    # Apply the same transformation that was applied to COLMAP points
    colmap_to_blender = np.array([
        [1, 0, 0],
        [0, 0, -1],
        [0, 1, 0]
    ])
    
    # Transform splat positions to match COLMAP coordinate system
    splat_positions_transformed = (colmap_to_blender @ splat_positions.T).T
    
    # Calculate centroids
    colmap_centroid = np.mean(colmap_positions, axis=0)
    splat_centroid = np.mean(splat_positions_transformed, axis=0)
    
    print(f"📍 COLMAP centroid: [{colmap_centroid[0]:.2f}, {colmap_centroid[1]:.2f}, {colmap_centroid[2]:.2f}]")
    print(f"📍 Splat centroid: [{splat_centroid[0]:.2f}, {splat_centroid[1]:.2f}, {splat_centroid[2]:.2f}]")
    
    # Calculate translation offset
    translation_offset = colmap_centroid - splat_centroid
    print(f"↗️ Translation offset: [{translation_offset[0]:.2f}, {translation_offset[1]:.2f}, {translation_offset[2]:.2f}]")
    
    # Calculate bounding boxes for better scale estimation
    colmap_bbox = np.ptp(colmap_positions, axis=0)  # Point-to-point range
    splat_bbox = np.ptp(splat_positions_transformed, axis=0)
    
    print(f"📦 COLMAP bbox: [{colmap_bbox[0]:.2f}, {colmap_bbox[1]:.2f}, {colmap_bbox[2]:.2f}]")
    print(f"📦 Splat bbox: [{splat_bbox[0]:.2f}, {splat_bbox[1]:.2f}, {splat_bbox[2]:.2f}]")
    
    # Use median of bbox ratios for more stable scaling
    scale_ratios = []
    for i in range(3):
        if splat_bbox[i] > 0:
            scale_ratios.append(colmap_bbox[i] / splat_bbox[i])
    
    if scale_ratios:
        scale_factor = np.median(scale_ratios)
        print(f"📏 Raw scale factor: {scale_factor:.3f}")
        
        # Apply conservative scale limits
        scale_factor = max(0.5, min(2.0, scale_factor))
        print(f"📏 Clamped scale factor: {scale_factor:.3f}")
    else:
        scale_factor = 1.0
        print("📏 Using default scale factor: 1.0")
    
    # Apply transformations to splat object
    splat_obj.location = tuple(translation_offset)
    splat_obj.scale = (scale_factor, scale_factor, scale_factor)
    
    # Also apply the coordinate system rotation
    import mathutils
    import mathutils
    rotation_matrix = mathutils.Matrix([
        [1, 0, 0],
        [0, 0, -1],
        [0, 1, 0]
    ])
    splat_obj.rotation_euler = rotation_matrix.to_euler()
    
    print(f"✅ Applied transformation:")
    print(f"   Location: [{splat_obj.location[0]:.2f}, {splat_obj.location[1]:.2f}, {splat_obj.location[2]:.2f}]")
    print(f"   Scale: [{splat_obj.scale[0]:.2f}, {splat_obj.scale[1]:.2f}, {splat_obj.scale[2]:.2f}]")
    print(f"   Rotation: [{np.degrees(splat_obj.rotation_euler[0]):.1f}°, {np.degrees(splat_obj.rotation_euler[1]):.1f}°, {np.degrees(splat_obj.rotation_euler[2]):.1f}°]")
    
    return splat_obj


def simple_icp_alignment(source_points: np.ndarray, 
                        target_points: np.ndarray,
                        max_iterations: int = 10,
                        tolerance: float = 0.001) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simple ICP alignment between two point clouds
    
    Returns:
        rotation_matrix: 3x3 rotation matrix
        translation: 3x1 translation vector
    """
    # Subsample points for faster computation
    max_points = 1000
    if len(source_points) > max_points:
        indices = np.random.choice(len(source_points), max_points, replace=False)
        source_subset = source_points[indices]
    else:
        source_subset = source_points.copy()
    
    if len(target_points) > max_points:
        indices = np.random.choice(len(target_points), max_points, replace=False)
        target_subset = target_points[indices]
    else:
        target_subset = target_points.copy()
    
    # Initialize transformation
    R = np.eye(3)
    t = np.zeros(3)
    
    prev_error = float('inf')
    
    for iteration in range(max_iterations):
        # Transform source points
        transformed_source = (R @ source_subset.T).T + t
        
        # Find closest points (simplified - just use centroid matching)
        source_centroid = np.mean(transformed_source, axis=0)
        target_centroid = np.mean(target_subset, axis=0)
        
        # Update translation
        t = target_centroid - source_centroid
        
        # Calculate current error
        current_error = np.linalg.norm(t)
        
        if abs(prev_error - current_error) < tolerance:
            break
            
        prev_error = current_error
    
    return R, t


class GaussianSplattingIntegration:
    """Integration class for Gaussian Splatting in Blender"""
    
    def __init__(self):
        self.splat_object = None
        self.splat_positions = None
        self.splat_colors = None
        self.splat_properties = None
        self._manual = False
        
    def load_gaussian_splats(self, ply_path: str, use_kiri: bool = True) -> bool:
        """Load Gaussian splats from PLY file"""
        if not Path(ply_path).exists():
            print(f"PLY file not found: {ply_path}")
            return False
        
        # Try KIRI import first if requested
        if use_kiri:
            self.splat_object = import_gaussian_splats_with_kiri(ply_path)
            if self.splat_object:
                print(f"Successfully imported splats with KIRI: {self.splat_object.name}")
                self._manual = False
                return True
        
        # Fallback to manual import
        try:
            positions, colors, properties = load_ply_gaussian_splats(ply_path)
            self.splat_positions = positions
            self.splat_colors = colors
            self.splat_properties = properties
            
            # Create point cloud representation
            self.splat_object = create_gaussian_splat_points(
                positions, colors, properties, "ManualGaussianSplats"
            )
            
            if self.splat_object:
                print(f"Successfully created splat object: {self.splat_object.name}")
                self._manual = True
                return True
                
        except Exception as e:
            print(f"Failed to load Gaussian splats: {e}")
            
        return False
    
    def align_with_colmap(self, colmap_positions: np.ndarray):
        """Align splats with COLMAP point cloud"""
        if self.splat_object and self.splat_positions is not None:
            # Only apply coordinate system rotation if using manual loader
            obj = align_gaussian_splats_with_colmap(
                self.splat_object, colmap_positions, self.splat_positions
            )
            if not self._manual:
                # Undo the axis rotation applied in aligner if KIRI already handles coords
                try:
                    obj.rotation_euler = (0.0, 0.0, 0.0)
                except Exception:
                    pass
            self.splat_object = obj
            
    def setup_visualization(self):
        """Setup optimal visualization settings"""
        setup_splat_visualization_settings()
        
        if self.splat_object:
            # Make splats visible in all view modes
            self.splat_object.display_type = 'TEXTURED'
            
            # Set point size for better visibility
            if hasattr(self.splat_object.data, 'vertices'):
                for vertex in self.splat_object.data.vertices:
                    vertex.select = False
