import os
import csv
import sys
import copy
import math
import time
import numpy
import string
import random
import shutil
import getopt
import subprocess

import random, time, pygame, sys
from pygame.locals import *

########################################
#         USAGE/ERROR MESSAGE          #
########################################

#ensure the correct number of arguments are provided:
if len(sys.argv)!=2:
    print "usage: Chess.py <database>"
    sys.exit()

########################################
#           GLOBAL VARIABLES           #
########################################

database = sys.argv[1]
square_size = 40 #size of each piece-square in pixels
display_surface = pygame.display.set_mode((square_size*8, square_size*8))

#dictionary. contains co-ordinates of various pieces (in 'Chess_database/Pieces.png') for mapping:
piece_mapper = {'B_rook':[[0,0], [40,0]],
                'B_horse':[[80,0], [120,0]],
                'B_bishop':[[160,0], [200,0]],
                'B_queen':[[240,0], [280,0]],
                'B_king':[[320,0], [360,0]],
                'B_pawn':[[400,0], [440,0]],
                'W_rook':[[40,40], [0,40]],
                'W_horse':[[120,40], [80,40]],
                'W_bishop':[[200,40], [160,40]],
                'W_queen':[[280,40], [240,40]],
                'W_king':[[360,40], [320,40]],
                'W_pawn':[[440,40], [400,40]],
                }

########################################
#             MAIN FUNCTION            #
########################################

def main():
    global display_surface, square_size, database, piece_mapper

    master_board = [['B_rook', 'B_horse', 'B_bishop', 'B_queen', 'B_king', 'B_bishop', 'B_horse', 'B_rook'],
                    ['B_pawn',  'B_pawn',   'B_pawn',  'B_pawn', 'B_pawn',   'B_pawn',  'B_pawn', 'B_pawn'],
                    ['NULL',      'NULL',     'NULL',    'NULL',   'NULL',     'NULL',    'NULL',   'NULL'],
                    ['NULL',      'NULL',     'NULL',    'NULL',   'NULL',     'NULL',    'NULL',   'NULL'],
                    ['NULL',      'NULL',     'NULL',    'NULL',   'NULL',     'NULL',    'NULL',   'NULL'],
                    ['NULL',      'NULL',     'NULL',    'NULL',   'NULL',     'NULL',    'NULL',   'NULL'],
                    ['W_pawn',  'W_pawn',   'W_pawn',  'W_pawn', 'W_pawn',   'W_pawn',  'W_pawn', 'W_pawn'],
                    ['W_rook', 'W_horse', 'W_bishop', 'W_queen', 'W_king', 'W_bishop', 'W_horse', 'W_rook']]

    turn = 'W_' #'B_'
    move_flags = {'B_king':False, 'W_king':False, 'B_rook_kingside':False, 'W_rook_kingside':False, 'B_rook_queenside':False, 'W_rook_queenside':False}
    pygame.init()
    
    #start screen:
    board_visualizer(turn, move_flags, master_board)
    pygame.display.flip()
    
    #turns start here:
    downclick_flag = False
    reset_flag = False
    position1 = []
    position2 = []
    while True:
        event = pygame.event.wait()
        
        #check if user wants to exit game:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            print "exiting 'Chess.py' application..."
            pygame.quit()
            sys.exit()
        
        #check for end-condition (WIN/LOSE):
        checkmate_event(turn, move_flags, master_board)
            
        #check for end-condition (STALEMATE):
        stalemate_event(turn, move_flags, master_board)
            
        #allow a human to perform actions:
        if turn == 'W_':
            #select piece:
            if event.type == pygame.MOUSEBUTTONDOWN and downclick_flag == False:
                position1 = pygame.mouse.get_pos()
                #print "position #1: "+str(position1)+" DC flag "+str(downclick_flag)
                board_visualizer(turn, move_flags, master_board)
                legal_moves = piece_highlighter(position1, turn, move_flags, master_board)
                if len(legal_moves) == 0:
                    reset_flag = 1
                    continue
            
            #move piece:
            if event.type == pygame.MOUSEBUTTONDOWN and downclick_flag == True:
                position2 = pygame.mouse.get_pos()
                #print "position #2: "+str(position2)+" DC flag "+str(downclick_flag)
                turn = piece_mover(position1, position2, legal_moves, turn, move_flags, master_board)
                board_visualizer(turn, move_flags, master_board)
        #allow the AI to perform a move:
        else:
            [start_position, end_position] = AI(turn, move_flags, master_board)
            #note that [start_position, end_position] have to be converted into 
            #pixel-positions before input to 'piece_mover()':
            turn = piece_mover([start_position[1]*square_size, start_position[0]*square_size], [end_position[1]*square_size, end_position[0]*square_size], [end_position], turn, move_flags, master_board)
            print str(turn)+"turn| no scoring scheme used in easy mode."
            board_visualizer(turn, move_flags, master_board)
                
        #toggle between actions:
        if event.type == pygame.MOUSEBUTTONUP:
            if reset_flag == True:
                reset_flag = False
                continue
            downclick_flag = not(downclick_flag)
            #print "mouseup"+" DC flag "+str(downclick_flag)

    return

########################################
#           OTHER FUNCTIONS            #
########################################

#define pawn_rewards. Pawns get rewarded for occupying these squares:
W_pawn_rewards = [[0.0,  0.0,  0.0,  0.0, 0.0, 0.0,  0.0,  0.0],
                  [0.4,  0.5,  0.6,  0.7, 0.7, 0.6,  0.5,  0.4],
                  [0.3,  0.4,  0.5,  0.6, 0.6, 0.5,  0.4,  0.3],
                  [0.2,  0.3,  0.4,  0.5, 0.5, 0.4,  0.3,  0.2],
                  [0.01, 0.02, 0.03, 0.4, 0.4, 0.03, 0.02, 0.01],
                  [0.0,  0.01, 0.02, 0.3, 0.3, 0.02, 0.01, 0.0],
                  [0.0,  0.0,  0.0,  0.0, 0.0, 0.0,  0.0,  0.0],
                  [0.0,  0.0,  0.0,  0.0, 0.0, 0.0,  0.5,  0.0]]

B_pawn_rewards = []
for i in range(7,-1,-1):
    B_pawn_rewards.append(W_pawn_rewards[i])

#the 'pawn_bonus' occurs when one pawn backs up another (from the bottom-side):
pawn_bonus = 0.15

#the 'castling_bonus' rewards the AI for castling:
castling_bonus = 0.5

#the worth of each piece:
piece_values = {'king': 1000, 'queen':9, 'rook':5, 'bishop':3, 'horse':3, 'pawn':1}

#this function makes a computer-calculated move:
#for now, the AI uses a Negamax search with alpha-beta pruning:
#search upto 4 moves (B/W, B/W):
def AI(turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper

    #create threat-map to determine if:
    #  -castling corridor is clear of threats
    #  -king is under attack or potentially threatened
    #  -a checkmate has occurred
    threat_map = threat_mapper(turn, move_flags, master_board)

    #make a list of pieces with at least 1 legal move:
    #also, place priority on any moves that result in a piece capture:
    legal_pieces = []
    for i in range(0,8):
        for j in range(0,8):
            if turn in master_board[i][j]:
                #if at least 1 legal move is found:
                SUBlegal_moves = king_defender([i,j], threat_map, turn, move_flags, master_board)
                if len(SUBlegal_moves) >= 1:
                    #store the pieces co-ordinates:
                    legal_pieces.append([i,j])
                    #check for attack moves:
                    for k in range(0,len(SUBlegal_moves)):
                        if 'W_' in master_board[SUBlegal_moves[k][0]][SUBlegal_moves[k][1]]:
                           return [[i,j], SUBlegal_moves[k]]

    #randomly select a piece:
    start_position = random.choice(legal_pieces)
    
    #randomly select a move for selected piece:
    end_position = random.choice(king_defender(start_position, threat_map, turn, move_flags, master_board))
    
    #return start and end position chosen:
    print "MOVE chosen by AI(): {"+master_board[start_position[0]][start_position[1]]+" at "+str(start_position)+"} to "+str(end_position)
    return [start_position, end_position]

def negamax(move_tree, depth, turn, move_flags, master_board):

    #create a threat-map for the current situation on board:
    threat_map = threat_mapper(turn, move_flags, master_board)
    #calculate current hypothetical turn. Alternate (B-W-B-W) throughout tree:
    if depth%2 == 0:
        hypo_turn = 'B_'
    else:
        hypo_turn = 'W_'
    #scan through all pieces:
    for i in range(0,8):
        for j in range(0,8):
            if hypo_turn in master_board[i][j]:
                #make a list of all legal moves for a piece:
                legal_moves = king_defender([i,j], threat_map, turn, move_flags, master_board)
                #scan through all legal moves:
                for move in range(0,len(legal_moves)):
                    #create a hypothetical master board with the move performed:
                    hypo_master_board = copy.deepcopy(master_board)
                    hypo_master_board[legal_moves[move][0]][legal_moves[move][1]] = hypo_master_board[i][j]
                    hypo_master_board[i][j] = 'NULL'
                    #check if 'negamax' has reached a leaf node:
                    if depth == 0:
                        #score position:
                        [white_score, black_score] = board_scorer(turn, move_flags, hypo_master_board)
                        
                    #perform alpha_beta_search on move, see if it is worthy of further exploration:
                    
                    
                    
    return
    
def board_scorer(turn, move_flags, master_board):
    global W_pawn_rewards, B_pawn_rewards, pawn_bonus, castling_bonus
    return [white_score, black_score]
    
#def alpha_beta_search():
#    return

#check if a checkmate has occurred:
def checkmate_event(turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper
    threat_map = threat_mapper(turn, move_flags, master_board)

    #check if the king is under attack:
    for i in range(0,8):
        for j in range(0,8):
            if turn+'king' in master_board[i][j]:
                if threat_map[i][j] != 1:
                    return
                
    #scan through all turn-pieces, see if there are any possible moves to counter check:
    counter_flag = 0
    for i in range(0,8):
        for j in range(0,8):
            if turn in master_board[i][j]:
                counter_flag += len(king_defender([i,j], threat_map, turn, move_flags, master_board))
                if counter_flag != 0:
                    return
    
    #if there are no counter-moves, a checkmate has ocurred:
    if counter_flag == 0:
        if turn == 'W_':
            END_image = pygame.image.load(database+"/LOSE_condition.png")
            display_surface.blit(END_image, (0, 0), (0,0, 319,319))
            pygame.display.flip()   
            print 'Game over. Black has won.'
            pygame.time.wait(5000)
            sys.exit()
        else:
            END_image = pygame.image.load(database+"/WIN_condition.png")
            display_surface.blit(END_image, (0, 0), (0,0, 319,319))
            pygame.display.flip()   
            print 'Game over. White has won.'
            pygame.time.wait(5000)
            sys.exit()
    return

#check if a stalemate has occurred:
def stalemate_event(turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper
    
    threat_map = threat_mapper(turn, move_flags, master_board)
    #count all possible legal moves:
    move_counter = 0
    for i in range(0,8):
        for j in range(0,8):
            if turn in master_board[i][j]:
                #check for any legal moves:
                move_counter += len(move_lister([i,j], threat_map, turn, move_flags, master_board))
    #check if no more legal moves exist:
    if move_counter == 0:
        END_image = pygame.image.load(database+"/STALEMATE_condition.png")
        display_surface.blit(END_image, (0, 0), (0,0, 319,319))
        pygame.display.flip()
        print 'Game over. Stalemate.'
        pygame.time.wait(5000)
        sys.exit()
                
    #check if WHITE has (king) and [(1 bishop) or (1 knight)] AND:
    #check if BLACK has (king) and [(1 bishop) or (1 knight)]
    #if the previous 'win_event()' function in 'main()' has not been triggered, then 2 kings still exist.
    dead_flags = {'B_pawn':0, 'W_pawn':0, 'B_horse':0, 'W_horse':0, 'B_bishop':0, 'W_bishop':0, 'B_rook':0, 'W_rook':0, 'B_queen':0, 'W_queen':0, 'B_king':0, 'W_king':0}
    for i in range(0,8):
        for j in range(0,8):
            if master_board[i][j] != 'NULL':
                dead_flags[master_board[i][j]] += 1
    #does the game meet some conditions for stalemate?
    if dead_flags['B_pawn']==0 and dead_flags['B_rook']==0 and dead_flags['B_queen']==0:
        if dead_flags['W_pawn']==0 and dead_flags['W_rook']==0 and dead_flags['W_queen']==0:
            #count number of bishop/horse pieces. They should be 0 or 1 (for each side) for a stalemate:
            if dead_flags['B_horse']+dead_flags['B_bishop'] <= 1:
                if dead_flags['W_horse']+dead_flags['W_bishop'] <= 1:
                    #all conditions are met for a stalemate:
                    END_image = pygame.image.load(database+"/STALEMATE_condition.png")
                    display_surface.blit(END_image, (0, 0), (0,0, 319,319))
                    pygame.display.flip() 
                    print 'Game over. Stalemate.'
                    pygame.time.wait(5000)
                    sys.exit()
    return

#move pieces around the board:
def piece_mover(position1, position2, legal_moves, turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper
    start_coordinates = [position1[1]/square_size, position1[0]/square_size]
    final_coordinates = [position2[1]/square_size, position2[0]/square_size]
    #loop through all legal moves to determine where to move piece:
    for i in range(0,len(legal_moves)):
        if legal_moves[i] == final_coordinates:
            #unflag all rooks moved to rule out castling:
            if 'B_rook' in master_board[start_coordinates[0]][start_coordinates[1]]:
                if start_coordinates == [0,0]:
                    move_flags['B_rook_queenside'] = True
                if start_coordinates == [0,7]:
                    move_flags['B_rook_kingside'] = True
            if 'W_rook' in master_board[start_coordinates[0]][start_coordinates[1]]:
                if start_coordinates == [7,0]:
                    move_flags['W_rook_queenside'] = True
                if start_coordinates == [7,7]:
                    move_flags['W_rook_kingside'] = True
            #unflag all kings moved to rule out castling:
            if 'B_king' in master_board[start_coordinates[0]][start_coordinates[1]] and start_coordinates == [0,4]:
                move_flags['B_king'] = True
            if 'W_king' in master_board[start_coordinates[0]][start_coordinates[1]] and start_coordinates == [7,4]:
                move_flags['W_king'] = True
            #unflag any captured virgin rooks:
            if turn == 'B_' and final_coordinates == [7,0]:
                move_flags['W_rook_queenside'] = True
            if turn == 'B_' and final_coordinates == [7,7]:
                move_flags['W_rook_kingside'] = True
            if turn == 'W_' and final_coordinates == [0,0]:
                move_flags['B_rook_queenside'] = True
            if turn == 'W_' and final_coordinates == [0,7]:
                move_flags['B_rook_kingside'] = True

            #change place of affected piece:
            master_board[final_coordinates[0]][final_coordinates[1]] = copy.deepcopy(master_board[start_coordinates[0]][start_coordinates[1]])
            #clear original location of piece:
            king_memory = master_board[start_coordinates[0]][start_coordinates[1]]
            master_board[start_coordinates[0]][start_coordinates[1]] = 'NULL'

            #check if a BLACK castling move is requested:
            if 'B_king' in king_memory:
                #BLACK, KINGSIDE:
                if start_coordinates == [0,4] and final_coordinates == [0,6]:
                    #change place of rook:
                    master_board[0][5] = 'B_rook'
                    #clear original position of rook:
                    master_board[0][7] = 'NULL'
                #BLACK, QUEENSIDE:
                if start_coordinates == [0,4] and final_coordinates == [0,2]:
                    #change place of rook:
                    master_board[0][3] = 'B_rook'
                    #clear original position of rook:
                    master_board[0][0] = 'NULL'
            #check if a castling move is requested:
            if 'W_king' in king_memory:
                #WHITE, KINGSIDE:
                if start_coordinates == [7,4] and final_coordinates == [7,6]:
                    #change place of rook:
                    master_board[7][5] = 'W_rook'
                    #clear original position of rook:
                    master_board[7][7] = 'NULL'
                #WHITE, QUEENSIDE:
                if start_coordinates == [7,4] and final_coordinates == [7,2]:
                    #change place of rook:
                    master_board[7][3] = 'W_rook'
                    #clear original position of rook:
                    master_board[7][0] = 'NULL'

            #queen any pawns:
            if 'pawn' in master_board[final_coordinates[0]][final_coordinates[1]]:
                if final_coordinates[0] == 7 or final_coordinates[0] == 0:
                    master_board[final_coordinates[0]][final_coordinates[1]] = str(turn+'queen')
            #change the turn:
            if turn == 'B_':
                turn = 'W_'
            else:
                turn = 'B_'
            return turn
    return turn

#creates a fresh board based ONLY on data from 'master_board':
def board_visualizer(turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper
    chessboard = pygame.image.load(database+"/ChessBoard.png")
    pieces_image = pygame.image.load(database+"/Pieces.png")
    display_surface.blit(chessboard, (0,0))
    
    for i in range(0,8): #scan through rows of 'master_board'
        for j in range(0,8): #scan through columns of 'master board'
            if master_board[i][j] != 'NULL':
                    sub_location = piece_mapper[master_board[i][j]][(i+j)%2]
                    display_surface.blit(pieces_image, (j*square_size, i*square_size), (sub_location[0], sub_location[1], square_size, square_size))
    pygame.display.flip()
    return

#define all legal moves for pieces:
def move_lister(piece_coordinates, threat_map, turn, move_flags, master_board):
    color = master_board[piece_coordinates[0]][piece_coordinates[1]][0:1]

    #SUB-function (called by 'move_lister' function):
    def movement(direction):
        SUBlegal_moves = []
        move_coordinates = [piece_coordinates[0]+direction[0], piece_coordinates[1]+direction[1]]
        while True:
            #check boundary conditions:
            if move_coordinates[0] > 7 or move_coordinates[0] < 0:
                break
            if move_coordinates[1] > 7 or move_coordinates[1] < 0:
                break
            #check for friendly collisions:
            if color in master_board[move_coordinates[0]][move_coordinates[1]]:
                break
            #check for enemy collisions:
            if color not in master_board[move_coordinates[0]][move_coordinates[1]] and master_board[move_coordinates[0]][move_coordinates[1]] != 'NULL':
                SUBlegal_moves.append(move_coordinates)
                break
            #append move to list:
            SUBlegal_moves.append(move_coordinates)
            #increment move:
            move_coordinates = [move_coordinates[0]+direction[0], move_coordinates[1]+direction[1]]
        return SUBlegal_moves

    def king_movement(direction):
        SUBlegal_moves = []
        move_coordinates = [piece_coordinates[0]+direction[0], piece_coordinates[1]+direction[1]]
        #check boundary conditions:
        if move_coordinates[0] > 7 or move_coordinates[0] < 0:
            return SUBlegal_moves
        if move_coordinates[1] > 7 or move_coordinates[1] < 0:
            return SUBlegal_moves
        #check for friendly collisions:
        if color in master_board[move_coordinates[0]][move_coordinates[1]]:
            return SUBlegal_moves
        #check for enemy collisions:
        if color not in master_board[move_coordinates[0]][move_coordinates[1]] and master_board[move_coordinates[0]][move_coordinates[1]] != 'NULL':
            SUBlegal_moves.append(move_coordinates)
            return SUBlegal_moves
        #append move to list:
        SUBlegal_moves.append(move_coordinates)
        return SUBlegal_moves
    
    current_piece = master_board[piece_coordinates[0]][piece_coordinates[1]]
    legal_moves = []
    
    if 'B_pawn' in current_piece:
        #check for pieces below B_pawn:
        if master_board[piece_coordinates[0]+1][piece_coordinates[1]] == 'NULL':
            legal_moves.append([piece_coordinates[0]+1, piece_coordinates[1]])
            #if black_pawn is at the starting position:
            if piece_coordinates[0] == 1:
                if master_board[piece_coordinates[0]+2][piece_coordinates[1]] == 'NULL':
                    legal_moves.append([piece_coordinates[0]+2, piece_coordinates[1]])
        #check for attack-opportunities:
        if piece_coordinates[1]+1 <= 7 and 'W_' in master_board[piece_coordinates[0]+1][piece_coordinates[1]+1]:
            legal_moves.append([piece_coordinates[0]+1, piece_coordinates[1]+1])
        if piece_coordinates[1]-1 >= 0 and 'W_' in master_board[piece_coordinates[0]+1][piece_coordinates[1]-1]:
            legal_moves.append([piece_coordinates[0]+1, piece_coordinates[1]-1])
        return legal_moves

    if 'W_pawn' in current_piece:
        #check for pieces above B_pawn:
        if master_board[piece_coordinates[0]-1][piece_coordinates[1]] == 'NULL':
            legal_moves.append([piece_coordinates[0]-1, piece_coordinates[1]])
            #if B_pawn is at the starting position:
            if piece_coordinates[0] == 6:
                if master_board[piece_coordinates[0]-2][piece_coordinates[1]] == 'NULL':
                    legal_moves.append([piece_coordinates[0]-2, piece_coordinates[1]])
        #check for attack-opportunities:
        if piece_coordinates[1]+1 <= 7 and 'B_' in master_board[piece_coordinates[0]-1][piece_coordinates[1]+1]:
            legal_moves.append([piece_coordinates[0]-1, piece_coordinates[1]+1])
        if piece_coordinates[1]-1 >= 0 and 'B_' in master_board[piece_coordinates[0]-1][piece_coordinates[1]-1]:
            legal_moves.append([piece_coordinates[0]-1, piece_coordinates[1]-1])
        return legal_moves
    
    #8 possible moves for a horse:
    if 'horse' in current_piece:
        #UP-LEFT:
        if piece_coordinates[0]-2 >= 0 and piece_coordinates[1]-1 >= 0:
            if color not in master_board[piece_coordinates[0]-2][piece_coordinates[1]-1]:
                legal_moves.append([piece_coordinates[0]-2,piece_coordinates[1]-1])
        #UP-RIGHT:
        if piece_coordinates[0]-2 >= 0 and piece_coordinates[1]+1 <= 7:
            if color not in master_board[piece_coordinates[0]-2][piece_coordinates[1]+1]:
                legal_moves.append([piece_coordinates[0]-2,piece_coordinates[1]+1])
        #DOWN-LEFT:
        if piece_coordinates[0]+2 <= 7 and piece_coordinates[1]-1 >= 0:
            if color not in master_board[piece_coordinates[0]+2][piece_coordinates[1]-1]:
                legal_moves.append([piece_coordinates[0]+2,piece_coordinates[1]-1])
        #DOWN-RIGHT:
        if piece_coordinates[0]+2 <= 7 and piece_coordinates[1]+1 <= 7:
            if color not in master_board[piece_coordinates[0]+2][piece_coordinates[1]+1]:
                legal_moves.append([piece_coordinates[0]+2,piece_coordinates[1]+1])
        #LEFT-UP:
        if piece_coordinates[0]-1 >= 0 and piece_coordinates[1]-2 >= 0:
            if color not in master_board[piece_coordinates[0]-1][piece_coordinates[1]-2]:
                legal_moves.append([piece_coordinates[0]-1,piece_coordinates[1]-2])
        #LEFT-DOWN:
        if piece_coordinates[0]+1 <= 7 and piece_coordinates[1]-2 >= 0:
            if color not in master_board[piece_coordinates[0]+1][piece_coordinates[1]-2]:
                legal_moves.append([piece_coordinates[0]+1,piece_coordinates[1]-2])
        #RIGHT-UP:
        if piece_coordinates[0]-1 >= 0 and piece_coordinates[1]+2 <= 7:
            if color not in master_board[piece_coordinates[0]-1][piece_coordinates[1]+2]:
                legal_moves.append([piece_coordinates[0]-1,piece_coordinates[1]+2])
        #RIGHT-DOWN:
        if piece_coordinates[0]+1 <= 7 and piece_coordinates[1]+2 <= 7:
            if color not in master_board[piece_coordinates[0]+1][piece_coordinates[1]+2]:
                legal_moves.append([piece_coordinates[0]+1,piece_coordinates[1]+2])
        return legal_moves

    if 'bishop' in current_piece:    
        #UP-LEFT:
        SUBlegal_moves = movement([-1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP-RIGHT:
        SUBlegal_moves = movement([-1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-LEFT:
        SUBlegal_moves = movement([1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-RIGHT:
        SUBlegal_moves = movement([1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        return legal_moves        

    if 'rook' in current_piece:
        #UP:
        SUBlegal_moves = movement([-1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN:
        SUBlegal_moves = movement([1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #LEFT:
        SUBlegal_moves = movement([0, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #RIGHT:
        SUBlegal_moves = movement([0, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        return legal_moves    

    if 'queen' in current_piece:
        #UP-LEFT:
        SUBlegal_moves = movement([-1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP-RIGHT:
        SUBlegal_moves = movement([-1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-LEFT:
        SUBlegal_moves = movement([1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-RIGHT:
        SUBlegal_moves = movement([1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP:
        SUBlegal_moves = movement([-1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN:
        SUBlegal_moves = movement([1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #LEFT:
        SUBlegal_moves = movement([0, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #RIGHT:
        SUBlegal_moves = movement([0, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        return legal_moves 

    if 'king' in current_piece:
        #UP-LEFT:
        SUBlegal_moves = king_movement([-1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP-RIGHT:
        SUBlegal_moves = king_movement([-1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-LEFT:
        SUBlegal_moves = king_movement([1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-RIGHT:
        SUBlegal_moves = king_movement([1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP:
        SUBlegal_moves = king_movement([-1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN:
        SUBlegal_moves = king_movement([1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #LEFT:
        SUBlegal_moves = king_movement([0, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #RIGHT:
        SUBlegal_moves = king_movement([0, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #CASTLING-KINGSIDE (BLACK):
        castle_flag = 0
        #check king/rook movement flags:
        if move_flags['B_king'] == False and move_flags['B_rook_kingside'] == False:
            castle_flag = castle_flag+1
        #check if path is clear of pieces and threats:
        clear_flag = True
        for i in range(5,7):
            if master_board[0][i] != 'NULL':
                clear_flag = False
        if clear_flag == True:
            castle_flag = castle_flag+1
        NOthreat_flag = True
        for i in range(4,8):
            if threat_map[0][i] != 0:
                NOthreat_flag = False
        if NOthreat_flag ==True:
            castle_flag = castle_flag+1
        #if all conditions for castling are met:
        if castle_flag == 3:
            legal_moves.append([0,6])
        #CASTLING-QUEENSIDE (BLACK):
        castle_flag = 0
        #check king/rook movement flags:
        if move_flags['B_king'] == False and move_flags['B_rook_queenside'] == False:
            castle_flag = castle_flag+1
        #check if path is clear of pieces and threats:
        clear_flag = True
        for i in range(1,4):
            if master_board[0][i] != 'NULL':
                clear_flag = False
        if clear_flag == True:
            castle_flag = castle_flag+1
        NOthreat_flag = True
        for i in range(0,5):
            if threat_map[0][i] != 0:
                NOthreat_flag = False
        if NOthreat_flag ==True:
            castle_flag = castle_flag+1
        #if all conditions for castling are met:
        if castle_flag == 3:
            legal_moves.append([0,2])
        #CASTLING-KINGSIDE (WHITE):
        castle_flag = 0
        #check king/rook movement flags:
        if move_flags['W_king'] == False and move_flags['W_rook_kingside'] == False:
            castle_flag = castle_flag+1
        #check if path is clear of pieces and threats:
        clear_flag = True
        for i in range(5,7):
            if master_board[7][i] != 'NULL':
                clear_flag = False
        if clear_flag == True:
            castle_flag = castle_flag+1
        NOthreat_flag = True
        for i in range(4,8):
            if threat_map[7][i] != 0:
                NOthreat_flag = False
        if NOthreat_flag ==True:
            castle_flag = castle_flag+1
        #if all conditions for castling are met:
        if castle_flag == 3:
            legal_moves.append([7,6])
        #CASTLING-QUEENSIDE (WHITE):
        castle_flag = 0
        #check king/rook movement flags:
        if move_flags['W_king'] == False and move_flags['W_rook_queenside'] == False:
            castle_flag = castle_flag+1
        #check if path is clear of pieces and threats:
        clear_flag = True
        for i in range(1,4):
            if master_board[7][i] != 'NULL':
                clear_flag = False
        if clear_flag == True:
            castle_flag = castle_flag+1
        NOthreat_flag = True
        for i in range(0,5):
            if threat_map[7][i] != 0:
                NOthreat_flag = False
        if NOthreat_flag ==True:
            castle_flag = castle_flag+1
        #if all conditions for castling are met:
        if castle_flag == 3:
            legal_moves.append([7,2])
        
        #make sure that the king isn't walking into a threat:
        safe_moves = []
        for i in range(0,len(legal_moves)):
            if threat_map[legal_moves[i][0]][legal_moves[i][1]] == 0:
                safe_moves.append(legal_moves[i])
        legal_moves = copy.deepcopy(safe_moves)
        return legal_moves
    
    return

#define all threatening moves for pieces:
def threat_lister(piece_coordinates, turn, move_flags, master_board):
    color = master_board[piece_coordinates[0]][piece_coordinates[1]][0:1]

    #SUB-functions (called by 'threat_lister' function):
    def movement(direction):
        SUBlegal_moves = []
        move_coordinates = [piece_coordinates[0]+direction[0], piece_coordinates[1]+direction[1]]
        while True:
            #check boundary conditions:
            if move_coordinates[0] > 7 or move_coordinates[0] < 0:
                break
            if move_coordinates[1] > 7 or move_coordinates[1] < 0:
                break
            #check for friendly collisions:
            if color in master_board[move_coordinates[0]][move_coordinates[1]]:
                SUBlegal_moves.append(move_coordinates)
                break
            #check for enemy collisions:
            if color not in master_board[move_coordinates[0]][move_coordinates[1]] and master_board[move_coordinates[0]][move_coordinates[1]] != 'NULL':
                SUBlegal_moves.append(move_coordinates)
                break
            #append move to list:
            SUBlegal_moves.append(move_coordinates)
            #increment move:
            move_coordinates = [move_coordinates[0]+direction[0], move_coordinates[1]+direction[1]]
        return SUBlegal_moves

    def king_movement(direction):
        SUBlegal_moves = []
        move_coordinates = [piece_coordinates[0]+direction[0], piece_coordinates[1]+direction[1]]
        #check boundary conditions:
        if move_coordinates[0] > 7 or move_coordinates[0] < 0:
            return SUBlegal_moves
        if move_coordinates[1] > 7 or move_coordinates[1] < 0:
            return SUBlegal_moves
        #check for friendly collisions:
        if color in master_board[move_coordinates[0]][move_coordinates[1]]:
            SUBlegal_moves.append(move_coordinates)
            return SUBlegal_moves
        #check for enemy collisions:
        if color not in master_board[move_coordinates[0]][move_coordinates[1]] and master_board[move_coordinates[0]][move_coordinates[1]] != 'NULL':
            SUBlegal_moves.append(move_coordinates)
            return SUBlegal_moves
        #append move to list:
        SUBlegal_moves.append(move_coordinates)
        return SUBlegal_moves
    
    current_piece = master_board[piece_coordinates[0]][piece_coordinates[1]]
    legal_moves = []
    
    if 'B_pawn' in current_piece:
        legal_moves = []
        if piece_coordinates[1] <= 6:
            legal_moves.append([piece_coordinates[0]+1,piece_coordinates[1]+1])
        if piece_coordinates[1] >= 1:
            legal_moves.append([piece_coordinates[0]+1,piece_coordinates[1]-1])
        return legal_moves

    if 'W_pawn' in current_piece:
        if piece_coordinates[1] <= 6:
            legal_moves.append([piece_coordinates[0]-1,piece_coordinates[1]+1])
        if piece_coordinates[1] >= 1:
            legal_moves.append([piece_coordinates[0]-1,piece_coordinates[1]-1])
        return legal_moves
    
    #8 possible moves for a horse:
    if 'horse' in current_piece:
        #UP-LEFT:
        if piece_coordinates[0]-2 >= 0 and piece_coordinates[1]-1 >= 0:
            legal_moves.append([piece_coordinates[0]-2,piece_coordinates[1]-1])
        #UP-RIGHT:
        if piece_coordinates[0]-2 >= 0 and piece_coordinates[1]+1 <= 7:
            legal_moves.append([piece_coordinates[0]-2,piece_coordinates[1]+1])
        #DOWN-LEFT:
        if piece_coordinates[0]+2 <= 7 and piece_coordinates[1]-1 >= 0:
            legal_moves.append([piece_coordinates[0]+2,piece_coordinates[1]-1])
        #DOWN-RIGHT:
        if piece_coordinates[0]+2 <= 7 and piece_coordinates[1]+1 <= 7:
            legal_moves.append([piece_coordinates[0]+2,piece_coordinates[1]+1])
        #LEFT-UP:
        if piece_coordinates[0]-1 >= 0 and piece_coordinates[1]-2 >= 0:
            legal_moves.append([piece_coordinates[0]-1,piece_coordinates[1]-2])
        #LEFT-DOWN:
        if piece_coordinates[0]+1 <= 7 and piece_coordinates[1]-2 >= 0:
            legal_moves.append([piece_coordinates[0]+1,piece_coordinates[1]-2])
        #RIGHT-UP:
        if piece_coordinates[0]-1 >= 0 and piece_coordinates[1]+2 <= 7:
            legal_moves.append([piece_coordinates[0]-1,piece_coordinates[1]+2])
        #RIGHT-DOWN:
        if piece_coordinates[0]+1 <= 7 and piece_coordinates[1]+2 <= 7:
            legal_moves.append([piece_coordinates[0]+1,piece_coordinates[1]+2])
        return legal_moves

    if 'bishop' in current_piece:    
        #UP-LEFT:
        SUBlegal_moves = movement([-1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP-RIGHT:
        SUBlegal_moves = movement([-1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-LEFT:
        SUBlegal_moves = movement([1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-RIGHT:
        SUBlegal_moves = movement([1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        return legal_moves        

    if 'rook' in current_piece:
        #UP:
        SUBlegal_moves = movement([-1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN:
        SUBlegal_moves = movement([1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #LEFT:
        SUBlegal_moves = movement([0, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #RIGHT:
        SUBlegal_moves = movement([0, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        return legal_moves    

    if 'queen' in current_piece:
        #UP-LEFT:
        SUBlegal_moves = movement([-1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP-RIGHT:
        SUBlegal_moves = movement([-1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-LEFT:
        SUBlegal_moves = movement([1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-RIGHT:
        SUBlegal_moves = movement([1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP:
        SUBlegal_moves = movement([-1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN:
        SUBlegal_moves = movement([1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #LEFT:
        SUBlegal_moves = movement([0, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #RIGHT:
        SUBlegal_moves = movement([0, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        return legal_moves 

    if 'king' in current_piece:
        #UP-LEFT:
        SUBlegal_moves = king_movement([-1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP-RIGHT:
        SUBlegal_moves = king_movement([-1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-LEFT:
        SUBlegal_moves = king_movement([1, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN-RIGHT:
        SUBlegal_moves = king_movement([1, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #UP:
        SUBlegal_moves = king_movement([-1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #DOWN:
        SUBlegal_moves = king_movement([1, 0])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #LEFT:
        SUBlegal_moves = king_movement([0, -1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        #RIGHT:
        SUBlegal_moves = king_movement([0, 1])
        for i in range(0,len(SUBlegal_moves)):
            legal_moves.append(SUBlegal_moves[i])
        return legal_moves
    
    return


#highlights a clicked piece and shows all legal moves:
#three highlighting modes exits:
#  -highlight the selected piece (green)
#  -highlight all legal moves (yellow)
def piece_highlighter(position, turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper

    #create threat-map to determine if:
    #  -castling corridor is clear of threats
    #  -king is under attack or potentially threatened
    #  -a checkmate has occurred
    threat_map = threat_mapper(turn, move_flags, master_board)
    #print numpy.matrix(threat_map)

    #calculate location of click, and piece selected:
    piece_coordinates = [position[1]/square_size, position[0]/square_size]
    current_piece = master_board[piece_coordinates[0]][piece_coordinates[1]]
    if current_piece == 'NULL' or turn not in current_piece:
        legal_moves = []
        return legal_moves
    
    #highlight the board-square which is selected: 
    highlights_image = pygame.image.load(database+"/Highlights.png")
    display_surface.blit(highlights_image, (piece_coordinates[1]*square_size, piece_coordinates[0]*square_size), (40,0, square_size, square_size))
    pygame.display.flip()

    #calculate legal moves that do not result in a king-attack:
    legal_moves = king_defender(piece_coordinates, threat_map, turn, move_flags, master_board)

    #display all legal moves on GUI:
    for i in range(0,len(legal_moves)):
        display_surface.blit(highlights_image, (legal_moves[i][1]*square_size, legal_moves[i][0]*square_size), (0,0, square_size, square_size))
        
    pygame.display.flip()
    return legal_moves

#calculate all moves (for a selected piece) that defend the king during a check:
def king_defender(piece_coordinates, threat_map, turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper
    
    current_piece = master_board[piece_coordinates[0]][piece_coordinates[1]]
    #calculate all normally legal moves for selected piece:
    legal_moves = move_lister(piece_coordinates, threat_map, turn, move_flags, master_board)
    blocking_moves = []
    #check if any of the moves can block the king-attack:
    for i in range(0,len(legal_moves)):
        #make the move on a hypothetical 'master_board':
        hypo_master_board = copy.deepcopy(master_board)
        hypo_master_board[legal_moves[i][0]][legal_moves[i][1]] = copy.deepcopy(hypo_master_board[piece_coordinates[0]][piece_coordinates[1]])
        hypo_master_board[piece_coordinates[0]][piece_coordinates[1]] = 'NULL'
        #make a hypothetical threat_map, check if the threat persists:
        hypo_threat_map = threat_mapper(turn, move_flags, hypo_master_board)
        check_flag = False
        for j in range(0,8):
            for k in range(0,8):
                if turn+'king' in hypo_master_board[j][k] and hypo_threat_map[j][k]==1:
                    check_flag = True
        #if the threat to king no longer persists on blocking:
        if check_flag == False:
            #append the current move to all 'blocking_moves':
            blocking_moves.append(legal_moves[i])

    #return all 'blocking_moves' with potential to defend the king:
    return blocking_moves

#create threat-map of opposing pieces:
def threat_mapper(turn, move_flags, master_board):
    global display_surface, square_size, database, piece_mapper
    
    threat_map = []
    [threat_map.append([0,0,0,0,0,0,0,0]) for i in range(0,8)]
    for i in range(0,8):
        for j in range(0,8):
            if master_board[i][j] != 'NULL' and turn not in master_board[i][j]:
                legal_moves = threat_lister([i,j], turn, move_flags, master_board)
                #add legal moves to threat matrix:
                for k in range(0,len(legal_moves)):
                    threat_map[legal_moves[k][0]][legal_moves[k][1]] = 1
    return threat_map

#execute main function:
if __name__ == '__main__':
    main()
















