# hotsparser
A Python library for parsing Heroes of the Storm replay files and storing basic information. I intend to add more functionality in the future, but this is not being actively kept up to date with the latest Heroes of the Storm builds.

## Requirements
Aside from *mpq* and *heroprotocol* (included in this repository, up to date as of October 24, 2016), this library requires Python 2.7 and [pandas](http://pandas.pydata.org/).

## Usage
Simply run the example parse_replays.py, which will attempt to parse all of the replay files in the /replays folder. The result is placed into a pandas DataFrame and written to disk.
