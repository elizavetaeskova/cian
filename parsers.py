"""
Parsers module with base data analysis workflows

Provides:
clearHTML(data) - clearing string from HTML tags

rooms(data) - parsing rooms from HTML data
price(data) - parsing price from HTML data
information(data) - parsing base information (
    total space,
    living space,
    kitchen space,
    type of building,
    telephone existence,
    balcony existence,
    floor,
    total floors number,
    new or not
) from HTML data table
metrdist(data) - parsing metro distance from HTML data
Coords(data) - parsing coordinates from HTML data
dist(data) - counting distance from coordinates

pars(data) - geeting all parsing together

Author: Elizaveta Eskova
"""

import re
import math

# Clear all HTML tags in string
def clearHTML(data):
    return re.sub('<[^>]*>', '', data)



# Number of rooms
def rooms(data):
    room = data.findAll('div', {'class':'object_descr_title'}) # Search information on the number of rooms
    for value in room:
        if re.search('([0-9]+)\-комн\. кв\.', clearHTML(str(value))) != None:  # Did we find anything?
            room = re.search('([0-9]+)\-комн\. кв\.', clearHTML(str(value))).group(1) # Get only the number
        else:
            room = '-'
    return {
        'Rooms':room
    }


# Price
def price(data):
    pr = data.findAll('div', {'class':'object_descr_price'})
    for value in pr:
         value = clearHTML(str(value))
    if len(pr) > 0: # Did we find anything?
        pr = value
        pr = clearHTML(str(pr)).replace('\n', '').replace('\t', '').split(' ')  # Remove the spaces, tabs and line breaks
        pr = "".join([i for i in pr if i.isdigit()][-3:])
        if pr < 1000000:  # If the seller made a mistake when he wrote the price
            pr = pr * 1000
        return {
            'Price':pr
        }
    else:
        return {
            'Price': '-'
        }

# Parser of the internal table list
def information(data):
    infor = data.findAll('table', {'class': 'object_descr_props flat sale', 'style': 'float:left'})  #Find the table
    if len(infor) > 0:   # Did we find anything?
        infor = clearHTML(str(infor[0])).replace('\n', '').replace('\t', '').replace(' ', '').replace('\xc2\xa0', '')   #Remove the spaces, tabs, line breaks and the special symbol

        #area of flat
        if re.search('Общаяплощадь\:([0-9]+(,[0-9]+)?)м', infor) != None:
            totsp = re.search('Общаяплощадь\:([0-9]+(,[0-9])?)м', infor).group(1)   # group(1) - get only the number without text
        else:
            totsp = '-'    # If the area is not available

        #living area
        if re.search('Жилаяплощадь\:([0-9]+(,[0-9]+)?)м', infor) != None:
            livesp = re.search('Жилаяплощадь\:([0-9]+(,[0-9])?)м', infor).group(1)
        else:
            livesp = '-' # If the area is not available

        #area of kitchen
        if re.search('Площадькухни\:([0-9]+(,[0-9]+)?)м', infor) != None:
            kitsp = re.search('Площадькухни\:([0-9]+(,[0-9])?)м', infor).group(1)
        else:
            kitsp = '-' # If the area is not available

        #type of house
        type = re.search('Типдома\:(новостройка|вторичка)(\,)?(монолитный|кирпичный|кирпично\-монолитный|.+)?(Тип)', infor)
        if type.group(1) == 'новостройка':
            new = 1
        elif type.group(1) == None:   # If the type of house is not available
            new = '-'
        else:
            new = 0


        brick = type.group(3)   # This information is also listed in the "type of house"
        if brick == 'монолитный' or brick == 'кирпичный' or brick == 'кирпично-монолитный':
            brick = 1
        elif brick == '' or brick == 'дом':   # If this information is not available
            brick = 'none'
        else:
            brick = 0

        # Telephone
        if re.search('Телефон', infor) != None:
            if re.search('Телефон\:да', infor) != None:
                tel = 1
            else:
                 tel = 0
        else:
            tel = '-'

        # Balcony
        if re.search('Балкон\:(.+)Лифт', infor) != None:
            bal = re.search('Балкон\:(.+)Лифт', infor).group(1)
            if bal == '-' or bal == '' or bal == 'нет':
                bal = 0
            else:
                bal = 1
        else:
            bal = '-'

        # Floors
        if re.search('Этаж\:([0-9]+)\/([0-9]+)', infor) != None:
            floors = re.search('Этаж\:([0-9]+)\/([0-9]+)', infor)
            floor = floors.group(1)   # This information is available in the first list
            nfloors = floors.group(2)   # This information is available in the second list
        else:    # If this information is not available
            floor = '-'
            nfloors = '-'


        return {
            'Totsp':totsp,
            'Livesp':livesp,
            'Kitsp':kitsp,
            'Brick':brick,
            'Tel':tel,
            'Bal':bal,
            'Floor':floor,
            'Nfloors':nfloors,
            'New':new
        }
    else:
        return {
            'Totsp': '-',
            'Livesp': '-',
            'Kitsp': '-',
            'Brick': '-',
            'Tel': '-',
            'Bal': '-',
            'Floor': '-',
            'Nfloors': '-',
            'New': '-'
        }


# Distance to the metro
def metrdist(data):
    if len(data.findAll('span', {'class':'object_item_metro_comment'})) != 0:
        mdist = data.findAll('span', {'class':'object_item_metro_comment'})

        mdist = clearHTML(str(mdist[0])).replace('\n', '').replace('\t', '').replace(' ', '')
        if re.search('([0-9]+)мин(\.)?(пешком|)', mdist) != None:
            mdist = re.search('([0-9]+)мин(\.)?(пешком|)', mdist)
            if mdist.group(3) == 'пешком':   # This information is available in the third ()
                walk = 1
            else:
                walk = 0
            md = mdist.group(1)   # Distance to the metro is available in the first ()
        else:
            md = '-'
            walk = '-'
    else:   # If this information is not available
            md = '-'
            walk = '-'
    return {
        'Metrdist':md,
        'Walk':walk
    }


def Coords(data):
    if data.findAll('div', {'class':'map_info_button_extend'}) != None:    #If the map is not found
        map = data.findAll('div', {'class':'map_info_button_extend'})
        map = re.split('&amp|center=|%2C', str(map))
        coords_list = []
        for item in map:
            if item[0].isdigit():
                coords_list.append(item)
        if len(coords_list) > 1:
            lat = float(coords_list[0])   # Latitude
            lon = float(coords_list[1])   # Altitude
        else:
            lat = '-'
            lon = '-'
    else:   # If this information is not available
        lat = '-'
        lon = '-'
    return lat, lon

# Distance to the center
def dist(data):
    if Coords(data)[0] != '-':
        # Coordinates of the zero kilometer
        a = 55.755831
        b = 37.617673
        latitude = 111.134861111 * (a - Coords(data)[0])
        longitude = 111.321377778 * (b * math.cos(math.radians(a)) - Coords(data)[1] * math.cos(math.radians(Coords(data)[0])))
        d = math.sqrt(latitude ** 2 + longitude ** 2) # Pythagorean
        d = round(d, 1)  # Round off to the first decimal place (ok with our accuracy)
    else:
        d = '-'
    return {
        'Dist':d
    }

# Putting the information together
def pars(data):
    return dict(rooms(data).items() + price(data).items() + information(data).items() + metrdist(data).items() + dist(data).items())