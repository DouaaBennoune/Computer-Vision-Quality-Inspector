from dotenv import load_dotenv
from pathlib import Path
from backend.core.config import logger
import os
from PIL import Image
from fastapi import HTTPException
from ultralytics import YOLO
import numpy
load_dotenv()

class Predictor:
    def __init__(self):
        env_path = os.getenv("model_path")
        if not env_path:
            logger.error("model_path is missing from the .env file!")
            raise ValueError("model_path is not set in the environment variables.")
        model_path=Path(env_path)
        if model_path.exists():
            self.model=YOLO(model_path)
            logger.info("model path found , model has been loaded ")
        else : 
            logger.info("model hasnt been loaded")
            raise FileNotFoundError(f"model didnt load successfully from {model_path}!")
     
    
    def predict(self,file):
        """ returns predicted images as YOLO object """
        try:
            predicted_images = self.model.predict(file)
        except Exception as e :
            logger.error(f"prediction failed! {e}")
            raise RuntimeError(f"model prediction failed . {e}")
        return predicted_images
    
    def save_predicted_images(self,predicted_image,img_id):
            """ returns the id ,  image link , predicted class and count  in a format that is suited for the Schema DefectsCount"""
            predictions_dir=Path("static/predictions")
            predictions_dir.mkdir(parents=True,exist_ok=True)
            Base_url="http://localhost:8000"

            images_boxes=predicted_image.plot()[..., ::-1] 
            
            img=Image.fromarray(images_boxes)
            #extracting image link
            save_path=predictions_dir/img_id
            img.save(save_path)
            image_link=f"{Base_url}/static/predictions/{img_id}"
            #extracting detected img class with count
            detected_classes=predicted_image.boxes.cls.cpu().numpy()
            names_dict=predicted_image.names
            class_counts = {}
            for cls_id in detected_classes:
                 class_name= names_dict[int(cls_id)]
                 class_counts[class_name]=class_counts.get(class_name,0)+1
            defects_list=[{"defect_class":k,"count":v} for k,v in class_counts.items()]
            return img_id,defects_list,image_link
            
            #.boxes
            #.probs Class probabilities.
            #.names Class name mapping.
            #.plot() Returns an annotated image (numpy array).
