from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import json
import ast
import io
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
    image = models.BinaryField()
    action = models.CharField(max_length=10) # ALLOW, DENY, BLUR
    ruleList = models.CharField(max_length=5000) # can be a lot of rules
    ownr = models.ForeignKey(User, null = False, on_delete=models.CASCADE) # Every image has one owner

    def create(self, ownr ):
        self.owner = ownr.username
        self.user = ownr.username
        self.rules = []

    def __str__(self):
        return str(self.name)

    def setImage(self,buf):  # Set image content from binary buffer
        if self.owner == self.user:
            self.image = buf
        else:
            raise Exception("User doesn't own the image !")

    def loadImage(self,filepath):  # we can save image as bytearray to make it easier for us to modification and database operations
        if self.owner == self.user:
            try:
                with open(filepath, "rb") as img:
                    self.image = bytearray(img.read())

            except IOError:
                print("Couldn't find the image in given path: " + filepath)
        else:
            raise Exception("User doesn't own the image !")

    def save(self, *args, **kwargs):
        self.ruleList = json.dumps(self.rules)
        super().save(*args, **kwargs)

    def load(self,name):
        im = LabeledImage.objects.get(name=name)
        self.image = im.image
        self.action = im.action
        self.ruleList = im.ruleList
        self.ownr = im.ownr
        self.owner = str(self.ownr)
        self.rules = json.loads(self.ruleList)


    def setDefault(self,action):
        if self.owner == self.user:
            self.action = action
        else:
            raise Exception("User doesn't own the image !")

    def addRule(self,matchexpr, shape, action, pos = -1):
        pos = int(pos)
        shape = ast.literal_eval(shape)
        if self.owner == self.user:
            rule = (matchexpr, shape, action)
            if pos == -1:
                self.rules.append(rule)
            else:
                self.rules.insert(pos, rule)
        else:
            raise Exception("User doesn't own the image !")

    def delRule(self,pos):
        if self.owner == self.user:
            del self.rules[pos]
        else:
            raise Exception("User doesn't own the image !")

    def getImage(self,user):

        user = str(User.objects.get(username=user))

        im = Image.open(io.BytesIO(self.image))
        width,height = im.size

        for w in range(width):
            for h in range(height):
                matchFound = False
                for rule in self.rules:
                    if rule[1][0].upper() == "CIRCLE":# get user groups and check for match
                        if insideCircle(w,h,rule[1]) and (re.fullmatch(rule[0],user) or matchGroup(user,rule)):
                            action = rule[2]
                            if action.upper() == "DENY":
                                im.putpixel( (w,h), (0,0,0))
                            matchFound = True
                            break;

                    elif rule[1][0].upper() == "RECTANGLE":
                        if insideRectangle(w,h,rule[1]) and (re.fullmatch(rule[0],user) or matchGroup(user,rule)):
                            action = rule[2]
                            if action.upper() == "DENY":
                                im.putpixel( (w,h), (0,0,0))
                            matchFound = True
                            break;

                    elif rule[1][0].upper() == "POLYLINE":
                        if insidePolyline(w,h,rule[1]) and (re.fullmatch(rule[0],user) or matchGroup(user,rule)):
                            action = rule[2]
                            if action.upper() == "DENY":
                                im.putpixel( (w,h), (0,0,0))
                            matchFound = True
                            break;
                if not matchFound: #Apply defaultAction if none of the rules match
                    if self.action.upper() == "DENY":
                        im.putpixel( (w,h), (0,0,0))

        return im
