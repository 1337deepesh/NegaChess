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
    print "usage: NegaChess.py <NegaChess_database>"
    print "    "
    print "                NegaChess: A Pygame Chess Engine/GUI.            "
    print "    Copyright (C) 2015 Deepesh Nagarajan (1337deepesh@gmail.com)"
    print "    "
    print "    This program is free software: you can redistribute it and/or modify"
    print "    it under the terms of the GNU General Public License as published by"
    print "    the Free Software Foundation, version 3 of the License."
    print "    "   
    print "    This program is distributed in the hope that it will be useful, but "
    print "    WITHOUT ANY WARRANTY; without even the implied warranty of"
    print "    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."
    print "    See the GNU General Public License <http://www.gnu.org/licenses/>"
    print "    for more details."
    print "    "
    sys.exit()

########################################
#             MAIN FUNCTION            #
########################################

def main():
    
    square_size = 40
    display_surface = pygame.display.set_mode((square_size*8, square_size*8))
    database = sys.argv[1]
    pygame.init()
    
    #start screen:
    MainScreen = pygame.image.load(database+"/MainScreen.png")
    option_highlights = pygame.image.load(database+"/MainScreen_highlights.png")
    display_surface.blit(MainScreen, (0,0))
    pygame.display.flip()
    [C1, C2] = [47,272]
    
    while True:
        event = pygame.event.wait()

        #check if user wants to exit game:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            print "exiting 'Chess_main.py' application..."
            pygame.quit()
            sys.exit()

        [Column, Row] = pygame.mouse.get_pos()
        
        if Column >= 47 and Column <= 272:
        #check if the user wants to play another human:
            if Row >= 47 and Row <= 112:
                [R1, R2] = [47, 112]
                option_highlights = pygame.image.load(database+"/MainScreen_highlights.png")
                display_surface.blit(option_highlights, (C1,R1), (C1,R1,C2-C1+1,R2-R1+1))
                pygame.display.flip()
                if event.type == pygame.MOUSEBUTTONDOWN:  
                    subprocess.call(["python", database+"/Chess_human.py", database])
                    pygame.init()
                    display_surface.blit(MainScreen, (0,0))
                    pygame.display.flip()
            #check if the user wants to play 0.5 move-depth AI (easy):
            elif Row >=127 and Row <= 192:
                [R1, R2] = [127, 192]
                option_highlights = pygame.image.load(database+"/MainScreen_highlights.png")
                display_surface.blit(option_highlights, (C1,R1), (C1,R1,C2-C1+1,R2-R1+1))
                pygame.display.flip()
                if event.type == pygame.MOUSEBUTTONDOWN:  
                    subprocess.call(["python", database+"/Chess_AI_easy.py", database])
                    pygame.init()
                    display_surface.blit(MainScreen, (0,0))
                    pygame.display.flip()
            #check if the user wants to play 0.5 move-depth AI (hard):
            elif Row >=207 and Row <= 272:
                [R1, R2] = [207, 272]
                option_highlights = pygame.image.load(database+"/MainScreen_highlights.png")
                display_surface.blit(option_highlights, (C1,R1), (C1,R1,C2-C1+1,R2-R1+1))
                pygame.display.flip()
                if event.type == pygame.MOUSEBUTTONDOWN:  
                    subprocess.call(["python", database+"/Chess_AI_hard.py", database])
                    pygame.init()
                    display_surface.blit(MainScreen, (0,0))
                    pygame.display.flip()

            else:
                display_surface.blit(MainScreen, (0,0))
                pygame.display.flip()
        else:
            display_surface.blit(MainScreen, (0,0))
            pygame.display.flip()
    
    return

if __name__ == '__main__':
    main()



