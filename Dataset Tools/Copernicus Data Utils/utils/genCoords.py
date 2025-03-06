"""
Script to generate coords with 50KM gaps between two specified coords
"""

from utils.calcCoords import getCoords
import curses

START_LATITUDE = 3.837160765147294
START_LONGITUDE = 101.02924793136883

END_LATITUDE = 2.4879317744244784
END_LONGITUDE = 102.77607410324383

current_lat = START_LATITUDE
current_long = START_LONGITUDE

output_file = open("../CoordsList.txt", 'a')
output_file.write(f"{START_LONGITUDE},{START_LATITUDE}\n")

i, j = 0, 0
stdscr = curses.initscr()
stdscr.addstr("")
stdscr.refresh()

while current_lat > END_LATITUDE :
    i += 1
    while current_long < END_LONGITUDE :
        j += 1

        # Displaying count with editable output
        stdscr.clear()
        stdscr.addstr(f"{i} -> {j}")
        stdscr.refresh()


        next_set, _ = getCoords(current_long, current_lat)
        next_long = next_set[2][0]
        output_file.write(f"{next_long},{current_lat}\n")

        current_long = next_long

    current_long = START_LONGITUDE
    next_set, _ = getCoords(current_long, current_lat)
    current_lat = next_set[0][1]

print("\nDone generating coords list")
curses.endwin()