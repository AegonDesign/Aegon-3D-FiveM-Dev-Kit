bl_info = {
    "name": "Aegon UV Tools",
    "author": "Aegon Design",
    "version": (7, 0, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Edit Mode > UV Menu & Aegon Tools Panel",
    "description": "Advanced UV Mapping and Stacking Tools",
    "category": "UV",
}

import bpy
import bmesh
from mathutils import Vector
import math
from math import sin, cos, pi
from bpy.props import (
    FloatProperty,
    FloatVectorProperty,
    BoolProperty,
    EnumProperty,
)

# -------------------------------------------------------------------
# 1. EXPERIMENTAL: SMART UV STACK - FIXED VERSION
# -------------------------------------------------------------------

class AEGON_OT_UVSmartStack(bpy.types.Operator):
    """Experimental: Smartly stack UVs based on geometry similarity"""
    bl_idname = "uv.aegon_smart_uv_stack"
    bl_label = "Smart UV Stack (Experimental)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and 
                context.object.type == 'MESH' and 
                context.object.mode == 'EDIT')

    def execute(self, context):
        obj = context.edit_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Select a mesh in Edit Mode!")
            return {'CANCELLED'}

        # Get bmesh from edit mode
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        # Get UV layer
        uv_layer = bm.loops.layers.uv.verify()

        # Group faces by vertex count and perimeter length
        groups = {}
        
        selected_faces = [f for f in bm.faces if f.select]
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected!")
            return {'CANCELLED'}

        for face in selected_faces:
            # Create a simple ID: (Vertex Count, Perimeter Length)
            perimeter = round(sum(edge.calc_length() for edge in face.edges), 3)
            face_id = (len(face.verts), perimeter)
            
            if face_id not in groups:
                groups[face_id] = []
            groups[face_id].append(face)

        total_stacked = 0

        # Stack each group internally
        for face_id, face_list in groups.items():
            if len(face_list) < 2: 
                continue  # No need to stack single faces
            
            # Group Leader (Reference) is the first face
            ref_face = face_list[0]
            ref_loops = ref_face.loops
            ref_center = sum((l[uv_layer].uv for l in ref_loops), Vector((0, 0))) / len(ref_loops)
            
            # Calculate reference direction
            ref_vec = ref_loops[1][uv_layer].uv - ref_loops[0][uv_layer].uv
            ref_angle = math.atan2(ref_vec.y, ref_vec.x)

            for i in range(1, len(face_list)):
                target_face = face_list[i]
                t_loops = target_face.loops
                t_center = sum((l[uv_layer].uv for l in t_loops), Vector((0, 0))) / len(t_loops)
                
                # Calculate target direction
                t_vec = t_loops[1][uv_layer].uv - t_loops[0][uv_layer].uv
                t_angle = math.atan2(t_vec.y, t_vec.x)
                
                angle_diff = ref_angle - t_angle
                cos_a, sin_a = math.cos(angle_diff), math.sin(angle_diff)

                for l in t_loops:
                    # Move to center, rotate, and place on Leader
                    uv = l[uv_layer].uv - t_center
                    x, y = uv.x, uv.y
                    uv.x = x * cos_a - y * sin_a
                    uv.y = x * sin_a + y * cos_a
                    l[uv_layer].uv = uv + ref_center
                
                total_stacked += 1

        # Update the mesh
        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, f"Aegon AI Success: Found {len(groups)} different groups, stacked {total_stacked} faces!")
        return {'FINISHED'}

# -------------------------------------------------------------------
# 2. EXPERIMENTAL STABLE: DEBUG UV ALIGN PERFECT - FIXED VERSION
# -------------------------------------------------------------------

class AEGON_OT_UVDebugAlignPerfect(bpy.types.Operator):
    """Stable: Align selected UVs perfectly to active face (position + rotation)"""
    bl_idname = "uv.aegon_debug_uv_align_perfect"
    bl_label = "UV Align Perfect (Stable)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and 
                context.object.type == 'MESH' and 
                context.object.mode == 'EDIT')

    def execute(self, context):
        obj = context.edit_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Select a mesh object and enter Edit Mode!")
            return {'CANCELLED'}

        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()

        # 1. Reference Face (Last selected)
        active_face = bm.faces.active
        if not active_face or not active_face.select:
            self.report({'WARNING'}, "A reference face must be selected!")
            return {'CANCELLED'}

        # Calculate reference center and first edge angle (direction)
        ref_loops = active_face.loops
        ref_center = sum((l[uv_layer].uv for l in ref_loops), Vector((0, 0))) / len(ref_loops)
        
        # Use angle between first two vertices as direction
        ref_vec = ref_loops[1][uv_layer].uv - ref_loops[0][uv_layer].uv
        ref_angle = math.atan2(ref_vec.y, ref_vec.x)

        count = 0
        for face in bm.faces:
            if face.select and face != active_face:
                f_loops = face.loops
                f_center = sum((l[uv_layer].uv for l in f_loops), Vector((0, 0))) / len(f_loops)
                
                # Selected face's current angle
                f_vec = f_loops[1][uv_layer].uv - f_loops[0][uv_layer].uv
                f_angle = math.atan2(f_vec.y, f_vec.x)
                
                # Calculate rotation difference
                angle_diff = ref_angle - f_angle
                
                # Create rotation matrix (to rotate around its own center)
                cos_a = math.cos(angle_diff)
                sin_a = math.sin(angle_diff)

                for l in f_loops:
                    # First move to center (zero origin)
                    uv = l[uv_layer].uv - f_center
                    
                    # Rotate (to face the same direction)
                    x, y = uv.x, uv.y
                    uv.x = x * cos_a - y * sin_a
                    uv.y = x * sin_a + y * cos_a
                    
                    # Move to reference center
                    l[uv_layer].uv = uv + ref_center
                
                count += 1

        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, f"Aegon Success: {count} faces perfectly aligned (rotation+position)!")
        return {'FINISHED'}

# -------------------------------------------------------------------
# 3. MAIN: UVW BOX MAP - ORIGINAL VERSION
# -------------------------------------------------------------------

def is_valid_context(context):
    if context.area.type != 'VIEW_3D':
        return False
    if not context.object or context.object.mode != 'EDIT':
        return False
    return context.object.type == 'MESH'

def get_uv_editable_objects(context):
    return [context.object]

def get_uv_layer(ops, bm, assign_uvmap):
    if not bm.loops.layers.uv:
        if assign_uvmap:
            bm.loops.layers.uv.new()
        else:
            ops.report({'WARNING'}, "Object must have more than one UV map")
            return None
    return bm.loops.layers.uv.verify()

def apply_box_map(bm, uv_layer, size, offset, rotation,
                  tex_aspect, force_axis,
                  force_axis_tex_aspect_correction,
                  force_axis_rotation):

    scale = 1.0 / size

    sx = 1.0 * scale
    sy = 1.0 * scale
    sz = 1.0 * scale
    ofx = offset[0]
    ofy = offset[1]
    ofz = offset[2]
    rx = rotation[0] * pi / 180.0
    ry = rotation[1] * pi / 180.0
    rz = rotation[2] * pi / 180.0

    farx = force_axis_rotation[0] * pi / 180.0
    fary = force_axis_rotation[1] * pi / 180.0
    farz = force_axis_rotation[2] * pi / 180.0

    sel_faces = [f for f in bm.faces if f.select]

    for f in sel_faces:
        n = f.normal
        for l in f.loops:
            co = l.vert.co
            x = co.x * sx
            y = co.y * sy
            z = co.z * sz
            aspect = tex_aspect

            transformed = False
            if force_axis == 'X':
                if abs(n[1]) < abs(n[0]) and abs(n[1]) >= abs(n[2]):
                    aspect *= force_axis_tex_aspect_correction
                    if n[1] >= 0.0:
                        u = -(x - ofx) * cos(fary) + (z - ofz) * sin(fary)
                        v = (x * aspect - ofx) * sin(fary) + (z * aspect - ofz) * cos(fary)
                    else:
                        u = (x - ofx) * cos(fary) + (z - ofz) * sin(fary)
                        v = -(x * aspect - ofx) * sin(fary) + (z * aspect - ofz) * cos(fary)
                    transformed = True
                elif abs(n[2]) < abs(n[0]) and abs(n[2]) >= abs(n[1]):
                    aspect *= force_axis_tex_aspect_correction
                    if n[2] >= 0.0:
                        u = (x - ofx) * cos(farz) + (y - ofy) * sin(farz)
                        v = -(x * aspect - ofx) * sin(farz) + (y * aspect - ofy) * cos(farz)
                    else:
                        u = -(x - ofx) * cos(farz) - (y + ofy) * sin(farz)
                        v = -(x * aspect + ofx) * sin(farz) + (y * aspect - ofy) * cos(farz)
                    transformed = True

            elif force_axis == 'Y':
                if abs(n[0]) < abs(n[1]) and abs(n[0]) >= abs(n[2]):
                    aspect *= force_axis_tex_aspect_correction
                    if n[0] >= 0.0:
                        u = (y - ofy) * cos(farx) + (z - ofz) * sin(farx)
                        v = -(y * aspect - ofy) * sin(farx) + (z * aspect - ofz) * cos(farx)
                    else:
                        u = -(y - ofy) * cos(farx) + (z - ofz) * sin(farx)
                        v = (y * aspect - ofy) * sin(farx) + (z * aspect - ofz) * cos(farx)
                    transformed = True
                elif abs(n[2]) >= abs(n[0]) and abs(n[2]) < abs(n[1]):
                    aspect *= force_axis_tex_aspect_correction
                    if n[2] >= 0.0:
                        u = (x - ofx) * cos(farz) + (y - ofy) * sin(farz)
                        v = -(x * aspect - ofx) * sin(farz) + (y * aspect - ofy) * cos(farz)
                    else:
                        u = -(x - ofx) * cos(farz) - (y + ofy) * sin(farz)
                        v = -(x * aspect + ofx) * sin(farz) + (y * aspect - ofy) * cos(farz)
                    transformed = True

            elif force_axis == 'Z':
                if abs(n[0]) >= abs(n[1]) and abs(n[0]) < abs(n[2]):
                    aspect *= force_axis_tex_aspect_correction
                    if n[0] >= 0.0:
                        u = (y - ofy) * cos(farx) + (z - ofz) * sin(farx)
                        v = -(y * aspect - ofy) * sin(farx) + (z * aspect - ofz) * cos(farx)
                    else:
                        u = -(y - ofy) * cos(farx) + (z - ofz) * sin(farx)
                        v = (y * aspect - ofy) * sin(farx) + (z * aspect - ofz) * cos(farx)
                    transformed = True
                elif abs(n[1]) >= abs(n[0]) and abs(n[1]) < abs(n[2]):
                    aspect *= force_axis_tex_aspect_correction
                    if n[1] >= 0.0:
                        u = -(x - ofx) * cos(fary) + (z - ofz) * sin(fary)
                        v = (x * aspect - ofx) * sin(fary) + (z * aspect - ofz) * cos(fary)
                    else:
                        u = (x - ofx) * cos(fary) + (z - ofz) * sin(fary)
                        v = -(x * aspect - ofx) * sin(fary) + (z * aspect - ofz) * cos(fary)
                    transformed = True

            if not transformed:
                if abs(n[0]) >= abs(n[1]) and abs(n[0]) >= abs(n[2]):
                    if n[0] >= 0.0:
                        u = (y - ofy) * cos(rx) + (z - ofz) * sin(rx)
                        v = -(y * aspect - ofy) * sin(rx) + (z * aspect - ofz) * cos(rx)
                    else:
                        u = -(y - ofy) * cos(rx) + (z - ofz) * sin(rx)
                        v = (y * aspect - ofy) * sin(rx) + (z * aspect - ofz) * cos(rx)
                elif abs(n[1]) >= abs(n[0]) and abs(n[1]) >= abs(n[2]):
                    if n[1] >= 0.0:
                        u = -(x - ofx) * cos(ry) + (z - ofz) * sin(ry)
                        v = (x * aspect - ofx) * sin(ry) + (z * aspect - ofz) * cos(ry)
                    else:
                        u = (x - ofx) * cos(ry) + (z - ofz) * sin(ry)
                        v = -(x * aspect - ofx) * sin(ry) + (z * aspect - ofz) * cos(ry)
                else:
                    if n[2] >= 0.0:
                        u = (x - ofx) * cos(rz) + (y - ofy) * sin(rz)
                        v = -(x * aspect - ofx) * sin(rz) + (y * aspect - ofy) * cos(rz)
                    else:
                        u = -(x - ofx) * cos(rz) - (y + ofy) * sin(rz)
                        v = -(x * aspect + ofx) * sin(rz) + (y * aspect - ofy) * cos(rz)

            l[uv_layer].uv = Vector((u, v))

class AEGON_OT_UVWBoxMap(bpy.types.Operator):
    """Main: Advanced UVW Box Mapping with projection control"""
    bl_idname = "uv.aegon_uvw_box_map"
    bl_label = "Aegon UVW Box Map"
    bl_options = {'REGISTER', 'UNDO'}

    size: FloatProperty(default=1.0, precision=4)
    rotation: FloatVectorProperty(size=3, subtype='XYZ')
    offset: FloatVectorProperty(size=3, subtype='XYZ')
    tex_aspect: FloatProperty(default=1.0, precision=4)
    assign_uvmap: BoolProperty(default=True)

    force_axis: EnumProperty(
        items=[('NONE', 'None', ''), ('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')],
        default='NONE'
    )
    force_axis_tex_aspect_correction: FloatProperty(default=3.14, precision=4)
    force_axis_rotation: FloatVectorProperty(size=3, subtype='XYZ')

    @classmethod
    def poll(cls, context):
        return is_valid_context(context)

    def execute(self, context):
        for obj in get_uv_editable_objects(context):
            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            uv_layer = get_uv_layer(self, bm, self.assign_uvmap)
            if not uv_layer:
                return {'CANCELLED'}

            apply_box_map(
                bm, uv_layer,
                self.size,
                self.offset,
                self.rotation,
                self.tex_aspect,
                self.force_axis,
                self.force_axis_tex_aspect_correction,
                self.force_axis_rotation
            )

            bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}

# -------------------------------------------------------------------
# PANEL AND MENU
# -------------------------------------------------------------------

class AEGON_PT_UVTools(bpy.types.Panel):
    """Aegon UV Tools Panel"""
    bl_label = "Aegon UV Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Aegon Tools"

    @classmethod
    def poll(cls, context):
        return (context.object and 
                context.object.type == 'MESH' and 
                context.object.mode == 'EDIT')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Main Tool
        box = layout.box()
        box.label(text="Main UV Tools", icon='MOD_UVPROJECT')
        box.operator("uv.aegon_uvw_box_map", icon='MOD_UVPROJECT')
        
        # Experimental Tools
        box = layout.box()
        box.label(text="Experimental Tools", icon='EXPERIMENTAL')
        box.operator("uv.aegon_smart_uv_stack", icon='UV_SYNC_SELECT')
        box.operator("uv.aegon_debug_uv_align_perfect", icon='SNAP_FACE_CENTER')

def menu_func_uv(self, context):
    """Add to UV Menu"""
    self.layout.separator()
    self.layout.label(text="Aegon Tools", icon='TOOL_SETTINGS')
    self.layout.operator("uv.aegon_uvw_box_map", icon='MOD_UVPROJECT')
    self.layout.separator()
    self.layout.label(text="Experimental", icon='EXPERIMENTAL')
    self.layout.operator("uv.aegon_smart_uv_stack", icon='UV_SYNC_SELECT')
    self.layout.operator("uv.aegon_debug_uv_align_perfect", icon='SNAP_FACE_CENTER')

# -------------------------------------------------------------------
# REGISTRATION
# -------------------------------------------------------------------

classes = [
    AEGON_OT_UVSmartStack,
    AEGON_OT_UVDebugAlignPerfect,
    AEGON_OT_UVWBoxMap,
    AEGON_PT_UVTools,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add to UV menu
    bpy.types.VIEW3D_MT_uv_map.append(menu_func_uv)

def unregister():
    # Remove from UV menu
    bpy.types.VIEW3D_MT_uv_map.remove(menu_func_uv)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()