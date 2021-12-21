import sys
import os
import time

# ts stores the time in seconds
ts1 = time.time()

os.system("Singular " + sys.argv[1])

ts2 = time.time()

print("Ran singular file in: " + str(ts2 - ts1) + " seconds")
