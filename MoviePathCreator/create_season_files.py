import os
import sys

base_output_path = "C:\\Temp\\media-test\\series\\Game of Thrones (2011)\\Season 01"

base_output_path = sys.argv[1]
season_num = int(sys.argv[2])
num_epps = int(sys.argv[3])

for x in range(1, num_epps + 1):

    file_name = "s%02de%02d.mkv" % (season_num, x)

    file_name = os.path.join(base_output_path, file_name)
    f = open(file_name, "w+")
    f.write("This is a test")
    f.close()

