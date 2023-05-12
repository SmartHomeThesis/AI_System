import os
import sys
import cv2
import math
import time
import pickle
import argparse
import numpy as np
import face_recognition
from imutils import paths


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", default="training_data/face", help="path to input directory of faces + images")
ap.add_argument("-e", "--encodings", type=str, default="models/face/encodings.pickle", help="path to serialized db of facial encodings")
ap.add_argument("-c", "--cpus", type=str, default="-1", help="number of cpus to use during encoding")
ap.add_argument("-d", "--detection-method", type=str, default="cnn", help="face detection model to use: either `hog` or `cnn`")

args = vars(ap.parse_args())


def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'


class FaceRecognition:
    cnt = 0
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_names = []
    process_current_frame = True

    def take_picture(self, name="Phuoc"):
        flag = True
        while flag:
            # Create folder to  save images from user input
            if not os.path.exists('training_data/face/' + name):
                os.mkdir('training_data/face/' + name)
                flag = False
            else:
                print("Name already exists. Please try again ................")
                return

        cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        img_counter = 1
        cv2.namedWindow("Take the picture", cv2.WINDOW_NORMAL)
        cam.set(3,640)
        cam.set(4,480)
        # used to record the time when we processed last frame
        prev_frame_time = 0
        while True:
            # Initialize the tick count
            ret, frame = cam.read()
            # Calculate the FPS
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            if not ret:
                print("Failed to grab frame")
                break
            blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
            net = cv2.dnn.readNetFromCaffe("models/face/deploy.prototxt.txt", "models/face/res10_300x300_ssd_iter_140000.caffemodel")
            net.setInput(blob)
            detections = net.forward()

            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                    (startX, startY, endX, endY) = box.astype("int")
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    crop_image = frame[startY:endY, startX:endX]
                # Display the FPS on the frame
            cv2.putText(frame, "FPS: {:.2f}".format(fps), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Take the picture", frame)
            k = cv2.waitKey(1)
            if k == ord('q'):
                print("Closing collecting data ................")
                break
            elif k % 256 == 32:
                # SPACE pressed
                img_name = "training_data/face/{}/{}.png".format(name, img_counter)
                cv2.imwrite(img_name, crop_image)
                print("{} written!".format(img_name))
                img_name = "training_data/face/{}/{}.png".format(name, img_counter)
                cv2.imwrite(img_name, crop_image)
                print("{} written!".format(img_name[19:]))
                img_counter += 1
                if img_counter == 6:
                    break

        cam.release()
        cv2.destroyAllWindows()

    def train_model(self):
        imagePaths = list(paths.list_images('training_data/face'))
        # print(imagePaths)
        knownEncodings = []
        knownNames = []
        # loop over the image paths
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            print("Processing image {}/{}".format(i+1, len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]
            # load the input image and convert it from BGR (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = facerecognition.face_locations(rgb, model=args["detection_method"])
            # compute the facial embedding for the face
            encodings = facerecognition.face_encodings(rgb, boxes)
            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                knownEncodings.append(encoding)
                knownNames.append(name)
                # dump the facial encodings + names to disk
                # print("[INFO] serializing encodings...")
                data = {"encodings": knownEncodings, "names": knownNames}
                f = open(args["encodings"], "wb")
                f.write(pickle.dumps(data))
                f.close()

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0,cv2.CAP_DSHOW) 
        data = pickle.loads(open(args["encodings"], "rb").read())
        video_capture.set(3, 640)
        video_capture.set(4, 480)
        video_capture.set(cv2.CAP_PROP_CONVERT_RGB, 1)
        if not video_capture.isOpened():
            sys.exit('Video source not found...')
        # used to record the time when we processed last frame
        prev_frame_time = 0

        # used to record the time at which we processed current frame
        new_frame_time = 0
        while True:
            ret, frame = video_capture.read()
            # Calculate the FPS
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            # Only process every other frame of video to save time
            # Display the FPS on the frame
            cv2.putText(frame, "FPS: {:.2f}".format(fps), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            if self.process_current_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                rgb_small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                # rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame,model=args["detection_method"])
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(data["encodings"], face_encoding)
                    name = 'Unknown'
                    confidence = '???'

                    # Calculate the shortest distance to face
                    face_distances = face_recognition.face_distance(data["encodings"], face_encoding)

                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = data["names"][best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    if confidence >= '90':
                        self.cnt += 1   
                    
                    self.face_names.append(f'{name} ({confidence})')

            self.process_current_frame = not self.process_current_frame

            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Create the frame with the name
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Face Recognition', frame)

            # Authenticate successfully
            if self.cnt == 5:
                video_capture.release()
                cv2.destroyAllWindows()
                return True, name[:name.index(" ")].upper()

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) == ord("q"):
                print("Closing recognition ................")
                break

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
fr = FaceRecognition()
fr.run_recognition()