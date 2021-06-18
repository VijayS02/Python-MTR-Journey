"""CSC111 Winter 2021 Project: MTR Journey Times, Part 1: Data Collection

This file generates the required data for the main program.

Copyright and Usage Information
===============================

All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2021 Vijay Sambamurthy.
"""
import csv
import urllib.parse
from collections.abc import Callable
from typing import Any

import requests


def load_utf8_csv(filename: str) -> list[list[str]]:
    """
    This function is used mainly for the files provided by the MTR as it exclusively sets the
    encoding type (read comments in function for more details).

    filename: A string containing the filename of the csv file that is to be read and parsed.

    return: a list of lists, each element of the larger list is one row.
    """
    data = []
    try:
        # Note that 'encoding="utf8"' is required here because the files contain
        # some traditional chinese characters and are encoded with utf8
        # according to the dataspec provided by the mtr, see:
        # https://opendata.mtr.com.hk/doc/DataDictionary.zip
        with open(filename, encoding="utf8") as file:
            reader = csv.reader(file)

            # Skip the header
            next(reader, None)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        raise Exception(f"The file `{filename}` could not be found.")
    return data


def remove_duplicate_stations(data: list[list[str]]) -> list[list[str]]:
    """Function removes stations if the line code and station combination ahs been seen already.

    This is required because the way the MTR gives data means that there is 2 entries per station
    on a line. (One for each direction along the line).

    return: a duplicate free version (for the purposes of this program) of the original data.
    """
    visited = []
    final = []
    for row in data:
        comb_code = row[0] + ":" + row[2]
        if comb_code not in visited:
            visited.append(comb_code)
            final.append(row)
    return final


def coordinate_finder(result: requests.Response) -> tuple:
    """
    One filter function for the send_get_request function. This filter function is used for
    getting a tuple (lat, long) from the wikipedia geoData api with type props=coordinate.
    More information found: https://www.mediawiki.org/wiki/Extension:GeoData
    """
    json_data = result.json()
    page_values = json_data['query']['pages'].values()
    coordinates = list(page_values)[0]['coordinates'][0]
    return (coordinates['lat'], coordinates['lon'])


def send_get_request(url: str,
                     filter_function: Callable[[requests.Response], Any] =
                     lambda result: result.json()) -> Any:
    """
    The function sends a get request to the given url and returns the result based on the filter
    function.

    NOTE: This function assumes a raw JSON object will be returned from the get call.

    url: The url of the address where the get request is to be made to.
    filter_function: A function that takes a requests.Response object and returns a result based on
    the function. This is an optional parameter, and if not supplied, a json response will be sent.

    return: resulting data passed through the filter function
    """
    res = requests.get(url)
    return filter_function(res)


def write_station_csv(data: list[list[str]], filename: str) -> None:
    """Writes out a list of Station data to the given filename
    """
    with open(filename, 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["Line Code", "Direction", "Station Code", "Station ID", "Chinese Name",
                         "English Name", "Sequence", "Lat", "Long"])
        for row in data:
            writer.writerow(row)
    file.close()


def generate_filter(filename: str) -> dict[str, str]:
    """Filter used to fix any typos seen in the original MTR data. Currently only whampoa is listed
    as whampo.

    filename: file containing filter details in a csv format <incorrect,corrected>

    returns: a dictionary {incorrect: corrected}
    """
    raw = load_utf8_csv(filename)
    return_data = {}
    for row in raw:
        return_data[row[0]] = row[1]
    return return_data


def station_name_filter(name: str, filter_dict: dict[str, str]) -> str:
    """Applies filters to the names of stations as described in generate_filter. But it also adds
    ' station' to the end of each station name.

    filter_dict: filter generated by generate_filter

    returns: modified station name
    """
    keys = filter_dict.keys()
    if name in keys:
        name = filter_dict[name]
    return name.replace("-", "–") + " station"


def get_stations_coordinates(raw_stations: list[list[str]], filter_file: str) -> None:
    """Generates coordinates for each station by sending a get request to a wikipedia API.

    raw_stations: data loaded from the MTR information lines_and_stations.csv
    filter_file: file containing filter for generate_filter function.

    this function is mutating and does not return any data.
    """
    name_filter = generate_filter(filter_file)
    total = len(raw_stations)
    for i in range(total):
        fixed_name = ""
        try:
            fixed_name = station_name_filter(raw_stations[i][5], name_filter)
            url_station_name = urllib.parse.quote(fixed_name)
            request_url = "https://en.wikipedia.org/w/api.php?action=query&prop=coordinates&" + \
                          f"titles={url_station_name}&coprop=country&format=json"
            print(request_url)

            coords = send_get_request(request_url, coordinate_finder)

            raw_stations[i].append(coords[0])
            raw_stations[i].append(coords[1])
        except KeyError:
            # In the case that wikipedia added (MTR) to the station name in order to avoid ambiguity
            print("Original Name failed, trying (MTR) version.")
            fixed_name += " (MTR)"
            url_station_name = urllib.parse.quote(fixed_name)
            request_url = "https://en.wikipedia.org/w/api.php?action=query&prop=coordinates&" + \
                          f"titles={url_station_name}&coprop=country&format=json"
            print(request_url)

            coords = send_get_request(request_url, coordinate_finder)

            raw_stations[i].append(coords[0])
            raw_stations[i].append(coords[1])

        print(f"{i + 1} of {total} stations completed.")


if __name__ == "__main__":

    # Load raw mtr provided data
    stations = load_utf8_csv('data/mtr_lines_and_stations.csv')
    # Remove unwanted empty csv data (There are blank lines at the end of the mtr data)
    stations = stations[:len(stations) - 3]

    # Remove duplicate stations
    stations = remove_duplicate_stations(stations)

    # Add coordinate information
    get_stations_coordinates(stations, 'data/filter.csv')

    # Write out coordinate new modified data
    write_station_csv(stations, "data/modified_lines_and_stations.csv")