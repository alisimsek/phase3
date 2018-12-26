from django.db import models

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=50)
    groups = models.ManyToManyField(Group)
    password = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)

class Image(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    action = models.CharField(max_length=10) # ALLOW, DENY, BLUR
    ruleList = models.CharField(max_length=5000) # can be a lot of rules
    owner = models.OneToOneField(User, null = False, on_delete=models.CASCADE) # Every image has one owner

    def __str__(self):
        return ' '.join(["Name: " + self.name, "\nAction: " + self.action, "\nRule List: " + self.ruleList, "\nOwner: " + self.owner])
