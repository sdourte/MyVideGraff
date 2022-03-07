#Imports
import kivy
import pymongo
import shutil # pour move un file
import numpy as np
#Audio & video
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os
#Pour déterminer le temps
from datetime import datetime
#Pour pouvoir récupérer l'image (utile pour les videos)
from PIL import Image as IM
#L'objet Clock vous permet de planifier un appel de fonction à l'avenir ; une ou plusieurs fois à des intervalles spécifiés
from kivy.clock import Clock
#La classe App est la base pour créer des applications Kivy. Considérez-le comme votre principal point d'entrée dans la boucle de course Kivy.
from kivy.app import App
#La classe Widget est la classe de base requise pour créer des widgets.
from kivy.uix.widget import Widget
#classe pour dessiner des formes
from kivy.graphics import Color, Ellipse, Line, Canvas, ClearColor
#Pour créer d'autres fenêtres window
from kivy.uix.screenmanager import Screen, ScreenManager
#Les property sont là pour init le type des valeurs des variables
from kivy.properties import StringProperty, ListProperty, NumericProperty
#Classe de base pour la création de la fenêtre Kivy par défaut.
from kivy.core.window import Window
Window.clearcolor = (.94, .94, .94, 1)
#On oblige le full screen
Window.fullscreen = 'auto'
Window.set_system_cursor = 'arrow'

#All the widgets
class Subject(Widget):
    pass

class Topics(Widget):
    pass

class Header(Widget):
    pass

class HeaderTopicName(Widget):
    pass

class HeaderSubjectTitle(Widget):
    pass
    
class Intervention(Widget):
    pass

class InterventionsSelectionEmpty(Widget):
    pass

class MyWidget(Widget):
    pass

class Audio(Widget):
    pass

class Video(Widget):
    pass

class AddVideoContent(Widget):
    pass

class Graffiti(Widget):
    pass

class AddGraffitiContent(Widget):
    pass

class GraffitiDraw(Widget):

    def on_touch_down(self, touch):
        #Affiche la position du curseur
        #print("cursor position :", touch)
        color = (.349, .5686, .392)
        with self.canvas:
            Color(*color, mode='hsv') # (numéro couleur rgb) / 255
            d = 5.
            if 0.25 < touch.spos[0] < 0.9 and 0.2 < touch.spos[1] < 0.7:
                Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                touch.ud['line'] = Line(points=(touch.x, touch.y),width=4)

    def on_touch_move(self, touch):
        if 0.25 < touch.spos[0] < 0.9 and 0.2 < touch.spos[1] < 0.7: #Ce sont les chiffres pour délimiter la zone de dessin
            try:
                touch.ud['line'].points += [touch.x, touch.y]
            except:
                pass
            
#Differents écrans
class TopicsSelectionScreen(Screen):
    pass

class TopicDisplayScreen(Screen):
    pass

class AddGraffitiScreen(Screen):
    pass

class AddVideoScreen(Screen):
    pass

#Main Class
class MyVideApp(App):
    #Les property sont là pour vérifier le type des valeurs des variables
    subjectsTitles = ListProperty()
    subjectTitle = StringProperty("")
    current_image = StringProperty("")
    actual_pos = StringProperty("")
    joined_actual_pos = StringProperty("")
    
    #Create the folder graff, videos and audios if it isn't already created
    actual_pos = str(os.getcwd())
    splitted_actual_pos = actual_pos.split('\\') #On split avec les \
    joined_actual_pos = "/".join(splitted_actual_pos) #On rassemble en remplaçant les \ par des /
    actual_folder = os.listdir(str(actual_pos))
    
    if "graffs" not in actual_folder:
        os.mkdir(joined_actual_pos + "/graffs")
    if "videos" not in actual_folder:
        os.mkdir(joined_actual_pos + "/videos")
    if "audios" not in actual_folder:
        os.mkdir(joined_actual_pos + "/audios")
        
    #Main function
    def build(self):

        #connection to DB
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        if self.client != None:
            db = self.client["VideGraff"]
            self.collection = db["data"]
            #Delete all of the infos to update the database
            if self.collection != None:
                self.collection.delete_many({})
            directories = os.listdir("data/")
            #Add all of the informations in the database
            for directory in directories: #iterate on subjects
                files = os.listdir("data/%s" % (directory))
                mylist = [{"title": directory}]
                self.collection.insert_many(mylist)
                
        #upadate DB if graffiti deleted
        directories = os.listdir("data/")

        if ".DS_Store" in directories:
                directories.remove(".DS_Store")
        
        for directory in directories: #iterate on subjects

            files = os.listdir("data/%s" % (directory))
            files.remove("subject")

            if ".DS_Store" in files:
                files.remove(".DS_Store")

            nbGraff = 0
            nbVid = 0
            
            for fileName in files:
                
                if "video_" in fileName:
                    nbVid += 1
                else:
                    nbGraff += 1

            myquery = { "title": directory }
            newvalues = { "$set": { "graffitis": nbGraff, "video": nbVid } }

            self.client["VideGraff"]["data"].update_many(myquery, newvalues)

        #app code
        #Init graff content
        addGraffitiContent = AddGraffitiContent()
        self.addGraffitiContentRef = addGraffitiContent
        self.myWidget = MyWidget()
        
        subjectName = StringProperty("")
        subjectCamNb = StringProperty("")
        subjectGrafNb = StringProperty("")

        #screens declaration
        self.topicsSelectionScreen = TopicsSelectionScreen(name ="screen_TopicsSelection")
        global topicDisplayScreen 
        topicDisplayScreen = TopicDisplayScreen(name="screen_TopicDisplay")
        addGraffitiScreen = AddGraffitiScreen(name="screen_AddGraffiti")
        addVideoScreen = AddVideoScreen(name="screen_AddVideo")

        #topics selection screen
        self.header = Header()
        self.topicsSelectionScreen.ids.top_box.add_widget(self.header)

        self.topics = Topics()
        self.header.ids.content_box.add_widget(self.topics)
        
        #takes info from mongodb
        subjectsTitles = self.collection.find({})
        
        listSubject = []
        for subject in subjectsTitles:
            self.subjectName = subject["title"]
            self.subjectCamNb = subject["video"]
            self.subjectGrafNb = subject["graffitis"]
            listSubject.append(Subject())

        for subject in listSubject:
            self.topics.ids.contents.add_widget(subject)
        
        #topic display screen
        self.headerTopicName = HeaderTopicName()
        topicDisplayScreen.ids.top_box.add_widget(self.headerTopicName)
        
        #add intervention
        self.inter = Intervention()
        self.headerTopicName.ids.content_box.add_widget(self.inter)
        
        #Add graff content
        graffs = []
        graffs = os.listdir(self.actual_pos + "/graffs")#  + str(actual_subject)
        #Add video and audio content
        audios = []
        videos = []
        audios = os.listdir(self.actual_pos + "/audios")
        videos = os.listdir(self.actual_pos + "/videos")
        # S'il n'y a pas de réactions, on affiche le chibi triste
        if graffs == [] and audios == [] and videos == []:
            self.nointervention = InterventionsSelectionEmpty()
            topicDisplayScreen.ids.box_inter.add_widget(self.nointervention)
        
        else:
            actual_subject = self.subjectName
            
            list_graffs = []
            list_audios = []
            list_videos = []
            #Graffitis
            for graffi in graffs:
                self.name_graffiti = str(graffi)
                
                self.name_graffiti_subject = str(graffi[:-14]) # On retire les caractères concernant l'heure pour qu'il ne reste que ceux qui désigne le sujet du graff
                list_graffs.append(Graffiti())
            for graff in list_graffs:
                self.inter.ids.content_box.add_widget(graff)
            #Audios
            for audi in audios:
                self.name_audio = str(audi)
                
                self.name_audio_subject = str(audi[:-20]) # On retire les caractères concernant l'heure pour qu'il ne reste que ceux qui désigne le sujet de l'audio
                list_audios.append(Audio())
            for audio in list_audios:
                self.inter.ids.content_box.add_widget(audio)
            #Videos
            for vid in videos:
                self.name_video = str(vid)
                
                self.name_video_subject = str(vid[:-20]) # On retire les caractères concernant l'heure pour qu'il ne reste que ceux qui désigne le sujet de la video
                list_videos.append(Video())
            for video in list_videos:
                self.inter.ids.content_box.add_widget(video)
        
        
        #add graffiti
        graffTitleHeader = HeaderSubjectTitle()
        addGraffitiScreen.ids.top_box.add_widget(graffTitleHeader)

        graffTitleHeader.ids.content_box.add_widget(self.addGraffitiContentRef)

        #paint widget
        paintGraffiti = addGraffitiContent.ids.painter_widget
        self.painter = GraffitiDraw()
        paintGraffiti.add_widget(self.painter)
        
        #add video
        videoTitleHeader = HeaderSubjectTitle()
        addVideoScreen.ids.top_box.add_widget(videoTitleHeader)

        addVideoContent = AddVideoContent()
        videoTitleHeader.ids.content_box.add_widget(addVideoContent)
        
        #add screens to screenmanager
        screenManager = ScreenManager()

        screenManager.add_widget(self.topicsSelectionScreen)
        screenManager.add_widget(topicDisplayScreen)
        screenManager.add_widget(addGraffitiScreen)
        screenManager.add_widget(addVideoScreen)

        return screenManager
    
    # Other usefull functions
    def move_audio_video(self):
        """ This function take video and audio files to put it in the right path because they are not display in the good spot
        """
        files = []
        files = os.listdir(self.actual_pos)
        
        for records in files:
            #On bouge les fichiers pour qu'ils soient triés
            if "wav" in records:
                shutil.move(self.actual_pos + "/" + str(records), self.actual_pos + "/audios")
                
            elif "mp4" in records:
                shutil.move(self.actual_pos + "/" + str(records), self.actual_pos + "/videos")
        
    def record_audio(self):
        """ This function is the function that create and launch an audio record
        """
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 2
        fs = 44100  # Record at 44100 samples per second
        seconds = 15
        #Name of the file
        actual_subject = self.subjectTitle
        time_now = datetime.now()
        hour_min_sec = time_now.strftime("%H" + "h" + "%M" + "m" + "%S" + "s") #On met le nom en fonction de l'heure pour ne pas avoir deux fois le même
        filename = str(actual_subject) + "_Audio_" + hour_min_sec + ".wav"

        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print('Recording')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []  # Initialize array to store frames
        
        #Asserts
        assert type(fs // chunk * seconds) == int #Pour être sûr que l'on manipule des int()
        assert type(filename) == str #On vérifie si le type de filename est bien un string car c'est un nom de fichier
        assert "wav" in filename #On vérifie que l'extension du graff est bonne (.wav)
        
        # Store data in chunks for 3 seconds
        for i in range(0, (fs // chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        print('Finished recording')

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
    
    def record_video(self):
        """ This function is the function that create and launch a video record (but without the sound of it)
        """
        #Init le nom que la vidéo aura
        actual_subject = self.subjectTitle
        time_now = datetime.now()
        hour_min_sec = time_now.strftime("%H" + "h" + "%M" + "m" + "%S" + "s") #On met le nom en fonction de l'heure pour ne pas avoir deux fois le même
        filename = str(actual_subject) + "_Video_" + hour_min_sec + ".mp4" #avi or mp4
        frames_per_sec = 24.0
        resolution = "480p"

        # Standard Video Dimensions Sizes
        STD_DIMENSIONS =  {
            "480p": (640, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4k": (3840, 2160),
        }
        dims = STD_DIMENSIONS["480p"]
        
        # Video Encoding, might require additional installs
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        def get_video_type(filename):
            """ Get the type of the filename
            """
            filename, ext = os.path.splitext(filename)
            if ext in VIDEO_TYPE:
                return  VIDEO_TYPE[ext]
            return VIDEO_TYPE['avi']
        
        #Tout ça c'est pour afficher la fenêtre d'enregistrement de la webcam
        cap = cv2.VideoCapture(0)
        out = cv2.VideoWriter(filename, get_video_type(filename), frames_per_sec, dims)
        
        while (True):
            ret, frame = cap.read()
            out.write(frame)
            cv2.imshow("Hello you", frame)
            #Ceci est pour mettre la fenetre au bon endroit
            cv2.setWindowProperty("Hello you",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            
            if cv2.waitKey(20) == ord("q"):
                break
            
        #Asserts
        assert ("mp4" in filename) or ("avi" in filename) #On vérifie que l'extension est bonne    
        assert dims in STD_DIMENSIONS.values() #Check if the dimensions are the good ones
        assert type(filename) == str #On vérifie si le type de filename est bien un string car c'est un nom de fichier
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
    def clear_graff(self):
        """ This function clears the graffiti when the user want to restart his draw
        """
        self.painter.canvas.clear()
        
    def make_a_screen(self):
        """ This function create and save a screenshot of the graffiti, then it resize the screenshot to just get the draw of the graffiti and nothing else
        """
        actual_pos = str(os.getcwd())
        splitted_actual_pos = actual_pos.split('\\') #On split avec les \
        joined_actual_pos = "/".join(splitted_actual_pos) #On rassemble en remplaçant les \ par des /
        actual_folder = os.listdir(str(actual_pos))
        #Ajouter une condition qui fait qu'on doit écrire pour save un graffiti
        print("Screenshot !!!")
        nameGraff = "screenshot"
        actual_subject = self.subjectTitle # Pour donner le nom au graff en fonction du sujet
        #Faire un screen complet de l'écran
        Window.screenshot(name=nameGraff + ".png")
        
        im = IM.open(fp=joined_actual_pos + "/screenshot0001.png", mode="r") # On ajoute 0001 car le screenshot ajoute ça au nom de l'image
        #Redimensionner la capture d'écran pour ne garder que le graffiti
        # Define box inside image
        left = 360
        top = 240
        width = 1040
        height = 480
        
        # Create Box
        box = (left, top, left+width, top+height)

        # Crop Image
        area = im.crop(box)
        
        #Delete the screenshot de base pour ne pas le réouvrir
        os.remove(joined_actual_pos + "/screenshot0001.png")

        # Save Image
        time_now = datetime.now()
        hour_min_sec = time_now.strftime("%H" + "h" + "%M" + "m" + "%S" + "s") #On met le nom en fonction de l'heure pour ne pas avoir deux fois le même
        new_name_img = str(hour_min_sec) + ".png"
        self.current_image = new_name_img
        
        #Asserts
        assert type(new_name_img) == str #On vérifie si le type de filename est bien un string car c'est un nom de fichier
        assert "png" in new_name_img #On vérifie que l'extension du graff est bonne (.png)
        
        #On sauvegarde le graffiti
        area.save("graffs/" + str(actual_subject) + "_" + new_name_img)
        print("Image saved")
        
    
if __name__ == "__main__":
    MyVideApp().run()