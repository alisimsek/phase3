from PIL import Image
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import io
import os
import sqlite3
import math
import re
import ast

class LabeledImage:

    def __init__(self, image = None, defaultAction = "ALLOW", ruleList = None, owner = None): # We need to specify the owner of the class while constructiong
        self.image = image    # self.image is in binary from. Convert it back to Image object to print it out
        self.defaultAction = defaultAction
        self.ruleList = ruleList or []
        self.owner = owner
        self.user = owner


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

    def load(self,name):
        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            result = cur.execute("select * from images where name = ?",(name,))
            result_list = result.fetchall()
            self.image = result_list[0][1]
            self.defaultAction = result_list[0][2]
            self.ruleList = ast.literal_eval(result_list[0][3]) # Convert stored ruleList back to its original form
            self.owner = result_list[0][4]
        except Exception as e:
            print("SQL error", e)
        finally:
            db.close()


    def save(self,name):
        if self.owner == self.user:
            try:
                db=sqlite3.connect("mydb.db")
                cur = db.cursor()
            except Exception as e:
                print("SQL error",e)

            try:
                ruleListString = str(self.ruleList) # Convert ruleList into string to be able to store it in database
                cur.execute("insert into images values (?,?,?,?,?)", (name,self.image,self.defaultAction,ruleListString,self.owner))
                db.commit()
            except Exception as e:
                print("SQL error",e)
            finally:
                db.close()
        else:
            raise Exception("User doesn't own the image !")

    def setDefault(self,action):
        if self.owner == self.user:
            self.defaultAction = action
        else:
            raise Exception("User doesn't own the image !")

    def addRule(self,matchexpr, shape, action, pos = -1):
        if self.owner == self.user:
            rule = (matchexpr, shape, action)
            if pos == -1:
                self.ruleList.append(rule)
            else:
                self.ruleList.insert(pos, rule)
        else:
            raise Exception("User doesn't own the image !")

    def delRule(self,pos):
        if self.owner == self.user:
            del self.ruleList[pos]
        else:
            raise Exception("User doesn't own the image !")

    def getImage(self,user):

        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
            res = cur.execute("select * from users where name = ?",(user,)).fetchall()
            if len(res) == 0:
                print("Couldn't find given user with name " + user + " in database: ")
                return
        except Exception as e:
            print("SQL error ",e)
            return False

        im = Image.open(io.BytesIO(self.image))
        width,height = im.size

        for w in range(width):
            for h in range(height):
                matchFound = False
                for rule in self.ruleList:
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
                    if self.defaultAction.upper() == "DENY":
                        im.putpixel( (w,h), (0,0,0))

        return im


class UserGroup: # Every method in this class is static

    @staticmethod
    def addUser(name, groups, password):
        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            cur.execute("insert into users values (?,?,?)", (name, "-".join(groups), password,))
            for group in groups:
                cur.execute("insert or ignore into groups values (?)",(group,))
            db.commit()
        except Exception as e:
            raise Exception("Username is taken")
        finally:
            db.close()

    @staticmethod
    def addGroup(name):
        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            cur.execute("insert into groups values (?)", (name,))
            db.commit()
        except Exception as e:
            print("SQL error",e)
        finally:
            db.close()

    @staticmethod
    def delUser(name):
        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            cur.execute("delete from users where name = ?",(name,))
            db.commit()
        except Exception as e:
            print("SQL error", e)
        finally:
            db.close()

    @staticmethod
    def delGroup(name): # del group from groups database, also update users database
        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            cur.execute("delete from groups where name = ?",(name,))
            db.commit()
            users = UserGroup.getUsers(name) ## Update users database after deleting a group
            for user in users:
                groups = UserGroup.getGroups(user)
                password = cur.execute("select password from users where name = ?",(user,)).fetchall()[0][0]
                groups.remove(name)
                UserGroup.delUser(user) # Delete user to update its group list
                UserGroup.addUser(user, groups, password)
        except Exception as e:
            print("SQL error", e)
        finally:
            db.close()

    @staticmethod
    def getGroups(name):
        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            resultSet = cur.execute("select groups from users where name = ?",(name,))
            return ((resultSet.fetchall())[0][0]).split("-")
        except Exception as e:
            print("SQL error", e)
        finally:
            db.close()

    @staticmethod
    def getUsers(name):
        userList = []

        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            resultSet = cur.execute("select * from users")
            for row in resultSet:
                if re.search(name,row[1]):
                    userList.append(row[0])
        except Exception as e:
            print("SQL error", e)
        finally:
            db.close()
            return userList

    @staticmethod
    def setPassword(user, password):
        try:
            db=sqlite3.connect("mydb.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL error",e)

        try:
            cur.execute("update users set password = ? where name = ?",(password,user,) )
            db.commit()
        except Exception as e:
            print("SQL error",e)
        finally:
            db.close()

    @staticmethod
    def isMember(user, group):
        userList = UserGroup.getUsers(group)
        if user in userList:
            return True

        return False




####################################  General purpose functions

def insideRectangle(x,y,rect):
    if (x >= rect[1] and x <= rect[3]) or (x <= rect[1] and x >= rect[3]):
        if (y >= rect[2] and y <= rect[4]) or (y <= rect[2] and y >= rect[4]):
            return True

    return False

def insideCircle(x,y,circ):
    center_x = circ[1]
    center_y = circ[2]
    radius = circ[3]
    if math.sqrt((x - center_x)**2 + (y - center_y)**2) <= radius:
        return True
    else:
        return False


def insidePolyline(x,y,polyline):
    points = polyline[1]
    polygon = Polygon(points)
    point = Point(x,y)
    return polygon.contains(point)

    """size = len(points)
    i = 0
    while i < size-1:
        point1 = points[i]
        point2 = points[i+1]
        try:
            slope = (point1[1]-point2[1])/ (point1[0]-point2[0])
            if (x <= point1[0] and x >= point2[0]) or (x >= point1[0] and x <= point2[0]):
                if (y <= point1[1] and y >= point2[1]) or (y >= point1[1] and y <= point2[1]):
                    if abs(y-point1[1] - slope * (x - point1[0])) < 0.01:
                        return True
        except Exception as e:
            if (x <= point1[0] and x >= point2[0]) or (x >= point1[0] and x <= point2[0]):
                if (y <= point1[1] and y >= point2[1]) or (y >= point1[1] and y <= point2[1]):
                    if abs(x-point1[0]) < 0.01:
                        return True

        i += 1
    return False"""


def matchGroup(user,rule):
    u = UserGroup()
    userGroups = u.getGroups(user)
    for group in userGroups:
        if re.fullmatch(rule[0],group):
            return True

    return False



def createTables():
    try:
        db=sqlite3.connect("mydb.db")
        cur = db.cursor()
    except Exception as e:
        print("SQL error",e)

    try:
        cur.execute("create table if not exists images(name TEXT primary key, image BLOB, action TEXT,ruleList TEXT, owner TEXT)")
        cur.execute("create table if not exists users(name TEXT primary key, groups TEXT, password TEXT)")
        cur.execute("create table if not exists groups(name TEXT primary key)")
        db.commit()
    except Exception as e:
        print("SQL error",e)
    finally:
        db.close()


def clearTables():

    try:
        db=sqlite3.connect("mydb.db")
        cur = db.cursor()
    except Exception as e:
        print("SQL error",e)

    try:
        cur.execute("delete from images")
        cur.execute("delete from users")
        cur.execute("delete from groups")
        db.commit()
    except Exception as e:
        print("SQL error",e)
    finally:
        db.close()

def dropTables():
    try:
        db=sqlite3.connect("mydb.db")
        cur = db.cursor()
    except Exception as e:
        print("SQL error",e)

    try:
        cur.execute("drop table images")
        cur.execute("drop table users")
        cur.execute("drop table groups")
        db.commit()
    except Exception as e:
        print("SQL error",e)
    finally:
        db.close()

def printTable(name):
    try:
        db=sqlite3.connect("mydb.db")
        cur = db.cursor()
    except Exception as e:
        print("SQL error",e)

    try:
        rs = cur.execute('select * from {}'.format(name)).fetchall()
        print("\n####### PRINTING " + name.upper() + " DATABASE #######")
        for row in rs:
            print(str(row))
    except Exception as e:
        print("SQL error",e)
    finally:
        db.close()

def imageList():
    try:
        db=sqlite3.connect("mydb.db")
        cur = db.cursor()
    except Exception as e:
        print("SQL error",e)

    try:
        rs = cur.execute('select owner, name from images').fetchall()
        return rs
    except Exception as e:
        print("SQL error",e)
    finally:
        db.close()


########################################
