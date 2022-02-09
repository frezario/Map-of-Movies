# Map-of-Movies
This repository is made in order to build interactive worldwide maps with Python programing language using folium library.
There are 2 main files - locations.list and map.py.
The first one is the example of the file that contains information about movies in a certain format, specifically: Title | Year of realese | A place where movie was filmed.
 The second one is a Python script that processes the data contained locations.list and builds a map with OpenStreetMap using folium library.
 The map is a html-file that will automatically be opened when map.py will finish it's work.
 To execute map.py, run your console, and enter the following:
 [path-to-python] [path-to-a-script] [year] [default-latitude] [default-longitude] [path-to-dataset]
 The axample of executing:
 python3 /home/frezario/Documents/Projects/Python/map.py 2000 50 50 /home/frezario/Documents/Projects/Python/locations.list
 The executing will last for 1-30 seconds, and it will eventually open .html file that contains a map.
 This map has the following interface:
![Screenshot_20220209_233832](https://user-images.githubusercontent.com/91615650/153294543-727a6b10-5d23-4d8e-b024-804e0d74f367.png)
It has 10 green marks and 10 red marks. Red marks are representing 10 closest films to the place defined by a user, while green ones - 10 farest.
Each of the mark will show you additional information if you hover it with your mouse:
![Screenshot_20220209_234355](https://user-images.githubusercontent.com/91615650/153295254-e3993e0a-351f-463c-9322-0fb2ad6b542c.png)
