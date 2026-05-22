from fastapi import UploadFile , HTTPException
from pathlib import Path
from PIL import Image
import io, zipfile
import magic
from app.core.config import logger
from typing import List

allowed_extensions = {".zip",".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
min_dim,max_dim= 32,8000
min_ratio,max_ratio= 0.2,5.0
non_image={".zip",".pdf", ".txt",".exe"}

def validate_file(img_id: str , content:bytes) : 
    
    try:
        img=Image.open(io.BytesIO(content))
        img.load()
    except Exception as e:
        logger.exception(f"{img_id} is not a valid image.")
        raise HTTPException(400 , f"{img_id} is not a valid image. {e}")
    # check dimensions
    w,h=img.size
    if w < min_dim or h <min_dim:
        logger.error(f"the image {img_id} is too small ({w}x{h}px). YOLO needs at least ({min_dim}px) per side .  ")
        raise HTTPException(400 , f"the image {img_id} is too small ({w}x{h}px). YOLO needs at least ({min_dim}px) per side .  ")
    if w > max_dim or h> max_dim : 
        logger.error(f"the image {img_id} is too large ({w}x{h}px). YOLO needs MAX ({max_dim}px) per side .  ")
        raise HTTPException(400 , f"the image {img_id} is too large ({w}x{h}px). YOLO needs MAX ({max_dim}px) per side .  ")
    ratio= w/h
    if not (min_ratio <= ratio <= max_ratio ) :
        logger.error(f"{img_id} extreme aspect ratio ({ratio:.2f}).Keep between {min_ratio} – {max_ratio}")   
        raise HTTPException(400 , f"{img_id} extreme aspect ratio ({ratio:.2f}).Keep between {min_ratio} – {max_ratio}")
    #check color mode 
    if img.mode in ("L","RGBA","P") or  img.mode != "RGB":
        img = img.convert("RGB")
    

    return img


def validate_folder(file:UploadFile):
    contents=file.file.read()
    file.file.seek(0)
    filename=file.filename
    if not zipfile.is_zipfile(io.BytesIO(contents)):
        logger.error("the folder is not a zip folder")
        raise HTTPException(400,f"the folder{filename} is not a zip folder")
    valid_images = []
    with zipfile.ZipFile(io.BytesIO(contents)) as zf : 
        for val_image in zf.infolist() :
            img_id = val_image.filename
            if img_id.startswith("__MACOSX") or img_id.startswith(".") or img_id.endswith("/"):
                continue
            ext=Path(img_id).suffix.lower()
            if ext not in allowed_extensions:
                if ext in non_image:
                    logger.error(f"this file {img_id} has been skipped ")
                    continue
                else:
                    logger.error(f"Unsupported file {img_id} inside ZIP")
                    raise HTTPException(400,f"Unsupported file {img_id} inside ZIP")
                    
            valid_images.append((img_id, zf.read(val_image)))
    if not valid_images :
        logger.error("the folder uploaded has no valid images")
        raise HTTPException(400,"the folder uploaded has no valid images")
    return valid_images

def validate_upload(file: List[UploadFile]):
    for f in file:
        if not file :
            logger.error("no files uploaded")
            raise HTTPException(400,"no files uploaded")
        
        filename= f.filename
        ext = Path(filename).suffix.lower()
        if ext not in allowed_extensions:
            logger.error("File format not supported ")
            raise HTTPException(400, f"Unsupported format '{ext}'. Allowed: {allowed_extensions}")
    return file
def last_validation(file: List[UploadFile]) :
    ready_images=[]
    img_ids = []
    if not file :
        logger.error("no files uploaded")
        raise HTTPException(400,"no files uploaded")
    for f in file:
        filename= f.filename
        ext = Path(filename).suffix.lower()
        if ext not in allowed_extensions:
            logger.error("File format not supported ")
            raise HTTPException(400, f"Unsupported format '{ext}'. Allowed: {allowed_extensions}")
        #validating a zip file
        
        if (ext==".zip"):
            valid_images=validate_folder(f)
            for img_id,contents in valid_images:
                valid_image = validate_file(img_id,contents)
                ready_images.append(valid_image)
                img_ids.append(img_id)
        #validating a single image
        elif ( ext in allowed_extensions):
            contents=f.file.read()
            f.file.seek(0)
            img_id=f.filename
            valid_image=validate_file(img_id,contents)
            ready_images.append(valid_image)
            img_ids.append(img_id)
        else:
            continue
    return ready_images,img_ids




