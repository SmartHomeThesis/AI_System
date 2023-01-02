from imutils import paths
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os,sys
import math
import numpy as np

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset",default="data/faces",
	 help="path to input directory of faces + images")
ap.add_argument("-e", "--encodings",type=str,default="models/encodings.pickle",help="path to serialized db of facial encodings")
ap.add_argument("-c", "--cpus",type=str,default="-1",help="number of cpus to use during encoding")
ap.add_argument("-d", "--detection-method", type=str, default="hog",
                help="face detection model to use: either `hog` or `cnn`")
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

    def __init__(self):
        print("Welcome to face recognition system")

    def take_picture(self):
        name = input("Enter your name: ")

        cam = cv2.VideoCapture(0)

        cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("press space to take a photo", 500, 300)

        img_counter = 0
        # Create folder to  save images from user input
        os.mkdir('data/faces/' + name)

        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            #
            # # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            # rgb_small_frame = small_frame[:, :, ::-1]

            # # Find all the faces and face encodings in the current frame of video
            # self.face_locations = face_recognition.face_locations(rgb_small_frame)
            # for (top, right, bottom, left) in zip(self.face_locations):
            #     print(top, right, bottom, left)
            #     # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            #     top *= 4
            #     right *= 4
            #     bottom *= 4
            #     left *= 4
            #
            #     # Create the frame with the name
            #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            #     cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)

                # Display the resulting image
            cv2.imshow("press space to take a photo", frame)
            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                img_name = "data/faces/{}/{}.png".format(name, img_counter)
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1
                if img_counter == 5:
                    break

        cam.release()

        cv2.destroyAllWindows()

    def train_model(self):
        imagePaths = list(paths.list_images('data/faces'))
        print(imagePaths)
        knownEncodings = []
        knownNames = []
        # loop over the image paths
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            print("[INFO] processing image {}/{}".format(i + 1,
                                                         len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]
            # load the input image and convert it from BGR (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb,
                                                    model="hog")
            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)
            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                knownEncodings.append(encoding)
                knownNames.append(name)
                # dump the facial encodings + names to disk
                print("[INFO] serializing encodings...")
                data = {"encodings": knownEncodings, "names": knownNames}
                f = open(args["encodings"], "wb")
                f.write(pickle.dumps(data))
                f.close()
    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)
        data = pickle.loads(open(args["encodings"], "rb").read())
        if not video_capture.isOpened():
            sys.exit('Video source not found...')

        while True:
            ret, frame = video_capture.read()

            # Only process every other frame of video to save time
            if self.process_current_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
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
                return True, name[:name.index(".")].upper()

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) == ord('q'):
                break

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()

fr = FaceRecognition()

while True:
    choice = int(input("\n 1. Take picture for trainning \n 2. Train Model \n 3. Face Recognition \n 4. Exit\n"))
    if choice == 1:
        fr.take_picture()
    if choice == 2:
        fr.train_model()
    if choice == 3:
        fr.run_recognition()
    else:
        exit()