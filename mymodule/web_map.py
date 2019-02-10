import folium
import pandas
from geopy.geocoders import Nominatim
import random


def main_function():
	'''
	None -> None
	This function firstly asks user to enter the year which will be
	used for making map with statistic about film. Then this
	function starts another functions for making map. When the map
	will be producing, this function will print information about
	process. Then it will print that production is done and
	name of HTML file.
	'''
	# indicat indicates wether year is typed
	indicat = False
	while indicat == False:
		year = input("Please type what year you want: ")
		try:
			if 1768 < int(year) < 3000:
				indicat = True
			else:
				print("You entered something wrong, please " +
					  "try again. (1768 < year < 3000")
		except:
			print("You entered something wrong, please " +
				   "try again. (notice that year must be int")
			continue
	# there locations.list.txt is the name of file with locations.
	# location dict is dictionary with information which is required
	# to build csv file
	locations_country_dict = dict_cordinats_maker(
		locations_reader(year, "locations.list.txt"))
	print("Reading locations...")
	name_csv_file = csv_maker(locations_country_dict[0])
	print("Making csv file...")
	map_name = map_maker(name_csv_file, year,
						 locations_country_dict[1])
	print("Making your map...")
	print("HTML file with map of {0} year in the directory,"
		  "its name: ".format(year), map_name)


def locations_reader(year, file_name):
	'''
	(str, str) -> lst

	This function reads information from file with locations and
	returns the dict, where keys are names of cities, and values
	are: lat, lon, [films which were produced in this city in this
	year in form of list], count (count is the number of films,
	which were produced in this year in the city).

	:param year: the year of production
	:param file_name: name of file with locations
	:return: [[cordinats, films]]
	'''
	set_of_films = set()
	film_ditector = False
	lst = []
	with open(file_name, "r", encoding="UTF-8", errors="ignore") \
		as file:
		for line in file:
			if line.startswith('"'):
				film_ditector = True
			list_line = line.split()
			if film_ditector == True and len(list_line) > 1 and \
					list_line[0].strip('"') not in set_of_films and \
					list_line[1].strip("()") == year.strip():
				titles = list_line[0].strip('"')
				origin = " ".join(list_line[2:])
				# origin is the locations inf about film from file
				set_of_films.add(titles)
				lst.append([titles, origin])
	return lst


def dict_cordinats_maker(information_lst):
	'''
	(lst) -> (dict, dict)

	This function makes dict where keys are strings of cordinats
	and values are titles of films on form of string and one more
	with countries and their frequences.
	:param information_lst
	:return: locations_dict, country_dict

	>>> dict_cordinats_maker([['Action', 'Los Angeles, \California, USA'], ['Ally', '20th Century Fox Studios - 10201 Pico Blvd., Century City, Los Angeles, California, USA']])
	{'34.0536834, -118.2427669': 'Action', '34.0555654, -118.4178565': 'Ally'}, {'USA' : 2}
	'''
	geolocator = Nominatim(user_agent="specify_your_app_name_here",
						   timeout=50000)
	locations_dict = {}
	country_dict = {}
	random.shuffle(information_lst)
	num = 150
	# there you can change the number of random locations(change num)
	if len(information_lst) > num:
		information_lst = information_lst[:num]
	print("the whole bumber of " +\
		  "films on the map",len(information_lst))
	for information in information_lst:
		title = information[0]
		ident = False
		location = geolocator.geocode(information[1])
		n = 1
		# this loop make coordinats, there was problem: geolocator
		# could not find coordinats of some adreass because of prefix
		# adreas
		while ident == False:
			if location:
				ident = True
			else:
				try:
					inf = information[1].split(",")[n]
					location = geolocator.geocode(inf)
					n += 1
				except:
					location = geolocator.geocode("New-York")
		cordinats = "{},{}".format(location.latitude,
									location.longitude)
		address = (location.address).split(",")[-1].strip()
		if address == 'USA':
			address = "United States"
		elif address == 'UK':
			address = "United Kingdom"
		print(address)
		print(cordinats)
		if address not in country_dict.keys():
			country_dict[address] = 1
		else:
			country_dict[address] += 1
		if cordinats not in locations_dict.keys():
			locations_dict[cordinats] = ["1" + ". " + title + " "]
		else:
			locations_dict[cordinats].append(
				str(len(locations_dict[cordinats]) + 1)
				+ ". " + title + " ")
	for key in locations_dict.keys():
		number = len(locations_dict[key])
		locations_dict[key].append(",{}".format(number))
	return locations_dict, country_dict


def csv_maker(locations_dict):
	'''
	This function makes csv file of films and their cordinats. It
	returns the name of csv file. For making csv file it uses
	dictionary from locations reader.

	:param locations_dict: key = lat, lon; value = titles of films
	:return: string with name of file
	'''
	with open("locations.csv", "w", encoding="UTF-8") as file:
		# making the head of csv file
		file.write("lat,lon,films,number\n")
		for key in locations_dict.keys():
			str_to_write = key + "," + " ".join(locations_dict[key])\
						+"\n"
			file.write(str_to_write)

	return "locations.csv"


def map_maker(name_csv_file, year, country_dict):
	'''
	(str, str) -> str

	This function makes map with 3 layers and return the name of
	this map.
	:param name_csv_file: the name of csv file wich will be used
	for making map.
	:param year: the year of films uses for naming map
	:return: the name of map

	Uses size_colour_creator
	'''
	data = pandas.read_csv(name_csv_file)
	lat = data['lat']
	lon = data['lon']
	films = data['films']
	number = data['number']
	mappy = folium.Map()
	fg_simple = folium.FeatureGroup(name="Locations_map")
	fg_statistic = folium.FeatureGroup(name="Statistic_map")
	fg_percent = folium.FeatureGroup(name="Percentage_map")
	fg_counry_statistic = folium.FeatureGroup(name="Country_stat")
	for lt, ln, titles in zip(lat, lon, films):
		fg_simple.add_child(folium.CircleMarker(location=[lt, ln],
												popup=(
												"films: " + titles),
												fill_color="blue",
												radius=25,
												fill_opacity=0.5))
	for lt, ln, films, n in zip(lat, lon, films, number):
		fg_statistic.add_child(folium.CircleMarker(
			location=[lt, ln],
		    popup=("The number of films in this place which "+\
				   "were made in {} year is ".format(year) + str(n)),
			radius=(size_colour_creator(n)[0]),
			fill_color=(size_colour_creator(n)[1]),
			fill_opacity=0.5))
	# w_n is whole number of films in this file.
	w_n = 0
	for n in number:
		w_n += n
	for lt, ln, n in zip(lat, lon, number):
		percent = round(100 / w_n * n, 2)
		fg_percent.add_child(folium.Marker(location=[lt, ln],
			popup=("The percentage of films filmed at this" +
			" location is {}% out of {}".format(percent, w_n)),
			icon=folium.Icon(color=size_colour_creator(n)[1])))
	fg_counry_statistic.add_child(folium.GeoJson(data=open(
		'world.json', 'r', encoding='utf-8-sig').read(),
		style_function=lambda x: {'fillColor':'green'
			if x['properties']['NAME'] in country_dict.keys()
			and country_dict[x['properties']['NAME']] < 2
else 'orange' if x['properties']['NAME'] in country_dict.keys()
			and country_dict[x['properties']['NAME']] < 10
			else 'red' if x['properties']['NAME'] in country_dict.keys()
else 'white'}))
	mappy.add_child(fg_simple)
	mappy.add_child(fg_statistic)
	mappy.add_child(fg_percent)
	mappy.add_child(fg_counry_statistic)
	mappy.add_child(folium.LayerControl())
	file_name = "Map_{}.html".format(year)
	mappy.save(file_name)
	return file_name


def size_colour_creator(n):
	'''
	int -> (int, str)
	This function returns the values of size and colours.

	:return: size, colour
	'''
	if n >= 5:
		return 20, "black"
	elif n > 2:
		return 15, "red"
	else:
		return 10, "green"


if __name__ == "__main__":
	main_function()