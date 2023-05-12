import os
import pickle
import wave

import numpy as np
import pyaudio
import python_speech_features as mfcc
from scipy.io.wavfile import read
from sklearn import preprocessing
from sklearn.mixture import GaussianMixture


def calculate_delta(array):
    rows, cols = array.shape
    deltas = np.zeros((rows,20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
              first =0
            else:
              first = i-j
            if i+j > rows-1:
                second = rows-1
            else:
                second = i+j 
            index.append((second,first))
            j+=1
        deltas[i] = ( array[index[0][0]]-array[index[0][1]] + (2 * (array[index[1][0]]-array[index[1][1]])) ) / 10
    return deltas

def extract_features(audio, rate):    
    mfcc_feature = mfcc.mfcc(audio, rate, 0.025, 0.01, 20, nfft = 1200, appendEnergy = True)    
    mfcc_feature = preprocessing.scale(mfcc_feature)
    delta = calculate_delta(mfcc_feature)
    combined = np.hstack((mfcc_feature,delta))
    return combined

def record_sample(name):
    for count in range(10):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 5
        audio = pyaudio.PyAudio()		
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

        Recordframes = []
        print("----------------------Recording " + f"{count+1}---------------------")
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            Recordframes.append(data)
        print("--------------------------Recording Stopped-------------------------")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        OUTPUT_FILENAME = name + "-sample" + str(count) + ".wav"
        WAVE_OUTPUT_FILENAME = os.path.join("training_data/voice/" + name, OUTPUT_FILENAME)

        trainedfilelist = open("training_set.txt", 'a')
        trainedfilelist.write(OUTPUT_FILENAME + "\n")

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(Recordframes))

        waveFile.close()    

def train_model():
    src = os.listdir('D:\Smart-Device-Controller-System\\training_data\\voice')
    dest = "models/voice/"

    count = 1
    features = np.asarray(())

    for (i, path) in enumerate(src): 
        sub_src = os.listdir('D:\Smart-Device-Controller-System\\training_data\\voice\\'+path)
        for (j, sub_path) in enumerate(sub_src):
            sr, audio = read('D:\Smart-Device-Controller-System\\training_data\\voice\\'+path+'\\'+sub_path)

            vector = extract_features(audio, sr)
            
            if features.size == 0:
                features = vector
            else:
                features = np.vstack((features, vector))

            if count == 10:    
                gmm = GaussianMixture(n_components=6, max_iter=200, covariance_type='diag', n_init=3)
                gmm.fit(features)
                
                # dumping the trained gaussian model
                picklefile = path.split("-")[0] + ".gmm"
                pickle.dump(gmm, open(dest + picklefile, 'wb'))
                print("Modelling completed for speaker:", picklefile, "with data point =", features.shape)   
                features = np.asarray(())
                count = 0

            count += 1
        
def test_model(audio):
    src = "models/voice/" 
    gmm_files = [os.path.join(src, fname) for fname in os.listdir(src) if fname.endswith(".gmm")]
     
    # load the Gaussian gender Models
    models = [pickle.load(open(fname, 'rb')) for fname in gmm_files]
    speakers = [fname.split("\\")[-1].split(".gmm")[0] for fname in gmm_files]
     
    # read the test directory and get the list of test audio files 
    sr, audio = read(audio)
    vector = extract_features(audio, sr)
    log_likelihood = np.zeros(len(models)) 
    
    for i in range(len(models)):
        gmm = models[i] 
        scores = np.array(gmm.score(vector))
        log_likelihood[i] = scores.sum()
         
    winner_score = np.max(log_likelihood)   
    print(winner_score)
    if winner_score <= -28:
        return "Unknown"
    winner = np.argmax(log_likelihood)
    winner_name = speakers[winner][13:]
    return winner_name

