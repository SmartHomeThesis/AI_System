# Hot-fix: error GPU-setup
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from deepface import DeepFace
import cv2
import time
import numpy as np
import pandas as pd

models = [
  "VGG-Face", 
  "Facenet", 
  "Facenet512", 
  "OpenFace", 
  "DeepFace", 
  "DeepID", 
  "ArcFace", 
  "Dlib", 
  "SFace",
]

metrics = ["cosine", "euclidean", "euclidean_l2"]


cap = cv2.VideoCapture(0)
while(True):
    ret, frame = cap.read()
    detected_face = DeepFace.extract_faces(frame, detector_backend='opencv',enforce_detection=False)
    facial_area = detected_face[0]['facial_area']
    print(detected_face[0]['facial_area'])
    # draw rectangle over face and open cv window base on return fron extract_faces {'x': 211, 'y': 80, 'w': 118, 'h': 151}
    cv2.rectangle(frame, (facial_area['x'],facial_area['y']), (facial_area['x'] + facial_area['w'], facial_area['y']+facial_area['w']), (0, 255, 0), 2)
    cv2.imshow("Face", frame)
    name_detected= "Unknown"
    response = DeepFace.find(img_path = frame, db_path = "faces/train_database", model_name = models[1], distance_metric = metrics[0], enforce_detection = False, detector_backend = 'opencv')
    path_name_image= response[0]['identity'][0]
    dirpath, filename = os.path.split(path_name_image)
    parts = dirpath.split("\\") # Use backslash as separator
    name_detected = parts[-1] # Last part contains the name
    print("NAME_Dectect",name_detected)
    cv2.putText(frame,name_detected,(facial_area['x']+6,facial_area['y']+6), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(255,255,255),2,cv2.LINE_AA)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
cap.release()