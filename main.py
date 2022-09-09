import gpxpy
import gpxpy.gpx
import requests
import json
import os
from bs4 import BeautifulSoup
import time
from colorama import Fore
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
gpx = gpxpy.gpx.GPX()
gpx.name = 'Munzee'
gpx.description = 'List of munzees in area'

headers = {
   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

print(Fore.WHITE + "Go to " + Fore.RED + "https://boundingbox.klokantech.com/" + Fore.WHITE + " to select a bounding box, put the CSV output here: ")
inputCoords = input()
inputCoords = inputCoords.split(",")

print("")
print("Add descriptions? This makes it much slower. (yes/no)")
add_desc = input()
add_desc = add_desc.lower()
print("")

API_response = requests.get("https://api.munzee.com/mapapi.php?ex_cap=0&ex_own=0&special=0&rovers=0&clan_id=0&vacant=0&virt=0&phys=0&swappable=0&uncaptured=0&lat2=" + str(inputCoords[1]) + "&lat1=" + str(inputCoords[3]) + "&lon2=" + str(inputCoords[2]) + "&lon1=" + str(inputCoords[0]) + "&playergroup=&forceflats=0&maptoken=&jsonp_callback=jQuery21407871864576856061_1661331044402&_=1661331044404")

json_API = API_response.text[API_response.text.find("(")+1:API_response.text.rfind(")")]
parsed_json = json.loads(json_API)

index = 0
try:
  current_munzee = parsed_json[index]
  normal_method = 1
except KeyError:
  normal_method = 0

amount = len(parsed_json)

for munzee in parsed_json:
  if normal_method == 1:
    current_munzee = parsed_json[index]
  else:
    try:
       current_munzee = parsed_json[str(munzee)]
    except KeyError:
      print(KeyError)
      current_munzee = ".KeyError"

  if current_munzee != ".KeyError":
    gpx_wps = gpxpy.gpx.GPXWaypoint()
    gpx_wps.latitude = current_munzee["lat"]
    gpx_wps.longitude = current_munzee["lon"]
    gpx_wps.symbol = "munzees"
    gpx_wps.name = current_munzee["name"]
 
    if add_desc == "yes":
      API_response = requests.get('https://www.munzee.com/m/' + current_munzee["user"] + "/" + str(current_munzee["number"]) + "/notes", headers=headers)
      soup = BeautifulSoup(API_response.text, 'html5lib')
      t = soup.find('div', attrs={"class":"munzee-main-area col-md-9"})
      description = t.renderContents()
      description = str(description)
      description = description[description.find("</div>")+10:description.find("</div>>")]
      description = description.strip()
      
      gpx_wps.description = description
      gpx_wps.comment = description
      
      print(Fore.WHITE + "(" + str(index + 1) + "/" + str(amount) + ") " + "Added Munzee " + Fore.RED + current_munzee["name"] + Fore.WHITE + " from " + Fore.BLUE + current_munzee["user"] + Fore.WHITE + " with description " + Fore.GREEN + description)
    else:
      print(Fore.WHITE + "(" + str(index + 1) + "/" + str(amount) + ") " + "Added Munzee " + Fore.RED + current_munzee["name"] + Fore.WHITE + " from " + Fore.BLUE + current_munzee["user"])
      
    gpx.waypoints.append(gpx_wps)
  else:
    print(Fore.RED + "Failed to process Munzee " + str(index + 1))
  index = index + 1

timestamp = str(round(time.time()))
f = open(os.path.join(__location__,("Munzees-" + timestamp + ".gpx")), "x")
f.close()
f = open((os.path.join(__location__,("Munzees-" + timestamp + ".gpx"))), "w")
f.write(gpx.to_xml())
f.close()

print("")
print(Fore.WHITE + 'Created GPX file')
if index > 999:
  print(Fore.RED + "WARNING, this GPX file contains over 1000 waypoints, which might be over the limit of some GPS devices.")
  print("More info at https://www.javawa.nl/limieten.html")