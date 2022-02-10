'''
A program to work with maps.
'''
import argparse
from functools import lru_cache
from typing import List, Tuple
import re
import webbrowser
import os
import folium
from geopy.geocoders import Nominatim, ArcGIS
from geopy import distance


arcgis = ArcGIS(timeout=10)
nominatim = Nominatim(timeout=10, user_agent="notme")
geocoders = [arcgis, nominatim]


def distance_between_two_points(point1: Tuple, point2: Tuple):
    """
    Returns the distance between two points on the sphere.
    Args:
        point1 (Tuple): the first point on the sphere.
        point2 (Tuple): the second point on the sphere.
    Returns:
        float: a distance between two points.
    Example:
        >>> distance_between_two_points((0, 0), (50, 50))
        7284.879296903492
    """
    return distance.distance(point1, point2).km


def get_user_data():
    """
    A function to return user data passed with args.
    All arguments are positional.
    Returns:
        tuple: a tuple that contains year, latitude, longitude and a path,
        all provided by a user
    Example:
        No example provided: positional arguments are required.
    """
    arg_parser = argparse.ArgumentParser(description='Arguments of the map')
    arg_parser.add_argument(
        'Year', type=int, help='the year of movies release dates')
    arg_parser.add_argument(
        'Lat', type=float, help='The latitude of the starting point.')
    arg_parser.add_argument(
        'Lon', type=float, help='The longitude of the starting point.')
    arg_parser.add_argument(
        'Path', type=str, help='A path to a file that contains a list of films')
    args = arg_parser.parse_args()
    return args.Year, args.Lat, args.Lon, args.Path


@lru_cache(maxsize=None)
def get_location_by_address(address: str):
    """
    Returns a tuple of latitude and longitude of an address, given as a string.
    Args:
        address: a string that represents an adress.
    >>> get_location_by_address('Washington')
    (38.890370000000075, -77.03195999999997, 'Washington, District of Columbia')
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


def get_info_by_year(path_to_file: str, year: int):
    """
    Processes a data, chosen by a year in a file.
    Args:
        path_to_file (str): a path to a file that contains an information
            about movies.
        year (int): a year of movies' date release.
    Returns:
        list: contains lists of [name, year, location],
        where name is a title of the movie,
        year - when movie was filmed,
        location - where movie was filmed.
    Example:
        type(get_info_by_year('locations.list', 2000))
        list
    """
    result = []
    with open(path_to_file, encoding='latin1') as file:
        for line in file:
            if '(' + str(year) + ')' in line:
                result.append(line.replace('\t', ' '))
    for num, item in enumerate(result):
        item = str(item)
        item = item.split()
        idx = item.index('(' + str(year) + ')')
        name = ' '.join(item[:idx])
        location = ' '.join(item[idx + 1:])
        name = name.strip()
        location = re.sub(r'\([^()]*\)', '', location)
        location = location.strip()
        result[num] = [name, year, location]
    return result


def get_info_formatted(movies_by_year: List[List]):
    """
    Transforms a list of movies that contains an actual location
    of the place where it was filmed.
    Args:
        movies_by_year (List[List]): a list of movies, selected by a
            certain year (see get_info_by_year() function).
    Returns:
        list: formatted list of movies that now contains a presice locaion.
    Example:
        >>> len(get_info_formatted(get_info_by_year('locations.list', 2000)))
        88
    """
    for item in movies_by_year:
        item[2] = get_location_by_address(item[2])
    return movies_by_year


def get_closest_movies(movies_formatted: List[List], location: Tuple):
    """
    Returns 10 closest movies to the selected location.
    Args:
        movies_formatted (List[List]): a list of lists, each of which contains a formatted info
        about movies, processed by a get_info_formatted() function.
        location (Tuple): a tuple containing latitude and longitude.
    Returns:
        list: the 10 closest movies.
    Example:
    >>> get_closest_movies(get_info_formatted(get_info_by_year('locations.list',2000)),(0,0))[0][0]
    '¡Ja me maaten...!'
    """
    for item in movies_formatted:
        item.append(distance_between_two_points(
            (item[2][0], item[2][1]), location))
    return sorted(movies_formatted, reverse=False, key=lambda obj: obj[3])[:10]


def get_farest_movies(movies_formatted: List[List], location: Tuple):
    """
    Returns 10 farest movies to the selected location.
    Args:
        movies_formatted (List[List]): a list of lists, each of which contains a formatted info
        about movies, processed by a get_info_formatted() function.
        location (Tuple): a tuple containing latitude and longitude.
    Returns:
        list: the 10 farest movies.
    Example:
    >>> get_farest_movies(get_info_formatted(get_info_by_year('locations.list',2000)),(0,0))[0][0]
    'i-Generation Superstars of Wrestling: Rodman Downunder'
    """
    for item in movies_formatted:
        item.append(distance_between_two_points(
            (item[2][0], item[2][1]), location))
    return sorted(movies_formatted, reverse=True, key=lambda obj: obj[3])[:10]


def build_map(path: str, lat: float, lon: float, *layouts: list):
    """
    Builds a map using a folium lib and saves it.
    Returns None.
    Args:
        path (str): a path to sav a map.
        lat (float): the latitude chosen.
        lon (float): the longitude chosen.
    """
    world_map = folium.Map(location=[lat, lon], zoom_start=5)
    html = """
    Film name:<br>
    {}<br>
    Coordinates:<br>
    latitude: {}<br>
    longitude: {}<br>
    Place:<br>
    {}
    """
    colors = ['red', 'green', 'blue']
    features = ['The closest', 'The farest', 'Custom']
    while len(layouts) > len(colors):
        colors.append('orange')
    while len(layouts) > len(features):
        colors.append('Custom')
    for idx, container in enumerate(layouts):
        feature_group = folium.FeatureGroup(name=features[idx])
        for item in container:
            iframe = folium.IFrame(html=html.format(
                item[0], item[2][0], item[2][1], item[2][2]), width=300, height=100)
            feature_group.add_child(folium.Marker(location=[item[2][0], item[2][1]],
                                                  popup=folium.Popup(iframe),
                                                  icon=folium.Icon(color=colors[idx])))
            world_map.add_child(feature_group)
    world_map.add_child(folium.LayerControl())
    world_map.save(path)
    webbrowser.open('file://' + os.path.realpath(path))


def main():
    '''
    The main function, in which all the magic takes place.
    '''
    year, lat, lon, path = get_user_data()
    movies_info = get_info_formatted(get_info_by_year(path, year))
    closest_movies = get_closest_movies(movies_info, (lat, lon))
    farest_movies = get_farest_movies(movies_info, (lat, lon))
    build_map('map.html', lat, lon, closest_movies, farest_movies)


if __name__ == '__main__':
    main()
