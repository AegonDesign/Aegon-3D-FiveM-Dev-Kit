<div align="center">

<img src="https://cdn.aegondesign.com/wysiwyg/1211819/699bd04a73ef7a133b7ff7782e11790c65dbfed5.webp" width="140" />

# 🏛️ Aegon-3D-FiveM-Dev-Kit

**Essential tools, Blender addons, and infrastructure for FiveM MLO creators.**

[![Release](https://img.shields.io/badge/RELEASE-AEGON-222?style=for-the-badge)](https://github.com/AegonDesign/Aegon-3D-FiveM-Dev-Kit/releases)
[![Discord](https://img.shields.io/badge/DISCORD-COMMUNITY-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.aegondesign.com)
[![Tebex](https://img.shields.io/badge/Tebex-Full_Pack-FF8C00?style=for-the-badge&logo=tebex&logoColor=white)](https://fivem.aegondesign.com/package/7263327)

---

> "I know exactly what it feels like to have a vision but lack the tools or guidance to bring it to life. We have all been at that starting line. This package is not a \"blessing from above\"; it is simply a toolkit prepared by a friend who has walked the same paths as you and wants to see you succeed. My only wish is for you to showcase your talent without being held back by technical hurdles. 🌟"

</div>

## 🛠️ The Aegon Engine (Blender Addons)

This kit isn't just a collection of scripts; it's a high-performance pipeline designed to eliminate the tedious parts of MLO creation.

| Tool | What it does | How to use it best |
| :--- | :--- | :--- |
| **🟢 Aegon Boolean PRO** | Automates clean cuts & bevels. | Use it for doors/windows; it handles the cleanup for you. |
| **📦 Aegon UVW Box Map** | Dynamic scale normalization & axis-correction. | No texture stretching on MLO walls. |
| **🎯 Perfect Align** | Face-to-UV vertex snapping & stable rotation. | Professional trim-sheet alignment. |
| **🧠 Smart UV Stack** | Stacks identical UV islands instantly. | Select identical objects/faces and run to save texture space. |
| **📉 Material Optimizer** | Merges duplicate materials via content. | Run before export to reduce your `.ytd` size. |
| **🚀 Poly Optimizer** | Cleans geometry for GTA V engine. | Fixes vertex overlaps & loose geometry. |
| **🔧 UV Fixer & Clamp** | Fixes lighting & exposure issues. | Eliminates "Neon Glow" & overexposure bugs. |

---

## 📖 Learning the Workflow: From Manual to Automated

This repository is designed to help you move faster. Follow these essential steps for a professional MLO:

| # | Phase | Process / Objective |
| :--- | :--- | :--- |
| **1** | **Mesh Cleanup** | **Poly Optimizer** automatically merges overlapping vertices and ensures everything is triangulated for the game engine. <br /> *Tip: Run this as your final step before exporting.* |
| **2** | **Texture Optimization** | **Material Optimizer** checks the actual data of your images (MD5 hashing). If it finds a match, it merges them to keep your MLO light and fast. |
| **3** | **Lighting & Exposure** | **UV Fixer** clamps Spec/Roughness values to industry standards so your lighting stays consistent. |
| **4** | **Consistent Scaling** | **Box Map Tool** normalizes the scale across all axes so your textures align perfectly in real-world scale. |
| **5** | **Smart UV Stacking** | **Smart UV Stack** stacks their UVs to give you higher resolution using less memory. |
| **6** | **"Pro" Boolean Workflow** | **Aegon Boolean** system uses a non-destructive approach with "Weighted Normals" to keep your shading perfectly smooth. |

---

## 💻 1. FiveM Showcase Server (Fully Native)
Unlike the heavy and dependent packs on the market, this server is built on a completely **Native (Pure)** structure.

*   **Zero Dependencies:** No QB-Core, ESX, or vRP required. 🍃
*   **Native Optimization:** Test MLOs in an environment that reflects true game performance.
*   **Pre-configured:** Optimized for MLO testing and fly-throughs.

---

## 📄 2. Cfx.re Forum Template
A practical "copy-paste" solution for those who say *"My time is valuable, I just want to produce."* 🎁

* **Effortless Presentation:** Just place your images and text.
* **Clean and Stylish:** Look organized and professional on forums.

---

## 📂 Files in this Kit

```text
├── Aegon Boolean.py            # Advanced Parametric Boolean System.
├── Aegon Poly Optimizer.py     # 4-Phase Mesh Optimization Pipeline.
├── Aegon Texture - UV Fixer.py # Upstream Node-Tree Repair & Clamping.
├── Aegon Texture - UV Fixer.py # Upstream Node-Tree Repair & Clamping.
├── Aegon UV.py                 # Core UV Manipulation & Perfect Align.
├── Material Optimizer.py       # MD5 Hash-based Asset Deduplication.
├── aegon_cfxre_template.html   # Universal Presentation Guide (HTML/MD).
└── aegon_blender_add-on_pack.zip # Final Production Bundle.
```

---

## ⚖️ The Talent is Yours, The Profit is Yours
You are **100% FREE TO SELL** anything you produce (Maps, MLOs, etc.) using these tools. I claim no rights or royalties over your artistic work. Your creativity, your business. 🤝

---

## 💰 Access and Support

*   **Free Access:** Blender Addons and Forum Template are free right here. 🔓
*   **Support (€20):** If you'd like to support the project and get the ready-to-use server pack, visit [Tebex](https://fivem.aegondesign.com/package/7263327). 🪙

<div align="center">

[Website](https://fivem.aegondesign.com) • [Discord](https://discord.aegondesign.com) • [Youtube](https://youtube.com/aegondesign) • [Showcase](https://play.aegondesign.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=FF8C00&height=60&section=footer" width="100%" />

</div>
