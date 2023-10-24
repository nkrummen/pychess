#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:19:35 2023

@author: nathankrummen
"""

from methods import *

import warnings

# Ignore FutureWarnings for the append method
warnings.filterwarnings("ignore", category=FutureWarning)


#step 0 (optional) update pickle files saved to local
#update_pickle(pickle_location='full_monty.pickle',user='yumyams',limit='null')

#step 1 - access pickle
x = load_pickle('full_monty.pickle')

test_match = (x.moves[1], x.White[1], x.Black[1], x.createdAt[1], x.lastMoveAt[1])

print(x.moves[1])

interpret_game(test_match)






#step 2 - turn string of moves from 1 game -> sequential DF with corresponding values from game engine.