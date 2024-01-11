"""
Main Game Script

This script initializes and runs the game, controlling the game's main loop.

Author: MONEEB ABDALBADIE NASRALLAH ALI KARRAR
Date: 18/12/2023

"""
import sys
import pygame
from gameFunctions import *


def main():
    """
    Main Game Script

    This script initializes and runs the game, controlling the game's main loop.

    Author: MONEEB ABDALBADIE NASRALLAH ALI KARRAR
    Date: 18/12/2023

    """
    window, arena, backGroundMusic, clickSound, \
        gameOverSound, winSound, background, \
        backRec, winnerImg, winnerRec = initialize_game()

    actors, missionaries, cannibals, boat_actor = create_actors(arena)
    gamegraph = create_gamegraph()
    passengers_dict = passengers(missionaries, cannibals, boat_actor)
    passengers_combination_dict = passengersCombination()

    game_loop(window, arena, actors, gamegraph, passengers_dict,
              passengers_combination_dict, clickSound,
              gameOverSound, winSound, background, backRec, winnerImg,
              winnerRec)


if __name__ == "__main__":
    main()
