from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from rembg import remove
from PIL import Image, ImageEnhance
import io
import json
import os

app = FastAPI()

# CORS allow करना ज़रूरी है ताकि Frontend और Backend बात कर सकें
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# डेटा स्टोर करने के लिए एक छोटी फाइल (Honor Wall के लिए)
DB_FILE = "honor_wall.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

# --- ROUTES ---

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    bg_color: str = Form("#000000"),
    canvas_size: str = Form("original")
):
    try:
        # 1. Image को Read करें
        input_image = Image.open(io.BytesIO(await file.read()))
        
        # 2. Background Remove करें
        output_image = remove(input_image)
        
        # 3. Brightness और Contrast Adjust करें
        enhancer_b = ImageEnhance.Brightness(output_image)
        output_image = enhancer_b.enhance(brightness)
        
        enhancer_c = ImageEnhance.Contrast(output_image)
        output_image = enhancer_c.enhance(contrast)

        # 4. Final Processing (RGBA to RGB with BG Color)
        final_img = Image.new("RGBA", output_image.size, bg_color)
        final_img.paste(output_image, (0, 0), output_image)
        final_img = final_img.convert("RGB")

        # 5. Response भेजें
        img_byte_arr = io.BytesIO()
        final_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-honor-wall")
async def get_wall():
    with open(DB_FILE, "r") as f:
        return json.load(f)

@app.post("/add-honor")
async def add_honor(name: str = Form(...), amount: str = Form(...)):
    with open(DB_FILE, "r+") as f:
        data = json.load(f)
        data.append({"name": name, "amount": amount})
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)