bl_info = {
    "name": "Aegon Boolean System PRO",
    "author": "Aegon Design",
    "version": (7, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N Panel > Aegon Tools",
    "description": "Professional Boolean Dev Kit | TR/EN | Smart Engine | GitHub Free",
    "category": "Object",
}

import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import (
    EnumProperty, BoolProperty, PointerProperty,
    FloatVectorProperty, FloatProperty, StringProperty,
)


# ══════════════════════════════════════════════════════════════════════════════
#  LOCALIZATION
# ══════════════════════════════════════════════════════════════════════════════

_TR = {
    # Bölüm başlıkları
    "sec_ops":       "Boolean İşlemleri",
    "sec_settings":  "Gelişmiş Ayarlar",
    "sec_manage":    "Yönetim",
    "sec_stack":     "Modifier Yöneticisi",
    "sec_info":      "Nesne Bilgisi",

    # Butonlar
    "apply_all":     "Hepsini Uygula",
    "op_difference": "Fark (Difference)",
    "op_union":      "Birleşim (Union)",
    "op_intersect":  "Kesişim (Intersect)",
    "op_slice":      "Dilimle (Slice)",
    "live_preview":  "Canlı Önizleme",
    "smart_cleanup": "Akıllı Temizlik",
    "show_cutters":  "Kesicileri Göster",
    "wire_toggle":   "Kafes Görünüm",
    "clear_all":     "Tüm Boolleri Temizle",
    "del_cutters":   "Kesicileri Sil",
    "apply_color":   "Rengi Tüm Kesicilere Uygula",
    "lang_btn":      "EN",
    # Yeni Özellikler
    "add_cube":      "Küp Ekle (Cube)",
    "add_cyl":       "Silindir Ekle (Cylinder)",
    "add_sph":       "Küre Ekle (Sphere)",
    "array_cut":     "Dizi Kesici (Array)",
    "auto_mirror":   "Simetri (Auto Mirror)",
    "array_count":   "Dizi Sayısı",
    "array_offset":  "Dizi Aralığı",
    "array_radial":  "Dairesel Dizi (Radial)",

    # Ayar isimleri
    "solver":        "Çözücü",
    "auto_apply":    "Otomatik Uygula",
    "auto_hide":     "Kesicileri Otomatik Gizle",
    "use_col":       "Kesici Koleksiyonu Kullan",
    "show_list":     "Modifier Listesi",
    "wire_color":    "Tel Rengi",
    "threshold":     "Çakışma Eşiği",
    "flip":          "Kesiciyi Ters Çevir",
    "to_top":        "En Üste Taşı",
    "prefix":        "Modifier Adı Öneki",
    "merge":         "Akıllı Birleştirme",
    "merge_dist":    "Birleştirme Mesafesi",
    "smooth":        "Smooth Shade Uygula",
    "wnormals":      "Weighted Normals Ekle",
    "use_bevel":     "Bevel Ekle",
    "bevel_amt":     "Bevel Miktarı",
    "bevel_seg":     "Bevel Segmanları",
    # Ayçözüm
    "solver_exact":  "Hassas (Exact)",
    "solver_fast":   "Hızlı (Fast)",
    # Ayırtıcı etiketler
    "algo_lbl":      "── Algoritma ──",
    "post_lbl":      "── Uygulama Sonrası ──",
    "visual_lbl":    "── Görsel ──",
    "core_lbl":      "── Temel ──",
    "solver_lbl":    "Çözücü:",

    # Bilgi
    "no_active":     "Aktif nesne yok",
    "obj":           "Nesne",
    "bool_count":    "Boolean Sayısı",
    "no_mods":       "— modifier yok —",
    "version":       "v6.0  ·  Aegon Design",

    # Tooltips
    "tip_difference": (
        "DIFFERENCE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Seçili kesici nesneleri aktif meshden çıkarır.\n"
        "\n"
        "Kullanım:\n"
        "  1) Kesici(leri) seç\n"
        "  2) Shift + Hedef mesh → aktif yap\n"
        "  3) Difference'a bas\n"
        "\n"
        "Birden fazla kesici aynı anda uygulanabilir."
    ),
    "tip_union": (
        "UNION\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kesicileri aktif mesh ile birleştirerek tek solid yapar.\n"
        "\n"
        "İdeal kullanım:\n"
        "  • Hard-surface detay ekleme\n"
        "  • Birden fazla parçayı tek geometriye dönüştürme"
    ),
    "tip_intersect": (
        "INTERSECT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aktif mesh ile kesicinin ÇAKIŞAN bölgesini korur,\n"
        "geri kalanını siler.\n"
        "\n"
        "İdeal kullanım:\n"
        "  • Geometry kırpma\n"
        "  • Maske oluşturma\n"
        "  • Ters kalıp alma"
    ),
    "tip_slice": (
        "SLICE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aktif meshini kesici boyunca iki ayrı parçaya böler.\n"
        "\n"
        "  Parça A → Orijinal nesne   (DIFFERENCE)\n"
        "  Parça B → Otomatik kopya   (INTERSECT)\n"
        "\n"
        "Her iki parça orijinal malzeme ve UV'yi korur."
    ),
    "tip_apply_all": (
        "HEPSİNİ UYGULA\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aktif nesnedeki TÜM Boolean modifier'ları kalıcı uygular.\n"
        "\n"
        "⚠  UYARI: Geometri kalıcı değişir!\n"
        "Uygulamadan önce Ctrl+D ile yedek al."
    ),
    "tip_live": (
        "CANLI ÖNİZLEME\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aktif nesnedeki TÜM Boolean modifier'ların\n"
        "viewport görünürlüğünü tek seferde AÇAR / KAPAR.\n"
        "\n"
        "Modifier'ları silmeden önce / sonra karşılaştır."
    ),
    "tip_quick_shape": (
        "HIZLI ŞEKİL\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "3D Cursor'un bulunduğu yere otomatik olarak\n"
        "bir kesici nesne (Küp/Silindir/Küre) ekler."
    ),
    "tip_array": (
        "DİZİ KESİCİ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aktif kesiciye Array modifier ekler ve hedef\n"
        "nesneden çoklu kesim yapar. Dairesel (Radial)\n"
        "veya Doğrusal (Linear) çalışabilir."
    ),
    "tip_cleanup": (
        "AKILLI TEMİZLİK\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Tek tıkla üç adımlı boolean sonrası temizlik:\n"
        "  • Merge by Distance (yinelenen vertex kaldır)\n"
        "  • Shade Smooth      (pürüzsüz gölgeleme)\n"
        "  • Weighted Normals  (dikişsiz shading)"
    ),
    "tip_show": (
        "KESİCİLERİ GÖSTER\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AEGON_Cutters koleksiyonundaki tüm gizli\n"
        "kesici nesneleri tekrar görünür hale getirir."
    ),
    "tip_wire": (
        "KAFES GÖRÜNÜM\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Seçili nesneleri Solid ↔ Wireframe arasında geçirir.\n"
        "Wireframe modunda kesicinin içinden hedefi görebilirsin."
    ),
    "tip_clear": (
        "TÜM BOOLLERİ TEMİZLE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aktif nesnedeki TÜM Boolean modifier'ları\n"
        "UYGULAMADAN kaldırır. Mesh geometrisi korunur.\n"
        "Kesiciler sahnede kalmaya devam eder."
    ),
    "tip_del": (
        "KESİCİLERİ SİL\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AEGON_Cutters koleksiyonundaki tüm\n"
        "kesici nesneleri kalıcı olarak siler.\n"
        "\n"
        "⚠  GERİ ALINAMAZ!"
    ),
    "tip_solver": (
        "ÇÖZÜCÜ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Exact  →  En yüksek kalite. Karmaşık ve ince\n"
        "           geometride güvenli sonuç verir.\n"
        "\n"
        "Fast   →  Hızlı hesaplama. Basit geometride\n"
        "           idealdir; yoğun mesh'lerde artefakt\n"
        "           oluşabilir."
    ),
    "tip_auto_apply": (
        "OTOMATİK UYGULA\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AÇIK  → İşlem sonrası modifier hemen kalıcı uygulanır.\n"
        "        Parametrik düzenleme mümkün olmaz.\n"
        "\n"
        "KAPALI → Modifier canlı kalır. Kesiciyi hareket\n"
        "         ettirerek sonucu gerçek zamanlı görebilirsin.\n"
        "         (Önerilen)"
    ),
    "tip_auto_hide": (
        "KESİCİLERİ OTOMATIK GİZLE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AÇIK  → İşlem tamamlanınca kesici otomatik gizlenir.\n"
        "        Viewport temiz kalır.\n"
        "\n"
        "KAPALI → Kesici görünür kalır; konumunu hemen\n"
        "         ayarlayabilirsin."
    ),
    "tip_col": (
        "KESİCİ KOLEKSİYONU\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AÇIK  → Kesiciler 'AEGON_Cutters' koleksiyonuna\n"
        "        taşınır. Sahne düzeni temiz kalır. (Önerilen)\n"
        "\n"
        "KAPALI → Kesiciler mevcut koleksiyonlarında kalır."
    ),
    "tip_threshold": (
        "ÇAKIŞMA EŞİĞİ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "İki yüzeyin 'çakışıyor' sayılması için gereken\n"
        "minimum mesafe (metre). Yalnızca Exact çözücüde aktif.\n"
        "\n"
        "Küçük → Daha hassas, ince yüzeylerde dikkat.\n"
        "Büyük → Daha toleranslı, küçük boşlukları kapatır."
    ),
    "tip_flip": (
        "KESİCİYİ TERS ÇEVİR\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kesme yönünü tersine çevirir.\n"
        "Açık (non-manifold) mesh'lerde beklenen\n"
        "sonucu almak için dene."
    ),
    "tip_top": (
        "EN ÜSTE TAŞI\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Yeni Boolean modifier'ı stack'in EN ÜSTÜNE\n"
        "yerleştirir. Çok modifier'lı objelerde\n"
        "elle sıralama ihtiyacını ortadan kaldırır."
    ),
    "tip_prefix": (
        "MODİFİER ADI ÖNEKİ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Oluşturulan modifier isimlerinin önüne eklenir.\n"
        "Örnek: 'PROJE_' → modifier adı 'PROJE_DIFFERENCE' olur.\n"
        "Boş bırakılırsa varsayılan 'AEGON_' kullanılır."
    ),
    "tip_merge": (
        "AKILLI BİRLEŞTİRME\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Modifier uygulandıktan sonra otomatik olarak\n"
        "Merge by Distance çalıştırır.\n"
        "Yinelenen (kopya) vertex'leri temizler."
    ),
    "tip_smooth": (
        "SMOOTH SHADE UYGULA\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Modifier uygulandıktan sonra otomatik\n"
        "Smooth Shade ekler. Pürüzsüz yüzey gölgeleme."
    ),
    "tip_wnorm": (
        "WEIGHTED NORMALS EKLE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Uygulama sonrası Weighted Normals modifier ekler.\n"
        "Boolean kenarlarını temiz ve dikişsiz gösterir."
    ),
    "tip_use_bevel": (
        "BEVEL EKLE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Uygulama sonrası mesh'e non-destructive Bevel ekler.\n"
        "Angle (Açı) limitini kullanarak sadece keskin\n"
        "kenarları (boolean kesişimleri dahil) yuvarlatır."
    ),
    "tip_wirecolor": (
        "TEL RENGİ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Yeni oluşturulan kesicilerin viewport'taki\n"
        "tel (wire) çizgilerinin rengi.\n"
        "Kesicileri tanımlamayı kolaylaştırır."
    ),
    "tip_applycolor": (
        "RENGİ TÜM KESİCİLERE UYGULA\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Seçili tel rengini sahnedeki mevcut TÜM\n"
        "AEGON kesici nesnelerine hemen uygular."
    ),
    "tip_mirror": (
        "OTOMATİK SİMETRİ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aktif nesneye anında bir Mirror modifier ekler\n"
        "ve bunu Boolean yığınının en sonuna yerleştirir."
    ),
    "tip_lang": "Arayüzü İngilizce'ye geçir  (Switch to English)",
    "tip_mod_up":      "Bu modifier'ı stack'te YUKARI taşı.",
    "tip_mod_down":    "Bu modifier'ı stack'te AŞAĞI taşı.",
    "tip_mod_apply":   "Yalnızca BU modifier'ı uygula — diğerleri dokunulmadan kalır.",
    "tip_mod_remove":  "Yalnızca BU modifier'ı kaldır — mesh değişmez.",
}

_EN = {
    "sec_ops":       "Boolean Operations",
    "sec_settings":  "Advanced Settings",
    "sec_manage":    "Management",
    "sec_stack":     "Modifier Manager",
    "sec_info":      "Object Info",
    "apply_all":     "Apply All",
    "op_difference": "Difference",
    "op_union":      "Union",
    "op_intersect":  "Intersect",
    "op_slice":      "Slice",
    "live_preview":  "Live Preview",
    "smart_cleanup": "Smart Cleanup",
    "show_cutters":  "Show Cutters",
    "wire_toggle":   "Toggle Wireframe",
    "clear_all":     "Clear All Booleans",
    "del_cutters":   "Delete Cutters",
    "apply_color":   "Apply Color to All Cutters",
    "lang_btn":      "TR",
    "add_cube":      "Add Cube",
    "add_cyl":       "Add Cylinder",
    "add_sph":       "Add Sphere",
    "array_cut":     "Array Cutter",
    "auto_mirror":   "Auto Mirror",
    "array_count":   "Array Count",
    "array_offset":  "Array Offset",
    "array_radial":  "Radial Array",
    "solver":        "Solver",
    "auto_apply":    "Auto Apply",
    "auto_hide":     "Auto Hide Cutters",
    "use_col":       "Use Cutter Collection",
    "show_list":     "Show Modifier List",
    "wire_color":    "Wire Color",
    "threshold":     "Overlap Threshold",
    "flip":          "Flip Cutter Normal",
    "to_top":        "Move Modifier to Top",
    "prefix":        "Modifier Prefix",
    "merge":         "Smart Merge by Distance",
    "merge_dist":    "Merge Distance",
    "smooth":        "Auto Shade Smooth",
    "wnormals":      "Add Weighted Normals",
    "use_bevel":     "Add Bevel",
    "bevel_amt":     "Bevel Amount",
    "bevel_seg":     "Bevel Segments",
    "solver_exact":  "Exact",
    "solver_fast":   "Fast",
    "algo_lbl":      "── Algorithm ──",
    "post_lbl":      "── Post-Process ──",
    "visual_lbl":    "── Visuals ──",
    "core_lbl":      "── Core ──",
    "solver_lbl":    "Solver:",
    "no_active":     "No active object",
    "obj":           "Object",
    "bool_count":    "Boolean Count",
    "no_mods":       "— no modifiers —",
    "version":       "v6.0  ·  Aegon Design",
    "tip_difference": (
        "DIFFERENCE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Subtracts selected cutter(s) from the active mesh.\n"
        "\n"
        "How to use:\n"
        "  1) Select the cutter(s)\n"
        "  2) Shift + click target mesh (make it active)\n"
        "  3) Press Difference\n"
        "\n"
        "Multiple cutters are processed simultaneously."
    ),
    "tip_union": (
        "UNION\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Merges selected cutter(s) into the active mesh.\n"
        "Combines volumes into a single solid object.\n"
        "\n"
        "Best for:\n"
        "  • Hard-surface additive detailing\n"
        "  • Joining multiple parts into one geometry"
    ),
    "tip_intersect": (
        "INTERSECT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Keeps only the overlapping volume between\n"
        "active mesh and cutter(s). Discards the rest.\n"
        "\n"
        "Best for:\n"
        "  • Trim masks\n"
        "  • Cookie-cutter shapes\n"
        "  • Reverse boolean molds"
    ),
    "tip_slice": (
        "SLICE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Splits the active mesh into TWO separate pieces.\n"
        "\n"
        "  Part A → original object   (DIFFERENCE)\n"
        "  Part B → auto-duplicate    (INTERSECT)\n"
        "\n"
        "Both parts keep original materials and UVs."
    ),
    "tip_apply_all": (
        "APPLY ALL\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Permanently applies ALL Boolean modifiers\n"
        "on the active object.\n"
        "\n"
        "⚠  WARNING: Destructive — back up first!"
    ),
    "tip_live": (
        "LIVE PREVIEW\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Toggles viewport visibility of ALL Boolean\n"
        "modifiers on the active object simultaneously.\n"
        "\n"
        "Compare before/after without removing modifiers."
    ),
    "tip_quick_shape": (
        "QUICK SHAPE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Instantly adds a primitive cutter (Cube/Cylinder/Sphere)\n"
        "at the 3D Cursor location."
    ),
    "tip_array": (
        "ARRAY CUTTER\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Adds an Array modifier to the cutter and applies\n"
        "a boolean operation. Can be Radial or Linear."
    ),
    "tip_cleanup": (
        "SMART CLEANUP\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "One-click post-boolean topology cleanup:\n"
        "  • Merge by Distance (remove duplicate verts)\n"
        "  • Shade Smooth      (smooth face shading)\n"
        "  • Weighted Normals  (clean seam-free shading)"
    ),
    "tip_show": (
        "SHOW CUTTERS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Reveals all hidden objects in the\n"
        "AEGON_Cutters collection."
    ),
    "tip_wire": (
        "TOGGLE WIREFRAME\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Switches selected objects between Solid\n"
        "and Wireframe display.\n"
        "Wireframe lets you see through cutters."
    ),
    "tip_clear": (
        "CLEAR ALL BOOLEANS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Removes ALL Boolean modifiers from active\n"
        "object WITHOUT applying. Mesh is preserved.\n"
        "Cutters stay in scene."
    ),
    "tip_del": (
        "DELETE CUTTERS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Permanently deletes all objects in\n"
        "AEGON_Cutters collection.\n"
        "\n"
        "⚠  CANNOT BE UNDONE!"
    ),
    "tip_solver": (
        "SOLVER\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Exact  →  Highest quality. Safe for complex\n"
        "           and thin geometry.\n"
        "\n"
        "Fast   →  Faster calculation. Great for simple\n"
        "           geometry; may artefact on dense meshes."
    ),
    "tip_auto_apply": (
        "AUTO APPLY\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ON  → Modifier applied immediately (destructive).\n"
        "      Parametric editing no longer possible.\n"
        "\n"
        "OFF → Modifier stays live. Reposition cutter\n"
        "      at any time. (Recommended)"
    ),
    "tip_auto_hide": (
        "AUTO HIDE CUTTERS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ON  → Cutters hidden after operation.\n"
        "      Keeps viewport clean.\n"
        "\n"
        "OFF → Cutters stay visible for repositioning."
    ),
    "tip_col": (
        "CUTTER COLLECTION\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ON  → Cutters moved into 'AEGON_Cutters'\n"
        "      collection. Keeps scene organised. (Recommended)\n"
        "\n"
        "OFF → Cutters stay in their current collection."
    ),
    "tip_threshold": (
        "OVERLAP THRESHOLD\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Minimum distance for surfaces to be considered\n"
        "overlapping. Active only with Exact solver.\n"
        "\n"
        "Smaller → More precise; caution on thin faces.\n"
        "Larger  → More tolerant; closes small gaps."
    ),
    "tip_flip": (
        "FLIP CUTTER NORMAL\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Reverses the cutter direction.\n"
        "Try this on open/non-manifold meshes\n"
        "if the result looks inverted."
    ),
    "tip_top": (
        "MOVE MODIFIER TO TOP\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Places the new Boolean modifier at the\n"
        "TOP of the modifier stack.\n"
        "Eliminates manual reordering on multi-modifier objects."
    ),
    "tip_prefix": (
        "MODIFIER PREFIX\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Custom text prepended to new modifier names.\n"
        "Example: 'PROJ_' → modifier named 'PROJ_DIFFERENCE'.\n"
        "Leave blank to use default 'AEGON_'."
    ),
    "tip_merge": (
        "SMART MERGE BY DISTANCE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "After applying modifier, automatically runs\n"
        "Merge by Distance to remove duplicate vertices."
    ),
    "tip_smooth": (
        "AUTO SHADE SMOOTH\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "After applying modifier, automatically\n"
        "applies Shade Smooth to all faces."
    ),
    "tip_wnorm": (
        "ADD WEIGHTED NORMALS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Adds a Weighted Normals modifier after apply.\n"
        "Produces clean, seam-free boolean edges."
    ),
    "tip_use_bevel": (
        "ADD BEVEL\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Adds a non-destructive Bevel modifier after application.\n"
        "Uses Angle limit to automatically round hard edges,\n"
        "including boolean intersections."
    ),
    "tip_wirecolor": (
        "WIRE COLOR\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Wire display color for newly created cutter objects.\n"
        "Makes cutters easy to identify in the viewport."
    ),
    "tip_applycolor": (
        "APPLY COLOR TO ALL CUTTERS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Applies the chosen wire color to all existing\n"
        "AEGON cutter objects in the scene right now."
    ),
    "tip_mirror": (
        "AUTO MIRROR\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Adds a Mirror modifier to the active object and\n"
        "places it safely at the end of the boolean stack."
    ),
    "tip_lang": "Switch interface language to Türkçe  (TR)",
    "tip_mod_up":      "Move this modifier UP in the stack.",
    "tip_mod_down":    "Move this modifier DOWN in the stack.",
    "tip_mod_apply":   "Apply ONLY this modifier — leave others untouched.",
    "tip_mod_remove":  "Remove ONLY this modifier — mesh unchanged.",
}

_LANGS = {'TR': _TR, 'EN': _EN}


def T(context, key):
    lang = context.scene.aegon_settings.language
    return _LANGS.get(lang, _EN).get(key, key)


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

class AEGON_PG_Settings(PropertyGroup):

    language: EnumProperty(
        name="Dil / Language",
        items=[('TR', "Türkçe", ""), ('EN', "English", "")],
        default='TR',
    )
    solver: EnumProperty(
        name="Solver",
        description="Exact: highest quality | Fast: faster calculation",
        items=[
            ('EXACT', "Exact", "High-precision solver — complex geometry safe"),
            ('FAST',  "Fast",  "Faster calculation — simple geometry"),
        ],
        default='EXACT',
    )
    auto_apply: BoolProperty(name="Auto Apply", default=False)
    auto_hide_cutters: BoolProperty(name="Auto Hide Cutters", default=True)
    use_collection: BoolProperty(name="Use Cutter Collection", default=True)
    show_mod_list: BoolProperty(name="Show Modifier List", default=True)

    cutter_wire_color: FloatVectorProperty(
        name="Wire Color",
        subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(1.0, 0.35, 0.0),
    )

    overlap_threshold: FloatProperty(
        name="Overlap Threshold",
        default=1e-6, min=0.0, max=1.0, precision=7,
    )
    flip_normals: BoolProperty(name="Flip Cutter Normal", default=False)
    move_to_top: BoolProperty(name="Move to Top", default=False)
    modifier_prefix: StringProperty(name="Modifier Prefix", default="AEGON_", maxlen=32)

    smart_merge: BoolProperty(name="Smart Merge", default=False)
    merge_threshold: FloatProperty(name="Merge Distance", default=0.0001, min=0.0, max=1.0, precision=5)
    auto_smooth: BoolProperty(name="Auto Shade Smooth", default=False)
    weighted_normals: BoolProperty(name="Weighted Normals", default=False)
    
    use_bevel: BoolProperty(name="Add Bevel", default=False)
    bevel_amount: FloatProperty(name="Bevel Amount", default=0.01, min=0.0001, max=1.0, precision=4)
    bevel_segments: bpy.props.IntProperty(name="Bevel Segments", default=3, min=1, max=10)

    array_count: bpy.props.IntProperty(name="Array Count", default=3, min=2, max=100)
    array_offset: FloatVectorProperty(name="Array Offset", size=3, default=(1.1, 0.0, 0.0))
    array_radial: BoolProperty(name="Radial Array", default=False)

    auto_mirror_axis: EnumProperty(
        name="Mirror Axis",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")],
        default='X'
    )



# ══════════════════════════════════════════════════════════════════════════════
#  CORE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def ensure_cutter_collection(context):
    name = "AEGON_Cutters"
    if name not in bpy.data.collections:
        col = bpy.data.collections.new(name)
        context.scene.collection.children.link(col)
    return bpy.data.collections[name]


def move_to_cutter_collection(obj, context):
    col = ensure_cutter_collection(context)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def apply_cutter_visuals(obj, s):
    r, g, b = s.cutter_wire_color
    obj.display_type = 'WIRE'
    obj.show_wire    = True
    obj.color        = (r, g, b, 1.0)


def validate_selection(context):
    active  = context.active_object
    cutters = [o for o in context.selected_objects if o != active]
    if not active:
        raise ValueError("No active object. Click your target mesh.")
    if active.type != 'MESH':
        raise ValueError(f"'{active.name}' is not a Mesh.")
    if not cutters:
        raise ValueError("No cutter selected. Shift-click at least one cutter.")
    bad = [o.name for o in cutters if o.type != 'MESH']
    if bad:
        raise ValueError(f"Non-mesh cutter(s): {bad}")
    return active, cutters


def build_modifier(active, operation, cutter, s):
    prefix = s.modifier_prefix.strip() or "AEGON_"
    mod = active.modifiers.new(name=f"{prefix}{operation}", type='BOOLEAN')
    mod.operation = operation
    mod.object    = cutter
    mod.solver    = s.solver

    if s.solver == 'EXACT':
        try:
            mod.double_threshold = s.overlap_threshold
        except AttributeError:
            pass

    try:
        mod.use_self = s.flip_normals
    except AttributeError:
        pass

    if s.move_to_top:
        for _ in range(len(active.modifiers)):
            if active.modifiers[0].name == mod.name:
                break
            try:
                bpy.ops.object.modifier_move_up(
                    {'active_object': active}, modifier=mod.name
                )
            except Exception:
                break
    return mod


def post_process(context, obj, s):
    if not (s.smart_merge or s.auto_smooth or s.weighted_normals or s.use_bevel):
        return
    prev = context.view_layer.objects.active
    context.view_layer.objects.active = obj

    if s.smart_merge:
        prev_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=s.merge_threshold)
        bpy.ops.object.mode_set(mode=prev_mode)

    if s.auto_smooth:
        bpy.ops.object.shade_smooth()
        
    if s.use_bevel:
        if not any(m.type == 'BEVEL' and m.name.startswith("AEGON_") for m in obj.modifiers):
            bvl = obj.modifiers.new("AEGON_Bevel", 'BEVEL')
            bvl.limit_method = 'ANGLE'
            bvl.angle_limit = 0.523599  # 30 degrees
            bvl.width = s.bevel_amount
            bvl.segments = s.bevel_segments
            bvl.profile = 0.5
            bvl.harden_normals = s.weighted_normals

    if s.weighted_normals:
        if not any(m.type == 'WEIGHTED_NORMAL' for m in obj.modifiers):
            wn = obj.modifiers.new("AEGON_WeightedNormals", 'WEIGHTED_NORMAL')
            wn.keep_sharp = True

    context.view_layer.objects.active = prev


def run_boolean(context, operation):
    try:
        active, cutters = validate_selection(context)
    except ValueError as e:
        return {'CANCELLED'}, str(e)

    s = context.scene.aegon_settings
    for cutter in cutters:
        mod = build_modifier(active, operation, cutter, s)
        apply_cutter_visuals(cutter, s)
        if s.use_collection:
            move_to_cutter_collection(cutter, context)
        if s.auto_hide_cutters:
            cutter.hide_set(True)
        if s.auto_apply:
            context.view_layer.objects.active = active
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except RuntimeError as e:
                return {'CANCELLED'}, str(e)

    post_process(context, active, s)
    return {'FINISHED'}, None


# ══════════════════════════════════════════════════════════════════════════════
#  OPERATORS
# ══════════════════════════════════════════════════════════════════════════════

class AEGON_OT_Difference(Operator):
    bl_idname     = "aegon.bool_difference"
    bl_label      = "Difference"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Difference"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_difference")

    def execute(self, context):
        res, err = run_boolean(context, 'DIFFERENCE')
        if err: self.report({'ERROR'}, err)
        return res


class AEGON_OT_Union(Operator):
    bl_idname     = "aegon.bool_union"
    bl_label      = "Union"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Union"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_union")

    def execute(self, context):
        res, err = run_boolean(context, 'UNION')
        if err: self.report({'ERROR'}, err)
        return res


class AEGON_OT_Intersect(Operator):
    bl_idname     = "aegon.bool_intersect"
    bl_label      = "Intersect"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Intersect"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_intersect")

    def execute(self, context):
        res, err = run_boolean(context, 'INTERSECT')
        if err: self.report({'ERROR'}, err)
        return res


class AEGON_OT_Slice(Operator):
    bl_idname     = "aegon.bool_slice"
    bl_label      = "Slice"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Slice"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_slice")

    def execute(self, context):
        try:
            active, cutters = validate_selection(context)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        s = context.scene.aegon_settings
        for cutter in cutters:
            dup      = active.copy()
            dup.data = active.data.copy()
            dup.name = active.name + "_Slice"
            context.collection.objects.link(dup)
            mod_a = build_modifier(active, 'DIFFERENCE', cutter, s)
            mod_b = build_modifier(dup,    'INTERSECT',  cutter, s)
            apply_cutter_visuals(cutter, s)
            if s.auto_hide_cutters:
                cutter.hide_set(True)
            if s.use_collection:
                move_to_cutter_collection(cutter, context)
            if s.auto_apply:
                try:
                    context.view_layer.objects.active = active
                    bpy.ops.object.modifier_apply(modifier=mod_a.name)
                    context.view_layer.objects.active = dup
                    bpy.ops.object.modifier_apply(modifier=mod_b.name)
                except RuntimeError as e:
                    self.report({'ERROR'}, str(e))
                    return {'CANCELLED'}
        post_process(context, active, s)
        return {'FINISHED'}


class AEGON_OT_ApplyAll(Operator):
    bl_idname     = "aegon.apply_all"
    bl_label      = "Apply All"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Apply All"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_apply_all")

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}
        mods = [m for m in obj.modifiers if m.type == 'BOOLEAN']
        if not mods:
            self.report({'INFO'}, "No Boolean modifiers found.")
            return {'CANCELLED'}
        context.view_layer.objects.active = obj
        for m in mods:
            try: bpy.ops.object.modifier_apply(modifier=m.name)
            except Exception as e: self.report({'WARNING'}, str(e))
        post_process(context, obj, context.scene.aegon_settings)
        self.report({'INFO'}, f"Applied {len(mods)} modifier(s).")
        return {'FINISHED'}


class AEGON_OT_ClearAll(Operator):
    bl_idname     = "aegon.clear_all"
    bl_label      = "Clear All Booleans"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Clear All Booleans"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_clear")

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}
        n = 0
        for m in [x for x in obj.modifiers if x.type == 'BOOLEAN']:
            obj.modifiers.remove(m)
            n += 1
        self.report({'INFO'}, f"Removed {n} modifier(s).")
        return {'FINISHED'}


class AEGON_OT_ShowCutters(Operator):
    bl_idname     = "aegon.show_cutters"
    bl_label      = "Show Cutters"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Show Cutters"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_show")

    def execute(self, context):
        col = bpy.data.collections.get("AEGON_Cutters")
        n   = 0
        for obj in bpy.data.objects:
            is_aegon = (col and obj.name in col.objects) or obj.name.startswith("AEGON_")
            if is_aegon and obj.hide_get():
                obj.hide_set(False)
                n += 1
        self.report({'INFO'}, f"Revealed {n} cutter(s).")
        return {'FINISHED'}


class AEGON_OT_DeleteCutters(Operator):
    bl_idname     = "aegon.delete_cutters"
    bl_label      = "Delete Cutters"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Delete Cutters"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_del")

    def execute(self, context):
        col = bpy.data.collections.get("AEGON_Cutters")
        if not col:
            self.report({'INFO'}, "AEGON_Cutters collection not found.")
            return {'CANCELLED'}
        n = len(list(col.objects))
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"Deleted {n} cutter(s).")
        return {'FINISHED'}


class AEGON_OT_WireframeToggle(Operator):
    bl_idname     = "aegon.wireframe_toggle"
    bl_label      = "Toggle Wireframe"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Toggle Wireframe"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_wire")

    def execute(self, context):
        objs = context.selected_objects or ([context.active_object] if context.active_object else [])
        for o in objs:
            o.display_type = 'WIRE' if o.display_type != 'WIRE' else 'SOLID'
        return {'FINISHED'}


class AEGON_OT_ApplyColorToAll(Operator):
    bl_idname     = "aegon.apply_color_all"
    bl_label      = "Apply Color to All Cutters"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Apply Color to All Cutters"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_applycolor")

    def execute(self, context):
        s   = context.scene.aegon_settings
        col = bpy.data.collections.get("AEGON_Cutters")
        targets = list(col.objects) if col else []
        for obj in bpy.data.objects:
            if obj.name.startswith("AEGON_") and obj not in targets:
                targets.append(obj)
        for obj in targets:
            apply_cutter_visuals(obj, s)
        self.report({'INFO'}, f"Color applied to {len(targets)} cutter(s).")
        return {'FINISHED'}


class AEGON_OT_LivePreview(Operator):
    bl_idname     = "aegon.live_preview"
    bl_label      = "Live Preview"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Live Preview"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_live")

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}
        mods = [m for m in obj.modifiers if m.type == 'BOOLEAN']
        if not mods:
            self.report({'INFO'}, "No Boolean modifiers.")
            return {'CANCELLED'}
        new_state = not mods[0].show_viewport
        for m in mods:
            m.show_viewport = new_state
        self.report({'INFO'}, f"Boolean preview {'ON' if new_state else 'OFF'}.")
        return {'FINISHED'}


class AEGON_OT_SmartCleanup(Operator):
    bl_idname     = "aegon.smart_cleanup"
    bl_label      = "Smart Cleanup"
    bl_options    = {'REGISTER', 'UNDO'}
    bl_description = "Smart Cleanup"

    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_cleanup")

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a Mesh object.")
            return {'CANCELLED'}
        s = context.scene.aegon_settings
        context.view_layer.objects.active = obj
        prev_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=s.merge_threshold)
        bpy.ops.object.mode_set(mode=prev_mode)
        bpy.ops.object.shade_smooth()
        if not any(m.type == 'WEIGHTED_NORMAL' for m in obj.modifiers):
            wn = obj.modifiers.new("AEGON_WeightedNormals", 'WEIGHTED_NORMAL')
            wn.keep_sharp = True
        self.report({'INFO'}, "Smart cleanup complete.")
        return {'FINISHED'}


class AEGON_OT_ToggleLang(Operator):
    bl_idname  = "aegon.toggle_lang"
    bl_label   = "Toggle Language"
    bl_options = {'REGISTER'}
    bl_description = "Toggle interface language between Turkish and English  |  Arayüz dilini TR / EN arasında geçir"

    def execute(self, context):
        s = context.scene.aegon_settings
        s.language = 'EN' if s.language == 'TR' else 'TR'
        return {'FINISHED'}


class AEGON_OT_AddCube(Operator):
    bl_idname = "aegon.add_cube"
    bl_label  = "Add Cube Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def description(cls, context, properties): return T(context, "tip_quick_shape")
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=context.scene.cursor.location)
        apply_cutter_visuals(context.active_object, context.scene.aegon_settings)
        return {'FINISHED'}

class AEGON_OT_AddCylinder(Operator):
    bl_idname = "aegon.add_cylinder"
    bl_label  = "Add Cylinder Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def description(cls, context, properties): return T(context, "tip_quick_shape")
    def execute(self, context):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2.0, location=context.scene.cursor.location)
        apply_cutter_visuals(context.active_object, context.scene.aegon_settings)
        return {'FINISHED'}

class AEGON_OT_AddSphere(Operator):
    bl_idname = "aegon.add_sphere"
    bl_label  = "Add Sphere Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def description(cls, context, properties): return T(context, "tip_quick_shape")
    def execute(self, context):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=context.scene.cursor.location)
        apply_cutter_visuals(context.active_object, context.scene.aegon_settings)
        return {'FINISHED'}

class AEGON_OT_ArrayCutter(Operator):
    bl_idname = "aegon.array_cutter"
    bl_label  = "Array Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def description(cls, context, properties):
        return T(context, "tip_array")

    def execute(self, context):
        try:
            active, cutters = validate_selection(context)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
            
        s = context.scene.aegon_settings
        
        for cutter in cutters:
            # Setup Array on cutter
            arr = cutter.modifiers.new(name="AEGON_Array", type='ARRAY')
            arr.count = s.array_count
            
            if s.array_radial:
                # Radial array logic: create empty, rotate it, use as object offset
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=active.location)
                empty = context.active_object
                empty.name = "AEGON_Radial_Axis"
                
                # Rotate empty by 360 / count
                import math
                empty.rotation_euler[2] = math.radians(360.0 / s.array_count)
                
                # Link empty to cutter array
                arr.use_relative_offset = False
                arr.use_object_offset = True
                arr.offset_object = empty
                
                # Manage empty
                if s.use_collection:
                    move_to_cutter_collection(empty, context)
                if s.auto_hide_cutters:
                    empty.hide_set(True)
            else:
                # Linear array logic
                arr.use_relative_offset = False
                arr.use_constant_offset = True
                arr.constant_offset_displace = s.array_offset
                
            # Perform boolean
            run_boolean(context, 'DIFFERENCE')
            
        return {'FINISHED'}


class AEGON_OT_AutoMirror(Operator):
    bl_idname = "aegon.auto_mirror"
    bl_label  = "Auto Mirror"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def description(cls, context, properties): return T(context, "tip_mirror")
    def execute(self, context):
        obj = context.active_object
        if not obj: return {'CANCELLED'}
        s = context.scene.aegon_settings
        mod = obj.modifiers.new("AEGON_Mirror", 'MIRROR')
        mod.use_axis[0] = (s.auto_mirror_axis == 'X')
        mod.use_axis[1] = (s.auto_mirror_axis == 'Y')
        mod.use_axis[2] = (s.auto_mirror_axis == 'Z')
        return {'FINISHED'}


class AEGON_OT_ModUp(Operator):
    bl_idname = "aegon.mod_up"
    bl_label  = "Move Up"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move modifier UP in the stack"
    mod_name: StringProperty()

    def execute(self, context):
        obj = context.active_object
        if obj:
            try: bpy.ops.object.modifier_move_up(modifier=self.mod_name)
            except Exception: pass
        return {'FINISHED'}


class AEGON_OT_ModDown(Operator):
    bl_idname = "aegon.mod_down"
    bl_label  = "Move Down"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move modifier DOWN in the stack"
    mod_name: StringProperty()

    def execute(self, context):
        obj = context.active_object
        if obj:
            try: bpy.ops.object.modifier_move_down(modifier=self.mod_name)
            except Exception: pass
        return {'FINISHED'}


class AEGON_OT_ModApplySingle(Operator):
    bl_idname  = "aegon.mod_apply_single"
    bl_label   = "Apply"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Apply ONLY this modifier — leave others untouched"
    mod_name: StringProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj: return {'CANCELLED'}
        context.view_layer.objects.active = obj
        try:
            bpy.ops.object.modifier_apply(modifier=self.mod_name)
            self.report({'INFO'}, f"Applied '{self.mod_name}'.")
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'}


class AEGON_OT_ModRemoveSingle(Operator):
    bl_idname  = "aegon.mod_remove_single"
    bl_label   = "Remove"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove ONLY this modifier — mesh unchanged"
    mod_name: StringProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj: return {'CANCELLED'}
        mod = obj.modifiers.get(self.mod_name)
        if mod: obj.modifiers.remove(mod)
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
#  UI PANEL
# ══════════════════════════════════════════════════════════════════════════════

class AEGON_PT_MainPanel(Panel):
    bl_label       = "Aegon Boolean"
    bl_idname      = "AEGON_PT_main_panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "Aegon Tools"

    def draw_header(self, context):
        self.layout.label(icon='MOD_BOOLEAN')

    def draw(self, context):
        layout = self.layout
        s      = context.scene.aegon_settings
        active = context.active_object

        # ── Top bar: lang toggle + version ───────────────────────────────────
        top = layout.row(align=True)
        top.scale_y = 1.0
        top.operator("aegon.toggle_lang",
                     text=T(context, "lang_btn"),
                     icon='WORLD',
                     emboss=True)
        top.separator()
        ver = top.row()
        ver.enabled = False
        ver.label(text=T(context, "version"))

        layout.separator(factor=0.5)

        # ── Object info box ───────────────────────────────────────────────────
        box = layout.box()
        box.scale_y = 0.85
        if active:
            bm = [m for m in active.modifiers if m.type == 'BOOLEAN']
            r1 = box.row()
            r1.label(text=f"{T(context,'obj')}:  {active.name}", icon='OBJECT_DATA')
            r2 = box.row()
            ic = 'MODIFIER_DATA' if bm else 'INFO'
            r2.label(text=f"{T(context,'bool_count')}:  {len(bm)}", icon=ic)
        else:
            box.label(text=T(context, "no_active"), icon='ERROR')

        layout.separator(factor=0.3)

        # ── Boolean Operations ────────────────────────────────────────────────
        hdr, body = layout.panel("aegon_ops", default_closed=False)
        hdr.label(text=T(context, "sec_ops"), icon='MOD_BOOLEAN')
        if body:
            r1 = body.row(align=True)
            r1.scale_y = 1.7
            r1.operator("aegon.bool_difference", text=T(context, "op_difference"), icon='SELECT_SUBTRACT')
            r1.operator("aegon.bool_union",      text=T(context, "op_union"),      icon='SELECT_EXTEND')

            r2 = body.row(align=True)
            r2.scale_y = 1.7
            r2.operator("aegon.bool_intersect",  text=T(context, "op_intersect"),  icon='SELECT_INTERSECT')
            r2.operator("aegon.bool_slice",      text=T(context, "op_slice"),      icon='MOD_BOOLEAN')

            body.separator(factor=0.4)

            # Quick Shapes
            r3 = body.row(align=True)
            r3.scale_y = 1.2
            r3.operator("aegon.add_cube", text=T(context, "add_cube"), icon='MESH_CUBE')
            r3.operator("aegon.add_cyl",  text=T(context, "add_cyl"),  icon='MESH_CYLINDER')
            r3.operator("aegon.add_sph",  text=T(context, "add_sph"),  icon='MESH_UVSPHERE')

            body.separator(factor=0.4)

            # Array Cutter
            box_arr = body.box()
            box_arr.label(text=T(context, "array_cut"), icon='MOD_ARRAY')
            col_arr = box_arr.column(align=True)
            col_arr.prop(s, "array_count", text=T(context, "array_count"))
            col_arr.prop(s, "array_radial", text=T(context, "array_radial"))
            if not s.array_radial:
                col_arr.prop(s, "array_offset", text=T(context, "array_offset"))
            col_arr.separator(factor=0.3)
            col_arr.operator("aegon.array_cutter", text=T(context, "array_cut"), icon='MOD_ARRAY')

            body.separator(factor=0.2)
            
            # Auto Mirror
            box_mir = body.box()
            box_mir.label(text=T(context, "auto_mirror"), icon='MOD_MIRROR')
            row_mir = box_mir.row(align=True)
            row_mir.prop(s, "auto_mirror_axis", text="")
            row_mir.operator("aegon.auto_mirror", text="Mirror", icon='MOD_MIRROR')

            body.separator(factor=0.4)

            ra = body.row()
            ra.scale_y = 1.2
            ra.alert = s.auto_apply
            ra.operator("aegon.apply_all",
                        text=T(context, "apply_all"),
                        icon='CHECKMARK')

            body.separator(factor=0.1)
            body.operator("aegon.live_preview",
                          text=T(context, "live_preview"),
                          icon='HIDE_OFF')

        layout.separator(factor=0.3)

        # ── Advanced Settings ─────────────────────────────────────────────────
        hdr3, body3 = layout.panel("aegon_set", default_closed=False)
        hdr3.label(text=T(context, "sec_settings"), icon='PREFERENCES')
        if body3:
            # Solver
            body3.label(text=T(context, "solver_lbl"), icon='MODIFIER')
            row_sv = body3.row(align=True)
            row_sv.prop_enum(s, "solver", 'EXACT', text=T(context, "solver_exact"))
            row_sv.prop_enum(s, "solver", 'FAST',  text=T(context, "solver_fast"))

            body3.separator(factor=0.5)
            body3.label(text=T(context, "core_lbl"))
            col = body3.column(align=True)
            col.prop(s, "auto_apply",        text=T(context, "auto_apply"))
            col.prop(s, "auto_hide_cutters", text=T(context, "auto_hide"))
            col.prop(s, "use_collection",    text=T(context, "use_col"))
            col.prop(s, "show_mod_list",     text=T(context, "show_list"))

            body3.separator(factor=0.5)
            body3.label(text=T(context, "algo_lbl"))
            col2 = body3.column(align=True)
            col2.prop(s, "overlap_threshold", text=T(context, "threshold"))
            col2.prop(s, "flip_normals",      text=T(context, "flip"))
            col2.prop(s, "move_to_top",       text=T(context, "to_top"))
            col2.prop(s, "modifier_prefix",   text=T(context, "prefix"))

            body3.separator(factor=0.5)
            body3.label(text=T(context, "post_lbl"))
            col3 = body3.column(align=True)
            col3.prop(s, "smart_merge", text=T(context, "merge"))
            sub = col3.column(align=True)
            sub.enabled = s.smart_merge
            sub.prop(s, "merge_threshold", text=T(context, "merge_dist"))
            col3.prop(s, "auto_smooth",      text=T(context, "smooth"))
            col3.prop(s, "weighted_normals", text=T(context, "wnormals"))
            
            col3.separator(factor=0.3)
            col3.prop(s, "use_bevel", text=T(context, "use_bevel"))
            sub_bvl = col3.column(align=True)
            sub_bvl.enabled = s.use_bevel
            sub_bvl.prop(s, "bevel_amount", text=T(context, "bevel_amt"))
            sub_bvl.prop(s, "bevel_segments", text=T(context, "bevel_seg"))

            body3.separator(factor=0.5)
            body3.label(text=T(context, "visual_lbl"))
            body3.prop(s, "cutter_wire_color", text=T(context, "wire_color"))
            body3.operator("aegon.apply_color_all",
                           text=T(context, "apply_color"),
                           icon='SHADERFX')

        layout.separator(factor=0.3)

        # ── Management ────────────────────────────────────────────────────────
        hdr4, body4 = layout.panel("aegon_mgmt", default_closed=False)
        hdr4.label(text=T(context, "sec_manage"), icon='TOOL_SETTINGS')
        if body4:
            safe = body4.column(align=True)
            safe.scale_y = 1.25
            safe.operator("aegon.show_cutters",     text=T(context, "show_cutters"), icon='HIDE_OFF')
            safe.operator("aegon.wireframe_toggle", text=T(context, "wire_toggle"),  icon='SHADING_WIRE')
            safe.operator("aegon.smart_cleanup",    text=T(context, "smart_cleanup"), icon='BRUSH_DATA')

            body4.separator(factor=0.3)
            danger = body4.column(align=True)
            danger.scale_y = 1.15
            danger.alert = True
            danger.operator("aegon.clear_all",      text=T(context, "clear_all"),   icon='X')
            danger.operator("aegon.delete_cutters", text=T(context, "del_cutters"), icon='TRASH')

        layout.separator(factor=0.3)

        # ── Modifier Stack Manager ────────────────────────────────────────────
        if s.show_mod_list and active:
            hdr5, body5 = layout.panel("aegon_stack", default_closed=False)
            hdr5.label(text=T(context, "sec_stack"), icon='MODIFIER')
            if body5:
                bm = [m for m in active.modifiers if m.type == 'BOOLEAN']
                if bm:
                    for m in bm:
                        row = body5.row(align=True)
                        row.scale_y = 0.95
                        # Viewport visibility eye
                        row.prop(m, "show_viewport", text="",
                                 icon='HIDE_OFF' if m.show_viewport else 'HIDE_ON',
                                 emboss=False)
                        # Name
                        cutter_tag = f"← {m.object.name}" if m.object else "← ?"
                        ic = 'SNAP_FACE' if m.solver == 'EXACT' else 'SNAP_VERTEX'
                        row.label(
                            text=f"{m.name}  [{m.operation[:3]}]  {cutter_tag}",
                            icon=ic,
                        )
                        # Stack order
                        op_u = row.operator("aegon.mod_up",   text="", icon='TRIA_UP',   emboss=False)
                        op_u.mod_name = m.name
                        op_d = row.operator("aegon.mod_down", text="", icon='TRIA_DOWN', emboss=False)
                        op_d.mod_name = m.name
                        # Apply / Remove
                        op_a = row.operator("aegon.mod_apply_single",  text="", icon='CHECKMARK', emboss=True)
                        op_a.mod_name = m.name
                        op_r = row.operator("aegon.mod_remove_single", text="", icon='X', emboss=False)
                        op_r.mod_name = m.name
                else:
                    body5.label(text=T(context, "no_mods"), icon='INFO')


# ══════════════════════════════════════════════════════════════════════════════
#  PIE MENU
# ══════════════════════════════════════════════════════════════════════════════

class AEGON_MT_PieMenu(bpy.types.Menu):
    bl_idname = "aegon.pie_menu"
    bl_label  = "Aegon Boolean PRO"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left (4 - West)
        pie.operator("aegon.bool_union", text=T(context, "op_union"), icon='SELECT_EXTEND')
        # Right (6 - East)
        pie.operator("aegon.bool_difference", text=T(context, "op_difference"), icon='SELECT_SUBTRACT')
        # Bottom (2 - South)
        pie.operator("aegon.live_preview", text=T(context, "live_preview"), icon='HIDE_OFF')
        # Top (8 - North)
        pie.operator("aegon.apply_all", text=T(context, "apply_all"), icon='CHECKMARK')
        
        # Top Left (7 - North West)
        pie.operator("aegon.bool_slice", text=T(context, "op_slice"), icon='MOD_BOOLEAN')
        # Top Right (9 - North East)
        pie.operator("aegon.bool_intersect", text=T(context, "op_intersect"), icon='SELECT_INTERSECT')
        # Bottom Left (1 - South West)
        pie.operator("aegon.smart_cleanup", text=T(context, "smart_cleanup"), icon='BRUSH_DATA')
        # Bottom Right (3 - South East)
        pie.operator("aegon.wireframe_toggle", text=T(context, "wire_toggle"), icon='SHADING_WIRE')


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTER
# ══════════════════════════════════════════════════════════════════════════════

classes = (
    AEGON_PG_Settings,
    AEGON_OT_Difference,
    AEGON_OT_Union,
    AEGON_OT_Intersect,
    AEGON_OT_Slice,
    AEGON_OT_ApplyAll,
    AEGON_OT_ClearAll,
    AEGON_OT_ShowCutters,
    AEGON_OT_DeleteCutters,
    AEGON_OT_WireframeToggle,
    AEGON_OT_ApplyColorToAll,
    AEGON_OT_LivePreview,
    AEGON_OT_SmartCleanup,
    AEGON_OT_ToggleLang,
    AEGON_OT_AddCube,
    AEGON_OT_AddCylinder,
    AEGON_OT_AddSphere,
    AEGON_OT_ArrayCutter,
    AEGON_OT_AutoMirror,
    AEGON_OT_ModUp,
    AEGON_OT_ModDown,
    AEGON_OT_ModApplySingle,
    AEGON_OT_ModRemoveSingle,
    AEGON_PT_MainPanel,
    AEGON_MT_PieMenu,
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aegon_settings = PointerProperty(type=AEGON_PG_Settings)

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS', shift=True)
        kmi.properties.name = "aegon.pie_menu"
        addon_keymaps.append((km, kmi))


def unregister():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    del bpy.types.Scene.aegon_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()