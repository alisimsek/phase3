from .models import *

class Element:
    def __init__(self):
        self.username = None
        self.imagename = None

def imageList():
    images = LabeledImage.objects.all()
    i = 0
    imList = []
    while i < images.count():
        image = images[i]
        element = Element()
        element.username =  image.owner.username
        element.imagename = image.name
        imList.append(element)
        i = i+1

    return imList
