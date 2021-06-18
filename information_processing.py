"""CSC111 Winter 2021 Project: MTR Journey Times, Part 2: Information Processing

This file is used in main to load data into the objects created in classes.py

Copyright and Usage Information
===============================

All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2021 Vijay Sambamurthy.
"""
import csv

from classes import SystemMap, Station, Line

# Parameter to change certain station's positions in order to make the program work with less change
# required.
# EXCLUSIONS = { Station_code: new station position (int as a string) }
EXCLUSIONS = {"LHP": "2.0"}


def load_csv_lines(filename: str) -> list[Line]:
    """A function designed to open lines.csv and convert each row into a Line object from classs.py.

    filename: string containing the path and file which is to be read.

    return: list of Line objects
    """
    lines = []
    try:
        # Note that 'encoding="utf8"' is required here because the files contain
        # some traditional chinese characters and are encoded with utf8
        # according to the dataspec provided by the mtr, see:
        # https://opendata.mtr.com.hk/doc/DataDictionary.zip
        with open(filename, encoding="utf8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                lines.append(Line(row[0], row[2], int(row[1])))
    except FileNotFoundError:
        raise Exception(f"The file `{filename}` could not be found.")
    return lines


def create_connections(current_line: Line, time: bool) -> None:
    """Creates connections within a line. The function does this by iterating through all possible
    positions along the line and the connecting each one with the next position.

    EXAMPLE:
        Suppose there is a line with 5 stations, resulting in line.stations as follows:
        {1: [station1], 2: [station2, station3], 3: station4, 4: station5}
        The function will start at 1 and then attach station 1 to all stations mapped with position
        2 (ASSUMING they are not in EXCLUSIONS). So, station1 will then connect to station2 and
        station3. Because of how line.add_connection method works, this means that station2 and
        station3 are also connected to station1.

        Then the program iterates a position, connecting both station2 and station3 to station4.
        Once again, the program iterates, connecting station4 to station5.
    """
    for seq in current_line.stations:
        if seq + 1 in current_line.stations:
            for station_a in current_line.stations[seq]:
                for station_b in current_line.stations[seq + 1]:
                    if station_b.station_code not in EXCLUSIONS:
                        current_line.add_connecion(station_a, station_b, time)


def load_csv_stations(filename: str, system: SystemMap, time: bool = False) -> None:
    """Function that converts a file generated by data_collection.py into a systemMap with
    connections. This function mutates a system and does not return any values.
    It does this by creating each line first, and then setting up the connections in the line using
    the above create_connections subprogram and then adding the line to the system.

    filename: file to be read and data to be parsed from
    time: whether to set weights as either time or distance between two stations (True = time)
    """
    try:
        # Note that 'encoding="utf8"' is required here because the files contain
        # some traditional chinese characters and are encoded with utf8
        # according to the dataspec provided by the mtr, see:
        # https://opendata.mtr.com.hk/doc/DataDictionary.zip
        prev_line = Line("", "", 0)
        with open(filename, encoding="utf8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if row[2] in EXCLUSIONS:
                    row[6] = EXCLUSIONS[row[2]]

                if prev_line.line_code != row[0]:
                    if prev_line.line_code != "":
                        create_connections(prev_line, time)
                        system.add_line(prev_line)
                    prev_line = system.lines[row[0]]
                coords = (float(row[7]), float(row[8]))
                # Replace is put here because of a typo seen in the original dataset provided by MTR
                current_station = Station(row[0], row[2],
                                          row[5].replace("Whampo", "Whampoa"), coords)
                prev_line.add_station(current_station, int(float(row[6])))

            create_connections(prev_line, time)
            system.add_line(prev_line)
    except FileNotFoundError:
        raise Exception(f"The file `{filename}` could not be found.")


if __name__ == "__main__":
    # Init an empty system map.
    main_system = SystemMap()

    # Load all the different lines into it.
    for line in load_csv_lines("data/lines.csv"):
        main_system.add_line(line)

    # Add stations and connections to the system.
    load_csv_stations("data/modified_lines_and_stations.csv", main_system, True)
