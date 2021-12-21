# Integer-Multiplier
Integer-Multiplier verification project for class

Note, the blif_parser.py should be used for the python parser of the .blif files.

The blif_parser.py file can be run as long as a proper .blif file is given as its first argument and a proper singular file to append is provided as its second argument. Providing a third argument will be used to define the write file with "write.sing" as a default write value if none is provided.

4X4mult.mapped.blif was created from running the following commands in ABC:
"gen -N 4 -m 4X4mult.blif; sweep; read_library and-xor.genlib; map; write_blif 4X4mult.mapped.blif"

This requires the and-xor.genlib library that is included in this repository. This is the general scheme that would be used for creating a multiplier .blif file as expected for the blif_parser.py file to be able to run it properly. The number after the -N argument is the number of bits for each input and this can be adjusted to make multipliers of varying widths.

The blif_parser.py was then run on this generated file as follows:

python3 blif_parser.py 4X4mult.mapped.blif GB-Rew.sing 4X4mult.sing

This was perfomed on the CADE machines to ensure it could be run by future students or faculty members.

Once this Singular file is generated the timing analysis can be run by using the timing.py file provided here as well. This timing.py file simply prints out the time it takes to run a Singular file that is provided as its argument, as follows:

python3 timing.py 4X4mult.sing

Note, that for this to run properly the Singular file should quit by itself. If the Singular file does not use the "quit;" at the end of the file a manual termination of Singular running needs to be used and this adds delay to the timing and human variability to it as well.

No other software needs to be run by the user to verify any results found from this report.

The GB-Rew.sing file was created to implement the work found in a paper found at this link: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7459464&tag=1.
This file tries to recreate the explained algorithm to create a GB and then reduce that GB prior to applying a membership test of the spec polynomial in the created GB.

Future work can be done in the GB-Rew.sing file to increase efficiency and also to fix any bugs that remain.
