import zipfile
import os

def pack_aegon():
    output_filename = "aegon_blender_add-on_pack.zip"
    scripts_to_include = [
        "Aegon Boolean.py",
        "Aegon Poly Optimizer.py",
        "Aegon Texture - UV Fixer.py",
        "Aegon UV.py",
        "Material Optimizer.py"
    ]
    
    print(f"🚀 Starting Aegon Release Packaging: {output_filename}")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for script in scripts_to_include:
            if os.path.exists(script):
                print(f"📦 Adding: {script}")
                zip_file.write(script)
            else:
                print(f"⚠️ Warning: {script} not found, skipping.")
                
    print(f"\n✅ Packaged successfully! Created {output_filename}")

if __name__ == "__main__":
    pack_aegon()
