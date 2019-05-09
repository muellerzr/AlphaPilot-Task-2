# This script is to be filled by the team members. 
# Import necessary libraries
# Load libraries
#
# This program proprietary to Team Titans of AlphaPilot Challenge
# Authors: Carson Wilber
# Team Captain: Ashok Yannam
#---------------------------------------------------#

import json
import cv2
import numpy as np
import model_output_correction
from yolo_model import YOLO

# Implement a function that takes an image as an input, performs any preprocessing steps and outputs a list of bounding box detections and assosciated confidence score. 

def process_image(img):
    """Resize, reduce and expand image.

    # Argument:
        img: original image.

    # Returns
        image: ndarray(64, 64, 3), processed image.
    """
    image = cv2.resize(img, (608, 608),
                       interpolation=cv2.INTER_LINEAR)
    image = np.array(image, dtype='float32')
    image /= 255.
    image = np.expand_dims(image, axis=0)

    return image

class GenerateFinalDetections():
    def __init__(self):
        self.yolo = YOLO(0.6, 0.5)

    def predict(self, image):
        """Use yolo v3 to detect images.

        # Argument:
            image: original image.

        # Returns:
            box: predicted gate.

        """
        original_width, original_height, _ = image.shape
        
        pimage = process_image(image)
        
        boxes, classes, scores = self.yolo.predict(pimage, image.shape)
        
        if boxes is not None:
            corners_filled_ordered = []
            scores_filled_ordered = []
            
            for class_expected in range(4):
                if not class_expected in classes:
                    corners_filled_ordered.extend([0.0, 0.0])
                    scores_filled_ordered.extend([0.5])
                else:
                    ordered_box = list(list(boxes)[list(classes).index(class_expected)])
                    midpoint_box = [ordered_box[0] + (ordered_box[2]/2.), ordered_box[1] + (ordered_box[3]/2.)]
                    corners_filled_ordered.extend(midpoint_box)
                    scores_filled_ordered.extend([list(scores)[list(classes).index(class_expected)]])
            
            ret = [[int(v) for v in model_output_correction.bad_xy_to_good_xy(corners_filled_ordered)] + [int(100.*(sum(scores_filled_ordered)/4.))/100.]]
            
            if len(ret[0]) == 9:
                return ret
            
        return [[int(original_width * 0.33), int(original_height * 0.33), int(original_width * 0.66), int(original_height * 0.33), int(original_width * 0.66), int(original_height * 0.66), int(original_width * 0.33), int(original_height * 0.66), 0.5]]
