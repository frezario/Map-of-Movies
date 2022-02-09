'''
A program to work with maps.
'''
import argparse
from functools import lru_cache
import re
import folium
from geopy.geocoders import Nominatim, ArcGIS


def get_user_data():
    '''
    A function to return user data passed like args.
    '''
    arg_parser = argparse.ArgumentParser(description='map parameters')
    arg_parser.add_argument(
        'Year', type=int, help='the year of movies release dates')
    arg_parser.add_argument('Lat', type=float, help='the latitude')
    arg_parser.add_argument('Lon', type=float, help='the longitude')
    arg_parser.add_argument('Path', type=str, help='a path to a dataset')
    args = arg_parser.parse_args()

    return args.Year, args.Lat, args.Lon, args.Path


arcgis = ArcGIS(timeout=10)
nominatim = Nominatim(timeout=10, user_agent="notme")
geocoders = [arcgis, nominatim]


@lru_cache(maxsize=None)
def geocode(address: str):
    """
    Returns a tuple of latitude and longitude of an address, given as a string
    >>> geocode("New York, USA")
    (40.71455000000003, -74.00713999999994, 'New York')
    """
    i = 0
    try:
        location = geocoders[i].geocode(address)
        if location is not None:
            return location.latitude, location.longitude, location.address
        i += 1
        location = geocoders[i].geocode(address)
        if location is not None:
            return location.latitude, location.longitude, location.address
    except AttributeError:
        return None


def get_info_by_year(path_to_file:str, year: int):
    '''
    Returns a list of all movies released at a certain year.
    '''
    result = []
    with open(path_to_file, encoding='latin1') as file:
        for line in file:
            if '(' + str(year) + ')' in line:
                result.append(line.replace('\t', ' '))
    for num, item in enumerate(result):
        item = str(item)
        item = item.split()
        name = ''
        location = ''
        index = 0
        for idx, each in enumerate(item):
            if each == '(' + str(year) + ')':
                index = idx
                break
            name += each + ' '
        for each in item[index + 1:]:
            location += each + ' '
        name = name.strip()
        location = re.sub(r'\([^()]*\)', '', location)
        location = location.strip()
        result[num] = (name, year, location)
    return result


def main():
    '''
    The main function
    '''
    year, lat, lon, path = get_user_data()
    world_map = folium.Map(location=[lat, lon], zoom_start=4)
    data = get_info_by_year(path, year)
    world_map.save('map.html')


# if __name__ == '__main__':
#     main()
