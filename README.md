# Integer-Multiplier
Integer-Multiplier verification project for class

Note, the blif_parser.py should be used for the python parser of the .blif files. The blif_reader.py file is now obsolete.

The blif_parser.py file can be run as long as a proper .blif file is given as its first argument. Providing a second argument will be used to define the write file with "write.sing" as a default write value if none is provided.

Multi4.blif was created from running the following commands in abc:
"gen -N 4 -m mult_tmp.blif; read_blif mult_tmp.blif; sweep; write_blif multi4.blif;"

write.sing was created from giving Multi4.blif as an input to the blif_parser.py program.
