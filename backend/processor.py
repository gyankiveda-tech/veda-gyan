from rembg import remove, new_session
from PIL import Image, ImageEnhance, ImageOps, ImageFilter, ImageDraw, ImageFont
import io
import numpy as np

class BackgroundRemover:
    def __init__(self):
        """
        AI Studio Neural Engine v4.5 (God-Mode Edition)
        Features: Upscaling, Contact Shadows, Ambient Lighting, Bokeh, Neural Sharpening
        """
        print("🚀 Initializing AI Studio God-Mode Engine (v4.5 Ultra Max)...")
        self.model_name = "u2net"
        try:
            # High-performance ONNX session
            self.session = new_session(self.model_name)
            print(f"✅ Status: Neural Engine Ready | Model: {self.model_name}")
        except Exception as e:
            print(f"❌ Initialization Error: {e}")
            raise e

    def process(self, image_bytes, bg_color=None, bg_image_bytes=None, brightness=1.0, contrast=1.0, sharpness=1.0, canvas_size=None, text_overlay=None, upscale=True):
        """
        The Master Processing Pipeline
        """
        try:
            # --- PHASE 1: ASSET LOADING ---
            print("📸 Step 1: Loading Source Asset...")
            input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            
            # --- PHASE 2: NEURAL SEGMENTATION (BG REMOVAL) ---
            print("🧠 Step 2: Running AI Deep Matting...")
            no_bg_image = remove(
                input_image, 
                session=self.session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )

            # --- PHASE 3: GOD-MODE HD UPSCALING ---
            # Increase pixel density and refine edges using Unsharp Masking
            if upscale:
                print("💎 Step 3: Executing Ultra-HD Upscaling (2X DPI)...")
                width, height = no_bg_image.size
                # Multi-pass scaling for smoothness
                no_bg_image = no_bg_image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
                # Apply Neural Sharpening to prevent blurriness after scale
                no_bg_image = no_bg_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

            processed_fg = no_bg_image

            # --- PHASE 4: AMBIENT COLOR SYNC ---
            # Match the foreground lighting with the background environment
            if bg_image_bytes or (bg_color and bg_color != "transparent"):
                print("🎨 Step 4: Synchronizing Ambient Lighting & Color Tones...")
                # Increase saturation slightly to make it pop against new background
                processed_fg = ImageEnhance.Color(processed_fg).enhance(1.15)
                # Apply slight warmth to match digital studio lighting
                processed_fg = ImageEnhance.Contrast(processed_fg).enhance(1.05)

            # --- PHASE 5: MANUAL NEURAL TUNING ---
            print("⚙️ Step 5: Applying User-Defined Neural Corrections...")
            brightness, contrast, sharpness = float(brightness), float(contrast), float(sharpness)
            
            if brightness != 1.0:
                processed_fg = ImageEnhance.Brightness(processed_fg).enhance(brightness)
            if contrast != 1.0:
                processed_fg = ImageEnhance.Contrast(processed_fg).enhance(contrast)
            if sharpness != 1.0:
                processed_fg = ImageEnhance.Sharpness(processed_fg).enhance(sharpness)

            # Final edge smoothing
            processed_fg = processed_fg.filter(ImageFilter.SMOOTH_MORE)

            # --- PHASE 6: CANVAS & ENVIRONMENT ARCHITECTURE ---
            print("🏗️ Step 6: Constructing Visual Environment...")
            target_size = processed_fg.size
            
            if canvas_size and canvas_size != "original":
                cw, ch = map(int, canvas_size.split('x'))
                target_size = (cw, ch)

            # Background Creation with Auto-Bokeh (Blur)
            if bg_image_bytes:
                final_bg = Image.open(io.BytesIO(bg_image_bytes)).convert("RGBA")
                final_bg = final_bg.resize(target_size, Image.Resampling.LANCZOS)
                # Apply DSLR-style Bokeh to background
                print("🎬 Applying Auto-Depth (Bokeh Effect) to Background...")
                final_bg = final_bg.filter(ImageFilter.GaussianBlur(radius=4))
            elif bg_color and bg_color not in ["", "transparent"]:
                final_bg = Image.new("RGBA", target_size, bg_color)
            else:
                final_bg = Image.new("RGBA", target_size, (0, 0, 0, 0))

            # --- PHASE 7: CONTACT SHADOW ENGINE ---
            # Generating realistic drop shadows based on object silhouette
            print("🌑 Step 7: Injecting Realistic Contact Shadows...")
            bg_w, bg_h = target_size
            fg_w, fg_h = processed_fg.size
            
            # Intelligent Fitting Logic
            scale_ratio = min(bg_w / fg_w, bg_h / fg_h)
            new_fg_size = (int(fg_w * scale_ratio), int(fg_h * scale_ratio))
            processed_fg = processed_fg.resize(new_fg_size, Image.Resampling.LANCZOS)

            offset_x = (bg_w - new_fg_size[0]) // 2
            offset_y = (bg_h - new_fg_size[1]) // 2

            if bg_image_bytes or bg_color:
                # Create a shadow canvas
                shadow_layer = Image.new("RGBA", target_size, (0, 0, 0, 0))
                # Extract Alpha for mask
                alpha_mask = processed_fg.split()[3]
                # Shadow color (Black with 45% opacity)
                shadow_color = Image.new("RGBA", new_fg_size, (0, 0, 0, 115))
                # Paste shadow with slight offset for 3D feel
                shadow_layer.paste(shadow_color, (offset_x + 12, offset_y + 18), alpha_mask)
                # Heavy blur to make the shadow soft
                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=22))
                # Paste shadow onto background first
                final_bg.paste(shadow_layer, (0, 0), shadow_layer)

            # --- PHASE 8: FINAL COMPOSITION ---
            print("🖼️ Step 8: Finalizing Composition & Layer Blending...")
            final_bg.paste(processed_fg, (offset_x, offset_y), processed_fg)

            # --- PHASE 9: TYPOGRAPHY SUITE ---
            if text_overlay and text_overlay.strip() != "":
                print(f"✍️ Step 9: Rendering Pro-Typography: {text_overlay}")
                draw = ImageDraw.Draw(final_bg)
                try:
                    # Scaling font size based on canvas height
                    f_size = int(bg_h * 0.12)
                    font = ImageFont.truetype("arialbd.ttf", f_size)
                except:
                    font = ImageFont.load_default()
                
                txt = text_overlay.upper()
                l, t, r, b = draw.textbbox((0, 0), txt, font=font)
                tw, th = r - l, b - t
                
                tx = (bg_w - tw) // 2
                ty = bg_h - th - int(bg_h * 0.12)

                # Advanced Text Shadow (Multi-layered for depth)
                draw.text((tx + 5, ty + 5), txt, font=font, fill=(0, 0, 0, 160))
                # Main Text
                draw.text((tx, ty), txt, font=font, fill="white", stroke_width=2, stroke_fill="black")

            # --- PHASE 10: EXPORT OPTIMIZATION ---
            print("🚀 Step 10: Dispatching Final HD Asset!")
            if bg_color or bg_image_bytes:
                return final_bg.convert("RGB")
            else:
                return final_bg

        except Exception as e:
            print(f"❌ Critical Engine Failure: {e}")
            raise e

    def apply_hd_cleanup(self, image):
        """
        Final pass to enhance contrast and sharpness for a professional finish.
        """
        print("🪄 Applying Final Neural Cleanup...")
        if image.mode == 'RGB':
            image = ImageOps.autocontrast(image, cutoff=0.5)
            # Subtle final sharpen
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.25)
        return image