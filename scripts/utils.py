# -*-coding:Utf-8 -*
import re
from obspy import UTCDateTime
import plotly.graph_objs as graph


#
# Log files utilities
#

# Split logs in several lines
def split_log_lines(content):
    splitted = []
    if "\r\n" in content:
        splitted = content.split("\r\n")
    elif "\r" in content:
        splitted = content.split("\r")
    elif "\n" in content:
        splitted = content.split("\n")
    if splitted[-1] == "":
        splitted = splitted[:-1]
    return splitted


# Search timestamps for a specific keyword
def find_timestamped_values(regexp, content):
    timestamped_values = list()
    lines = split_log_lines(content)
    for line in lines:
        value_catch = re.findall(regexp, line)
        timestamp_catch = re.findall("(\d+):", line)
        if len(value_catch) > 0:
            v = value_catch[0]
            d = UTCDateTime(int(timestamp_catch[0]))
            timestamped_values.append([v, d])
    return timestamped_values


# Format log files
def format_log(log):
    datetime_log = ""
    lines = split_log_lines(log)
    for line in lines:
        catch = re.findall("(\d+):", line)
        if len(catch) > 0:
            timestamp = catch[0]
            isodate = UTCDateTime(int(timestamp)).isoformat()
            datetime_log += line.replace(timestamp, isodate) + "\r\n"
    formatted_log = "".join(datetime_log)
    return formatted_log


#
# Plot utilities
#

# Plot vertical lines with plotly
def plotly_vertical_shape(position, ymin=0, ymax=1, name='name', color='blue'):
    xval = list()
    yval = list()
    for ps in position:
        xval.append(ps)
        xval.append(ps)
        xval.append(None)
        yval.append(ymin)
        yval.append(ymax)
        yval.append(None)

    lines = graph.Scatter(x=xval,
                          y=yval,
                          name=name,
                          line=dict(color=color,
                                    width=1.5),
                          hoverinfo='x',
                          mode='lines'
                          )
    return lines


# Get an array of date objects
def get_date_array(date, length, period):
    date_list = list()
    i = 0
    while i < length:
        date_list.append(date + i * period)
        i += 1
    return date_list


# Get an array of time values
def get_time_array(length, period):
    # Compute time
    time_list = list()
    i = 0.0
    while i < length:
        time_list.append(i * period)
        i += 1.
    return time_list


# Convert raw data amplitude to pascal
def counts2pascal(data):
    factor = 0.178 / 1000. * 10. ** (23. / 20.) * 2. ** 24. / 5. * 2. ** 4.
    return data / factor

