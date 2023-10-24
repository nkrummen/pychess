# -*- coding: utf-8 -*-
"""
Spyder Editor

"""

import lichess.api

import re

import stockfish as sf

import pickle

import pandas as pd

import chess

import chess.engine

from datetime import datetime

##~~~~~

from lichess.format import JSON, SINGLE_PGN

user = lichess.api.user('yumyams')

#~~~~~~~

def update_pickle(pickle_location,user,limit):
    #hit API, grab all the games (in JSON, hopefully), convert to df, clean it up, save to pickle.
    
    #[1] check if limited, otherwise grab it all.
    if limit == 'null':
        pgn_x = lichess.api.user_games(user,format=JSON)
    else:
        pgn_x = lichess.api.user_games(user,max=limit,format=JSON)
    
    #[2] drop JSON into df.
    main_df_0 = pd.DataFrame(pgn_x)
    
    #DF at this stage is cols below. ~! cleaning actions 
        #{id(str)
        #rated(bool)
        #speed()
        #perf()
        #createdAt(int) ~! need to interpret int
        #lastMoveat(int) ~! need to interpret int
        #status
        #players(nested Dic) ~! need to unpack
        #winner()
        #clock()
    
    #[3]take the nested dict column out
    ripped_column = (main_df_0.players)
    
    #[4]temp lists we'll fill up as we parse the nested dict
    white = []
    black = []
    white_rating = []
    black_rating = []

    #[5] iter through column & snipe values into lists
    for row in ripped_column:
        white.append(row['white']['user']['id'])
        black.append(row['black']['user']['id'])
        white_rating.append(row['white']['rating'])
        black_rating.append(row['black']['rating'])

    #[6] rebuid lists into dict (theres certainly a smarter way to do this, but w/e. Small big-O here..)
    data = {
        'White': white,
        'Black': black,
        'white_rating': white_rating,
        'black_rating': black_rating
        }

    #[7] convert dict to pd
    unpacked_player_df = pd.DataFrame(data)
    
    #[8] concat pd back to OG pd
    main_df_1 = pd.concat([main_df_0,unpacked_player_df],axis=1)
    
    #[9] drop old nested dict column
    main_df_2 = main_df_1.drop('players',axis=1)
    
    #[10] convert times into readable datetime
    main_df_2['createdAt'] = pd.to_datetime(main_df_2['createdAt'],unit='ms')
    main_df_2['lastMoveAt'] = pd.to_datetime(main_df_2['lastMoveAt'],unit='ms')
   
    #[11] Gucci. Push to pickle.
    with open(pickle_location, 'wb') as file:
        pickle.dump(main_df_2, file)
        
    print("~~API data pulled, cleaned, & pickled")
    #print("heres a preview...")
    #print(main_df_2)
    

##~~~~~~
##~~~~~~
##~~~~~~

def load_pickle(pickle_file):
    #I actually hate PGNs. Lets make it tabular.
    with open(pickle_file, 'rb') as file:
        pgn_x = pickle.load(file)
    return pgn_x

##~~~~~~
##~~~~~~
##~~~~~~


#stockfish_path = r'/Users/nathankrummen/anaconda3/lib/python3.10/site-packages/stockfish'
stockfish_path = r'/opt/homebrew/Cellar/stockfish/16/bin/stockfish'

def interpret_game(single_set):
    play_string = single_set[0]
    
    if (single_set[1] == 'yumyams'):
        Nate = 'white'
    else:
        Nate = 'black'
    
    #This is the blank DF we'll fill in with the data from the list of moves.
    columns = ['play','absolute_score','nate_relative_score','est_play_speed']
    inner_gameplay_df = pd.DataFrame(columns=columns)
    
    list_of_moves = play_string.split()
    #total_tempo = (single_set[4] - single_set[3]).total_seconds() / len(list_of_moves)
    
    game_length = (single_set[4] - single_set[3]).total_seconds()
    est_tempo = game_length / len(list_of_moves)
    
    
    board = chess.Board()
    
    with chess.engine.SimpleEngine.popen_uci(stockfish_path, debug=True) as engine:
        for move in list_of_moves:
            board.push_san(move)
            engine_config= chess.engine.Limit(time=0.5) #, nodes=10000, depth=20
            analysis = engine.analyse(board, engine_config)

            ##This is the logic to absolut-ize the score, & from the Yum-Yams/Nate perspective.
            pov_score_string = str(analysis['score'])
            #print(pov_score_string)
            match = re.match(r"PovScore\(Cp\(([+-]?\d+)\), ([A-Z]+)\)", pov_score_string)
            #print(match)
            numeric_value = int(match.group(1))
            #print(numeric_value)
            side = match.group(2)
            #print(side)
            
            #if POV is white's, then score is True.
            if(side == 'WHITE'):
                absolute_score = numeric_value
            else:
                absolute_score = numeric_value*(-1)
            
            #Check Nate's POV, adjust.
            if(Nate == 'white'):
                nate_pov = absolute_score
            else:
                nate_pov = absolute_score*(-1)
            
            #concat(inner_gameplay_df,[move,absolute_score,nate_pov,est_tempo],ignore_index=True,axis=0,join='outer')
            inner_gameplay_df = inner_gameplay_df.append([move, absolute_score, nate_pov, est_tempo], ignore_index=True)
            
            #inner_gameplay_df = pd.concat([inner_gameplay_df, pd.Series([move, absolute_score, nate_pov, est_tempo])], ignore_index=True, axis=0, join='outer')
    return print(inner_gameplay_df)


def uci_to_san(uci_move):
    board = chess.Board()
    move = chess.Move.from_uci(uci_move)
    san_move = board.san(move)
    return san_move


"""


# Initialize the chess board
board = chess.Board()

# Create a UCI protocol engine
engine = chess.engine.SimpleEngine.popen_uci("path/to/stockfish")

for move_str in moves:
    # Convert move string to a move object
    move = chess.Move.from_uci(move_str)

    # Make the move on the board
    board.push(move)

    # Calculate the best move and evaluation from the engine
    result = engine.play(board, chess.engine.Limit(time=0.1))
    
    # Print the move, evaluation, and the updated board
    print(f"Move: {move.uci()}, Eval: {result.info['score']}, Board:")
    print(board)

# Print the final board position
print("Final Board:")
print(board)

# Close the engine when done
engine.quit()


"""


