from fastapi import APIRouter, UploadFile , File , HTTPException
import io 
from typing import List
from app.models.schemas import PredictionSummary,YoloPredictions,DefectsCount
from app.services.yolo_engine import Predictor
from app.utils.validators import validate_upload,last_validation
from app.core.config import logger

router=APIRouter()
yolo_service=Predictor()

@router.post("/predict",response_model=PredictionSummary)
async def predict_defects(file: List[UploadFile] = File(...)
):
    try:
        file=validate_upload(file)
        ready_images,img_ids=last_validation(file)
        predicted_images=yolo_service.predict(ready_images)
        results=[]
        for img , id in zip(predicted_images,img_ids) :
            
            img_id,image_class,image_link=yolo_service.save_predicted_images(img,id)
            results.append({
                'id':img_id,
                'defects':image_class,
                'image_link':image_link
            })

                
            
        counts={'crazing':0,'inclusion':0,'patches':0,'pitted_surface':0,'rolled_in_scale':0,'rolled_in_scale':0,'scratches':0}
        for defect in results:
            class_key=defect['defects']
            if class_key in counts:
                counts[class_key]+=1
        
        return PredictionSummary(
            crazing=counts['crazing'],
            inclusion= counts['inclusion'],
            patches= counts['patches'],
            pitted_surface= counts['pitted_surface'],
            rolled_in_scale= counts['rolled_in_scale'],
            scratches= counts['scratches'],
            
            dashboard= results
        )
    except Exception as he : 
        raise he
    except Exception as e :
        logger.exception("Unexpected internal processing error during final Prediction")
        raise HTTPException(500,f"internal processing error :{str(e)}")


