from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageFilter
import ast
import io
import re
from .helper import *

# Create your models here.
"""class Group(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class MyUser(models.Model):

    name = models.CharField(max_length=50)
    groups = models.ManyToManyField(Group)
    password = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)"""

class LabeledImage(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to = 'static/uploaded_images/')
    action = models.CharField(max_length=10) # ALLOW, DENY, BLUR
    ruleList = models.CharField(max_length=5000) # can be a lot of rules
    owner = models.ForeignKey(User, null = False, on_delete=models.CASCADE) # Every image has one owner

    def __str__(self):
        return str(self.name)

    def setImage(self,buf):  # Set image content from binary buffer
        self.image = buf


    def loadImage(self,filepath):  # we can save image as bytearray to make it easier for us to modification and database operations

        try:
            with open(filepath, "rb") as img:
                self.image = bytearray(img.read())

        except IOError:
            print("Couldn't find the image in given path: " + filepath)


    def load(self,name):
        im = LabeledImage.objects.get(name=name)
        self.name = im.name
        self.image = im.image
        self.action = im.action
        self.ruleList = im.ruleList
        self.owner = im.owner


    def setDefault(self,action):
        self.action = action


    def addRule(self,matchexpr, shape, action, pos = -1):
        pos = int(pos)
        shape = ast.literal_eval(shape)
        if self.ruleList == '':
            rules = []
        else:
            rules = ast.literal_eval(self.ruleList)  #Convert string back to list

        rule = (matchexpr, shape, action)
        if pos == -1:
            rules.append(rule)
        else:
            rules.insert(pos, rule)

        self.ruleList = str(rules) #Convert list to str


    def delRule(self,pos):
        rules = ast.literal_eval(self.ruleList)  #Convert string back to list
        del rules[pos]
        self.ruleList = str(rules) #Convert list to str


    def getImage(self,user):

        user = User.objects.get(username=user)

        im = Image.open(self.image)
        width,height = im.size

        if self.ruleList == '':
            if self.action == 'ALLOW':
                return im
            rules = []
        else:
            rules = ast.literal_eval(self.ruleList)  #Convert string back to list

        blurred_image =  im.filter(ImageFilter.BLUR)

        for w in range(width):
            for h in range(height):
                matchFound = False
                for rule in rules:
                    if rule[1][0].upper() == "CIRCLE":# get user groups and check for match
                        if insideCircle(w,h,rule[1]) and (re.fullmatch(rule[0],user.username) or matchGroup(user,rule)):
                            action = rule[2]
                            if action.upper() == "DENY":
                                im.putpixel( (w,h), (0,0,0))
                            elif action.upper() == "BLUR":
                                im.putpixel( (w,h), blurred_image.getpixel((w,h)))
                            matchFound = True
                            break;

                    elif rule[1][0].upper() == "RECTANGLE":
                        if insideRectangle(w,h,rule[1]) and (re.fullmatch(rule[0],user.username) or matchGroup(user,rule)):
                            action = rule[2]
                            if action.upper() == "DENY":
                                im.putpixel( (w,h), (0,0,0))
                            elif action.upper() == "BLUR":
                                im.putpixel( (w,h), blurred_image.getpixel((w,h)))
                            matchFound = True
                            break;

                    elif rule[1][0].upper() == "POLYLINE":
                        if insidePolyline(w,h,rule[1]) and (re.fullmatch(rule[0],user.username) or matchGroup(user,rule)):
                            action = rule[2]
                            if action.upper() == "DENY":
                                im.putpixel( (w,h), (0,0,0))
                            elif action.upper() == "BLUR":
                                im.putpixel( (w,h), blurred_image.getpixel((w,h)))
                            matchFound = True
                            break;
                if not matchFound: #Apply defaultAction if none of the rules match
                    if self.action.upper() == "DENY":
                        im.putpixel( (w,h), (0,0,0))
                    elif self.action.upper() == "BLUR":
                        im.putpixel( (w,h), blurred_image.getpixel((w,h)))

        return im
