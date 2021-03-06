from itertools import count
from pickle import FRAME
from time import sleep
import time
import tensorflow as tf
import multiprocessing as mp
import redis
import pickle
import struct
import subprocess
import imutils
import threading
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

from imutils.video import VideoStream
import imutils
import cv2,os,urllib.request
import numpy as np
from django.conf import settings
#os.system("cmd python "+os.path.join(settings.BASE_DIR,'helper/help.py'))
#subprocess.Popen(["python", os.path.join(settings.BASE_DIR,'streamapp/helper/help.py')], shell=False)
face_detection_videocam = cv2.CascadeClassifier(os.path.join(
			settings.BASE_DIR,'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))
face_detection_webcam = cv2.CascadeClassifier(os.path.join(
			settings.BASE_DIR,'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))
# load our serialized face detector model from disk
prototxtPath = os.path.sep.join([settings.BASE_DIR, "face_detector/deploy.prototxt"])
weightsPath = os.path.sep.join([settings.BASE_DIR,"face_detector/res10_300x300_ssd_iter_140000.caffemodel"])
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model(os.path.join(settings.BASE_DIR,'face_detector/mask_detector.model'))
r=redis.Redis(host='localhost', port=7000)
r.delete('start')
f=None
	
def task1():
	global f,r
	print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
	print("ID of process running task 1: {}".format(os.getpid()))

	video = cv2.VideoCapture(0)
	t2=time.time()
	while True:
    	
		success, image =video.read()
		#cv2.putText(image,"60",(0,0))
		f=image
		
		#sleep(0.01)
		#f=image
		"""
		try:

			f = pickle.loads(r.get('frame'))
		
			print("good load")
		except :
			print("fail frame")
		"""

t1 = threading.Thread(target=task1, name='t1')	
t1.start()




class VideoCamera(object):
	def __init__(self):
		global r
		
		if r.get('start')==None:
			
			r.set('start',"yes")
			

	def __del__(self):
		#self.video.release()
		pass

	def get_frame(self):
		global f
		#frame = pickle.loads(r.get('frame'))
		#a=frame
		#a=f
		"""
		print(type(a))
		try:
			a=a.decode()
		except:
			pass
		print(type(a))
		"""
		image=f
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.

		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		faces_detected = face_detection_videocam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
		for (x, y, w, h) in faces_detected:
			cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
		frame_flip = cv2.flip(image,1)
		ret, jpeg = cv2.imencode('.jpg', frame_flip)
		return jpeg.tobytes()

class MyVideoCamera(object):
	def __init__(self):
		
		self.t1=0
		self.t2=0
		pass
		
		

	def __del__(self):
		#self.video.release()
		pass

	def get_frame(self):
		
		global f

		self.t1=time.time()
		image=cv2.putText(f,str(int(1/(self.t1-self.t2))),(50,50),1,4,(255, 0, 0),2,-1,False)
		self.t2=time.time()
		#frame = pickle.loads(r.get('frame'))
		#a=frame
		#a=f
		#print(type(a))
		#try:
		
		#a=a.decode()
		#except:
		#	pass
		#print(type(a))
		#image=f
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.

		#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		#faces_detected = face_detection_videocam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
		#for (x, y, w, h) in faces_detected:
		#	cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
		#frame_flip = cv2.flip(image,1)
		ret, jpeg = cv2.imencode('.jpg', image)

		return jpeg.tobytes()


class IPWebCam(object):
	def __init__(self):
		self.url = "http://192.168.0.100:8080/shot.jpg"

	def __del__(self):
		cv2.destroyAllWindows()

	def get_frame(self):
		imgResp = urllib.request.urlopen(self.url)
		imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
		img= cv2.imdecode(imgNp,-1)
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces_detected = face_detection_webcam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
		for (x, y, w, h) in faces_detected:
			cv2.rectangle(img, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
		resize = cv2.resize(img, (640, 480), interpolation = cv2.INTER_LINEAR) 
		frame_flip = cv2.flip(resize,1)
		ret, jpeg = cv2.imencode('.jpg', frame_flip)
		return jpeg.tobytes()


class MaskDetect(object):
	def __init__(self):
		self.vs = VideoStream(src=0).start()
		
		print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

	def __del__(self):
		cv2.destroyAllWindows()

	def detect_and_predict_mask(self,frame, faceNet, maskNet):
		# grab the dimensions of the frame and then construct a blob
		# from it
		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
									 (104.0, 177.0, 123.0))

		# pass the blob through the network and obtain the face detections
		faceNet.setInput(blob)
		detections = faceNet.forward()

		# initialize our list of faces, their corresponding locations,
		# and the list of predictions from our face mask network
		faces = []
		locs = []
		preds = []

		# loop over the detections
		for i in range(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with
			# the detection
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the confidence is
			# greater than the minimum confidence
			if confidence > 0.5:
				# compute the (x, y)-coordinates of the bounding box for
				# the object
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")

				# ensure the bounding boxes fall within the dimensions of
				# the frame
				(startX, startY) = (max(0, startX), max(0, startY))
				(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

				# extract the face ROI, convert it from BGR to RGB channel
				# ordering, resize it to 224x224, and preprocess it
				face = frame[startY:endY, startX:endX]
				face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
				face = cv2.resize(face, (224, 224))
				face = img_to_array(face)
				face = preprocess_input(face)

				# add the face and bounding boxes to their respective
				# lists
				faces.append(face)
				locs.append((startX, startY, endX, endY))

		# only make a predictions if at least one face was detected
		if len(faces) > 0:
			# for faster inference we'll make batch predictions on *all*
			# faces at the same time rather than one-by-one predictions
			# in the above `for` loop
			faces = np.array(faces, dtype="float32")
			preds = maskNet.predict(faces, batch_size=32)

		# return a 2-tuple of the face locations and their corresponding
		# locations
		return (locs, preds)

	def get_frame(self):
		frame = self.vs.read()
		frame = imutils.resize(frame, width=650)
		frame = cv2.flip(frame, 1)
		# detect faces in the frame and determine if they are wearing a
		# face mask or not
		(locs, preds) = self.detect_and_predict_mask(frame, faceNet, maskNet)

		# loop over the detected face locations and their corresponding
		# locations
		for (box, pred) in zip(locs, preds):
			# unpack the bounding box and predictions
			(startX, startY, endX, endY) = box
			(mask, withoutMask) = pred

			# determine the class label and color we'll use to draw
			# the bounding box and text
			label = "Mask" if mask > withoutMask else "No Mask"
			color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

			# include the probability in the label
			label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

			# display the label and bounding box rectangle on the output
			# frame
			cv2.putText(frame, label, (startX, startY - 10),
						cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
			cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
		ret, jpeg = cv2.imencode('.jpg', frame)
		return jpeg.tobytes()
		
class LiveWebCam(object):
	def __init__(self):
		self.url = cv2.VideoCapture("rtsp://admin:Mumbai@123@203.192.228.175:554/")

	def __del__(self):
		cv2.destroyAllWindows()

	def get_frame(self):
		success,imgNp = self.url.read()
		resize = cv2.resize(imgNp, (640, 480), interpolation = cv2.INTER_LINEAR) 
		ret, jpeg = cv2.imencode('.jpg', resize)
		return jpeg.tobytes()


#p = mp.Process(target=func())
#p.start()