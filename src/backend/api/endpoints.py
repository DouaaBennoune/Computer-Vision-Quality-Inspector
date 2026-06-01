from fastapi import Form,APIRouter, UploadFile , File , HTTPException,Depends, WebSocket, WebSocketDisconnect
import io 
from pathlib import Path
import os
from dataclasses import dataclass
from typing import List
from backend.models.schemas import PredictionSummary,YoloPredictions,DefectsCount
from backend.services.yolo_engine import Predictor
from backend.utils.validators import validate_upload,last_validation
from backend.core.config import logger

import cv2
import numpy as np
import base64
import json
import paho.mqtt.publish as publish

router=APIRouter()
yolo_service=Predictor()

# mqtt configuration (PLC Bridge)
mqtt_broker="mqtt-broker"
mqtt_topic="factory/line1/control"
def trigger_factory_alarm(command:str,reason:str):
    """sends a command to the Factory I/O conveyor belt"""
    payload=json.dumps({"command":command,"reason":reason})
    try:
        publish.single(mqtt_topic,payload,hostname=mqtt_broker)
        print(f"MQTT Signal Sent : {command} ({reason})")
    except Exception as e:
        print(f"Failed To Send MQTT Signal: {e}")

# Image detection route
@router.post("/predict",response_model=PredictionSummary)
async def predict_defects(file: List[UploadFile] = File(...)):
    try:

        file=validate_upload(file)
        ready_images,img_ids=last_validation(file)
        predicted_images=yolo_service.predict(ready_images)
        results=[]
        global_counts = {
            'crazing': 0, 'inclusion': 0, 'patches': 0, 
            'pitted_surface': 0, 'rolled-in_scale': 0, 'scratches': 0
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
            rolled_in_scale= global_counts['rolled-in_scale'],
            scratches= global_counts['scratches'],
            
            dashboard= results
        )
    except Exception as he : 
        raise he
    except Exception as e :
        logger.exception("Unexpected internal processing error during final Prediction")
        raise HTTPException(500,f"internal processing error :{str(e)}")

# Live Video route for Factory (PLC) Simulation
@router.websocket("/ws/simulation")
async def websocket_simulation(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data=await websocket.receive_text()
            img_bytes=base64.b64decode(data)
            np_arr=np.frombuffer(img_bytes,np.uint8)
            img= cv2.imdecode(np_arr,cv2.IMREAD_COLOR)

            predicted_image=yolo_service.model.predict(img,verbose=False)[0]
            annotated_image=predicted_image.plot()[...,::-1]

            detected_classes=predicted_image.boxes.cls.cpu().numpy()
            names_dict=predicted_image.names
            class_counts={}
            for cls_id in detected_classes:
                class_name = names_dict[int(cls_id)].replace("-","_")
                class_counts[class_name]= class_counts.get(class_name,0)+1

            alarm_triggered= False
            alarm_reason=""
            # critical
            # These defects compromise the structural integrity of the steel.
            if class_counts.get("inclusion", 0) > 0:
                alarm_reason = "CRITICAL: Inclusion Defect!"
                
            elif class_counts.get("crazing", 0) > 0:
                alarm_reason = "CRITICAL: Crazing (Cracking) Detected!"
                
            elif class_counts.get("pitted_surface", 0) > 0:
                alarm_reason = "CRITICAL: Pitted Surface Detected!"
                
            # Warning
            # Minor surface blemishes that downgrade the steel if clustered.
            elif class_counts.get("scratches", 0) >= 3:
                alarm_reason = f"WARNING: Too many Scratches ({class_counts.get('scratches')})!"
                
            elif class_counts.get("patches", 0) >= 2:
                alarm_reason = f"WARNING: Too many Patches ({class_counts.get('patches')})!"
                
            elif class_counts.get("rolled_in_scale", 0) >= 2:
                alarm_reason = f"WARNING: Rolled-in Scale accumulation ({class_counts.get('rolled_in_scale')})!"
                

            if alarm_reason != "":
                # If any of the rules above were broken, STOP the belt!
                alarm_triggered = True
                trigger_factory_alarm("STOP_CONVEYOR", alarm_reason)
            else:
                # If no rules were broken, keep the belt moving!
                trigger_factory_alarm("RESUME_CONVEYOR", "Surface Clean")

            # Encode annotated image back to Base64 to send to Streamlit
            _, buffer = cv2.imencode('.jpg', annotated_image)
            encoded_img = base64.b64encode(buffer).decode('utf-8')
            await websocket.send_json({
                "image": encoded_img,
                "alarm": alarm_triggered,
                "reason": alarm_reason
            })



    except WebSocketDisconnect:
        print("Simulation Client Disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")

