from tkinter import N
import redis
from time import sleep, time
import pickle
import cv2,os,urllib.request


class Frames:
    	
    my_f=None

    @staticmethod
    def start_frame():
        x=time()
        r=redis.Redis(host='localhost', port=6379)
        r.delete('start')
        if r.get('start')==None:
            r.set('start', 'True')
            print(r.get('start'))
            video = cv2.VideoCapture(0)
            while True:
                success, image =video.read()
                try:
                    my_f=image
                    a = pickle.dumps(image)
                    r.set('frame', a)
                    print("another frame"+str(x))
                    sleep(0.05)
                except :
                    print("fail frame")
			#map_async()

	
Frames.start_frame()