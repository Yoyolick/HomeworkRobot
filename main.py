# imports
import time
import datetime
import cv2
import re
import pytesseract as tess
from PIL import Image
from selenium import webdriver
from tests import servertest
#from tests import visualizeTuples
from octocontrol import OctoprintAPI
from gcodelibtest.textToGcode import textToGcode
import matplotlib.pyplot as plt

# set offset for image rotation, should be fed from electron later (potentially)
offset = -90 #or just prompt at the beginning or as an optional arg

#test server
def testConnection(ip,port):
    return(servertest.tests().connectTest(ip,port))

#take screenshot of webcam as well as trim and rotate it by specified offset
def getWebcamFrame(): 
    # get octoprint login creds from file
    with open("loginCreds.txt", "r") as loginCreds:
        octoCreds = loginCreds.read().split(" ")

    # create headless webdriver
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    path = "chromedriver.exe"
    driver = webdriver.Chrome(path, options=op)

    # send webdriver to local octoprint page and login
    driver.get('http://octopi.local/?#control')  # redirect to webcam page

    print(datetime.datetime.now(), "- driver started")

    driver.find_element_by_id("login-user").send_keys(octoCreds[0])  # enter username
    driver.find_element_by_id("login-password").send_keys(octoCreds[1])  # enter password
    driver.find_element_by_id("login-button").click()  # login

    print(datetime.datetime.now(), "- logged in")

    time.sleep(6)  # wait for stream to load
    driver.execute_script("window.scrollTo(1080, 0)")  # scroll to top right
    driver.save_screenshot("images\\stream.png")  # take screenshot

    print(datetime.datetime.now(), "- screenshot taken")

    driver.quit()  # terminate driver

    print(datetime.datetime.now(), "- driver quit")

    # crop screenshot for parsing
    im = Image.open("images\\stream.png")  # load the image
    im = im.crop((160, 180, 745, 545))  # crop out corners
    im = im.rotate(offset, expand=True).save("images\\stream.png")  # rotate and save

#parse the text from screenshot and calculate it as a multiplication problem
def calculateAnswer():
    #retrieve path on system to tesseract executable from file
    with open("tesseractPath.txt", "r") as tessPath:
        tess.pytesseract.tesseract_cmd = tessPath.read()

    #convert image text to a list of strings seperated by the multiplication operand
    text = tess.image_to_string(Image.open('images\\stream.png'), lang='eng', config='-c tessedit_char_whitelist=1234567890x')
    text = text.split("x") #replace this with if statement for logical character contained and then decide how to solve the problem
    #maybe find library that solves from string so that you can do anything
    #check basic validity of answers before engraving
    return(int(text[0]) * int(text[1]))

    def visualize():
        tuples = textToGcode("a",1,0).toGcode()

#getWebcamFrame()
#print(calculateAnswer())
#print(testConnection("octopi.local","5000"))

#octoApi = OctoprintAPI("octopi.local",5000,"70D10AE2AB3048B8AEA90CD1F4B74C3D") #put key in file
#octoApi.send_gcode("G0 X10")

#print(textToGcode("a",1,0).toGcode()) #change cmds is broken
#print(textToGcode("a",1,0).toGcodeWithArgs("OFF","ON","FAST","SLOW"))
print(textToGcode("a",1,0).toGcode()) 

#previewTuples()

# conscise TODO
# - pipeline to send commands to printer
# - take calculated answer and transfer number points to gcode commands for printer
# - print mount for pi on back of laser
# - extra cable management
# - cleanup repo files
# - electron application?