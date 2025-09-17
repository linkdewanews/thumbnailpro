import flet as ft
import os
import cv2
from PIL import Image
import math
import shutil
import time
import threading
import sys
import subprocess
import numpy as np

# =================================================================================================
# BAGIAN 1: FUNGSI LOGIKA UTAMA
# =================================================================================================

def open_folder_in_explorer(path):
    if sys.platform == "win32": os.startfile(path)
    elif sys.platform == "darwin": subprocess.Popen(["open", path])
    else: subprocess.Popen(["xdg-open", path])

def apply_watermark(pil_image, text, position):
    if not text: return pil_image
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    h, w, _ = cv_image.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = min(w, h) / 900
    font_thickness = int(font_scale * 1.8)
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
    margin = int(min(w,h) * 0.03)
    positions = {
        "Pojok Kiri Atas": (margin, margin + text_h),
        "Pojok Kanan Atas": (w - text_w - margin, margin + text_h),
        "Pojok Kiri Bawah": (margin, h - margin),
        "Pojok Kanan Bawah": (w - text_w - margin, h - margin),
        "Tengah": ((w - text_w) // 2, (h + text_h) // 2)
    }
    org = positions.get(position, positions["Pojok Kanan Bawah"])
    cv2.putText(cv_image, text, (org[0]+2, org[1]+2), font, font_scale, (0,0,0), font_thickness, cv2.LINE_AA)
    cv2.putText(cv_image, text, org, font, font_scale, (255,255,255), font_thickness, cv2.LINE_AA)
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

def process_videos_in_thread(page, folder_path_input, aspect_ratio_choice, watermark_text, watermark_pos, log_view, progress_bar, progress_text, process_button, open_folder_button):
    def log(message, icon=ft.Icons.INFO_OUTLINE, color=ft.Colors.WHITE70):
        log_entry = ft.Row([ft.Icon(name=icon, color=color, size=14), ft.Text(message, font_family="Roboto Mono", size=12, color=color, expand=True, selectable=True)], opacity=0, animate_opacity=200)
        log_view.controls.append(log_entry)
        page.update(); time.sleep(0.05); log_entry.opacity = 1; page.update()

    try:
        log_view.controls.clear(); progress_bar.value = None; progress_text.value = "Menyiapkan..."; page.update()
        output_folder_name = "Thumbnail Results"
        main_output_folder = os.path.join(folder_path_input, output_folder_name)
        os.makedirs(main_output_folder, exist_ok=True)
        thumb_w, thumb_h, cols, rows = (1080, 1080, 3, 3) if aspect_ratio_choice == '1:1' else (1080, 1920, 4, 4)
        log(f"Mode: {aspect_ratio_choice}, Grid: {cols}x{rows}", icon=ft.Icons.SETTINGS_ROUNDED, color="#22d3ee")
        if watermark_text: log(f"Watermark: '{watermark_text}' di {watermark_pos}", icon=ft.Icons.BRANDING_WATERMARK, color="#22d3ee")
        video_files = [f for f in os.listdir(folder_path_input) if os.path.isfile(os.path.join(folder_path_input, f)) and f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm'))]
        if not video_files: log("Tidak ada file video ditemukan.", icon=ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_300); progress_bar.value = 0; progress_text.value = "Gagal"
        for i, filename in enumerate(video_files):
            progress_value = (i + 1) / len(video_files); progress_bar.value = progress_value; progress_text.value = f"{progress_value:.0%}"; page.update()
            file_name_no_ext = os.path.splitext(filename)[0]
            specific_result_folder = os.path.join(main_output_folder, file_name_no_ext)
            if os.path.exists(specific_result_folder): log(f"'{filename}' sudah ada, dilewati.", icon=ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=ft.Colors.GREEN_ACCENT_400); continue
            log(f"Memproses '{filename}'...", icon=ft.Icons.ROCKET_LAUNCH_OUTLINED, color=ft.Colors.CYAN_300)
            os.makedirs(specific_result_folder, exist_ok=True)
            vid = cv2.VideoCapture(os.path.join(folder_path_input, filename))
            total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
            vid.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
            ret_orig, frame_orig_bgr = vid.read()
            if ret_orig:
                img_orig = Image.fromarray(cv2.cvtColor(frame_orig_bgr, cv2.COLOR_BGR2RGB)).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                img_orig = apply_watermark(img_orig, watermark_text, watermark_pos)
                img_orig.save(os.path.join(specific_result_folder, "thumbnail_original.jpg"))
            collage_frames = [Image.fromarray(cv2.cvtColor(vid.read()[1], cv2.COLOR_BGR2RGB)) for i_frame in range(cols*rows) if vid.set(cv2.CAP_PROP_POS_FRAMES, math.floor(total_frames * (i_frame + 1) / ((cols*rows) + 1))) and vid.read()[0]]
            if not collage_frames: raise Exception("Gagal ambil frame.")
            if len(collage_frames) < cols*rows: 
                log(f"Video '{filename}' pendek, frame diduplikasi.", icon=ft.Icons.INFO_OUTLINE_ROUNDED, color=ft.Colors.AMBER_300)
                i_dup = 0
                while len(collage_frames) < cols*rows: collage_frames.append(collage_frames[i_dup]); i_dup = (i_dup + 1) % len(collage_frames)
            collage_image = Image.new('RGB', (thumb_w, thumb_h))
            cell_w, cell_h = thumb_w // cols, thumb_h // rows
            for idx, frame in enumerate(collage_frames):
                frame = frame.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
                collage_image.paste(frame, ((idx % cols) * cell_w, (idx // rows) * cell_h))
            collage_image = apply_watermark(collage_image, watermark_text, watermark_pos)
            collage_image.save(os.path.join(specific_result_folder, f"thumbnail_collage_{cols}x{rows}.jpg"))
            vid.release()
            shutil.move(os.path.join(folder_path_input, filename), os.path.join(specific_result_folder, filename))
        log("Semua video selesai diproses!", icon=ft.Icons.CELEBRATION_ROUNDED, color="#10B981")
        open_folder_button.data = main_output_folder; open_folder_button.disabled = False
    except Exception as e: log(f"ERROR: {e}", icon=ft.Icons.ERROR_OUTLINE_ROUNDED, color=ft.Colors.RED_ACCENT_400); progress_bar.value = 0; progress_text.value = "Error!"
    finally: process_button.disabled = False; page.update()

# =================================================================================================
# BAGIAN 2: DESAIN FINAL (Layout Dua Kolom)
# =================================================================================================

def main(page: ft.Page):
    page.title = "Thumbnail Generator Pro"
    page.window_width = 1200; page.window_height = 800; page.window_min_width = 1100; page.window_min_height = 750
    page.padding = 0

    # --- PALET WARNA & GAYA KONSISTEN ---
    ACCENT_COLOR = "#22d3ee"; BG_COLOR = "#1f2630"; SURFACE_COLOR = "#2c3440"; BORDER_COLOR = ft.Colors.WHITE24
    page.bgcolor = BG_COLOR; page.theme_mode = ft.ThemeMode.DARK; page.fonts = {"Roboto Mono": "https://fonts.google.com/specimen/Roboto+Mono"}; page.theme = ft.Theme(color_scheme_seed=ACCENT_COLOR)

    selected_ratio = ft.Text("9:16", visible=False)

    def pick_folder_dialog(e): folder_picker.get_directory_path(dialog_title="Pilih Folder Video")
    def on_folder_picked(e: ft.FilePickerResultEvent): 
        if e.path: folder_path_field.value = e.path; process_button.disabled = False; page.update()
    def start_processing(e):
        if not folder_path_field.value: page.snack_bar = ft.SnackBar(content=ft.Text("Pilih folder dulu, bre!"), bgcolor="#D32F2F"); page.snack_bar.open = True; page.update(); return
        process_button.disabled = True; open_folder_button.disabled = True; page.update()
        threading.Thread(target=process_videos_in_thread, args=(page, folder_path_field.value, selected_ratio.value, watermark_field.value, watermark_pos_dropdown.value, log_view, progress_bar, progress_text, process_button, open_folder_button), daemon=True).start()
    def open_result_folder(e): 
        if e.control.data and os.path.exists(e.control.data): open_folder_in_explorer(e.control.data)

    folder_picker = ft.FilePicker(on_result=on_folder_picked); page.overlay.append(folder_picker)

    # --- KONTROL UI ---
    folder_path_field = ft.TextField(label="Folder Video", read_only=True, expand=True, border_color=BORDER_COLOR)
    def select_ratio_handler(e): selected_ratio.value = e.control.data; update_selector_styles(); page.update()
    def create_ratio_selector(ratio_value, icon, text):
        return ft.Container(content=ft.Column([ft.Icon(icon, size=20), ft.Text(text, weight=ft.FontWeight.BOLD, size=11)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=5), expand=True, height=75, alignment=ft.alignment.center, border_radius=ft.border_radius.all(8), data=ratio_value, on_click=select_ratio_handler, animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT))
    portrait_selector = create_ratio_selector("9:16", ft.Icons.STAY_CURRENT_PORTRAIT_ROUNDED, "Portrait 9:16"); square_selector = create_ratio_selector("1:1", ft.Icons.CROP_SQUARE_ROUNDED, "Square 1:1")
    def update_selector_styles():
        is_portrait = selected_ratio.value == "9:16"
        portrait_selector.bgcolor = SURFACE_COLOR; portrait_selector.border = ft.border.all(2, ACCENT_COLOR) if is_portrait else ft.border.all(1, BORDER_COLOR)
        square_selector.bgcolor = SURFACE_COLOR; square_selector.border = ft.border.all(2, ACCENT_COLOR) if not is_portrait else ft.border.all(1, BORDER_COLOR)
    update_selector_styles()
    watermark_field = ft.TextField(label="Teks Watermark (Opsional)", border_color=BORDER_COLOR)
    watermark_pos_dropdown = ft.Dropdown(options=[ft.dropdown.Option(p) for p in ["Pojok Kanan Bawah", "Pojok Kiri Atas", "Pojok Kanan Atas", "Pojok Kiri Bawah", "Tengah"]], value="Pojok Kanan Bawah", border_color=BORDER_COLOR)
    progress_text = ft.Text("Menunggu...", color=ft.Colors.WHITE70); progress_bar = ft.ProgressBar(value=0, bar_height=8, color=ACCENT_COLOR, bgcolor=BG_COLOR, expand=True)
    log_view = ft.ListView(expand=True, spacing=8, auto_scroll=True, padding=ft.padding.only(left=10, right=5))
    process_button = ft.FilledButton("Mulai Proses", icon=ft.Icons.PLAY_ARROW_ROUNDED, on_click=start_processing, disabled=True, style=ft.ButtonStyle(padding=ft.padding.symmetric(vertical=15, horizontal=25), shape=ft.RoundedRectangleBorder(radius=8)))
    open_folder_button = ft.OutlinedButton("Buka Hasil", icon=ft.Icons.FOLDER_OPEN_ROUNDED, on_click=open_result_folder, disabled=True, style=ft.ButtonStyle(padding=ft.padding.symmetric(vertical=15, horizontal=20), shape=ft.RoundedRectangleBorder(radius=8)))

    # --- STRUKTUR LAYOUT DUA KOLOM ---
    page.appbar = ft.AppBar(leading=ft.Icon(ft.Icons.MOVIE_FILTER_SHARP, color=ACCENT_COLOR), leading_width=50, title=ft.Text("Thumbnail Generator Pro", font_family="Roboto Mono", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), bgcolor=SURFACE_COLOR)

    control_panel = ft.Container(
        content=ft.Column([
            ft.Text("1. Input Folder", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
            ft.Row([folder_path_field, ft.OutlinedButton("Pilih...", on_click=pick_folder_dialog, style=ft.ButtonStyle(color=ACCENT_COLOR, side=ft.BorderSide(1, ACCENT_COLOR)))]),
            ft.Divider(height=25, color="transparent"),
            ft.Text("2. Orientasi Output", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
            ft.Row([portrait_selector, square_selector], spacing=20),
            ft.Divider(height=25, color="transparent"),
            ft.Text("3. Watermark (Opsional)", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
            watermark_field,
            watermark_pos_dropdown,
            ft.Divider(height=35, color="transparent"),
            ft.Row([open_folder_button, process_button], alignment=ft.MainAxisAlignment.END),
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=ft.padding.symmetric(horizontal=30, vertical=25),
    )

    log_panel = ft.Container(
        content=ft.Column([
            ft.Text("Progres & Log", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
            ft.Row([progress_bar, progress_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            ft.Container(log_view, expand=True, bgcolor=SURFACE_COLOR, border_radius=8, padding=12, margin=ft.margin.only(top=10)),
        ]),
        padding=ft.padding.symmetric(horizontal=30, vertical=25),
    )

    page.add(
        ft.Row(
            [
                ft.Column([control_panel], expand=5),
                ft.VerticalDivider(),
                ft.Column([log_panel], expand=7),
            ],
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)