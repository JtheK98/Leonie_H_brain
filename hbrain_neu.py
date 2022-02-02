"""
Program description:
    This program can be used for the parsing a string including normal words as well as emotions.
    Therefore a TTS (text to speech) module, emofani (emotion face animation) module and MIRA (todo) are used

How to use:
    1. Start the program
    2. Send messages to UDP port ("127.0.0.2", 20001) 
    2.1 Add emotions in square brackets [] in the text (valid emotions can be find in the function getEmo)
    2.2 Add eyeposition in curly brackets {} in the text
    2.3 Change language using dollar signs$$



Example:
    '[:-)] Hallo! [:-/] wie geht es euch allen?[:-)]{10,50} gut hoffe ich! $en$ how are you doing?'
    
"""

import socket
import larynx
import sounddevice as sd
import time


#inits

#sampling rate
fs=22050

#IPs and ports
adressen = {"MIRAAD->HBrain"        : ("127.0.0.2", 20001),
            "HBrain->MIRAAD"        : ("192.168.188.10",  5000),
            
            "EmoFani->HBrain"       : ("127.0.0.3", 20001),
            "HBrain->EmoFani"       : (socket.gethostname(), 11000)            
            }

sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
now = (int(time.time() * 1000))
bufferSize = 1024
sock.bind(adressen["MIRAAD->HBrain"])

# #set eyeposition to 0
# sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazex=" + str(0))
# sock.sendto(sendeString, adressen["HBrain->EmoFani"])
# sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazey=" + str(0))
# sock.sendto(sendeString, adressen["HBrain->EmoFani"])



#default voice
voice = 'en-us_blizzard_fls-glow_tts'#de-de_eva_k-glow_tts' #german female 1


#functions
def selectvoice(newvoice):
    #get voice from parsing
    if(newvoice=='de-de_eva_k-glow_tts' or newvoice=='de' or newvoice=='de-de'):
        voice='de-de_eva_k-glow_tts' #german female 1
        
    elif(newvoice=='de-de_kerstin-glow_tts'):
        voice='de-de_kerstin-glow_tts' #german female 2
    
    if(newvoice=='en-us_blizzard_fls-glow_tts' or newvoice=='en' or newvoice=='en-us'):
        voice='en-us_blizzard_fls-glow_tts' #english female 1   
    
    elif(newvoice=='en-us_cmu_ljm-glow_tts'):
        voice='en-us_cmu_ljm-glow_tts' #english female 2
        
    elif(newvoice=='en-us_cmu_eey-glow_tts'):
        voice='en-us_cmu_eey-glow_tts' #english female 3
        
    elif(newvoice=='en-us_cmu_slp-glow_tts'):
        voice='en-us_cmu_slp-glow_tts' #english indian female
        
    else: #default voice
        voice = 'de-de_eva_k-glow_tts' #german female 1

    
    return voice

def getEmo(emotion):
    #get emotion from parsing            
    if emotion == 'neutral' or emotion == ':-|' or emotion == '0':
        emotion = ";d:expression=neutral%100"
    
    elif emotion == 'happy' or emotion == ':-)' or emotion == '1':
        emotion =";d:expression=happy%100"

    elif emotion == 'sad' or emotion == ':-(' or emotion == '5':
        emotion = ";d:expression=sad%100"
    
    elif emotion == 'attentive':
        emotion = ";d:expression=attentive%100"
    
    elif emotion == 'excited' or emotion == ':-O' or emotion == '2':
        emotion = ";d:expression=excited%60"

    elif emotion == 'laughing' or emotion == ':-D' or emotion == '3':
        emotion =  ";d:expression=excited%100"

    elif emotion == ':-/':
        emotion = ";d:pleasure=-37"
               
    elif emotion == 'relaxed':
        emotion = ";d:expression=relaxed%100"
    
    elif emotion == 'sleepy':
        emotion = ";d:expression=sleepy%100"
    
    elif emotion == 'frustrated' or emotion == '-.-' or emotion == '4':
        emotion = ";d:expression=frustrated%100"
        
    return emotion


def parse_eyepostion(eyeposition):
    #parse string of eye position for x and y 
    i=0
    j=0
    eyepositionX=''
    eyepositionY=''
    
    #for x
    while i < len(eyeposition):
        
        char=eyeposition[i]     
        if(char != ','):
            eyepositionX+=char
        if(char==','):
            j=i+1
            break
        i=i+1
    
        
    #for y
    while j < len(eyeposition):
        
        char=eyeposition[j]  
        eyepositionY+=char
        j=j+1
        
    return int(eyepositionX),int(eyepositionY)
    
def speaking(voice,fs,text):
    #set emofani to talking
    EmoFaniString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:talking=True")
    sock.sendto(EmoFaniString, adressen["HBrain->EmoFani"])
    
    #speak text and wait until its finished
    speech = larynx.text_to_speech(text,voice)
    time.sleep(0.1)
    sd.play(speech.audio,fs)
    sd.wait()
    
    #set emofani to not talking
    EmoFaniString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:talking=False")
    sock.sendto(EmoFaniString, adressen["HBrain->EmoFani"])


def parsing(original_string,voice, fs):
    #parse received string for TTS, emofani and MIRA
    
    #declarations
    tts=''
    emotion=''
    emochar=''
    eyepositionX=0
    eyepositionY=0
    newvoice=voice
    i=0 
    
    #start parsing string
    while i < len(original_string):
        
        char=original_string[i]
        
        
        #detect new emotion
        if(char=='['):
            j=i
            
            
            #say text so far
            if (tts !=''):
                speaking(selectvoice(newvoice),fs,tts)
                
            tts=''
            
            while True:
                j=j+1
                emochar=original[j]
                
                #end of emotion string
                if emochar ==']':
                    #send emotion to emofani
                    emo= str.encode(str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + getEmo(emotion)))
                    sock.sendto(emo, adressen["HBrain->EmoFani"])
                    emotion=''
                    break
                else:
                    emotion+=emochar
                    
            i=j   
        
        #detect new voice    
        elif(char=='$'):
            j=i
            
            
            #say text so far
            if (tts !=''):
                speaking(selectvoice(newvoice),fs,tts)
                
            tts=''
            newvoice=''
            
            while True:
                j=j+1
                voicechar=original[j]
                
                #end of voice string
                if voicechar =='$':
                    newvoice=selectvoice(newvoice)
                    break
                else:
                    newvoice+=voicechar
                    
            i=j   
        
        
        #detect new eyeposition
        elif(char=='{'):
            j=i
            
            
            #say text so far
            if (tts !=''):
                speaking(selectvoice(newvoice),fs,tts)
            tts=''
            eyeposition=''
            
            while True:
                j=j+1
                eyechar=original[j]
                
                #end of voice string
                if eyechar =='}':
                    eyepositionX,eyepositionY=parse_eyepostion(eyeposition)                   
                    eyeposition=''
                    
                    #move head: TODO
                    #sendeString = str("#NAV##ROTHEAD#" + str(-180 - eyepositionX) + "#")
                    #sock.sendto(sendeString, adressen["HBrain->MIRAAD"])
                    
                    
                    
                    #control eyeposition in x and y
                    if abs(eyepositionX) < 100:                    
                        sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazey=" + str(eyepositionY))
                        sock.sendto(sendeString, adressen["HBrain->EmoFani"])
                    
                    if abs(eyepositionX) >= 100 and abs(eyepositionX) < 900:  
                        
                        sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazey=" + str(0))
                        sock.sendto(sendeString, adressen["HBrain->EmoFani"])
                        #sendeString = str("#NAV##ROTHEAD#" + str(eyepositionX) + "#")
                        #sock.sendto(sendeString, adressen["HBrain->MIRAAD"])
                    
                    if abs(eyepositionX) >= 900:  
                        if eyepositionX >0:
                            eyepositionX=eyepositionX-900
                        if eyepositionX <0:
                            eyepositionX=eyepositionX+900
                        sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazey=" + str(eyepositionY))
                        sock.sendto(sendeString, adressen["HBrain->EmoFani"])
                        #sendeString = str("#NAV##ROTHEAD#" + str(900) + "#")
                        #sock.sendto(sendeString, adressen["HBrain->MIRAAD"])
                    
                    
                    if eyepositionY > 150:
                        eyepositionY=150
                        
                    elif eyepositionY < -150:
                        eyepositionY=-150
                        
                    sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazex=" + str(eyepositionX))
                    sock.sendto(sendeString, adressen["HBrain->EmoFani"])
                    
                    break
                else:
                    eyeposition+=eyechar
                    
            i=j  
            
        #skip punctuation   
        elif(char=='!' or char=='?' or char=='.' or char=='(' or char==')'):
            tts+=''
        
            
        #adopt letters
        else:
            tts+=char
            
        i=i+1    
    
    
    #say rest of text
    if (tts !=''):
        speaking(selectvoice(newvoice),fs,tts)
    

while(True):
    try:
        #receive messages from upd server
        bytesAddressPair = sock.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        original = message.decode("utf-8")
        print(original)
        #parsing and robot controlling
        parsing(original, voice, fs)
    
    except KeyboardInterrupt:
        #set eyeposition to 0
        sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazex=" + str(0))
        sock.sendto(sendeString, adressen["HBrain->EmoFani"])
        sendeString = str.encode("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazey=" + str(0))
        sock.sendto(sendeString, adressen["HBrain->EmoFani"])
        
        print('Stopped script')
        