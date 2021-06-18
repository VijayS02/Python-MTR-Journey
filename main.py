"""CSC111 Winter 2021 Project: MTR Journey Times, Part 4: Main program

This is the main program that is to be run

Note: Some of this code has been taken from a1 of the CSC111 materials. This code has been modified
to suit the needs of this program.

Copyright and Usage Information
===============================

All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2021 Vijay Sambamurthy.
"""
from typing import Optional

import pygame
from pygame.color import THECOLORS

from classes import SystemMap
from data_collection import load_utf8_csv, write_station_csv
from information_processing import load_csv_lines, load_csv_stations
from visualization import draw_circle, draw_mappings, draw_path, draw_text, initialize_screen, \
    SQUARE_SIZE

AEL_BOX_WIDTH = 200
AEL_BOX_HEIGHT = 50

# Fare types
OCT_ADT = 4
OCT_STU = 5
SING_ADT = 6
OCT_CON_CHILD = 7
OCT_CON_ELD = 8
OCT_CON_PWD = 9
SING_CON_CHILD = 10
SINGLE_CON_ELD = 11


def generate_box_mapping(data: list[list[str]],
                         coord_data: list[tuple[int, int]]) -> dict[str: tuple[int, int]]:
    """Takes the list of coordinates and applies the same duplicate removal process in mapping.py
    and matches the given coordinate to the given station.

    coord_data: data generated by the mapping.py program
    data: list of station codes in order as seen in the main data that will be used in this program

    return: a dictionary containing a mapping of {station_code: position} where position is the top
    left of the station's click box
    """
    sta_data = data.copy()
    coord_vals = coord_data.copy()

    stations = {}
    for val in sta_data:
        temp = val[2]
        if temp not in stations:
            stations[temp] = coord_vals.pop()
    return stations


def get_click_station(event: pygame.event,
                      mapped_coords: dict[str: tuple[int, int]]) -> Optional[str]:
    """Based on a click event, this function will return which station was clicked.

    It does this by checking if the position was within the click box. Simply put, suppose the click
    happened at x,y. where 0,0 is the top left of the screen and 100,0 is 100 pixels from the left
    along the top.

    this function checks if square start x <= x <= square end x AND
    square start y <= y <= square end y

    this square size is defined by mapping and the SQUARE_SIZE parameter in visualization.py

    mapped_coords: the dictionary generated by generate_box_mapping

    return: station code in the form of a string
    """
    for key in mapped_coords:
        lower_x = mapped_coords[key][0]
        upper_x = lower_x + SQUARE_SIZE
        if lower_x <= event.pos[0] <= upper_x:
            lower_y = mapped_coords[key][1]
            upper_y = lower_y + SQUARE_SIZE
            if lower_y <= event.pos[1] <= upper_y:
                return key
    return None


def set_station(sta_fr: str, sta_to: str, event: pygame.event,
                mapped_coords: dict[str: tuple[int, int]]) -> (str, str):
    """Based on a click, this function will set either the destination station (right/middle click)
    or the source station (left click) by seeing if a station was clicked on using the
    get_click_station function.

    return: updated source station and destination station ids.
    """
    key = get_click_station(event, mapped_coords)
    if key is not None:
        if event.button == 1 and sta_to != key:
            sta_fr = key
        elif event.button == 3 and sta_fr != key:
            sta_to = key
    return sta_fr, sta_to


def run_path(sta_fr: str, sta_to: str, system: SystemMap,
             ael_mode: bool) -> Optional[tuple[Optional[list[str]], float]]:
    """This function simply checks if valid entries have been provided for source and destination
    stations. If so, it will call the dijkstra function from classes.py

    system: the generated system containing all station and line information.
    sta_fr: source station code
    sta_to: destination station code

    return: returns the same values as dijkstra method in classes.py
    """
    if sta_fr is not sta_to and sta_fr is not None and sta_to is not None:
        return system.dijkstra(sta_fr, sta_to, ael_mode)
    return None


def draw_ael_selector(screen: pygame.Surface, ael: bool, pos: tuple[int, int]) -> None:
    """Draws the airport express mode selector button on the screen at the given position
    """
    color = "green"
    if ael:
        text = "AIRPORT EXPRESS ON"
    else:
        text = "AIRPORT EXPRESS OFF"
        color = "red"

    pygame.draw.rect(screen, THECOLORS[color], (pos[0], pos[1],
                                                AEL_BOX_WIDTH, AEL_BOX_HEIGHT), 2)

    draw_text(screen, text, (pos[0] + 5, pos[1] + 5))


def check_ael_click(event: pygame.event, ael: bool, pos: tuple[int, int]) -> bool:
    """Checks if airport express button has been clicked and then switches the ael mode
    if it is clicked.
    """
    if pos[0] <= event.pos[0] <= pos[0] + AEL_BOX_WIDTH:
        if pos[1] <= event.pos[1] <= pos[1] + AEL_BOX_HEIGHT:
            return not ael
    return ael


def set_price_text(path: list[str], weight_raw: float,
                   system: SystemMap, price_data: list[list[str]], unit: str) -> str:
    """Returns the text for the price based on the given input parameters.

    return: String that represents what text to display.
    """
    weight = round(weight_raw, 2)
    prices = get_price_info(path, system, price_data)
    if prices is not None:
        # If price information is available
        station1_name = system.stations[path[0]].english_name
        station2_name = system.stations[path[-1]].english_name
        # This can be changed from OCT_ADT to any of the constants described at the
        # top of the file. From the "fare types" section.
        text = f"Octopus adult fare from {station1_name} to {station2_name}: " + \
               str(prices[OCT_ADT]) + f"HK$, this journey is {weight} {unit}(s)"
    else:
        text = f"This journey is {weight} {unit}(s)"
    return text


def run_main(boxes: list[tuple[int, int]], mapping: dict[str: tuple[int, int]],
             system: SystemMap, price_data: list[list[str]], params: tuple[str, bool]) -> None:
    """Run the full program.
    Displays an MTR map which can be clicked. Left click sets the source station, right click
    sets the destination station. A visualization of the path will then be generated and shown.
    In addition, the price of the given trip will be listed.

    params: Tuple containing (<the str unit describing the weights in the graph>, <a boolean value
    describing whether or not the program should show the boundaries of each station's click box.>)
    """
    image = pygame.image.load(r'data/mtrmap.png')
    screen = initialize_screen((image.get_width(), image.get_height() + 100),
                               [pygame.MOUSEBUTTONDOWN], "Calibration")
    station_start = None
    station_to = None
    path = []
    text = ""
    ael_button_pos = (image.get_width() - 300, image.get_height() + 30)
    ael_mode = False

    while True:
        # Draw the MTR Map (on a white background)
        screen.fill(THECOLORS['white'])
        screen.blit(image, (0, 0))
        draw_path(screen, path, mapping)
        # Create button for airport express mode
        draw_ael_selector(screen, ael_mode, ael_button_pos)

        if params[1]:
            draw_mappings(screen, boxes)

        # Draw clicked stations
        if station_start is not None:
            draw_circle(screen, mapping[station_start], 'green')

        if station_to is not None:
            draw_circle(screen, mapping[station_to], 'red')

        draw_text(screen, text, (20, image.get_height() + 20))
        draw_text(screen, "Left click to select source, Right click for destination",
                  (20, image.get_height() + 50))

        pygame.display.flip()

        # Wait for an event (either pygame.MOUSEBUTTONDOWN or pygame.QUIT)
        event = pygame.event.wait()

        if event.type == pygame.MOUSEBUTTONDOWN:
            ael_mode = check_ael_click(event, ael_mode, ael_button_pos)
            # Handle the click event
            station_start, station_to = set_station(station_start, station_to, event, mapping)
            result = run_path(station_start, station_to, system, ael_mode)
            if result is not None:
                # If an actual path was generated
                path = result[0]
                text = set_price_text(result[0], result[1], system, price_data, params[0])

        elif event.type == pygame.QUIT:
            break

    pygame.display.quit()


def get_price_info(path: list[str], system: SystemMap,
                   price_data: list[list[str]]) -> Optional[list]:
    """This function takes a path and generates the price listings for the given source and
    destination station by looking them up from the price_info data.

    price_info: the data read from the mtr_lines_fares.csv file
    system: a map of the entire system containing stations and lines
    path: path generated by dijkstra algorithm in classes.py
    """
    if path is None:
        return None
    station_src = system.stations[path[0]].english_name
    station_dst = system.stations[path[-1]].english_name
    for entry in price_data:
        if entry[0] == station_src and entry[2] == station_dst:
            return entry
    return None


def append_to_modified(modified: str, append: str, new: str) -> None:
    """This function simply combines 2 csvs by adding the entries in them together and writes it out
    to a new file.

    This is required because the MTR information does not contain a line for walking (i.e. beteween
    central and Hong Kong station). By adding a custom append.csv, we can account for this and add
    a "line" of sorts which operates at walking speed.
    """
    modified_data = load_utf8_csv(modified)
    modified_data += load_utf8_csv(append)
    write_station_csv(modified_data, new)


def user_select_weight_mode() -> bool:
    """Gets user input on whether time or km is to be used as weights for the stations.

    return: boolean value dictating if time should be used (true = time, false = km)
    """
    print("Would you like distances between the stations to be in Km or Minutes? ")
    res = input("Please enter 'km' or 'min'.\n")
    while res not in ["km", 'min']:
        print("Would you like distances between the stations to be in Km or Minutes? ")
        res = input("Please enter 'km' or 'min'.\n")
    return res == "min"


if __name__ == "__main__":
    # Load raw station data
    station_data = load_utf8_csv("data/modified_lines_and_stations.csv")
    # Load raw line data
    coords = load_utf8_csv("data/coord_mappings.csv")[::-1]
    # Load price information
    price_info = load_utf8_csv("data/mtr_lines_fares.csv")

    tupled_coords = []
    for i in range(len(coords)):
        # Convert coordinates to integers and lists to tuples
        tupled_coords.append((int(coords[i][0]), int(coords[i][1])))

    # Generate the click box mapping for use later on
    coord_mapping = generate_box_mapping(station_data, tupled_coords)

    # Initialize the system
    main_system = SystemMap()

    # Add all the lines to the system
    for line in load_csv_lines("data/lines.csv"):
        main_system.add_line(line)

    # Append the required modifications to the raw data (read append_to_modified())
    append_to_modified("data/modified_lines_and_stations.csv",
                       "data/append.csv", "data/modified_lines_and_stations_APPENDED.csv")

    # Set the units the user would like.
    unit_bool = user_select_weight_mode()
    if unit_bool:
        units = "min"
    else:
        units = "km"

    # Load the data into the system
    load_csv_stations("data/modified_lines_and_stations_APPENDED.csv", main_system, unit_bool)

    # Change False to True if you would like the click boxes to be shown.
    run_main(tupled_coords, coord_mapping, main_system, price_info, (units, False))
