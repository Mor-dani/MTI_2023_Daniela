#Program for combining the functions for retrieving ingredients, shaking to generate a recipe,
#and generating an image

import time
import math

#for the mpu
from mpu6050 import mpu6050
mpu = mpu6050(0x68)
#for reading button presses
import RPi.GPIO as GPIO
#Defining the GPIO notation- Board uses the pins on board instead of the GPIO numbers
GPIO.setmode(GPIO.BOARD)
SELECT_PIN = 40
GPIO.setup(SELECT_PIN, GPIO.IN)
LED_PIN = 38
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, False)

LED_PIN_WAIT = 36
GPIO.setup(LED_PIN_WAIT, GPIO.OUT)
GPIO.output(LED_PIN_WAIT, False)

#for getting ingredients from google drive:
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
    ]

creds = ServiceAccountCredentials.from_json_keyfile_name("secret_key.json")

#text to speech
from google.cloud import texttospeech
from google.oauth2 import service_account
#playing the text to speech sound
from pydub import AudioSegment
from pydub.playback import play

#Chat GPT communication
import openai
import json

openai.api_key = "blAbl@"#need to add the personal key for open_ai

#Image generator:
from craiyon import Craiyon, craiyon_utils
#for encoding the images
import base64
from io import BytesIO
from PIL import Image

# Computer vision
import cv2
from google.cloud import vision



#getting the ingredients from the cloud

def download_ingredients_from_cloud():
    file = gspread.authorize(creds)
    workbook = file.open("Ingredients")
    sheet = workbook.sheet1

    #Downloading all the data
    ingredients_list = sheet.get_all_records()
    #currently as a json, changing to pandas for easier management
    ingredients_df = pd.DataFrame.from_dict(ingredients_list)
    #print(ingredients_df)

    #Making the string for sending to chatgpt
    return ingredients_df


def format_request(ingredients_df):
    ingredients_text = ', '.join(ingredients_df.Combined)
    request_text = "recipe in a json format for the keys: Name, Ingredients Name, Ingredients, Instructions, short Dall-E prompt. The Dall-E prompt should include the name of the dish and the ingredients. I only have the following ingredients: " + ingredients_text + ". It's ok to only include some of the ingredients, you don't need to try to include as many as possible. Instructions should be formatted as an array. Only return the json reponse, do not add any other text or introduction. The names for the keys must match the ones given?"  
    return request_text

def waiting_for_shake():
    print("Waiting for user input")
    while True:
        accel_data = mpu.get_accel_data()
        acc_x = accel_data['x']
        acc_y = accel_data['y']
        acc_z = accel_data['z']
        
        acc_total = math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
        print("Acc total : "+str(acc_total))
        if(acc_total>20.0):
            print("I've been shaken!!")
            return 1
        
        #read to see if button is pressed, if it is, return 2
        if GPIO.input(SELECT_PIN): #if button is pressed
            return 2
        time.sleep(0.1)

def json_formatting(full_data):
    recipe_name = full_data["Name"]
    recipe_steps = full_data["Instructions"]
    recipe_image = full_data["short Dall-E prompt"]
    recipe_ingredients = full_data["Ingredients Name"]
    return recipe_name, recipe_steps, recipe_image, recipe_ingredients

def generate_image(recipe_image):
    generator = Craiyon()
    print(recipe_image)
    result = generator.generate(recipe_image)
    print(result)

    images = craiyon_utils.encode_base64(result.images)
    for i in images:
        image = Image.open(BytesIO(base64.decodebytes(i)))
        image.save("food_image.png","PNG")
        image.show()
        break
    
    #maybe need to save the image to show it later in the ui
    return

def text_to_speech_func(text_to_say):
    # Instantiates a client_audio
    
    creds = service_account.Credentials.from_service_account_file("food_id_key.json")

    # Instantiates a client_audio
    client_audio = texttospeech.TextToSpeechClient(credentials = creds)

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text="Next, " + text_to_say)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client_audio.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
    
    audio_file = "/home/pi/Desktop/MTI/A3/Aux_folder/output.mp3"

    sound = AudioSegment.from_file(audio_file)
    print("Play sound!")
    play(sound)
    time.sleep(0.5)
        
#For computer vision
def takephoto():
    #camera = picamera.PiCamera()
    #camera.capture('image.jpg')
    ret, img = cap.read()
    cv2.imshow('Frame', img)
    cv2.imwrite('/home/pi/Desktop/MTI/A3/Aux_folder/image.jpg',img)
    #return img

def computer_vision():
    global ingredients_df
    print(ingredients_df)
    takephoto() # First take a picture
    """Run a label request on a single image"""
    creds = service_account.Credentials.from_service_account_file("food_id_key.json")
    client = vision.ImageAnnotatorClient(credentials = creds)
    with open('/home/pi/Desktop/MTI/A3/Aux_folder/image.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations
    print('Labels:')
    real_item = ""

    for label in labels:
        #print(label.description)
        print ("Is this: " + label.description + "?")
        print("shake for no, press for yes")
        text_to_speech_func("Is this a " + label.description + "? shake for no, press for yes")
        next_step = waiting_for_shake ()
        if (next_step == 2):
            #pressed: yay yay
            real_item = "1 " + label.description
            data1 = {"Combined": real_item, "Weight/Volume" : 1}
            ingredients_df =ingredients_df.append(data1, ignore_index=True)
            print(ingredients_df)
            text_to_speech_func(label.description + " has been added to your ingredients")
            break
        time.sleep(1)
    #shaken: nay nay
        
    cap.release()
    cv2.destroyAllWindows()
    
#Initialise getting ingredients from the cloud and communication with Chatgpt
ingredients_df = download_ingredients_from_cloud()
#Chatgpt
messages = [ {"role": "system", "content": "Can you respond as if you were a chef?" } ]

while True: 
    #Can either shake to generate a recipe or go to input ingredients
    text_to_speech_func("Shake to generate a recipe, or press to enter new ingredients")
    next_step = waiting_for_shake()
    print(next_step)
    #print(request_text)
    final_recipe = False

    if next_step == 1:
        while not final_recipe:
            text_to_speech_func("Generating a recipe")
            GPIO.output(LED_PIN_WAIT, True)
            request_text = format_request(ingredients_df)
            print("sending request")
            #Sending request to chatgpt
            #message = input("You: ")
            initial_request = "Can you give me a " + request_text

            messages.append(
                {"role": "user", "content": initial_request},
            )

            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )

            reply = chat.choices[0].message
            #reply is in json format, need to  access the values
            print(reply.content)
            full_data = json.loads(reply.content)
            print(reply.content)
            messages.append(reply)
            recipe_name, recipe_steps, recipe_image, recipe_ingredients = json_formatting(full_data)
            print(recipe_steps)


            #Requesting the image from the image generator
            print("We are cooking your recipe")
            
            generate_image(recipe_image)
            GPIO.output(LED_PIN_WAIT, False)
            
            #Check if user likes the recipe or not
            text_to_speech_func("What about " +  recipe_name + "?")
            text_to_speech_func("If you would like to cook the recipe, press the burger, otherwise, shake for another suggestion")
            print("If you would like to cook the recipe, press the burger, otherwise, shake for another suggestion")
            next_step_recipe = waiting_for_shake()
            if(next_step_recipe == 2):
                #They press to select, continue to read the steps
                final_recipe = True
                break
            print("Getting a new recipe")
            text_to_speech_func("Generating a new recipe")
            time.sleep(1)
            

        #text_to_speech_func(recipe_steps)
        print("Starting your recipe :)")
        GPIO.output(LED_PIN, True)
        print(recipe_steps)
        for step in recipe_steps:
            #print(step)
            #Go line by one requesting the sound
            print(step)
            text_to_speech_func(step)
            #wait for person to request the next step
            print("When you are ready for the next step, press the burger. If you'd like to repeat, shake the burger")
            #ready for the next step = press =2
            #repeat the step = shake = 1
            next_step_read = 0
            while next_step_read != 2:
                next_step_read = waiting_for_shake()
                if(next_step_read == 1):
                    #They shake to request repeat
                    print(step)
                    text_to_speech_func(step)
                    time.sleep(1)
                
            print("Fetching the next step")
        
        
        print("Enjoy your meal!!")
        text_to_speech_func("Enjoy your meal")
        GPIO.output(LED_PIN, False)
            
     

    elif next_step == 2:
        print("take photo of the ingredients")
        text_to_speech_func("Taking a photo of your ingredient")
        #Image review
        num = 1
        cap = cv2.VideoCapture(0)
        computer_vision()
    
    
    time.sleep(1)
            
    




    
    

                                                                                                             
