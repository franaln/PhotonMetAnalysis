g++ -g -Wall fix_jets_v18.cxx $(root-config --libs --cflags) -lTreePlayer -o fix_jets_v18

g++ -g -Wall create_efake_mini.cxx $(root-config --libs --cflags) -lTreePlayer -o create_efake_mini
g++ -g -Wall create_jfake_mini.cxx $(root-config --libs --cflags) -lTreePlayer -o create_jfake_mini
