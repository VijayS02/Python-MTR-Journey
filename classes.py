"""CSC111 Winter 2021 Project: MTR Journey Times, Classes: Station, Line

This file contains the class definitions for the objects used throughout the different modules
in the project.

Note: Some of this code has been taken from a1 of the CSC111 materials. This code has been modified
to suit the needs of this program.

Copyright and Usage Information
===============================

All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2021 Vijay Sambamurthy.
"""
from __future__ import annotations
from heapq import heappop, heappush
from typing import Optional

import geopy.distance


LINES = ["AEL", "DRL", "EAL", "ISL", "KTL", "TML", "TCL", "TKL", "TWL", "WRL", "KTL", "SIL"]


class Station:
    """A station object.

    Instance Attributes:
        - line_codes: The line codes for this given station (multiple because stations can be on
        multiple lines)
        - station_code: The three letter code for the current station
        - chinese_name: Traditional chinese name for the station
        - coords: coordinates for this current station
        - english_name: English name for the station
        - neighbours: Regular neighbours for this station. Stored in a mapping station_code: weight
        (Note that weight could be either time or distance depending on load_csv_stations)
        - ael_neighbours: Airport Express neighbours for this station stored similarly to
        neighbours
    """
    line_codes: set[str]
    station_code: str
    coords: tuple[float, float]
    english_name: str
    neighbours: dict[str, float]
    ael_neighbours: dict[str, float]

    def __init__(self, line_code: str, station_code: str,
                 english_name: str, pos: tuple[float, float]) -> None:
        """Initialize a new Station with the given input values.

        This Station is initialized with no neighbours.
        """
        self.line_codes = {line_code}
        self.station_code = station_code
        self.english_name = english_name
        self.neighbours = {}
        self.coords = pos
        self.ael_neighbours = {}

    def add_line(self, line_code: str) -> None:
        """Add a line to this station
        """
        self.line_codes.add(line_code)

    def add_neighbour(self, station: str, value: float, ael: bool = False) -> None:
        """Add a neighbour. If ael is true, they will be added as an airport express neighbour

        value: is the weight between this station and the station to be added as a neighbour.
        """
        if ael:
            self.ael_neighbours[station] = value
        else:
            self.neighbours[station] = value

    def get_weight(self, station: str, ael: bool) -> float:
        """Get weight between this station and the specified station (if it exists as a neighbour).

        If ael is set to true, it will check in airport express neighbours also. Otherwise,
        airport express neighbours are ignored.
        """
        if ael:
            if station in self.ael_neighbours:
                return self.ael_neighbours[station]
            elif station in self.neighbours:
                return self.neighbours[station]
            else:
                raise ValueError
        else:
            if station in self.neighbours:
                return self.neighbours[station]
            else:
                raise ValueError


def get_dist(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """Get the distance between 2 latitude and longitude pairs.
    """
    return geopy.distance.distance(coord1, coord2).km


class Line:
    """A line object.

    Instance Attributes:
        - line_code: The three letter line code describing this line
        - stations: a dictionary mapping containing : {position of station along line : station}
        - english_name: English name for the line
        - operating_speed: (Average) Operating speed of the trains traveling on the line
    """
    line_code: str
    stations: dict[int: list[Station]]
    english_name: str
    operating_speed: int

    def __init__(self, line_code: str, english_name: str, operating_speed: int) -> None:
        """Initialize a new Line with the given input values.

        This Line is initialized with no Stations.
        """
        self.line_code = line_code
        self.english_name = english_name
        self.operating_speed = operating_speed
        self.stations = {}

    def add_station(self, station: Station, sequence: int) -> None:
        """Add a station to the line
        """
        if sequence in self.stations:
            self.stations[sequence].append(station)
        else:
            self.stations[sequence] = [station]

    def add_connecion(self, sta1: Station, sta2: Station, time: bool) -> None:
        """Add a connection between 2 stations on a line.
        This sets each station as a neighbour of the other (If this line is airport express then
        they will be added as Airport Express neighbours)
        """
        ael = self.line_code == "AEL"
        weight = get_dist(sta1.coords, sta2.coords)
        if time:
            weight = (weight / self.operating_speed) * 60 + 1
        sta1.add_neighbour(sta2.station_code, weight, ael)
        sta2.add_neighbour(sta1.station_code, weight, ael)


class SystemMap:
    """An entire metro system map.

    Instance Attributes:
        - lines: a dictionary mapping containing {line_code : line}
        - stations: a dictionary mapping containing {station_code : station}
    """
    lines: dict[str, Line]
    stations: dict[str, Station]

    def __init__(self) -> None:
        """Initialize an empty system"""
        self.lines = {}
        self.stations = {}

    def add_station(self, station: Station) -> None:
        """Add a station to the system Map.
        If it already exists, copy the properties of the station object to the existing station in
        the map.
        """
        if station.station_code in self.stations:
            cur_sta = self.stations[station.station_code]
            for line_code in station.line_codes:
                cur_sta.add_line(line_code)
            for neighbour in station.neighbours:
                cur_sta.add_neighbour(neighbour, station.get_weight(neighbour, False))
            for neighbour in station.ael_neighbours:
                cur_sta.add_neighbour(neighbour, station.get_weight(neighbour, True), True)
            self.stations[station.station_code] = cur_sta
        else:
            self.stations[station.station_code] = station

    def add_line(self, line: Line) -> None:
        """Add a line and all the stations on the line to the system.
        """
        self.lines[line.line_code] = line
        for key in line.stations:
            for station in line.stations[key]:
                self.add_station(station)

    def dijkstra(self, station_start: str, station_end: str,
                 airport_exp: bool = False) -> tuple[Optional[list[str]], float]:
        """Shortest path algorithm between 2 stations on a system map. This uses heapq from python
        in order to decrease running time. Dijkstra's runtime is based on decrease_key and pop_min
        runtime.

        station_start: station_code of source station
        station_end: station_code of destination station
        airport_express: whether airport express can be used or not.
        """
        if station_start not in self.stations and station_end not in self.stations:
            return (None, 0)
        q = []
        visited = {}
        heappush(q, (0, station_start, None))
        heappush(q, (float('inf'), None, None))
        data = (None, 0, False)
        while q:
            (dist, cur_station, prev) = heappop(q)

            # This while loop is used because decrease key does not exist for heapq
            # This works because if the station has been popped from the priority queue already,
            # it means that the station already had a shorter path to it. And thus it can be
            # ignored.
            while cur_station in visited:
                if len(q) == 0:
                    # Path was not found
                    break
                (dist, cur_station, prev) = heappop(q)

            if cur_station is None:
                break

            if cur_station == station_end:
                data = (prev, dist, True)
                break

            visited[cur_station] = (dist, prev)
            cur_station_obj = self.stations[cur_station]

            if airport_exp:
                # Check all neighbours if airport express is allowed
                neighs = cur_station_obj.neighbours.copy()
                neighs.update(cur_station_obj.ael_neighbours)
            else:
                # Only check regular neighbours
                neighs = cur_station_obj.neighbours.copy()

            for neigh_code in neighs:
                neigh = self.stations[neigh_code]
                heappush(q, (dist + neigh.get_weight(cur_station, airport_exp),
                             neigh_code, cur_station))

        if data[2]:
            # If destination was reached, backtrack to generate a path that was taken. NOTE: Prev
            # is used here to meet PyTa requirements (previous would have been used to avoid
            # confusion between variables
            prev = data[0]
            path = [station_end]
            while prev is not None:
                path.append(prev)
                prev = visited[prev][1]
            # Reverse the path so that it starts at the source station
            return (path[::-1], data[1])

        # No path was found
        return (None, 0)
