The .blif files were created using commands like the following in abc:
gen -N 32 -m 32X32mult.blif; sweep; read_library and-xor.genlib; map; write_blif 32X32mult.mapped.blif

The .sing files were created by running the blif_parser.py on the mapped.blif file and writing to a corresponding .sing file with similar name.
