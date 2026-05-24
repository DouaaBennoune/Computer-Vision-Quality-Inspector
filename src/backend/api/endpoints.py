from fastapi import Form,APIRouter, UploadFile , File , HTTPException,Depends
import io 
from pathlib import Path
import os
from dataclasses import dataclass
from typing import List
from backend.models.schemas import PredictionSummary,YoloPredictions,DefectsCount
from backend.services.yolo_engine import Predictor
from backend.utils.validators import validate_upload,last_validation
from backend.core.config import logger

router=APIRouter()
yolo_service=Predictor()


@router.post("/predict",response_model=PredictionSummary)
async def predict_defects(file: List[UploadFile] = File(...)):
    try:

        file=validate_upload(file)
        ready_images,img_ids=last_validation(file)
        predicted_images=yolo_service.predict(ready_images)
        results=[]
        global_counts = {
            'crazing': 0, 'inclusion': 0, 'patches': 0, 
            'pitted_surface': 0, 'rolled_in_scale': 0, 'scratches': 0
        }
        for img , id in zip(predicted_images,img_ids) :
            
            img_id,defects_list,image_link=yolo_service.save_predicted_images(img,id)
            results.append({
                'id':img_id,
                'defects':defects_list,
                'image_link':image_link
            })

                
            
        
            for defect in defects_list:
                class_key=defect['defect_class']
                if class_key in global_counts:
                    global_counts[class_key]+=defect["count"]
        
        return PredictionSummary(
            crazing=global_counts['crazing'],
            inclusion= global_counts['inclusion'],
            patches= global_counts['patches'],
            pitted_surface= global_counts['pitted_surface'],
            rolled_in_scale= global_counts['rolled_in_scale'],
            scratches= global_counts['scratches'],
            
            dashboard= results
        )
    except Exception as he : 
        raise he
    except Exception as e :
        logger.exception("Unexpected internal processing error during final Prediction")
        raise HTTPException(500,f"internal processing error :{str(e)}")
    
        

