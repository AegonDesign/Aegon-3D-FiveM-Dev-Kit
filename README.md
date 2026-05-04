<div align="center">

<img src="https://cdn.aegondesign.com/wysiwyg/1211819/699bd04a73ef7a133b7ff7782e11790c65dbfed5.webp" width="120" />

# 🏛️ Aegon 3D - FiveM Development Kit

**A collection of tools to automate manual 3D workflows and accelerate MLO creation.**

[![Latest Release](https://img.shields.io/github/v/release/AegonDesign/Aegon-3D-FiveM-Dev-Kit?style=for-the-badge&color=222)](https://github.com/AegonDesign/Aegon-3D-FiveM-Dev-Kit/releases)
[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.aegondesign.com)
[![FiveM](https://img.shields.io/badge/FiveM-Reference-blue?style=for-the-badge&logo=fivem&logoColor=white)](https://fivem.net)

---

> "I know exactly what it feels like to have a vision but lack the tools or guidance to bring it to life. We have all been at that starting line. This package is not a \"blessing from above\"; it is simply a toolkit prepared by a friend who has walked the same paths as you and wants to see you succeed. My only wish is for you to showcase your talent without being held back by technical hurdles. 🌟"

</div>

## 🛠️ Addon Collection & Usage Guide

These tools were built to solve common MLO production bottlenecks. Use this guide to understand how to apply them to your workflow.

| Tool Name | What it does | How to use it best |
| :--- | :--- | :--- |
| **🟢 Boolean System** | Automates clean cuts & bevels. | Use it for doors/windows; it handles the cleanup for you. |
| **🧠 Smart UV Stack** | Stacks identical UV islands instantly. | Select identical objects/faces and run to save texture space. |
| **📉 Material Optimizer** | Merges duplicate materials via content. | Run before export to reduce your `.ytd` size and improve FPS. |
| **🚀 Poly Optimizer** | Cleans geometry for GTA V engine. | Use after modeling to fix vertex overlaps & loose geometry. |
| **🔧 UV Fixer & Clamp** | Fixes lighting & exposure issues. | Run if your textures look too bright or "glowy" in-game. |
| **📦 Box Map Tool** | Normalizes texture scales on axes. | Best for walls/floors to ensure seamless texture tiling. |
| **🎯 Perfect Align** | Snaps faces to UV coordinates. | Use for trim-sheets to get perfect pixel alignment. |

---

## 📖 Learning the Workflow: From Manual to Automated

This repository is designed to help you move faster. Instead of spending hours on technical cleanup, follow these steps:

### 1. Mesh Cleanup (The Poly Pipeline)
Don't worry about messy geometry. The **Poly Optimizer** automatically follows a cleaning sequence to prepare models for the engine:
*   It merges overlapping vertices.
*   It removes useless geometry.
*   It ensures everything is triangulated for the game engine.
*   *Tip: Run this as your final step before exporting.*

### 2. Texture Optimization (The Material Engine)
Duplicate textures are the main cause of lag. The **Material Optimizer** checks the actual data of your images (not just names). If it finds a match, it merges them into one. 
*   *Goal: Keep your MLO light and fast for every player.*

### 3. Lighting & Exposure (UV Fixer)
If your model looks different in-game than in Blender, it's often due to "Spec/Roughness" values. The **UV Fixer** clamps these values to industry standards so your lighting stays consistent.

---

## 💻 Showcase & Presentation Tools

### 1. Native Showcase Server
A clean environment to test your MLOs without the weight of heavy frameworks like QB or ESX. Just you and your creation.

### 2. Presentation Template
A simple guide to presenting your work. Includes HTML and Markdown formats for forums. (See [aegon_forum_template.html](aegon_forum_template.html))

---

## 📂 Files in this Kit

```text
├── Aegon Boolean.py            # Clean cut system.
├── Aegon Poly Optimizer.py     # Automated cleanup pipeline.
├── Aegon Texture - UV Fixer.py # Lighting & UV repair.
├── Aegon UV.py                 # Mapping & Alignment tools.
├── Material Optimizer.py       # Asset deduplication script.
└── aegon_forum_template.html   # Universal presentation guide.
```

---

## ⚖️ License & Philosophy
You are **100% free to sell** anything you create using these tools. I claim no rights. I just want to see the community grow and create better MLOs. 🤝

<div align="center">

[Community Discord](https://discord.aegondesign.com) • [YouTube Tutorials](https://youtube.com/aegondesign)

<img src="https://capsule-render.vercel.app/api?type=waving&color=333&height=60&section=footer" width="100%" />

</div>
