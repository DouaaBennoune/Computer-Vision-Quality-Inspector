from dotenv import load_dotenv
from pathlib import Path
from app.core.config import logger
import os
from PIL import Image
from fastapi import HTTPException
from ultralytics import YOLO

load_dotenv()

class Predictor:
    def __init__(self):
        model_path=Path(os.getenv("model_path"))
        if model_path.exists():
            self.model=YOLO(model_path)
            logger.info("model path found , model has been loaded ")
        else : 
            logger.info("model path not found , model hasnt been loaded")
            raise HTTPException(400,f"model path : {model_path} , not found !")
     
    
    def predict(self,file):
        """ returns predicted images as YOLO object """
        try:
            predicted_images = self.model.predict(file)
        except Exception as e :
            logger.error(f"prediction failed! {e}")
            raise RuntimeError(f"model prediction failed . {e}")
        return predicted_images
    
    def save_predicted_images(self,predicted_image,img_id):
            """ returns the id , class , image link of the predicted images"""
            predictions_dir=Path("static/predictions")
            predictions_dir.mkdir(parents=True,exist_ok=True)
            Base_url="http://localhost:8000"
            images_boxes=predicted_image.plot()
            image_classes=predicted_image.names[1]
            
            img=Image.fromarray(images_boxes)
            save_path=predictions_dir/img_id
            img.save(save_path)
            image_link=f"{Base_url}/static/predictions/{img_id}"
            return img_id,image_classes,image_link
            
            #.boxes
            #.probs Class probabilities.
            #.names Class name mapping.
            #.plot() Returns an annotated image (numpy array).
