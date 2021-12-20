# Integer-Multiplier
Integer-Multiplier verification project for class

Note, the blif_parser.py should be used for the python parser of the .blif files. The blif_reader.py file is now obsolete.

The blif_parser.py file can be run as long as a proper .blif file is given as its first argument. Providing a second argument will be used to define the write file with "write.sing" as a default write value if none is provided.

Mult32.mapped.blif was created from running the following commands in abc:
"gen -N 32 -m 32X32mult.blif; sweep; read_library and-xor.genlib; map; write_blif 32X32mult.mapped.blif"

This requires the and-xor.genlib library that is included in this repository.

write.sing was created from giving Multi4.blif as an input to the blif_parser.py program.
