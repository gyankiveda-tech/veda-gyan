from rembg import remove, new_session
from PIL import Image, ImageEnhance, ImageOps, ImageFilter, ImageDraw, ImageFont
import io
import numpy as np
import os

class BackgroundRemover:
    def __init__(self):
        """
        AI Studio Neural Engine v4.5 (Render Optimized Edition)
        Features: Tiny Model (u2netp), CPU Matting, Memory Safe Upscaling
        """
        print("🚀 Initializing AI Studio Engine (Optimized for Render)...")
        # 'u2netp' is the tiny version of the model. 
        # Crucial for staying within Render's 512MB RAM limit.
        self.model_name = "u2netp" 
        try:
            # Force CPU Execution to prevent "No onnxruntime backend" error on Render
            self.session = new_session(self.model_name, providers=['CPUExecutionProvider'])
            print(f"✅ Status: Neural Engine Ready | Mode: CPU | Model: {self.model_name}")
        except Exception as e:
            print(f"❌ Initialization Error: {e}")
            self.session = None # Fallback

    def process(self, image_bytes, bg_color=None, bg_image_bytes=None, brightness=1.0, contrast=1.0, sharpness=1.0, canvas_size=None, text_overlay=None, upscale=True):
        """
        The Master Processing Pipeline - Optimized for Low RAM
        """
        try:
            # --- PHASE 1: ASSET LOADING ---
            print("📸 Step 1: Loading Source Asset...")
            input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            
            # --- PHASE 2: NEURAL SEGMENTATION ---
            print("🧠 Step 2: Running AI Deep Matting (Tiny Model Mode)...")
            # If session failed in init, try simple remove
            no_bg_image = remove(
                input_image, 
                session=self.session if self.session else None,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )

            # --- PHASE 3: HD UPSCALING (Memory Optimized) ---
            if upscale:
                print("💎 Step 3: Executing HD Upscaling...")
                width, height = no_bg_image.size
                # Render limit alert: We use 1.5x instead of 2x to save RAM if image is large
                # If image is more than 2MP, scale down the factor to avoid OOM (Out of Memory)
                scale_factor = 1.5 if (width * height) > 2000000 else 2
                no_bg_image = no_bg_image.resize((int(width * scale_factor), int(height * scale_factor)), Image.Resampling.LANCZOS)
                no_bg_image = no_bg_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

            processed_fg = no_bg_image

            # --- PHASE 4: AMBIENT COLOR SYNC ---
            if bg_image_bytes or (bg_color and bg_color != "transparent"):
                print("🎨 Step 4: Synchronizing Lighting...")
                processed_fg = ImageEnhance.Color(processed_fg).enhance(1.15)
                processed_fg = ImageEnhance.Contrast(processed_fg).enhance(1.05)

            # --- PHASE 5: NEURAL TUNING ---
            print("⚙️ Step 5: Applying User Corrections...")
            brightness, contrast, sharpness = float(brightness), float(contrast), float(sharpness)
            
            if brightness != 1.0:
                processed_fg = ImageEnhance.Brightness(processed_fg).enhance(brightness)
            if contrast != 1.0:
                processed_fg = ImageEnhance.Contrast(processed_fg).enhance(contrast)
            if sharpness != 1.0:
                processed_fg = ImageEnhance.Sharpness(processed_fg).enhance(sharpness)

            processed_fg = processed_fg.filter(ImageFilter.SMOOTH_MORE)

            # --- PHASE 6: CANVAS ARCHITECTURE ---
            print("🏗️ Step 6: Constructing Environment...")
            target_size = processed_fg.size
            if canvas_size and canvas_size != "original":
                cw, ch = map(int, canvas_size.split('x'))
                target_size = (cw, ch)

            if bg_image_bytes:
                final_bg = Image.open(io.BytesIO(bg_image_bytes)).convert("RGBA")
                final_bg = final_bg.resize(target_size, Image.Resampling.LANCZOS)
                print("🎬 Applying Depth Bokeh...")
                final_bg = final_bg.filter(ImageFilter.GaussianBlur(radius=4))
            elif bg_color and bg_color not in ["", "transparent"]:
                final_bg = Image.new("RGBA", target_size, bg_color)
            else:
                final_bg = Image.new("RGBA", target_size, (0, 0, 0, 0))

            # --- PHASE 7: CONTACT SHADOW ---
            print("🌑 Step 7: Injecting Shadows...")
            bg_w, bg_h = target_size
            fg_w, fg_h = processed_fg.size
            
            scale_ratio = min(bg_w / fg_w, bg_h / fg_h)
            new_fg_size = (int(fg_w * scale_ratio), int(fg_h * scale_ratio))
            processed_fg = processed_fg.resize(new_fg_size, Image.Resampling.LANCZOS)

            offset_x = (bg_w - new_fg_size[0]) // 2
            offset_y = (bg_h - new_fg_size[1]) // 2

            if bg_image_bytes or bg_color:
                shadow_layer = Image.new("RGBA", target_size, (0, 0, 0, 0))
                alpha_mask = processed_fg.split()[3]
                shadow_color = Image.new("RGBA", new_fg_size, (0, 0, 0, 115))
                shadow_layer.paste(shadow_color, (offset_x + 8, offset_y + 12), alpha_mask)
                # Reduced blur radius to save CPU cycles on Render
                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15)) 
                final_bg.paste(shadow_layer, (0, 0), shadow_layer)

            # --- PHASE 8: FINAL COMPOSITION ---
            final_bg.paste(processed_fg, (offset_x, offset_y), processed_fg)

            # --- PHASE 9: TYPOGRAPHY (Render/Linux Fix) ---
            if text_overlay and text_overlay.strip() != "":
                print(f"✍️ Step 9: Rendering Typography...")
                draw = ImageDraw.Draw(final_bg)
                f_size = int(bg_h * 0.10)
                try:
                    # Linux servers usually have DejaVuSans or LiberationSans
                    font_paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arialbd.ttf"]
                    font = None
                    for path in font_paths:
                        if os.path.exists(path):
                            font = ImageFont.truetype(path, f_size)
                            break
                    if not font: font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
                
                txt = text_overlay.upper()
                l, t, r, b = draw.textbbox((0, 0), txt, font=font)
                tw, th = r - l, b - t
                tx = (bg_w - tw) // 2
                ty = bg_h - th - int(bg_h * 0.10)

                draw.text((tx + 3, ty + 3), txt, font=font, fill=(0, 0, 0, 160))
                draw.text((tx, ty), txt, font=font, fill="white", stroke_width=1, stroke_fill="black")

            # --- PHASE 10: EXPORT ---
            print("🚀 Step 10: Dispatching Asset!")
            return final_bg.convert("RGB") if (bg_color or bg_image_bytes) else final_bg

        except Exception as e:
            print(f"❌ Critical Failure: {e}")
            raise e

    def apply_hd_cleanup(self, image):
        if image.mode == 'RGB':
            image = ImageOps.autocontrast(image, cutoff=0.5)
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.25)
        return image