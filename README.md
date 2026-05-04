<div align="center">

<img src="https://cdn.aegondesign.com/wysiwyg/1211819/699bd04a73ef7a133b7ff7782e11790c65dbfed5.webp" width="140" />

# 🏛️ Aegon-3D-FiveM-Dev-Kit

**Industrial-grade infrastructure, high-leverage Blender addons, and professional presentation tools for MLO creators.**

[![Latest Release](https://img.shields.io/github/v/release/AegonDesign/Aegon-3D-FiveM-Dev-Kit?style=for-the-badge&color=FF8C00)](https://github.com/AegonDesign/Aegon-3D-FiveM-Dev-Kit/releases)
[![Tebex](https://img.shields.io/badge/Tebex-Full_Pack-FF8C00?style=for-the-badge&logo=tebex&logoColor=white)](https://fivem.aegondesign.com/package/7263327)
[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.aegondesign.com)
[![FiveM](https://img.shields.io/badge/FiveM-Native_Ready-blue?style=for-the-badge&logo=fivem&logoColor=white)](https://fivem.net)

---

> "I know exactly what it feels like to have a vision but lack the tools or guidance to bring it to life. We have all been at that starting line... My goal is to give you the leverage to cross that line with speed." 🌟

</div>

## 🛠️ The Aegon Engine (Blender Addons)

This kit is a high-performance 3D pipeline designed to eliminate technical overhead and maximize artistic throughput.

| Tool | Technical Core (Hard Analysis) | Production Impact |
| :--- | :--- | :--- |
| **🟢 Aegon Boolean PRO** | **Parametric Modifier Manager & Slice Engine.** | Non-destructive cuts with auto-bevel/clean. |
| **🧠 Smart UV Stack** | **Geometry Perimeter & Vertex Pattern Matching.** | Instant stacking for 100+ identical objects. |
| **📉 Material Optimizer** | **MD5-based Image Content Deduplication.** | Merges thousands of duplicate textures by hash. |
| **🚀 Poly Optimizer** | **4-Phase Sequence: Merge -> Dissolve -> Tris -> Clean.** | Guarantees GTA V engine-ready mesh topology. |
| **🔧 UV Fixer & Clamp** | **Upstream Node-Tree Spec/Roughness Clamping.** | Eliminates "Neon Glow" & overexposure bugs. |
| **📦 Aegon Box Map** | **Dynamic Scale Normalization & Axis Correction.** | Flawless texture scaling across variable scales. |
| **🎯 Perfect Align** | **Coordinate-locked Face-to-UV vertex snapping.** | Millimeter-perfect trim-sheet alignment. |

---

## 🔬 Technical Deep Dive: Why Aegon?

Most tools just "click and hope." Aegon tools use **Deterministic Logic** to ensure your MLOs never crash a player's game.

### 1. MD5 Content Hashing (Material Optimizer)
Instead of checking filenames (which can be wrong), we read the raw binary data of every texture. If two textures are identical, we merge them.
*   **Result:** Reduced .ytd size, lower VRAM usage, and zero redundant draw calls.

### 2. The 4-Phase Geometry Pipeline (Poly Optimizer)
We don't just "decimate." We follow a strict engineering sequence:
1.  **Merge:** Fixes overlapping vertices from messy imports.
2.  **Dissolve:** Removes useless edges that don't contribute to the shape.
3.  **Triangulate:** Forces the engine-required 3-point face structure.
4.  **Delete Loose:** Purges "ghost geometry" that causes culling bugs.

### 3. Parametric Boolean System (Aegon Boolean PRO)
Our boolean system manages a dedicated `AEGON_Cutters` collection. It automatically applies **Weighted Normals** and **Bevel** modifiers post-operation to ensure perfect shading even on low-poly meshes.

---

## 💻 1. FiveM Showcase Server (Fully Native)
Unlike heavy, dependency-bloated packs, this server is **Pure Native**.

*   **Zero Dependencies:** No QB-Core, ESX, or vRP required. 🍃
*   **Performance Baseline:** Test MLOs in an environment that reflects true game performance.
*   **Aegon Pre-set:** Pre-configured with 8 custom scripts for fly-throughs and lighting tests.

---

## 📄 2. Forum Presentation Guide
A professional solution for creators who want their work to stand out. 🎁

*   **Universal Support:** Includes HTML, Markdown (Cfx.re), and BBCode versions.
*   **Aesthetic First:** Premium dark-themed design to increase conversion rates on stores.
*   **Easy Integration:** See [aegon_forum_template.html](aegon_forum_template.html) for the full guide.

---

## 📂 Repository Structure

```text
├── Aegon Boolean.py            # Advanced Parametric Boolean System.
├── Aegon Poly Optimizer.py     # 4-Phase Mesh Optimization Pipeline.
├── Aegon Texture - UV Fixer.py # Upstream Node-Tree Repair & Clamping.
├── Aegon UV.py                 # Core UV Manipulation & Perfect Align.
├── Material Optimizer.py       # MD5 Hash-based Asset Deduplication.
├── aegon_forum_template.html   # Universal Presentation Guide (HTML/MD).
└── aegon_blender_add-on_pack.zip # Final Production Bundle.
```

---

## ⚖️ Your Creativity, Your Profit
You are **100% FREE TO SELL** anything you produce (Maps, MLOs, etc.) using these tools. I claim no rights or royalties. Your success is the project's success. 🤝

---

## 💰 Support the Vision

*   **Free Access:** Core tools are open-source right here. 🔓
*   **Full Server Pack (€20):** Get the ready-to-run showcase server at [Tebex](https://fivem.aegondesign.com/package/7263327). 🪙

<div align="center">

[Website](https://fivem.aegondesign.com) • [Discord](https://discord.aegondesign.com) • [Youtube](https://youtube.com/aegondesign) • [Showcase](https://play.aegondesign.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=FF8C00&height=60&section=footer" width="100%" />

</div>
