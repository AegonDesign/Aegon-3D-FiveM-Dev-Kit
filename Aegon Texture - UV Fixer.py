bl_info = {
    "name": "Aegon Texture & UV Fixer",
    "author": "aegon",
    "version": (3, 3),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Aegon Tools",
    "description": "Texture arama, klasör tarama, boş node loglama, eksik UV node'larını ekler, auto smooth temizleme ve Spec/Roughness clamp (upstream takipli).",
    "category": "Object",
}

import bpy
import os
import traceback
from math import radians

# -------------------------
# Helpers
# -------------------------
def desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def write_log(filename, lines):
    try:
        path = os.path.join(desktop_path(), filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path
    except Exception:
        return None

def append_error_log(msg):
    try:
        p = os.path.join(desktop_path(), "Aegon_Error_Log.txt")
        with open(p, "a", encoding="utf-8") as f:
            f.write(msg + "\n\n")
        return p
    except Exception:
        return None

# -------------------------
# Existing utilities (unchanged / stable)
# -------------------------
def isolate_objects_in_localview(objs, context):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        try:
            obj.select_set(True)
            context.view_layer.objects.active = obj
        except Exception:
            pass
    try:
        bpy.ops.view3d.localview(frame_selected=True)
    except Exception:
        pass

def find_unused_nodes():
    empty_nodes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if mat and mat.use_nodes:
                try:
                    for node in mat.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and (getattr(node, "image", None) is None):
                            empty_nodes.append((obj.name, mat.name, node.name))
                except Exception:
                    append_error_log("find_unused_nodes: " + traceback.format_exc())
    return empty_nodes

def fix_missing_uv_maps_on_selected():
    fixed_details = []
    for obj in bpy.context.selected_objects:
        try:
            if obj.type != 'MESH':
                continue
            active_uv = None
            if obj.data.uv_layers:
                if obj.data.uv_layers.active:
                    active_uv = obj.data.uv_layers.active.name
            if not active_uv:
                continue
            for slot in obj.material_slots:
                mat = slot.material
                if not (mat and mat.use_nodes):
                    continue
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links

                uv_nodes = [n for n in nodes if n.bl_idname == "ShaderNodeUVMap" or n.type == 'UVMAP']
                if uv_nodes:
                    for uv_node in uv_nodes:
                        if not getattr(uv_node, "uv_map", ""):
                            uv_node.uv_map = active_uv
                            fixed_details.append(f"{obj.name} | {mat.name} | {uv_node.name} set to {active_uv}")
                else:
                    new_uv = nodes.new(type="ShaderNodeUVMap")
                    new_uv.uv_map = active_uv
                    new_uv.location = (-400, 0)
                    fixed_details.append(f"{obj.name} | {mat.name} | NewUVNode {new_uv.name} -> {active_uv}")

                    for node in nodes:
                        if node.type == 'TEX_IMAGE':
                            try:
                                vec_input = node.inputs.get("Vector")
                                if vec_input and not vec_input.is_linked:
                                    links.new(new_uv.outputs.get("UV"), vec_input)
                            except Exception:
                                append_error_log("UV bind error: " + traceback.format_exc())
        except Exception:
            append_error_log("fix_missing_uv_maps_on_selected: " + traceback.format_exc())
    return fixed_details

def clear_custom_normals_and_smooth():
    processed = []
    ctx = bpy.context
    prev_mode = ctx.mode
    prev_active = ctx.view_layer.objects.active
    prev_selection = [o for o in ctx.selected_objects]

    try:
        for obj in list(bpy.data.objects):
            if obj.type != "MESH":
                continue
            try:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                ctx.view_layer.objects.active = obj

                try:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.customdata_custom_splitnormals_clear()
                except Exception:
                    append_error_log(f"custom_splitnormals_clear failed for {obj.name}: {traceback.format_exc()}")

                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except Exception:
                    pass

                mesh = obj.data
                try:
                    for p in mesh.polygons:
                        p.use_smooth = True
                except Exception:
                    append_error_log(f"set use_smooth failed for {obj.name}: {traceback.format_exc()}")

                try:
                    mesh.use_auto_smooth = True
                    mesh.auto_smooth_angle = radians(30.0)
                except Exception:
                    append_error_log(f"auto_smooth set failed for {obj.name}: {traceback.format_exc()}")

                processed.append(obj.name)
            except Exception:
                append_error_log("clear_custom_normals_and_smooth (per object): " + traceback.format_exc())
                continue
    finally:
        try:
            bpy.ops.object.select_all(action='DESELECT')
            for o in prev_selection:
                try:
                    o.select_set(True)
                except Exception:
                    pass
            ctx.view_layer.objects.active = prev_active
            if prev_mode != ctx.mode:
                try:
                    bpy.ops.object.mode_set(mode=prev_mode)
                except Exception:
                    pass
        except Exception:
            pass

    return processed

# -------------------------
# NEW: Deep clamp with upstream traversal
# -------------------------
def clamp_spec_roughness_nodes(max_value=10.0, max_depth=20):
    """
    Derin tarama ile clamp:
    - materials, worlds, node_groups içindeki node'ları tarar.
    - input ismi içinde 'spec' veya 'rough' geçen tüm socket'leri bulur.
    - eğer socket bağlıysa upstream kaynak socket'leri rekürsif takip edip
      default_value'larını clamp eder.
    - numeric veya tuple/list içindeki numeric elemanları clamp eder.
    Dönen liste: (owner_label, node_name, socket_name, old_val, new_val)
    """
    modified = []
    visited = set()

    def socket_id(sock):
        # benzersiz id için kombinasyon
        try:
            return (id(sock), getattr(sock, "name", ""), getattr(getattr(sock, "node", None), "name", ""))
        except Exception:
            return id(sock)

    def clamp_value_on_socket(sock, owner_label_for_report=None):
        """
        Sock: node input/output socket (NodeSocket)
        owner_label_for_report: str, hangi top-level blok taraması başlattı (Material:..., World:..., NodeGroup:...)
        """
        sid = socket_id(sock)
        if sid in visited:
            return
        visited.add(sid)

        # attempt clamp on this socket's default_value
        try:
            val = getattr(sock, "default_value", None)
            if isinstance(val, (int, float)):
                if val > max_value:
                    old = val
                    try:
                        sock.default_value = max_value
                        modified.append((owner_label_for_report, getattr(getattr(sock, "node", None), "name", "NOD"), sock.name, old, max_value))
                    except Exception:
                        append_error_log(f"Failed to assign numeric default_value on socket {sock.name} ({sock})")
            elif isinstance(val, (tuple, list)):
                new = list(val)
                changed = False
                for i, comp in enumerate(new):
                    if isinstance(comp, (int, float)) and comp > max_value:
                        new[i] = max_value
                        changed = True
                if changed:
                    new_val = type(val)(new)
                    try:
                        sock.default_value = new_val
                        modified.append((owner_label_for_report, getattr(getattr(sock, "node", None), "name", "NOD"), sock.name, val, new_val))
                    except Exception:
                        append_error_log(f"Failed to assign tuple/list default_value on socket {sock.name} ({sock})")
        except Exception:
            append_error_log("clamp_value_on_socket default_value read error: " + traceback.format_exc())

        # if socket has incoming links (i.e. is input socket), follow from_socket(s)
        try:
            # socket.links is list of Link objects connecting this socket
            for link in getattr(sock, "links", []) or []:
                # incoming: for an input socket, link.from_socket is upstream output
                from_sock = getattr(link, "from_socket", None)
                if from_sock is None:
                    continue
                # Recurse to from_sock
                try:
                    clamp_value_on_socket(from_sock, owner_label_for_report)
                except Exception:
                    append_error_log("clamp recursion error: " + traceback.format_exc())
        except Exception:
            append_error_log("clamp socket.links iterate error: " + traceback.format_exc())

    def process_node_collection(nodes, owner_label):
        for node in nodes:
            # check node inputs (these are NodeSocket objects)
            for sock in getattr(node, "inputs", []):
                try:
                    name = sock.name.lower()
                    if ("spec" in name) or ("rough" in name):
                        clamp_value_on_socket(sock, owner_label)
                except Exception:
                    append_error_log("process_node_collection socket loop: " + traceback.format_exc())

    # Materials
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        try:
            process_node_collection(mat.node_tree.nodes, f"Material:{mat.name}")
        except Exception:
            append_error_log("clamp_spec_roughness_nodes (material): " + traceback.format_exc())

    # Worlds
    for world in bpy.data.worlds:
        if not world.use_nodes:
            continue
        try:
            process_node_collection(world.node_tree.nodes, f"World:{world.name}")
        except Exception:
            append_error_log("clamp_spec_roughness_nodes (world): " + traceback.format_exc())

    # Node Groups (global node groups)
    for ng in bpy.data.node_groups:
        try:
            process_node_collection(ng.nodes, f"NodeGroup:{ng.name}")
        except Exception:
            append_error_log("clamp_spec_roughness_nodes (nodegroup): " + traceback.format_exc())

    return modified

# -------------------------
# Operators
# -------------------------
class AEGONTOOLS_OT_FixUVMaps(bpy.types.Operator):
    bl_idname = "aegon.fix_uv_maps"
    bl_label = "Fix Missing UV Maps"
    bl_description = "Seçili objelerin eksik UV Map node'larını ekler ve image texture node'larına otomatik bağlar."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        details = fix_missing_uv_maps_on_selected()
        if details:
            p = write_log("Aegon_UV_Fix_Report.txt", details)
            self.report({'INFO'}, f"{len(details)} değişiklik yapıldı. Rapor: {p}")
        else:
            self.report({'INFO'}, "Hiçbir UV node düzenlenmedi/eklenmedi (seçili objelerde aktif UV bulunmuyor olabilir).")
        return {'FINISHED'}

class AEGONTOOLS_OT_FindTexture(bpy.types.Operator):
    bl_idname = "aegon.find_texture"
    bl_label = "Find by Texture Name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        texture_name = context.scene.aegon_texture_name.strip()
        if not texture_name:
            self.report({'ERROR'}, "Lütfen bir texture adı girin.")
            return {'CANCELLED'}

        found_objects = []
        try:
            for obj in bpy.data.objects:
                if obj.type != 'MESH':
                    continue
                for slot in obj.material_slots:
                    mat = slot.material
                    if mat and mat.use_nodes:
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and getattr(node, "image", None):
                                if texture_name.lower() in node.image.name.lower():
                                    found_objects.append(obj.name)
                                    break
        except Exception:
            append_error_log("FindTexture scan error: " + traceback.format_exc())

        empty_nodes = find_unused_nodes()
        lines = []
        lines.append("=== BULUNAN OBJELER ===")
        for i, name in enumerate(found_objects, 1):
            lines.append(f"map {i}: {name}")
        lines.append("")
        lines.append("=== BOŞ TEXTURE NODE'LAR ===")
        if empty_nodes:
            for obj_name, mat_name, node_name in empty_nodes:
                lines.append(f"[{obj_name}] | Mat: {mat_name} | Node: {node_name} -> NO IMAGE")
        else:
            lines.append("Boş image node bulunamadı.")
        p = write_log("Aegon_Texture_Found.txt", lines)
        if context.scene.aegon_local_view and found_objects:
            objs = [bpy.data.objects.get(n) for n in found_objects if bpy.data.objects.get(n)]
            isolate_objects_in_localview(objs, context)
        self.report({'INFO'}, f"{len(found_objects)} obje bulundu. Rapor: {p}")
        return {'FINISHED'}

class AEGONTOOLS_OT_FindTexturesInFolder(bpy.types.Operator):
    bl_idname = "aegon.find_textures_in_folder"
    bl_label = "Scan Folder & List Usage"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        folder = context.scene.aegon_texture_folder
        if not folder or not os.path.isdir(folder):
            self.report({'ERROR'}, "Geçerli bir klasör seçin.")
            return {'CANCELLED'}

        textures_in_folder = [f for f in os.listdir(folder)
                              if f.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".exr", ".hdr", ".tga"))]

        used_textures = {}
        try:
            for obj in bpy.data.objects:
                if obj.type != 'MESH':
                    continue
                for slot in obj.material_slots:
                    mat = slot.material
                    if mat and mat.use_nodes:
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and getattr(node, "image", None):
                                img_name = node.image.name
                                used_textures.setdefault(img_name, []).append(obj.name)
        except Exception:
            append_error_log("FindTexturesInFolder scan error: " + traceback.format_exc())

        empty_nodes = find_unused_nodes()
        lines = []
        lines.append("=== KULLANILAN TEXTURELER ===")
        counter = 1
        for tex_name, objs in used_textures.items():
            lines.append(f"\nmap {counter}: {tex_name}")
            for objname in objs:
                lines.append(f"   - {objname}")
            counter += 1

        unused = [t for t in textures_in_folder if not any(t in tex for tex in used_textures.keys())]
        lines.append("\n=== KULLANILMAYAN TEXTURELER ===")
        if unused:
            for t in unused:
                lines.append(f"- {t}")
        else:
            lines.append("Tüm texture'ler bir şekilde kullanılıyor.")

        lines.append("\n=== BOŞ TEXTURE NODE'LAR ===")
        if empty_nodes:
            for obj_name, mat_name, node_name in empty_nodes:
                lines.append(f"[{obj_name}] | Mat: {mat_name} | Node: {node_name} -> NO IMAGE")
        else:
            lines.append("Boş image node bulunamadı.")

        p = write_log("Aegon_Texture_Report.txt", lines)

        if context.scene.aegon_local_view and used_textures:
            all_objs = []
            for objs in used_textures.values():
                for o in objs:
                    if o in bpy.data.objects:
                        all_objs.append(bpy.data.objects[o])
            if all_objs:
                isolate_objects_in_localview(all_objs, context)

        self.report({'INFO'}, f"Rapor oluşturuldu: {p}")
        return {'FINISHED'}

class AEGONTOOLS_OT_ClearNormalsSmooth(bpy.types.Operator):
    bl_idname = "aegon.clear_normals_smooth"
    bl_label = "Clear Custom Normals + Auto Smooth"
    bl_description = "Tüm objelerden Custom Split Normals Data temizler ve 30° Auto Smooth uygular."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        processed = clear_custom_normals_and_smooth()
        lines = [f"Clear Custom Split Normals + Auto Smooth applied to {len(processed)} objects."]
        lines += processed
        p = write_log("Aegon_ClearNormals_Report.txt", lines)
        self.report({'INFO'}, f"{len(processed)} objeye uygulandı. Rapor: {p}")
        return {'FINISHED'}

class AEGONTOOLS_OT_ClampSpecRoughness(bpy.types.Operator):
    bl_idname = "aegon.clamp_spec_roughness"
    bl_label = "Clamp Spec/Roughness to 10 (Deep)"
    bl_description = "Tüm nodelardaki Spec/Roughness input'larını tarar; bağlıysa upstream kaynaklarda da clamp eder."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            modified = clamp_spec_roughness_nodes(10.0)
            lines = [f"{len(modified)} input değeri sınırlandı (10 ile)."]
            for m in modified:
                # m: (owner_label, node_name, socket_name, old_val, new_val)
                lines.append(f"{m[0]} | {m[1]} | {m[2]} : {m[3]} -> {m[4]}")
            p = write_log("Aegon_Clamp_Report.txt", lines)
            self.report({'INFO'}, f"{len(modified)} değer sınırlandı. Rapor: {p}")
        except Exception:
            append_error_log("AEGONTOOLS_OT_ClampSpecRoughness.execute: " + traceback.format_exc())
            self.report({'ERROR'}, "Clamp işlemi sırasında hata oluştu. Log'a bak.")
        return {'FINISHED'}

# -------------------------
# UI Panel
# -------------------------
class AEGONTOOLS_PT_Panel(bpy.types.Panel):
    bl_label = "Aegon Texture & UV Fixer"
    bl_idname = "AEGONTOOLS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Aegon Tools"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "aegon_texture_folder", text="Texture Folder")
        layout.operator("aegon.find_textures_in_folder", text="Scan Folder & List Usage", icon='FILE_FOLDER')

        layout.separator()
        layout.prop(context.scene, "aegon_texture_name", text="Texture Name")
        layout.operator("aegon.find_texture", text="Find by Texture Name", icon='VIEWZOOM')

        layout.separator()
        layout.operator("aegon.fix_uv_maps", text="Fix Missing UV Maps", icon='UV')

        layout.separator()
        layout.operator("aegon.clear_normals_smooth", text="Clear Custom Normals + Auto Smooth", icon='MOD_SMOOTH')

        layout.separator()
        layout.operator("aegon.clamp_spec_roughness", text="Clamp Spec/Roughness (Deep)", icon='MATERIAL')

        layout.separator()
        layout.prop(context.scene, "aegon_local_view", text="Use Local View")

# -------------------------
# Registration
# -------------------------
classes = (
    AEGONTOOLS_OT_FixUVMaps,
    AEGONTOOLS_OT_FindTexture,
    AEGONTOOLS_OT_FindTexturesInFolder,
    AEGONTOOLS_OT_ClearNormalsSmooth,
    AEGONTOOLS_OT_ClampSpecRoughness,
    AEGONTOOLS_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aegon_texture_name = bpy.props.StringProperty(
        name="Texture Name",
        description="Aramak istediğin texture adını buraya gir",
        default=""
    )
    bpy.types.Scene.aegon_texture_folder = bpy.props.StringProperty(
        name="Texture Folder",
        subtype='DIR_PATH',
        description="Tarama yapmak istediğin texture klasörünü seç"
    )
    bpy.types.Scene.aegon_local_view = bpy.props.BoolProperty(
        name="Use Local View",
        description="Bulunan objeleri local view'a al",
        default=True
    )

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    for prop in ("aegon_texture_name", "aegon_texture_folder", "aegon_local_view"):
        try:
            delattr(bpy.types.Scene, prop)
        except Exception:
            pass

if __name__ == "__main__":
    register()
