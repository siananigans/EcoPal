from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
import overpy
import math
from geopy.geocoders import Nominatim
from .models import Saved_search
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

def Make_box(longitude, latitude, distance):#Function to make the openstreet maps box search area
    distance = int(distance)
    longitude = float(longitude)
    latitude = float(latitude)
    OneDegree = 111 #Degree to km ratio
    NewDistance = distance/OneDegree # hypotenuse
    Line = (math.sin(0.785398)) * NewDistance # makes distace from right angled triangle formula
    long1 = longitude - Line # 4 coordinates
    long2 = longitude + Line
    lat1 = latitude - Line
    lat2 = latitude + Line
    Coords = [long1,lat1,long2,lat2]
    # then send to search to query open street maps
    return search(str(Coords[0]),str(Coords[1]),str(Coords[2]),str(Coords[3]), longitude, latitude, distance)


def Find_Coords(request):
    # get your location and distancce
    distance = request.POST['Distance']
    longitude = request.POST['Longitude']
    latitude = request.POST['Latitude']
    # send to function to find area
    results = Make_box(longitude, latitude, distance)
    return HttpResponse(results)#['myCoords']
    #return render(request, "results.html", results )

def search(a,b,c,d, lo,la, dis):
    #use coords to query open street maps
    # bbox is the box with range set by user
    bbox = b+","+a+","+d+","+c
    # my api
    api = overpy.Overpass()
    # endpoint
    r = api.query("""node["amenity"="recycling"]("""+bbox+""");out;""")
    coords = []
    # extract info needed
    coords += [(float(node.lon), float(node.lat), node.tags) for node in r.nodes]
    if len(coords) == 0:
        return "There are no places for you to recycle whithin this radius."
    var = {'myCoords' : coords}
    # sort the information
    return sort(var['myCoords'], lo, la, dis)
    

def sort(lst, lo, la, dis): # sort the results

    newlst = []
    i = 0
    while i < len(lst):
        newlst.append("Result: ")
        tmp = lst[i]
        Coords = (lo,la)
        # if coordintes are given, find distance from user and address
        if len(tmp) == 3:
            newlst.append(FindDist(tmp[0:2], Coords) + " Km away. ")
            newlst.append(nodeLocation(tmp[0:2]) + ". ")
        else:
            newlst.append("No Coordinates given. ")

        if tmp[2]:
            dic = tmp[2]
            # if name is given in tags return it
            if 'name' in dic.keys():
                newlst.append("Name = " + dic["name"] + ". ")
            if 'recycling_type' in dic.keys():
                newlst.append("Recycling Type = " +dic["recycling_type"] + ". ")
            # shows what the place can recycle
            terms = [k for k in dic.keys() if 'recycling:' in k and dic[k] == "yes"]
            for n in terms:
                newlst.append("You can recycle " + n[10:] + " here. ")
    
        i += 1
    
    newlst.append(dis)
    mydict = {
        "MyLst" : newlst
    }
    return mydict["MyLst"]

def FindDist(TheirCo, MyCo): #find dist from their coordinates to mine
    eq1 = (MyCo[0]- float(TheirCo[0]))**2 #distance formula
    eq2 = (MyCo[1]- float(TheirCo[1]))**2
    codist = math.sqrt(eq1+eq2)
    kmDist = codist*111 # ratio
    return str(round(kmDist, 1))

def nodeLocation(Coords): # Use geopy to find address of node
    TheirCo = (str(Coords[1]) + ", " + str(Coords[0]))
    geolocator = Nominatim(user_agent="EcoPal")
    location = geolocator.reverse(TheirCo)
    return location.address


def save_search(request):
    savedSearch = Saved_search()
    search = request.POST['Data']
    savedSearch.result = search
    Uname = request.user
    savedSearch.user = User.objects.get(username=Uname)
    savedSearch.save()
    return HttpResponse("Working")
