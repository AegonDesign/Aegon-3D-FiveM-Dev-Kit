bl_info = {
    "name": "Aegon Material Optimizer",
    "author": "Aegon",
    "version": (2, 2, 1),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > Aegon Tools",
    "description": "Material optimizer + YTD-ready texture renamer/copy. Hash-based image dedupe, deep node-tree equality, material report, UV rename/remove and safer ops. Fixed ReferenceError removal issue.",
    "category": "Material",
}

import bpy
import os
import shutil
import time
import json
import hashlib

TOLERANCE = 0.01

# -----------------------------
# Helpers
# -----------------------------
def float_equal(a, b, tol=TOLERANCE):
    try:
        return abs(a - b) <= tol
    except:
        return False

def bpy_abspath(path):
    try:
        return bpy.path.abspath(path)
    except:
        return path

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def unique_filename(output_dir, base_name, ext):
    candidate = f"{base_name}.{ext}"
    candidate_path = os.path.join(output_dir, candidate)
    if not os.path.exists(candidate_path):
        return candidate
    idx = 1
    while True:
        candidate = f"{base_name}_{idx}.{ext}"
        candidate_path = os.path.join(output_dir, candidate)
        if not os.path.exists(candidate_path):
            return candidate
        idx += 1

def write_log(output_dir, lines):
    ensure_folder(output_dir)
    log_path = os.path.join(output_dir, "AegonTools_log.txt")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- Log @ {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            for ln in lines:
                f.write(ln + "\n")
    except Exception as e:
        print("Failed to write log:", e)

def sanitize_tag(tag):
    if not tag:
        return ""
    s = str(tag).strip()
    s = s.replace(" ", "_")
    s = s.replace("/", "_").replace("\\", "_")
    for ch in [":", "*", "?", "\"", "<", ">", "|"]:
        s = s.replace(ch, "_")
    return s

def sanitize_name(name):
    if not name:
        return "noname"
    s = str(name)
    s = s.replace(" ", "_")
    for ch in ["/","\\",":","*","?","\"","<",">","|"]:
        s = s.replace(ch, "_")
    return s

# -----------------------------
# File / Image hashing helpers
# -----------------------------
def md5_for_file(path, chunk_size=8192):
    try:
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def md5_for_image(image):
    """
    Return md5 hex for an image:
    - If packed: use packed_file.data bytes
    - Else: use file contents (via filepath)
    Returns None on failure.
    """
    try:
        # packed
        if getattr(image, "packed_file", None) is not None and getattr(image.packed_file, "data", None) is not None:
            try:
                data = image.packed_file.data
                return hashlib.md5(data).hexdigest()
            except Exception:
                pass
        # file-based
        fp = bpy_abspath(image.filepath)
        if fp and os.path.exists(fp):
            return md5_for_file(fp)
        return None
    except Exception:
        return None

# -----------------------------
# Node & image utilities (collects ALL TEX_IMAGE nodes)
# -----------------------------
def get_all_image_nodes_for_mat(mat):
    out = {}
    try:
        if not mat.use_nodes or mat.node_tree is None:
            return out
        nodes = mat.node_tree.nodes
        principled = None
        for n in nodes:
            if n.type == 'BSDF_PRINCIPLED':
                principled = n
                break
        # semantic detection
        if principled:
            input_socket = principled.inputs.get("Base Color")
            if input_socket and input_socket.links:
                from_node = input_socket.links[0].from_node
                if from_node.type == 'TEX_IMAGE' and getattr(from_node, "image", None):
                    out['base'] = from_node
            input_socket = principled.inputs.get("Normal")
            if input_socket and input_socket.links:
                from_node = input_socket.links[0].from_node
                if from_node.type == 'NORMAL_MAP':
                    if getattr(from_node, "inputs", None) and from_node.inputs[1].links:
                        img_node = from_node.inputs[1].links[0].from_node
                        if img_node.type == 'TEX_IMAGE' and getattr(img_node, "image", None):
                            out['normal'] = img_node
                elif from_node.type == 'TEX_IMAGE' and getattr(from_node, "image", None):
                    out['normal'] = from_node
            for key, sock_name in (('roughness','Roughness'), ('metallic','Metallic'), ('emissive','Emission')):
                sock = principled.inputs.get(sock_name)
                if sock and sock.links:
                    from_node = sock.links[0].from_node
                    if from_node.type == 'TEX_IMAGE' and getattr(from_node, "image", None):
                        out[key] = from_node
        tex_count = 0
        for n in nodes:
            if n.type == 'TEX_IMAGE' and getattr(n, "image", None):
                if n in out.values():
                    continue
                key = sanitize_name(n.name) if n.name else f"tex_{tex_count}"
                if key in out:
                    key = f"{key}_{tex_count}"
                out[key] = n
                tex_count += 1
    except Exception as e:
        print("get_all_image_nodes_for_mat error:", e)
    return out

def image_node_to_path(image):
    try:
        return bpy_abspath(image.filepath)
    except:
        return None

# -----------------------------
# Heuristics: maptype detection
# -----------------------------
def detect_map_type_from_node_and_image(node, image):
    if not node and not image:
        return "map"
    names = []
    if node and getattr(node, "name", None):
        names.append(node.name.lower())
    if image and getattr(image, "name", None):
        names.append(image.name.lower())
    combined = " ".join(names)
    if "base" in combined or "albedo" in combined or "diffuse" in combined:
        return "base"
    if ("normal" in combined or "nrm" in combined or "normalmap" in combined or "bump" in combined) and ("height" not in combined):
        return "normal"
    if "rough" in combined or "rgh" in combined:
        return "roughness"
    if "metal" in combined or "metallic" in combined:
        return "metallic"
    if "spec" in combined or "specular" in combined:
        return "specular"
    if "ao" in combined or "ambient" in combined:
        return "ao"
    if "emit" in combined or "emiss" in combined:
        return "emissive"
    if "height" in combined or "disp" in combined:
        return "height"
    if node and getattr(node, "name", None):
        return sanitize_name(node.name)
    if image and getattr(image, "name", None):
        return sanitize_name(image.name.split('.')[-1])
    return "map"

# -----------------------------
# Node-tree signature for deep equality
# -----------------------------
def node_tree_signature(mat):
    try:
        if not mat.use_nodes or mat.node_tree is None:
            return "NO_NODETREE"
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        node_infos = []
        for n in nodes:
            info = {"type": n.type, "name": n.name}
            if n.type == 'TEX_IMAGE':
                img = getattr(n, "image", None)
                path = bpy_abspath(img.filepath) if img else ""
                info["image_path"] = os.path.normpath(path) if path else ""
                info["image_name"] = img.name if img else ""
                if img:
                    try:
                        info["colorspace"] = img.colorspace_settings.name
                    except:
                        info["colorspace"] = ""
            elif n.type == 'BSDF_PRINCIPLED':
                vals = {}
                for key in ('Base Color','Metallic','Roughness','Specular','Clearcoat','Emission'):
                    inp = n.inputs.get(key)
                    if inp is None:
                        continue
                    try:
                        if hasattr(inp, "default_value"):
                            v = inp.default_value
                            if hasattr(v, "__len__") and len(v) >= 3:
                                vals[key] = tuple(round(float(x),4) for x in v[:4])
                            else:
                                vals[key] = round(float(v),4)
                        else:
                            vals[key] = None
                    except:
                        vals[key] = None
                info["principled_defaults"] = vals
            elif n.type == 'RGB':
                try:
                    info["color"] = tuple(round(float(x),4) for x in n.outputs[0].default_value[:4])
                except:
                    pass
            elif n.type == 'VALUE':
                try:
                    info["value"] = round(float(n.outputs[0].default_value),4)
                except:
                    pass
            node_infos.append(json.dumps(info, sort_keys=True))

        link_infos = []
        for l in links:
            try:
                from_node = l.from_node
                to_node = l.to_node
                from_socket = l.from_socket.name if l.from_socket else ""
                to_socket = l.to_socket.name if l.to_socket else ""
                link_infos.append(f"{from_node.type}:{from_socket}->{to_node.type}:{to_socket}")
            except:
                pass

        node_infos_sorted = sorted(node_infos)
        link_infos_sorted = sorted(link_infos)

        sig = "|".join(node_infos_sorted) + "||" + "|".join(link_infos_sorted)
        return sig
    except Exception as e:
        print("node_tree_signature error:", e)
        return "SIG_ERROR"

# -----------------------------
# Material comparison functions
# -----------------------------
def materials_equal_by_textures(mat1, mat2):
    try:
        n1 = get_all_image_nodes_for_mat(mat1)
        n2 = get_all_image_nodes_for_mat(mat2)
        if set(n1.keys()) != set(n2.keys()):
            return False
        for k in n1.keys():
            p1 = image_node_to_path(n1[k].image)
            p2 = image_node_to_path(n2[k].image)
            if p1 is None or p2 is None:
                return False
            if os.path.normpath(p1) != os.path.normpath(p2):
                return False
        return True
    except Exception as e:
        print("materials_equal_by_textures error:", e)
        return False

def materials_equal_deep(mat1, mat2):
    try:
        s1 = node_tree_signature(mat1)
        s2 = node_tree_signature(mat2)
        return s1 == s2
    except Exception as e:
        print("materials_equal_deep error:", e)
        return False

# -----------------------------
# Core operations (kept same as before)
# -----------------------------
def safe_remove_material(mat, dry_run=False):
    if mat is None:
        return False
    if getattr(mat, "library", None) is not None:
        return False
    if mat.users == 0:
        if dry_run:
            return True
        try:
            bpy.data.materials.remove(mat)
            return True
        except Exception:
            return False
    return False

def remove_unused_materials(dry_run=False):
    removed = []
    mats = list(bpy.data.materials)
    for mat in mats:
        if not mat.users:
            name_copy = mat.name
            if dry_run:
                removed.append(name_copy)
            else:
                if safe_remove_material(mat, dry_run=False):
                    removed.append(name_copy)
    print("Unused materials removed:", removed)
    return removed

def merge_duplicate_materials(scope='ALL', use_strict=True, dry_run=False):
    mats = list(bpy.data.materials)
    if scope == 'SELECTED':
        sel_objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        used_mats = set()
        for o in sel_objs:
            for s in o.material_slots:
                if s.material:
                    used_mats.add(s.material)
        mats = [m for m in mats if m in used_mats]

    compare_func = materials_equal_deep if use_strict else materials_equal_by_textures

    sig_map = {}
    for m in mats:
        try:
            sig = node_tree_signature(m) if use_strict else None
        except:
            sig = None
        if not use_strict:
            nodes = get_all_image_nodes_for_mat(m)
            paths = sorted([os.path.normpath(bpy_abspath(n.image.filepath)) for n in nodes.values() if getattr(n,"image",None)])
            sig = "TEX|" + "|".join(paths)
        sig_map.setdefault(sig, []).append(m)

    merge_log = []
    for sig, group in sig_map.items():
        if len(group) <= 1:
            continue
        master = group[0]
        for other in group[1:]:
            if compare_func(master, other):
                merge_log.append((other.name, master.name))
                if not dry_run:
                    for obj in bpy.data.objects:
                        for slot in obj.material_slots:
                            if slot.material == other:
                                slot.material = master
                    try:
                        if other.users == 0 and getattr(other, "library", None) is None:
                            bpy.data.materials.remove(other)
                    except:
                        pass
    for old, new in merge_log:
        print(f"Merged (planned/done): '{old}' -> '{new}'")
    return merge_log

def remove_unused_slots_per_object(scope='ALL', dry_run=False):
    objs = []
    if scope == 'SELECTED':
        objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    else:
        objs = [o for o in bpy.data.objects if o.type == 'MESH']
    removed_info = []
    for obj in objs:
        used_indices = {poly.material_index for poly in obj.data.polygons}
        for idx in reversed(range(len(obj.material_slots))):
            if idx not in used_indices:
                mat = obj.material_slots[idx].material
                removed_info.append((obj.name, idx, mat.name if mat else "<none>"))
                if not dry_run:
                    try:
                        bpy.context.view_layer.objects.active = obj
                        if obj.mode != 'OBJECT':
                            try:
                                bpy.ops.object.mode_set(mode='OBJECT')
                            except:
                                pass
                        obj.active_material_index = idx
                        bpy.ops.object.material_slot_remove()
                    except Exception:
                        try:
                            obj.material_slots.pop(idx)
                        except:
                            pass
                    if mat and mat.users == 0 and getattr(mat, "library", None) is None:
                        try:
                            bpy.data.materials.remove(mat)
                        except:
                            pass
    print("Removed unused material slots per object (dry_run={})".format(dry_run))
    return removed_info

def multi_object_optimization(scope='ALL', use_strict=False, dry_run=False):
    log = merge_duplicate_materials(scope=scope, use_strict=use_strict, dry_run=dry_run)
    print("Multi-object optimization completed (dry_run={}).".format(dry_run))
    return log

# -----------------------------
# UV helpers
# -----------------------------
def find_uv_map_for_image_node(img_node):
    try:
        current = img_node
        visited = set()
        while current:
            if id(current) in visited:
                return None
            visited.add(id(current))
            if getattr(current, "type", None) == 'UVMAP':
                return getattr(current, "uv_map", None)
            vec_input = None
            try:
                vec_input = current.inputs.get('Vector')
            except:
                vec_input = None
            if vec_input and vec_input.links:
                from_node = vec_input.links[0].from_node
                current = from_node
                continue
            return None
    except Exception:
        return None

# -----------------------------
# Prepare YTD for ALL image nodes + material report/rename option + UV management
#  (fixed: no direct deletion, name-based canonical references, safe guards)
# -----------------------------
def prepare_ytd_export_and_material_report(scope='ALL', base_output_dir=None, custom_tag="", dry_run=False, rename_distinct=False, remove_unused_uvs=False, rename_used_uvs=False):
    # determine base output dir
    if base_output_dir and base_output_dir.strip():
        base_dir = bpy_abspath(base_output_dir)
    else:
        try:
            base_dir = os.path.dirname(bpy.data.filepath) or bpy_abspath("//")
        except:
            base_dir = bpy_abspath("//")
    output_dir = ensure_folder(os.path.join(base_dir, "AegonTools_Output"))
    log_lines = []
    material_report = {
        "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "materials": []
    }

    # choose target materials
    if scope == 'SELECTED':
        sel_objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        target_mats = []
        seen = set()
        for o in sel_objs:
            for slot in o.material_slots:
                m = slot.material
                if m and id(m) not in seen:
                    target_mats.append(m)
                    seen.add(id(m))
    else:
        target_mats = list(bpy.data.materials)

    # Prepare list of image nodes
    image_entries = []
    for m in target_mats:
        nodes_map = get_all_image_nodes_for_mat(m)
        for node_key, img_node in nodes_map.items():
            try:
                if not img_node or not getattr(img_node, "image", None):
                    continue
                image = img_node.image
            except ReferenceError:
                # image datablock removed, skip gracefully
                continue
            # packed or missing handling
            if getattr(image, "packed_file", None) is not None:
                image_entries.append((m, img_node, image, None, "PACKED"))
                continue
            orig_path = bpy_abspath(image.filepath)
            if not orig_path or not os.path.exists(orig_path):
                image_entries.append((m, img_node, image, None, "MISSING"))
                continue
            norm = os.path.normpath(orig_path)
            image_entries.append((m, img_node, image, norm, "OK"))

    # Group by normalized origin path
    path_groups = {}
    for (m, img_node, image, norm, status) in image_entries:
        key = norm if norm else (status + "_" + (image.name if image else "none"))
        path_groups.setdefault(key, []).append((m, img_node, image, norm, status))

    # First: path-based dedupe -> store canonical by name (string) to avoid ReferenceError later
    canonical_map = {}  # norm_path -> canonical_image_name (string)
    for key, entries in path_groups.items():
        if key.startswith("PACKED_") or key.startswith("MISSING_"):
            continue
        canonical_image_obj = None
        for (m, node, image, norm, status) in entries:
            if image is not None:
                canonical_image_obj = image
                break
        if canonical_image_obj is None:
            continue
        canonical_name = canonical_image_obj.name
        canonical_map[key] = canonical_name
        for (m, node, image, norm, status) in entries:
            try:
                if image is None:
                    continue
                if image.name != canonical_name:
                    # lookup canonical by name (safe)
                    canonical_obj = bpy.data.images.get(canonical_name)
                    if canonical_obj:
                        try:
                            node.image = canonical_obj
                            log_lines.append(f"PATH_DEDUP_NODE: Material '{m.name}', node '{getattr(node,'name','<noname>')}' reassigned image '{image.name}' -> canonical '{canonical_name}'")
                        except Exception as e:
                            log_lines.append(f"PATH_DEDUP_ERROR_ASSIGN: Could not assign canonical '{canonical_name}' to node '{getattr(node,'name','<noname>')}' : {e}")
                    else:
                        log_lines.append(f"PATH_DEDUP_SKIP: Canonical image '{canonical_name}' no longer exists (skipped reassignment).")
                    # do NOT remove image datablock automatically (log only)
                    log_lines.append(f"PATH_DEDUP_NOTE: Consider manual cleanup for image datablock '{image.name}' if unused.")
            except ReferenceError:
                # image object removed mid-process
                log_lines.append(f"PATH_DEDUP_REFREMOVED: Image datablock referenced by node removed during processing.")
            except Exception as e:
                log_lines.append(f"PATH_DEDUP_ERROR: {e}")

    # Second: hash-based dedupe (content-based) -> map to canonical image names (strings)
    hash_map = {}  # (hash, colorspace) -> canonical_image_name
    for (m, node, image, norm, status) in image_entries:
        if status != "OK":
            continue
        if image is None:
            continue
        try:
            h = md5_for_image(image)
            if not h:
                continue
            colorspace = ""
            try:
                colorspace = image.colorspace_settings.name
            except:
                colorspace = ""
            key = (h, colorspace)
            if key not in hash_map:
                # store canonical name
                hash_map[key] = image.name
            else:
                canonical_name = hash_map[key]
                canonical_obj = bpy.data.images.get(canonical_name)
                if canonical_obj:
                    try:
                        node.image = canonical_obj
                        log_lines.append(f"HASH_DEDUP_NODE: Material '{m.name}', node '{getattr(node,'name','<noname>')}' reassigned image '{image.name}' -> canonical '{canonical_name}'")
                    except Exception as e:
                        log_lines.append(f"HASH_DEDUP_ERROR_ASSIGN: {e}")
                    log_lines.append(f"HASH_DEDUP_NOTE: Consider manual cleanup for image datablock '{image.name}' if unused.")
                else:
                    log_lines.append(f"HASH_DEDUP_SKIP: Canonical image '{canonical_name}' not found (skipped).")
        except ReferenceError:
            log_lines.append("HASH_DEDUP_REFREMOVED: image datablock removed while hashing")
        except Exception as e:
            log_lines.append(f"HASH_DEDUP_ERROR_MAIN: {e}")

    # Material grouping & optional renaming of distinct materials (safe id-based)
    mat_signatures = {}
    for m in target_mats:
        try:
            sig = node_tree_signature(m)
        except Exception:
            sig = "SIGERR"
        mat_signatures[id(m)] = {"signature": sig, "mat": m, "orig_name": m.name}

    groups = {}
    for mid, info in mat_signatures.items():
        groups.setdefault(info["signature"], []).append(mid)

    report_entries = []
    rename_map = {}
    mat_counter = 1
    for sig, mids in groups.items():
        names = [mat_signatures[mid]["mat"].name for mid in mids]
        entry = {"signature_hash": sig[:200], "materials": names, "group_size": len(names)}
        report_entries.append(entry)
        if len(mids) == 1:
            mid = mids[0]
            mat_obj = mat_signatures[mid]["mat"]
            mat_name = mat_obj.name
            if rename_distinct and not dry_run:
                try:
                    new_mat_name = f"aegon_mat_{mat_counter}_{sanitize_name(mat_name)}"
                    mat_obj.name = new_mat_name
                    rename_map[mat_name] = new_mat_name
                    log_lines.append(f"RENAMED_MATERIAL: {mat_name} -> {new_mat_name}")
                except Exception as e:
                    log_lines.append(f"ERROR_RENAME_MATERIAL: {mat_name} -> {e}")
                mat_counter += 1
            else:
                suggested = f"aegon_mat_{mat_counter}_{sanitize_name(mat_name)}"
                entry["suggested_name"] = suggested
                mat_counter += 1
    material_report["groups"] = report_entries

    # THIRD PHASE: copy canonical images (from canonical_map and from hash_map canonical images)
    copied_map = {}  # norm_orig -> (dst_filename, canonical_image_name)
    idx = 1
    tag_clean = sanitize_tag(custom_tag)

    # Build canonical_images_to_process: norm_path -> canonical_image_name
    canonical_images_to_process = {}
    for norm_path, canonical_name in canonical_map.items():
        canonical_images_to_process[norm_path] = canonical_name
    # include hash_map canonical images if they have a path and not already included
    for (h, cs), canonical_name in hash_map.items():
        img_obj = bpy.data.images.get(canonical_name)
        if not img_obj:
            continue
        try:
            orig = bpy_abspath(img_obj.filepath)
            norm = os.path.normpath(orig) if orig and os.path.exists(orig) else None
            if norm and norm not in canonical_images_to_process:
                canonical_images_to_process[norm] = canonical_name
        except Exception:
            continue

    for norm_path in sorted(list(canonical_images_to_process.keys())):
        canonical_name = canonical_images_to_process[norm_path]
        canonical_image = bpy.data.images.get(canonical_name)
        if canonical_image is None:
            log_lines.append(f"COPY_SKIP_NOTFOUND: Canonical image '{canonical_name}' not found in bpy.data.images - skipping")
            continue
        try:
            if getattr(canonical_image, "packed_file", None) is not None:
                log_lines.append(f"PACKED_CANONICAL: Image '{canonical_image.name}' is packed, skipped copy/rename.")
                continue
        except ReferenceError:
            log_lines.append(f"COPY_REFREMOVED: Canonical image '{canonical_name}' removed during processing; skipping")
            continue
        try:
            orig_path = bpy_abspath(canonical_image.filepath)
        except Exception:
            orig_path = None
        if not orig_path or not os.path.exists(orig_path):
            log_lines.append(f"MISSING_CANONICAL: Image '{canonical_image.name}' source missing: {orig_path}")
            continue
        orig_filename = os.path.basename(orig_path)
        ext = orig_filename.split('.')[-1] if '.' in orig_filename else 'dds'
        if tag_clean:
            base_name = f"aegon_{idx}_{tag_clean}"
        else:
            base_name = f"aegon_{idx}"
        # map hint
        map_hint = None
        found_node = None
        for (m, node, image, norm, status) in image_entries:
            if norm == norm_path and image and image.name == canonical_image.name:
                found_node = node
                break
        if found_node:
            map_hint = detect_map_type_from_node_and_image(found_node, canonical_image)
        if map_hint:
            base_name = f"{base_name}_{map_hint}"
        new_filename = unique_filename(output_dir, base_name, ext)
        dst_path = os.path.join(output_dir, new_filename)

        if dry_run:
            log_lines.append(f"DRY_COPY_CANONICAL: {orig_path} -> {dst_path}")
            copied_map[norm_path] = (new_filename, canonical_name)
            idx += 1
            continue

        try:
            shutil.copy2(orig_path, dst_path)
            log_lines.append(f"COPIED_CANONICAL: {orig_path} -> {dst_path}")
            try:
                canonical_image.name = new_filename
                if bpy.data.is_saved:
                    canonical_image.filepath = bpy.path.relpath(dst_path)
                else:
                    canonical_image.filepath = dst_path
                try:
                    canonical_image.reload()
                except Exception:
                    pass
                copied_map[norm_path] = (new_filename, canonical_image.name)
                log_lines.append(f"UPDATED_CANONICAL_IMAGE: datablock '{canonical_image.name}' now points to '{dst_path}'")
            except ReferenceError:
                log_lines.append(f"ERROR_UPDATE_CANONICAL_IMAGE_REFREMOVED: canonical image removed while updating")
            except Exception as e:
                log_lines.append(f"ERROR_UPDATE_CANONICAL_IMAGE: {canonical_image.name} -> {e}")
        except Exception as e:
            log_lines.append(f"ERROR_COPY_CANONICAL: {orig_path} -> {dst_path} : {e}")

        idx += 1

    # FOURTH PHASE: build material_report entries (status per material/map)
    for m in target_mats:
        mat_name = m.name
        nodes_map = get_all_image_nodes_for_mat(m)
        if not nodes_map:
            log_lines.append(f"SKIP_NO_IMAGES: Material '{mat_name}' has no image nodes.")
            material_report["materials"].append({"material": mat_name, "maps": {}, "signature": mat_signatures.get(id(m), {}).get("signature", "UNKNOWN")})
            continue

        mat_entry = {"material": mat_name, "maps": {}, "signature": mat_signatures.get(id(m), {}).get("signature", "UNKNOWN")}
        for mapkey, img_node in nodes_map.items():
            try:
                image = img_node.image
            except ReferenceError:
                mat_entry["maps"][mapkey] = {"status": "MISSING_DB", "info": "image datablock removed"}
                continue
            if getattr(image, "packed_file", None) is not None:
                mat_entry["maps"][mapkey] = {"status": "PACKED", "image_name": image.name}
                continue
            try:
                orig_path = bpy_abspath(image.filepath)
            except Exception:
                orig_path = None
            if not orig_path or not os.path.exists(orig_path):
                mat_entry["maps"][mapkey] = {"status": "MISSING", "image_name": image.name, "source": orig_path}
                continue
            norm = os.path.normpath(orig_path)
            if norm in copied_map:
                dst_filename, canonical_name = copied_map[norm]
                mat_entry["maps"][mapkey] = {"status": "COPIED_OR_REUSED", "dst": dst_filename, "image_datablock": canonical_name}
            else:
                # try match via hash
                h = md5_for_image(image)
                matched = False
                if h:
                    for k_norm, (fname, canon_name) in copied_map.items():
                        try:
                            canon_obj = bpy.data.images.get(canon_name)
                            if canon_obj and md5_for_image(canon_obj) == h:
                                mat_entry["maps"][mapkey] = {"status": "COPIED_OR_REUSED_BY_HASH", "dst": fname, "image_datablock": canon_obj.name}
                                matched = True
                                break
                        except Exception:
                            pass
                if not matched:
                    if norm in canonical_map:
                        mat_entry["maps"][mapkey] = {"status": "PLANNED", "info": "planned during dry-run or skipped copy", "image_name": image.name}
                    else:
                        mat_entry["maps"][mapkey] = {"status": "UNCHANGED", "image_name": image.name}
        material_report["materials"].append(mat_entry)

    # FIFTH PHASE: UV rename/remove pass (if requested)
    objects_in_scope = []
    if scope == 'SELECTED':
        objects_in_scope = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    else:
        objects_in_scope = [o for o in bpy.data.objects if o.type == 'MESH']

    meshes_in_scope = {o.data for o in objects_in_scope if hasattr(o, "data") and o.data is not None}
    used_uv_names = set()
    for (m, img_node, image, norm, status) in image_entries:
        try:
            uv = find_uv_map_for_image_node(img_node)
            if uv:
                used_uv_names.add(uv)
        except Exception:
            pass

    uv_logs = []
    if remove_unused_uvs or rename_used_uvs:
        for mesh in list(meshes_in_scope):
            try:
                uv_layers = mesh.uv_layers
                if not uv_layers:
                    continue
                for l in uv_layers:
                    original_name = l.name
                    if original_name in used_uv_names and rename_used_uvs:
                        if tag_clean:
                            new_name = f"aegon_{tag_clean}_{original_name}"
                        else:
                            new_name = f"aegon_{original_name}"
                        if new_name != original_name:
                            if dry_run:
                                uv_logs.append(f"DRY_RENAME_UV: Mesh '{getattr(mesh,'name','<mesh>')}' layer '{original_name}' -> '{new_name}'")
                            else:
                                try:
                                    l.name = new_name
                                    uv_logs.append(f"RENAMED_UV: Mesh '{getattr(mesh,'name','<mesh>')}' layer '{original_name}' -> '{new_name}'")
                                except Exception as e:
                                    uv_logs.append(f"ERROR_RENAME_UV: Mesh '{getattr(mesh,'name','<mesh>')}' layer '{original_name}' -> {e}")
                if remove_unused_uvs:
                    remaining_layers = list(mesh.uv_layers)
                    for l in list(remaining_layers):
                        orig_name = l.name
                        check_name = orig_name
                        if orig_name.startswith("aegon_"):
                            parts = orig_name.split("_")
                            if tag_clean:
                                suffix = "_".join(parts[2:]) if len(parts) > 2 else "_".join(parts[1:])
                            else:
                                suffix = "_".join(parts[1:]) if len(parts) > 1 else parts[0]
                            if suffix:
                                check_name = suffix
                        if check_name not in used_uv_names:
                            if len(mesh.uv_layers) <= 1:
                                uv_logs.append(f"SKIP_DELETE_ONLY_UV: Mesh '{getattr(mesh,'name','<mesh>')}' layer '{orig_name}' (only UV left)")
                                continue
                            if dry_run:
                                uv_logs.append(f"DRY_DELETE_UV: Mesh '{getattr(mesh,'name','<mesh>')}' layer '{orig_name}' would be removed (unused)")
                            else:
                                try:
                                    mesh.uv_layers.remove(l)
                                    uv_logs.append(f"DELETED_UV: Mesh '{getattr(mesh,'name','<mesh>')}' layer '{orig_name}' removed (unused)")
                                except Exception as e:
                                    uv_logs.append(f"ERROR_DELETE_UV: Mesh '{getattr(mesh,'name','<mesh>')}' layer '{orig_name}' -> {e}")
            except Exception as e:
                uv_logs.append(f"ERROR_PROCESS_MESH_UV: Mesh '{getattr(mesh,'name','<mesh>')}' -> {e}")

    log_lines.extend(uv_logs)

    # write logs and material report json
    write_log(output_dir, log_lines)
    report_path = os.path.join(output_dir, "material_report.json")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(material_report, f, indent=2, ensure_ascii=False)
    except Exception as e:
        write_log(output_dir, [f"ERROR_WRITE_REPORT: {e}"])

    print(f"Prepare YTD + material report completed. (dry_run={dry_run}) Output: {output_dir}")
    return output_dir

# -----------------------------
# Addon Properties & UI (with UV options)
# -----------------------------
class AegonProperties(bpy.types.PropertyGroup):
    remove_unused: bpy.props.BoolProperty(
        name="Remove Unused Materials",
        description="Sahnede kullanılmayan materyalleri siler (GLOBAL).",
        default=True
    )
    merge_duplicate: bpy.props.BoolProperty(
        name="Merge Duplicate Materials",
        description="Aynı materyali (deep node equality ile) birleştirir.",
        default=True
    )
    use_strict: bpy.props.BoolProperty(
        name="Use Strict (Deep Node Equality)",
        description="Node-tree seviyesinde kesin eşitlik kullan (daha güvenlidir).",
        default=True
    )
    rename_distinct: bpy.props.BoolProperty(
        name="Rename Distinct Materials",
        description="Birleştirilmeyen materyallere aegon_mat_... isimleri atar.",
        default=False
    )
    remove_slots: bpy.props.BoolProperty(
        name="Remove Unused Slots per Object",
        description="Objelerde polylere bağlı olmayan materyal slotlarını siler.",
        default=True
    )
    multi_object_opt: bpy.props.BoolProperty(
        name="Multi-Object Optimization",
        description="Farklı objelerde aynı materyal referanslarını tekleştirir.",
        default=False
    )
    ytd_prep: bpy.props.BoolProperty(
        name="Prepare YTD Export",
        description="Texture dosyalarını kopyalar, yeniden adlandırır ve node'ları günceller.",
        default=True
    )
    apply_scope: bpy.props.EnumProperty(
        name="Apply To",
        description="İşlemleri hangi alana uygulamak istiyorsun?",
        items=[('ALL', "All", "Apply to entire scene"), ('SELECTED', "Selected", "Apply to selected objects only")],
        default='ALL'
    )
    output_dir: bpy.props.StringProperty(
        name="Output Folder",
        description="Texture kopyalarının konulacağı ana klasör (AegonTools_Output alt klasör oluşturulur). Leave empty for blend file directory.",
        default="",
        subtype='DIR_PATH'
    )
    custom_tag: bpy.props.StringProperty(
        name="Custom Tag (insert before map type)",
        description="Dosya adına eklenecek özel etiket. Örnek: MLO_Adi veya mapname.",
        default=""
    )
    dry_run: bpy.props.BoolProperty(
        name="Dry Run (Preview Only)",
        description="Dry Run aktifse gerçek değişiklik yapılmaz; yapılacaklar log'a yazılır.",
        default=True
    )
    create_backup: bpy.props.BoolProperty(
        name="Create Backup (.blend copy)",
        description="Çalıştırmadan önce bir .blend yedeği oluştur.",
        default=False
    )
    use_custom_order: bpy.props.BoolProperty(
        name="Use Custom Operation Order",
        description="İşlem sırasını elle belirle (ilk iki adımı seç).",
        default=False
    )
    order_first: bpy.props.EnumProperty(
        name="First Operation",
        description="Öncelikli olarak çalıştırılacak işlem.",
        items=[
            ('REMOVE_UNUSED', "Remove Unused", ""),
            ('MERGE_DUP', "Merge Duplicate", ""),
            ('REMOVE_SLOTS', "Remove Slots", ""),
            ('MULTI_OPT', "Multi-Object Opt", ""),
            ('YTD_PREP', "Prepare YTD", ""),
        ],
        default='MERGE_DUP'
    )
    order_second: bpy.props.EnumProperty(
        name="Second Operation",
        description="İkinci olarak çalıştırılacak işlem.",
        items=[
            ('REMOVE_UNUSED', "Remove Unused", ""),
            ('MERGE_DUP', "Merge Duplicate", ""),
            ('REMOVE_SLOTS', "Remove Slots", ""),
            ('MULTI_OPT', "Multi-Object Opt", ""),
            ('YTD_PREP', "Prepare YTD", ""),
        ],
        default='YTD_PREP'
    )
    # UV options
    remove_unused_uvs: bpy.props.BoolProperty(
        name="Remove Unused UV layers",
        description="Hedef scope içindeki mesh'lerde kullanılmayan UV katmanlarını siler (dry-run ile test et).",
        default=False
    )
    rename_used_uvs: bpy.props.BoolProperty(
        name="Rename Used UV layers (add aegon prefix)",
        description="Kullanılan UV katmanlarına aegon_ öneki ekler (veya custom tag ile aegon_<tag>_...).",
        default=False
    )

class AEGON_PT_MaterialOptimizerPanel(bpy.types.Panel):
    bl_label = "Aegon Material Optimizer"
    bl_idname = "AEGON_PT_material_optimizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aegon Tools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.aegon_props

        layout.label(text="Material Optimization Options")
        layout.prop(props, "apply_scope")
        layout.separator()

        col = layout.column(align=True)
        col.prop(props, "remove_unused")
        col.label(text="— Sahnede hiç kullanılmayan materyalleri siler. (GLOBAL operation)", icon='INFO')

        col.prop(props, "merge_duplicate")
        col.label(text="— Aynı materyali (deep node equality ile) birleştirir.", icon='INFO')

        col.prop(props, "use_strict")
        col.label(text="— Deep node equality: en küçük node farkını bile algılar ve birleştirmez.", icon='INFO')

        col.prop(props, "rename_distinct")
        col.label(text="— Birleştirilmeyen materyallere aegon_mat_... isimleri atar.", icon='INFO')

        col.prop(props, "remove_slots")
        col.label(text="— Objelerde polylere bağlı olmayan materyal slotlarını kaldırır.", icon='INFO')

        col.prop(props, "multi_object_opt")
        col.label(text="— Çoklu obje optimizasyonu (merge tekrarı).", icon='INFO')

        col.prop(props, "ytd_prep")
        col.label(text="— Tüm image node'ları için texture kopyalama & node güncelleme.", icon='INFO')

        layout.separator()
        layout.prop(props, "custom_tag")
        layout.label(text="— Custom tag eklenecek: aegon_<idx>_<tag>_<maptype>.", icon='INFO')
        layout.prop(props, "output_dir")
        layout.label(text="— Output klasör seçimi.", icon='INFO')

        layout.separator()
        layout.prop(props, "dry_run")
        layout.label(text="— Dry Run: gerçek değişiklik yapmadan rapor üretir (tavsiye).", icon='INFO')
        layout.prop(props, "create_backup")
        layout.label(text="— Create Backup: .blend yedeği alır.", icon='INFO')

        layout.separator()
        layout.label(text="UV options (optional):")
        layout.prop(props, "rename_used_uvs")
        layout.label(text="— Kullanılan UV katmanlarına aegon_ öneki ekler.", icon='INFO')
        layout.prop(props, "remove_unused_uvs")
        layout.label(text="— Kullanılmayan UV katmanlarını kaldırır (dikkatli ol).", icon='INFO')

        layout.separator()
        layout.prop(props, "use_custom_order")
        if props.use_custom_order:
            row = layout.row(align=True)
            row.prop(props, "order_first")
            row.prop(props, "order_second")
            layout.label(text="— Custom order: önce First sonra Second; aynı seçim tekrarlanırsa atlanır.", icon='INFO')

        layout.separator()
        layout.operator("aegon.run_optimizer", text="Run Optimizer (Apply Selected Settings)")

# -----------------------------
# Runner
# -----------------------------
def _run_operation_by_key(key, props, scope, dry, ran_ops, output_dir):
    if key in ran_ops:
        return []
    log = []
    if key == 'REMOVE_UNUSED':
        if props.remove_unused:
            log.append("Running Remove Unused Materials")
            remove_unused_materials(dry_run=dry)
            ran_ops.add(key)
    elif key == 'MERGE_DUP':
        if props.merge_duplicate:
            log.append("Running Merge Duplicate Materials")
            merge_duplicate_materials(scope=scope, use_strict=props.use_strict, dry_run=dry)
            ran_ops.add(key)
    elif key == 'REMOVE_SLOTS':
        if props.remove_slots:
            log.append("Running Remove Unused Slots per Object")
            remove_unused_slots_per_object(scope=scope, dry_run=dry)
            ran_ops.add(key)
    elif key == 'MULTI_OPT':
        if props.multi_object_opt:
            log.append("Running Multi-Object Optimization")
            multi_object_optimization(scope=scope, use_strict=props.use_strict, dry_run=dry)
            ran_ops.add(key)
    elif key == 'YTD_PREP':
        if props.ytd_prep:
            log.append("Running Prepare YTD Export and Material Report")
            prepare_ytd_export_and_material_report(
                scope=scope,
                base_output_dir=output_dir,
                custom_tag=props.custom_tag,
                dry_run=dry,
                rename_distinct=props.rename_distinct,
                remove_unused_uvs=props.remove_unused_uvs,
                rename_used_uvs=props.rename_used_uvs
            )
            ran_ops.add(key)
    return log

class AEGON_OT_RunOptimizer(bpy.types.Operator):
    bl_idname = "aegon.run_optimizer"
    bl_label = "Run Material Optimizer"

    def execute(self, context):
        props = context.scene.aegon_props
        scope = 'SELECTED' if props.apply_scope == 'SELECTED' else 'ALL'
        dry = props.dry_run
        output_dir = props.output_dir if props.output_dir else ""

        if props.create_backup and not dry:
            bpath = save_backup_copy()
            if bpath:
                self.report({'INFO'}, f"Aegon Tools: Backup created -> {bpath}")
        try:
            bpy.ops.ed.undo_push(message="Aegon Tools - before optimization")
        except:
            pass

        ran_ops = set()
        if props.use_custom_order:
            _run_operation_by_key(props.order_first, props, scope, dry, ran_ops, output_dir)
            _run_operation_by_key(props.order_second, props, scope, dry, ran_ops, output_dir)

        default_sequence = ['REMOVE_UNUSED','MERGE_DUP','REMOVE_SLOTS','MULTI_OPT','YTD_PREP']
        for key in default_sequence:
            if key in ran_ops:
                continue
            _run_operation_by_key(key, props, scope, dry, ran_ops, output_dir)

        try:
            bpy.ops.ed.undo_push(message="Aegon Tools - after optimization")
        except:
            pass

        self.report({'INFO'}, "Aegon Tools: Optimization finished. Check AegonTools_Output/material_report.json and AegonTools_log.txt")
        return {'FINISHED'}

# -----------------------------
# Register
# -----------------------------
classes = (
    AegonProperties,
    AEGON_PT_MaterialOptimizerPanel,
    AEGON_OT_RunOptimizer,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aegon_props = bpy.props.PointerProperty(type=AegonProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "aegon_props"):
        del bpy.types.Scene.aegon_props

if __name__ == '__main__':
    register()