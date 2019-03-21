import sys
import requests
import json
from common_functions import extract_values

##
# Global definitions
##
mbta_url = "https://api-v3.mbta.com/"
routes_url = mbta_url + "routes?filter[type]=0,1"
r = requests.get(routes_url) 
line_queries = {
    'Red': 'stops?filter[route]=Red&include=route&filter[direction_id]=1',
    'Orange': 'stops?filter[route]=Orange&include=route&filter[direction_id]=1',
    'Blue': 'stops?filter[route]=Blue&include=route&filter[direction_id]=1',
    'Mattapan': 'stops?filter[route]=Mattapan&include=route&filter[direction_id]=1',
    'Green-E': 'stops?filter[route]=Green-E&include=route&filter[direction_id]=1',
    'Green-D': 'stops?filter[route]=Green-D&include=route&filter[direction_id]=1',
    'Green-C': 'stops?filter[route]=Green-C&include=route&filter[direction_id]=1',
    'Green-B': 'stops?filter[route]=Green-B&include=route&filter[direction_id]=1'
}

##
# functions
##

##
# get_line_connections
##
def get_line_connections(subway_dict, value_to_find):
  '''
  Get list of keys from a dictionary of subway lines which has a given value o
  '''
  list_of_connections = []
  for l, v in subway_dict.items():
    if l == value_to_find:
      list_of_connections.append(v)
  return list_of_connections

##
# get_lines
##

def get_lines(stop_to_find):
  ''' 
  Find the lines where a stop is located
  '''
  list_of_lines = []
  for l, v in lines.items():
    if stop_to_find[0] in v:
      list_of_lines.append(l)
  return list_of_lines

##
# subway_routes
#    prints the MBTA subway routes 
## 

def list_subway_lines(): 
  subway_routes = [] 
  output_string = ''
  route_values = extract_values(r.json(), 'long_name') 
  subway_routes = route_values[0:] 
  for i in range(len(subway_routes)): 
    if len(output_string) > 0: 
      output_string = output_string + ', ' + subway_routes[i]
    else:
      output_string = subway_routes[i]
  print("The name of the subway lines are: ", output_string)

#
subway_number_stops = {}
subway_connections = {}

def find_route_ids():
  route_ids = []
  # ids returns the attribute "self" which is of the form /routes/<name> 
  # NOTE TO SELF: IS THERE A BETTER WAY TO DO THIS?
  ids = extract_values(r.json(), 'self')
  for j in range(len(ids)):
    route_ids.append(ids[j][8:])
  return(route_ids)

def seed_dictionaries(): 
  #
  route_ids = find_route_ids()

  # create dictionaries where the key is the name of the subway line
  # the values will be added later
  # 1) subway_stops : lists the subways stops for each line
  subway_stops = dict.fromkeys(route_ids,0)
  # 2) subway_connections : list stops where the line has a connection with another
  subway_connections = dict.fromkeys(route_ids,0)
  # 3) subway_number_stops: total number of stops for each line
  subway_number_stops = dict.fromkeys(route_ids,0)

def get_subway_stops(): 
  subway_stops = {}
  for key, value in line_queries.items():
    u_query = mbta_url + value
    s = requests.get(u_query)
    stops = extract_values(s.json(), 'name')
    subway_stops[key] = stops.copy()
  return(subway_stops)

##
# max_min_stops
#   The name of the subway route with the most stops as well as a count of its stops
###

def max_min_stops(): 
  # List the stops for each of the routes and add them to the dictionary 
  # For each line, run a query to find the list of stops 
  seed_dictionaries()
  s = get_subway_stops()
  for key, value in s.items():
    subway_number_stops[key] = len(value) 
    max_num_stops = max(subway_number_stops.values()) 
    min_num_stops = min(subway_number_stops.values()) 

  print('The', max(subway_number_stops, key=subway_number_stops.get), 'line has the most stops:  ', max_num_stops) 
  print('The', min(subway_number_stops, key=subway_number_stops.get), 'line has the fewer stops:  ', min_num_stops)

##
# line_connections:
#   Find the connections for each of the subway lines
##
def line_connections(): 
  route_ids = find_route_ids()
  s = get_subway_stops()
  for k in range(len(route_ids)): 
    to_compare = s[route_ids[k]] 
    print("the", route_ids[k], "line connects with:") 
    line_connections = [] 
    for i, j in s.items(): 
      if route_ids[k] != i: 
        compare_with = s[i] 
        intersection = list(set(to_compare) & set(compare_with)) 
        if len(intersection) > 0: 
          for x in range(len(intersection)): 
            line_connections.append(intersection[x]) 
          print("   - ", i, "line at", ", ".join(intersection)) 
    subway_connections[route_ids[k]] = list(dict.fromkeys(line_connections))

##
# travel_rout
#   finds the lines to take from one stop to another
##
def travel_route(s):
  # 
  routes = find_route_ids()
  lines_from = []
  lines_to = []
  n = s[0]
  name = n.split(',')
  # TODO: error or print a message if the user entered more than two stops
  print('Finding the line(s) to travel from', name[0], 'to', name[1], '...')
  s = get_subway_stops()
  for k in range(len(routes)):
    line_stops = s[routes[k]]
    if name[0] in line_stops:
      lines_from.append(routes[k])
    if name[1] in line_stops:
      lines_to.append(routes[k])

  # check stop names are valid names
  # if not, print an error and return
  if len(lines_from) == 0:
    print('The stop', name[0], 'is not a valid stop name, verify the name, exiting ...')
  if len(lines_to) == 0:
    print('The stop', name[1], 'is not a valid stop name, verify the name, exiting ...')
  if not lines_from or not lines_to:
    print('Restart the script with valid subway stop names.')

  # check if the stops are on the same line
  share_line = [value for value in lines_from if value in lines_to]
  if share_line:
    print(name[0] , 'to' , name[1] , ' ====> ', share_line)
  else:
    # get connection lines from one stop to the other
    print('The traveler needs to go from', name[0], 'on', lines_from, 'to', name[1], 'on', lines_to)
    # Find if the from line has a connection with the to line


##
# Start here
##

if __name__ == '__main__': 
  import argparse
  
  parser = argparse.ArgumentParser(description = "MBTA subway script")
  parser.add_argument("-l", default=False, action="store_true", dest="list_lines", 
      help="subway lines of type 0 and 1")
  parser.add_argument("-s", default=False, action="store_true", dest="stops", 
      help="subway routes with most and fewer stops and line connections")
  parser.add_argument("-c", nargs=1, dest='c_route', help="lines to travel between two stops, e.g. -c Central,Harvard")

  args = parser.parse_args()
  if args.list_lines:
    list_subway_lines()
  if args.stops:
    max_min_stops()
    line_connections()
  if args.c_route:
    travel_route(args.c_route)
  print('good bye....')
