import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import json
import os
from typing import Optional
from processor import BackgroundRemover

app = FastAPI(title="VEDA VERSE | Neural Engine & Shagun System")

# --- CORS Setup (ताकि Frontend Backend से बात कर सके) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Files & Database Setup ---
DB_FILE = "honor_wall.json"

def initialize_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)

initialize_db()

# --- Initialize AI Engine ---
try:
    remover = BackgroundRemover()
except Exception as e:
    print(f"⚠️ Warning: Could not initialize AI engine: {e}")
    remover = None

@app.get("/")
def home():
    return {
        "status": "Online",
        "engine": "Veda Verse Neural Engine 🚀",
        "db_status": "Connected"
    }

# --- 1. IMAGE PROCESSING ENDPOINT ---
@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...),
    bg_image: Optional[UploadFile] = File(None),
    bg_color: Optional[str] = Form(None),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    sharpness: float = Form(1.0),
    canvas_size: Optional[str] = Form("original"),
    text_overlay: Optional[str] = Form(None),
    upscale: bool = Form(True)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid Asset: Must be an image.")

    if not remover:
        raise HTTPException(status_code=500, detail="Neural Engine is offline.")

    try:
        contents = await file.read()
        bg_image_bytes = None
        if bg_image:
            bg_image_bytes = await bg_image.read()
        
        # मास्टर न्यूरल लॉजिक - processor.py से कॉल हो रहा है
        processed_image = remover.process(
            image_bytes=contents,
            bg_color=bg_color,
            bg_image_bytes=bg_image_bytes,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            canvas_size=canvas_size,
            text_overlay=text_overlay,
            upscale=upscale
        )
        
        # HD Cleanup
        processed_image = remover.apply_hd_cleanup(processed_image)
        
        # इमेज को बाइट्स में बदलें ताकि यूजर को वापस भेज सकें
        img_byte_arr = io.BytesIO()
        processed_image.save(img_byte_arr, format='PNG', optimize=True, quality=100)
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")

    except Exception as e:
        print(f"❌ Engine Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. HONOR WALL & SHAGUN SYSTEM ---

@app.get("/get-honor-wall")
async def get_wall():
    try:
        if not os.path.exists(DB_FILE):
            return []
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

@app.post("/add-honor")
async def add_honor(
    name: str = Form(...), 
    amount: str = Form(...),
    txn_id: Optional[str] = Form("MANUAL")
):
    try:
        # डेटा लोड करना
        data = []
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        
        # न्यू एंट्री तैयार करना
        new_entry = {
            "name": name.strip().upper(),
            "amount": amount,
            "txn_id": txn_id.strip() if txn_id else "MANUAL",
            "status": "APPROVED",
            "timestamp": os.path.getmtime(DB_FILE) if os.path.exists(DB_FILE) else 0
        }
        
        # डेटा को लिस्ट के शुरू में जोड़ना ताकि लेटेस्ट पहले दिखे
        data.insert(0, new_entry)
        
        # सुरक्षित रूप से सेव करना
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
            
        return {"status": "success", "message": f"Added {name} to Honor Wall"}
    except Exception as e:
        print(f"❌ DB Write Error: {e}")
        return {"status": "error", "message": "Failed to save data"}

if __name__ == "__main__":
    # Reload=True सिर्फ़ डेवलपमेंट के लिए है
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)