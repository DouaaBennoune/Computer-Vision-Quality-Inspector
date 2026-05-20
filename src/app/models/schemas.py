from pydantic import BaseModel
from typing import List 
from enum import Enum

class DefectClasses(str,Enum):
    crazing= "crazing"
    inclusion= "inclusion"
    patches= "patches"
    pitted_surface= "pitted_surface"
    rolled_in_scale= "rolled_in_scale"
    scratches= "scratches"

class DefectsCount(BaseModel)  :
    "Schema for defining the defect class and its count "
    defect_class : DefectClasses
    count : int
    


class YoloPredictions(BaseModel):
    "Schema for individual image prediction details"
    id: str
    defects  : List[DefectsCount]
    image_link : str


class PredictionSummary(BaseModel):
    "Schema for the total number of each defect class"

    crazing: int
    inclusion: int
    patches: int
    pitted_surface: int
    rolled_in_scale: int
    scratches: int
    
    dashboard: List[YoloPredictions]

class ErrorResponse(BaseModel):
    detail: str


