bl_info = {
    "name": "Aegon Poly Optimizer",
    "author": "Aegon",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Aegon Tools",
    "description": "Geometry optimization, triangulation, and edge reduction tool.",
    "category": "Mesh",
}

import bpy
import bmesh
from math import radians

# ------------------------------------------------------------------------
#    Helpers (Yardımcılar)
# ------------------------------------------------------------------------

def get_target_objects(context):
    """
    Scope ayarına göre (Selected veya All) işlem yapılacak objeleri döndürür.
    Sadece MESH tipi objeleri seçer.
    """
    scope = context.scene.aegon_poly_scope
    targets = []

    if scope == 'SELECTED':
        targets = [obj for obj in context.selected_objects if obj.type == 'MESH']
    else:  # ALL
        targets = [obj for obj in context.scene.objects if obj.type == 'MESH']
    
    return targets

# ------------------------------------------------------------------------
#    Operator 1: Optimize Geometry (Merge -> Dissolve -> Triangulate)
# ------------------------------------------------------------------------

class AEGON_OT_PolyOptimize(bpy.types.Operator):
    bl_idname = "aegon.poly_optimize"
    bl_label = "Optimize Geometry"
    bl_description = "Merge (0.001m) -> Ltd Dissolve (5°) -> Triangulate -> Delete Loose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = get_target_objects(context)
        
        if not objects:
            self.report({'WARNING'}, "No mesh objects found in scope!")
            return {'CANCELLED'}

        # Mevcut modu kaydet (genelde Object mode beklenir ama garanti olsun)
        if context.active_object and context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        count = 0
        for obj in objects:
            # Objeyi aktif yap
            context.view_layer.objects.active = obj
            
            # Edit moda geç
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Hepsini Seç
            bpy.ops.mesh.select_all(action='SELECT')
            
            # 1. Merge by Distance (0.001 m)
            bpy.ops.mesh.remove_doubles(threshold=0.001)
            
            # 2. Limited Dissolve (5 Derece)
            bpy.ops.mesh.dissolve_limited(angle_limit=radians(5.0))
            
            # 3. Triangulate (Ctrl + T)
            bpy.ops.mesh.quads_convert_to_tris()
            
            # 4. Clean Up - Delete Loose (Çok Önemli!)
            bpy.ops.mesh.delete_loose()
            
            # Object moda geri dön
            bpy.ops.object.mode_set(mode='OBJECT')
            count += 1

        self.report({'INFO'}, f"Aegon Optimization: {count} objects processed.")
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Operator 2: Reduce Edges (Tris to Quads + Mark Sharp)
# ------------------------------------------------------------------------

class AEGON_OT_ReduceEdges(bpy.types.Operator):
    bl_idname = "aegon.reduce_edges"
    bl_label = "Reduce Edges"
    bl_description = "Tris to Quads (Alt+J) -> Mark Sharp -> Delete Loose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = get_target_objects(context)
        
        if not objects:
            self.report({'WARNING'}, "No mesh objects found in scope!")
            return {'CANCELLED'}

        if context.active_object and context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        count = 0
        for obj in objects:
            context.view_layer.objects.active = obj
            
            # Edit moda geç
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Hepsini Seç
            bpy.ops.mesh.select_all(action='SELECT')
            
            # 1. Tris to Quads (Alt + J)
            bpy.ops.mesh.tris_convert_to_quads()
            
            # 2. Mark Sharp (Kenarları Güçlendiren Mavi Yap)
            # Seçili tüm kenarları Sharp olarak işaretler
            bpy.ops.mesh.mark_sharp()
            
            # 3. Clean Up - Delete Loose (Çok Önemli!)
            bpy.ops.mesh.delete_loose()
            
            # Object moda geri dön
            bpy.ops.object.mode_set(mode='OBJECT')
            count += 1

        self.report({'INFO'}, f"Aegon Edge Reduction: {count} objects processed.")
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel UI
# ------------------------------------------------------------------------

class AEGON_PT_PolyOptimizerPanel(bpy.types.Panel):
    bl_label = "Aegon Poly Optimizer"
    bl_idname = "AEGON_PT_PolyOptimizerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Aegon Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Kutu tasarımı
        box = layout.box()
        box.label(text="Scope / Kapsam:", icon='OUTLINER_DATA_MESH')
        
        # Seçim Radio Butonları (Scope)
        row = box.row(align=True)
        row.prop(scene, "aegon_poly_scope", expand=True)
        
        box.separator()
        
        # Buton 1: Optimize
        col = box.column(align=True)
        op1 = col.operator("aegon.poly_optimize", text="Optimize Geometry", icon='MOD_DECIM')
        
        # Buton 2: Reduce
        col.separator()
        op2 = col.operator("aegon.reduce_edges", text="Reduce Edges", icon='MOD_WIREFRAME')

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    AEGON_OT_PolyOptimize,
    AEGON_OT_ReduceEdges,
    AEGON_PT_PolyOptimizerPanel,
)

def register():
    # Scene Properties (Scope Seçimi için)
    bpy.types.Scene.aegon_poly_scope = bpy.props.EnumProperty(
        name="Scope",
        description="Choose which objects to process",
        items=[
            ('SELECTED', "Only Selected", "Process only currently selected objects"),
            ('ALL', "All Objects", "Process all mesh objects in the scene"),
        ],
        default='SELECTED'
    )
    
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.aegon_poly_scope

if __name__ == "__main__":
    register()