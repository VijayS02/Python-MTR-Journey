---
author:
- Vijay Sambamurthy
date: Friday, 16th March, 2021
title: "CSC111 Project: Speed information for the Hong Kong MTR"
---

# Introduction {#introduction .unnumbered}

Note: This is mostly similar to the original project proposal, changes
have been highlighted through italicized text.

Hong Kong is a city known for its fast paced lifestyle and amazing
public transport. One of the most rapid features of Hong Kong is its MTR
(Mass Transit Railway) system. This system carries almost half of Hong
Kong's entire population to their destinations each day (MTR, 2021).

![HK MTR System Map](mtrsystemmap){#fig:subim1 width="0.9\\linewidth"
height="5cm"}

![MTR System Map based on real positions](hkroutemap){#fig:subim2
width="0.9\\linewidth" height="5cm"}

The MTR system is comprised of 11 different lines and over 98 stations.
During this research, the light rail line will be excluded as it is a
completely different type of train, it is also much less commonly used
and is generally not quite considered part of the MTR (it has its own
system map). Each line operates at different speeds and frequencies. The
MTR operates very similarly to the London underground in terms of
structure. Also note that MTR is partially privatized corporation and
runs franchised contracts to countries and cities all over the world
including London, Shenzen, and Sydney.

Most people using the system rely on its efficiency and organization to
get to their destination on time. However, train information and timings
are not a concern for most of the population due to the 1-2 minute
frequency of most lines on the Hong Kong system. But, knowing this
information to an accurate extent (less than 5 minutes of error) could
make people more dependant on the MTR and allow them to fit tighter
schedules because they can easily account for traveling time. The Hong
Kong MTR has delays so rarely that whenever such events occur, they can
easily be expected to be the front page of every local news outlet.

Personally, there was interest as to finding out the timings of the
system and possibly building an app to give information on how long a
journey would take. *Note that there is already an MTR app which
provides this service, however, I am curious as to how accurate it is.
Unfortunately, in the robots.txt of the MTR website, scraping data from
the journey planner is not allowed, meaning that comparisons will have
to be done manually.* Leading me to the question, ***How long does a
given Hong Kong MTR journey approximately take?*** This question is
important in the context of Hong Kong (due to the rushed nature of the
city) and transportation in general due to the reasons explained above.

*In order to investigate the Hong Kong MTR and find out possible route
times, the speed of each line, latitude, and longitude data will be
taken from Wikipedia's API in order to calculate distances between
certain stations.*

# Dataset Description {#dataset-description .unnumbered}

The starting point for the program is the following dataset taken from
<https://data.gov.hk/en-data/dataset/mtr-data-routes-fares-barrier-free-facilities>.
While there is no public location information available data for the MTR
stations. Anyone can acces data containing a list of all MTR stations,
route fares, and station IDs. Some example rows of the \"MTR Lines
(except Light Rail) & Stations\" dataset provided by MTR is:

::: center
+-------+-------+-------+-------+-------+-------+-------+---+
| Line  | Dire  | St    | St    | Ch    | En    | Seq   |   |
| Code  | ction | ation | ation | inese | glish | uence |   |
|       |       | Code  | ID    | Name  | Name  |       |   |
+:=====:+:=====:+:=====:+:=====:+:=====:+:=====:+:=====:+:=:+
| AEL   | DT    | AWE   | 56    | :::   | Asia  | 1.00  |   |
|       |       |       |       |  CJK* | World |       |   |
|       |       |       |       | UTF   | -Expo |       |   |
|       |       |       |       | 8bsmi |       |       |   |
|       |       |       |       | 博    |       |       |   |
|       |       |       |       | 覽館  |       |       |   |
|       |       |       |       | :::   |       |       |   |
+-------+-------+-------+-------+-------+-------+-------+---+
| EAL   | L     | FOT   | 69    | :::   | Fo    | 7.00  |   |
|       | MC-DT |       |       |  CJK* | Tan   |       |   |
|       |       |       |       | UTF   |       |       |   |
|       |       |       |       | 8bsmi |       |       |   |
|       |       |       |       | 火炭  |       |       |   |
|       |       |       |       | :::   |       |       |   |
+-------+-------+-------+-------+-------+-------+-------+---+
| KTL   | DT    | MOK   | 6     | :::   | Mong  | 14.00 |   |
|       |       |       |       |  CJK* | Kok   |       |   |
|       |       |       |       | UTF   |       |       |   |
|       |       |       |       | 8bsmi |       |       |   |
|       |       |       |       | 旺角  |       |       |   |
|       |       |       |       | :::   |       |       |   |
+-------+-------+-------+-------+-------+-------+-------+---+
:::

While most of this is not important, it can be combined with information
from wikipedia which, contains coordinate information, to create a new
dataset. This new dataset that will be created will contain: Line Code,
Direction, Station Code, Station ID, Chinese Name, English Name,
Sequence, Latitude, and Longitude. Each station will have multiple
entries, 2 for each line it is on because of the \"direction\" variable
that MTR has provided. This direction describes whether the direction is
\"up track\" or \"down track\".

In order to get the latitude and longitude data, wikipedia has an API
(<https://en.wikipedia.org/w/api.php>). This can then be used to get a
JSON response containing an object which will contain the coordinates of
the given looked up station. All of this information will be stored in a
CSV file called *modified_stations_and_lines.csv*

Each of the lines that will be used will have research conducted by me
separately to find the operating speed of the train and the acceleration
times. This data will be stored in a CSV file called *lines.csv*. This
contains: Line code, Operating speed (in Kmph), Line English Name for
all lines on the network. It also contains an extra line \"walking\"
which is used for the path between Hong Kong and Central.

A second file created by me, labeled *append.csv* contains information
for the walkway between Central and Hong Kong station. This is required
because there is a walkway between Central and Hong Kong station that is
inside the paid area (area where the train travellers can interchange
lines). By creating this append file, I am pretty much simulating a new
line. This will be appended to the modified lines and stations csv data.

Finally, a third file created by me, titled *filter.csv* is useed to fix
any typos or changes in the station names. This was created because
there is a typo in the station \"Whampoa\" which is simply listed as
\"Whampo\" on the *stations_and_lines.csv*

Python will then use the *lines.csv* file in conjunction with the data
from *modified_stations_and_lines.csv* to calculate \"weights\" which
are actually the time taken to go between adjacent stations. This
calculation will be done by adding 1 minute to the time taken to travel
the distance between the two stations. This one minute is simply an
approximation of the time it takes for the MTR to get up to speed and
the time taken for it to decelerate to a stop. The distance traveled in
this time is negligible. This approximation of 1 minute is taken from me
manually timing a few lines during my journeys on them in the past week.
( See references )

All of this information will be stored in
*modified_stations_and_lines_APPENDED.csv* and *lines.csv*.

After the new dataset has been created, python can then take the newly
created CSV file and consider each station as a node on the graph of the
entire MTR station map. After this, operations can be easily done to
calculate shortest paths.

# Computational Overview {#computational-overview .unnumbered}

**Note: The reason for the separation between airport express and
regular lines is that airport express is significantly more expensive
and most people do not travel on the line unless they need to get to the
airport.**

Before going into the functions executed by the program itself, we must
first look at *classes.py* which contains 3 classes. The first of which
is a **station** object, this object stores station data including
english names, coordinates, neighbours, line codes and more. There are 3
main methods for this class, *add_line*, which simply adds a line code
to the station's line codes. *add_neighbour*, which adds a neighbour to
either airport express neighbours or regular neighbours depending on the
parameters of the method. And finally, *get_weight* which returns the
edge weight between this station and the station specified in the
parameter. This function will only look at airport express neighbours if
specified to in the parameters.

The next class is the **line** object, which contains simple line
information like line code, english name for the line, stations on the
line and operating speeds. Stations that are on the line are stored
based on the sequence at which they are seen on the line. For example,
the Tung Chung Line has the following stations mapping (each entry in
the value's list is a station object):\
\
{1: \[Tung Chung station\], 2: \[Sunny Bay station\], 3: \[Tsing Yi
Station\], 4: \[Lai King station\], 5: \[Nam Cheong station\] \...}\
\
This was done because of the case of the East rail line and the Tseung
Kwan O line, which both have multiple stations at a given sequence on
the line.

![Multiple Starting stations on the East Rail
Line](east_rail_multiple){#fig:subim1 width="0.9\\linewidth"
height="5cm"}

![Multiple stations along the Tseung Kwan O
line](tko_multiple){#fig:subim2 width="0.9\\linewidth" height="5cm"}

The **line** class also has two methods, the first of which is the
*add_station* method, which adds a station to the line. Next, is the
*add_connection* method, which simply makes the 2 stations specified in
the parameters have each other as neighbours (possibly airport express
neighbours if the line is the Airport Express).

Finally, the **SystemMap** class (graph) is comprised of a dictionary of
lines and a dictionary of stations and stores all the stations. The
*add_station* method copies the properties of the station to an existing
version if it already exists, otherwise it simply adds a new station.
The *add_line* method simply adds the line to the lines mapping and adds
every station in the line using the *add_station method*.

\
\
Finally, the main method of the program, **dijkstra**. This algorithm is
an implementation of dijkstra's shortest path algorithm, which uses a
priority queue and generates the shortest path between 2 nodes on a
graph. Here, it generates the shortest path between 2 stations on the
system. A priority queue is used here because the running time of
dijkstra's algorithm is heavily dependant on the *decrease key* and
*extract min* functions of the data type that is being used. A Fibonacci
heap would have been ideal to use in this situation but is a significant
amount of work to implement manually based on a List in python. Hence,
*heapq*, a module in python which is easy to use for what is required
when implementing dijkstra's, was used. Unfortunately, there is no
*decrease key* function. So instead, this version of the algorithm
simply adds a station to the heapq multiple times. And if it has been
visited, it means that there was already a shorter path to that station
found previously, and hence any later entries found in the priority
queue can be ignored.

In addition, this function accounts for whether the user would like to
use airport express or not by looking at the airport express neighbours
of a station if allowed.

The function returns the optimal path between 2 stations.

The functions of the program is split up into 4 separate parts: *Data
collection, information processing, mapping, and the main program*.

1.  **Data Collection**\
    In data collection, the *data_collection* python file is used. This
    file simply loads in the *mtr_lines_and_stations.csv* file and then
    applies some processing.\
    \
    First, it removes the extra lines (Empty rows of a csv file that
    simply contain commas E.g. \",,,,,,\") that are found at the end of
    the file. These blank lines seem to serve no purpose and hence are
    removed.\
    Then, duplicate stations are removed. I.e. if a row of the dataset
    has a line code and station code pair that has already been
    accounted for, that entry in the dataset is ignored.\
    After this, the main function of data collection is run.
    *get_station_coordinates* is a function which takes in the dataset
    which now has no duplicates and then for each line a station is on,
    it sends a get request to a Wikipedia API using the *requests*
    module and then appends the respective data to each station's row in
    the dataset. For example, if the current row is describing Hong Kong
    station, it finds Hong Kong station's coordinates through the API
    and then appends that to that row of Hong Kong station.\
    \
    Finally, the newly modified data is then written out to a file.

2.  **Information Processing**\
    The *information_processing* file mainly contains functions that are
    used to load the data into their respective objects and is used to
    generate a System map from the csv data provided. It does this by
    creating each line separately first, and then running a connections
    function which adds the connections between neighbouring stations.
    Finally, after each line is completed, it adds the entire line to
    the System Map.

3.  **Mapping** This python file is used to inform python where the
    respective stations on the image of the mtr map are. It does this by
    displaying a station name using *pygame* and then expecting the user
    to left click on where they would like the click box for that
    respective station to be. As a result, the coordinates and click
    boxes of the app can be easily changed whenever needed. It then
    writes out this data to a file titled *coord_mappings.csv*. See
    *mapping.py* for more detailed information.

4.  **Main Program** The main program that runs the interactive UI
    through *pygame* which displays a clickable MTR map. Before
    generating the UI however, it first prompts the user (in the
    console) for the units used to describe the weights in the System
    Map, i.e. the units for the edges between two stations on the
    network. After this, the user can then left click to select a source
    station and right click to select a destination station. Once a
    valid selection has been made, price information is looked up from
    the *mtr_lines_fares.csv* and a shortest path is made. The program
    then displays the shortest path in the form of a blue line on the
    image and text beneath containing price and weight information.

    In addition, the user can select whether or not they would like to
    use the airport express via the Airport Express button in the bottom
    right hand side of the screen.

    NOTE: if *run_main* is run with the last parameter
    (*show_station_boxes*) set to true, then the click boxes of each
    station will be displayed on the screen.

*pygame* was used when making interactive elements because the positions
for which clicks are searched can be easily modified from a csv file,
making it easy to change station positions if required. In addition, the
raw nature of *pygame* allows a path to be easily drawn.

# Instructions for Obtaining Datasets {#instructions-for-obtaining-datasets .unnumbered}

Please ensure that all imports in *requirements.txt* have been
installed.

The zip file uploaded to markus titled *data.zip* contains all the data
required for this program.

This file should be unziped at the same level as *main.py* using
something like 7zip's \"Extract Here\" function. This will make a new
folder tilted data appear at the same level as *main.py*. Within this
folder should immediately be 9 items. Suppose *main.py* is at the root
directory \"/main.py\". Then the directory of the mtrmap.png should be
\"/data/mtrmap.png\".

Some of the data in the provided zip file is automatically generated by
the program but has been provided in case the program takes too long.
*mtr_lines_and_stations.csv* and *mtr_lines_fares.csv* are csv files
downloaded from the MTR website. *modified_mtr_lines_and_stations.csv*,
coord_mappings.csv and *modified_mtr_lines_and_stations_APPENDED.csv*
are automatically generated by the programs if executed in the order
described by computational overview. (i.e. data_collection.py mapping.py
main.py). The rest have been manually made by me.

PLEASE NOTE: *mapping.py* takes a few minutes to complete, especially if
the user is not as familiar with the MTR system. (e.g. Kowloon station
may be confused for Kowloon Tong station)

Mapping.py's boxes should be placed something like the following image:

![Example Result of Mapping.py](mapping_ex)

If any mistake is made during mapping, press the right mouse to undo.\
\
**Main.py**\
\
When running main.py, please enter the units that are required in the
console. In addition, the *run_main* function's call in the
\"\_\_main\_\_\" block can be altered to show the click boxes of each
station.

Then a window should pop up which shows the MTR map and some other
information.

# Changes from Proposal {#changes-from-proposal .unnumbered}

As mentioned at the start, changes in the introduction were italicized
but will be reiterated here. The program now distinguishes between
routes that are using airport express and routes that are not using the
airport express. Not all fares are shown for each route, only the fare
for an adult with an octopus card (This can be changed, see main.py's
constants and *run_main* for more details).

# Discussion {#discussion .unnumbered}

After using the program that was made to check the time of some journeys
that I travel regularly, I can say that it is fairly accurate in terms
of MTR travel speed. However, once comparing it to the MTR's official
times, I see some significant disparities. But, my father, who times
some of his daily journeys has found that the MTR app does overestimate
the time taken during travel by a significant amount. It does this to
account for the fact that people traveling on the MTR will not have
instant interchanges. Unfortunately, my program does not account for
this and assumes that switching between every line (except Hong Kong to
Central) does not take any time and that the trains are already there
waiting. This is because it is hard to get raw timing information
between two MTR stations without manually timing them as MTR does not
provide this information. The method of using latitude and longitude
data to find the distance between them assumes that the rail follows the
\"as the crow flies\" path and that the MTR always travels at operating
speeds between every two stations. This is not the case in reality. The
MTR does not always travel at it's max operating speed.

Nonetheless, the travel times are fairly accurate given that they do not
account for interchange and waiting.

A significant difficulty encountered when making the app, was the
programmatic importing of the CSV MTR data into the system graph because
of the 2 special cases of Lohas park and Lok Ma Chau.

In the future, an update to this program would be to account for
interchange times and possibly using the real time train information
provided by the MTR to calculate how much waiting is needed to be done
if the journey began as soon as possible. Moreover, the graphics
displaying the path to be taken is somewhat flimsy and could have been
updated by possibly using a sort of masking method to show and hide
certain parts of a secondary image which is a highlighted version of the
MTR map. This would result in a more natural look to the UI.

# References {#references .unnumbered}

Commons.wikimedia.org. 2021. File:Hong Kong Railway Route Map blank.svg.
online Available at:\
https://commons.wikimedia.org/wiki/File:Hong_Kong_Railway_Route_Map_blank.svg
\[Accessed 14 March 2021\].

Mtr.com.hk. 2021. MTR \> Patronage Updates. online Available at:\
https://www.mtr.com.hk/en/corporate/investor/patronage.php \[Accessed 11
March 2021\].

Mtr.com.hk. 2021. MTR \> System Map. online Available at:\
http://www.mtr.com.hk/en/customer/services/system_map.html \[Accessed 13
March 2021\].

Data.gov.hk. 2021. \| DATA.GOV.HK. online Available at:\
https://data.gov.hk/en-datasets/search/MTR \[Accessed 13 March 2021\].

https://en.wikipedia.org/wiki/Dijkstra

https://www.pygame.org/docs/

https://geopy.readthedocs.io/en/stable/

Station acceleration times (Note these values varied heavily from
station to station, this is simply an average):\
Tung Chung Line - 23.5 seconds\
Tsueng Kwan O Line - 27.2 seconds\
East Rail Line - 31.1 seconds\
Kwun Tong Line - 30.2 seconds\
