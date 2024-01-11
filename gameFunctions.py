"""
Game Functions Module

This module contains functions necessary for the implementation of the
game logic,
including initialization, the game loop, and various game-related actions.

Author: MONEEB ABDALBADIE NASRALLAH ALI KARRAR
Date: 18/12/2023

"""
import sys
import pygame
FONT_SIZE_LARGE = 48
FONT_SIZE_SMALL = 15
LINE_HEIGHT = 25
MOVES_FONT_SIZE = 24
BOAT_MAX_CAPACITY = 2
MOUSE_BUTTON_LEFT = 1
WAIT_FAILURE = 3000
WAIT_SUCCESS = 2000
WAIT_GAME_EXPLANATION = 7000
BOAT_MOVE_STEP = 70
WAIT_QUIT = 1000
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 650
BOAT_START_X = 480
BOAT_START_Y = 250
LINE_SPACING_FACTOR = 10


def initialize_game():
    """
    Initialize the game by setting up the Pygame window,
    loading sounds and images,
    and returning the necessary game objects.

    Parameters:
    None

    Returns:
    window: Pygame window object
    arena: Pygame Rect object representing the game arena
    backGroundMusic: Pygame Sound object for background music
    clickSound: Pygame Sound object for click sound
    gameOverSound: Pygame Sound object for game over sound
    winSound: Pygame Sound object for win sound
    background: Pygame Surface object for the game background
    backRec: Rect object for the background
    winnerImg: Pygame Surface object for the winner image
    winnerRec: Rect object for the winner image
    """
    pygame.init()
    pygame.mixer.init()
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    arena = window.get_rect()
    backGroundMusic = pygame.mixer.Sound("GameBackGroundSound.mp3")
    clickSound = pygame.mixer.Sound("clickSound.wav")
    gameOverSound = pygame.mixer.Sound("gameOver.wav")
    winSound = pygame.mixer.Sound("winSound.wav")
    backGroundMusic.set_volume(.1)
    clickSound.set_volume(1)
    gameOverSound.set_volume(.7)
    backGroundMusic.play(-1)
    background = pygame.image.load("backGround.jpg")
    backRec = background.get_rect()
    winnerImg = pygame.image.load("winner.jpg")
    winnerRec = winnerImg.get_rect()
    return window, arena, backGroundMusic, clickSound, \
        gameOverSound, winSound, background, backRec, winnerImg, winnerRec


def create_actors(arena):
    """
    Create actor objects, including missionaries, cannibals, and the boat.

    Parameters:
    arena: Pygame Rect object representing the game arena

    Returns:
    actors: List of actor dictionaries
    missionaries: List of missionary dictionaries
    cannibals: List of cannibal dictionaries
    boat_actor: Dictionary representing the boat actor
    """
    actors_per_line = 3
    line_spacing = arena.height / LINE_SPACING_FACTOR
    boat_right_side = False
    cannibal1 = {"file": "cannibal.png"}
    cannibal2 = {"file": "cannibal.png"}
    cannibal3 = {"file": "cannibal.png"}
    missionary1 = {"file": "missionary.png"}
    missionary2 = {"file": "missionary.png"}
    missionary3 = {"file": "missionary.png"}
    boat = {"file": "boat.png"}
    missionaries = [missionary1, missionary2, missionary3]
    cannibals = [cannibal1, cannibal2, cannibal3]
    boat_actor = boat
    actors = [cannibal1, cannibal2, cannibal3, missionary1, missionary2,
              missionary3, boat]
    for i, actor in enumerate(actors):
        if actor["file"] == "boat.png":
            actor["surf"] = pygame.image.load(actor["file"])
            actor["rect"] = actor["surf"].get_rect()
            actor["rect"].midleft = (
                BOAT_START_X, arena.center[1] + BOAT_START_Y
                )
            actor["on_boat"] = False
            actor["right_side"] = boat_right_side
        else:
            actor["surf"] = pygame.image.load(actor["file"])
            actor["rect"] = actor["surf"].get_rect()
            line = i // actors_per_line
            index_in_line = i % actors_per_line
            actor["rect"].midleft = (
                30*i,
                (line * line_spacing) + (index_in_line + 5) * line_spacing)
            actor["on_boat"] = False
            actor["original_position"] = actor["rect"].topleft
            actor["right_side"] = boat_right_side
    return actors, missionaries, cannibals, boat_actor


def game_loop(window, arena, actors, gamegraph, passengers,
              passengersCombination, clickSound,
              gameOverSound, winSound, background, backRec, winnerImg,
              winnerRec):
    """
    Main game loop controlling the game's flow and actions.

    Parameters:
    window: Pygame window object
    arena: Pygame Rect object representing the game arena
    actors: List of actor dictionaries
    gamegraph: Dictionary representing the game graph for possible states
    passengers: Dictionary representing possible passenger configurations
    passengersCombination: Dictionary representing valid combinations
    of passengers
    backGroundMusic: Pygame Sound object for background music
    clickSound: Pygame Sound object for click sound
    gameOverSound: Pygame Sound object for game over sound
    winSound: Pygame Sound object for win sound
    background: Pygame Surface object for the game background
    backRec: Rect object for the background
    winnerImg: Pygame Surface object for the winner image
    winnerRec: Rect object for the winner image

    Returns:
    None
    """
    movement_count = 0
    ferry_step = -5
    action = "listen"
    gamestate = (3, 3, 1)
    fpsClock = pygame.time.Clock()
    welcomeScreen(window, arena)
    gameExplanationScreen(window, arena)
    clicked_actors = []
    while True:
        events = pygame.event.get()
        if action == "listen":
            boat_objects_count = sum(
                actor["on_boat"]
                for actor in actors
                if actor["file"] != "boat.png")
            clicked_actors, on_boat = get_mouse_click(
                actors, events, arena,
                BOAT_START_Y, clicked_actors, clickSound
                            )
            if clicked_actors and on_boat is not None:
                travelers = [actor["file"] for actor in clicked_actors]
                for key, value in passengers.items():
                    clicked_actors_tuple = tuple(
                        (actor["file"], actor.get("original_position"))
                        for actor in clicked_actors)
                    if set(clicked_actors_tuple) == set(
                        (actor["file"], actor.get("original_position"))
                        for actor in value
                            ):
                        for key2, values2 in passengersCombination.items():
                            if (key == key2):
                                if values2 in gamegraph[gamestate]:
                                    gamestate = gamegraph[gamestate][values2]
                                    ferry_who = clicked_actors
                                    if on_boat and "boat.png" in travelers:
                                        if boat_objects_count > 0:
                                            ferry_step = -ferry_step
                                            action = "ferry"
                                            movement_count += 1
        if action == "ferry":
            done = ferry(actors, ferry_step)
            if done:
                if gamegraph[gamestate] == "failure":
                    action = "failure"
                elif gamegraph[gamestate] == "success":
                    action = "success"
                else:
                    action = "listen"

        if action == "failure":
            failure(window, arena, gameOverSound)
            sys.exit()

        if action == "success":
            success(window, winnerImg, winnerRec, winSound)
            sys.exit()

        window.blit(background, backRec)
        display_movement_count(window, movement_count)
        for actor in actors:
            window.blit(actor["surf"], actor["rect"])

        pygame.display.flip()
        fpsClock.tick(120)


def failure(window, arena, gameOverSound):
    """
    Display failure message and handle failure state.

    Parameters:
    window: Pygame window object
    arena: Pygame Rect object representing the game arena
    gameOverSound: Pygame Sound object for game over sound

    Returns:
    None
    """
    gameOverSound.play()
    myfont = pygame.font.Font('freesansbold.ttf', FONT_SIZE_LARGE)
    msg = myfont.render("OOOOOOOOOH NOOOOOOOOO!!!!!!!!!", True, (255, 0, 0))
    msg_box = msg.get_rect()
    msg_box.center = arena.center
    window.blit(msg, msg_box)
    pygame.display.flip()
    pygame.time.wait(WAIT_FAILURE)


def success(window, winnerImg, winnerRec, winSound):
    """
    Display success message and handle success state.

    Parameters:
    window: Pygame window object
    winnerImg: Pygame Surface object for the winner image
    winnerRec: Rect object for the winner image
    winSound: Pygame Sound object for win sound

    Returns:
    None
    """
    winSound.play()
    window.blit(winnerImg, winnerRec)
    pygame.display.flip()
    pygame.time.wait(WAIT_SUCCESS)


def welcomeScreen(window, arena):
    """
    Display the welcome screen message.

    Parameters:
    window: Pygame window object
    arena: Pygame Rect object representing the game arena

    Returns:
    None
    """
    myfont = pygame.font.Font('freesansbold.ttf', FONT_SIZE_LARGE)
    msg = myfont.render("Welcome to our game : ", True, (255, 0, 0))
    msg_box = msg.get_rect()
    msg_box.center = (arena.center[0], arena.center[1] - 50)
    window.blit(msg, msg_box)
    pygame.display.flip()
    pygame.time.wait(WAIT_QUIT)


def gameExplanationScreen(window, arena):
    """
    Display the game explanation screen with rules and objectives.

    Parameters:
    window: Pygame window object
    arena: Pygame Rect object representing the game arena

    Returns:
    None
    """
    myfont = pygame.font.Font('freesansbold.ttf', FONT_SIZE_SMALL)
    explanationLine = ["Game roles To Win: ",
                       "1.Three missionaries and three cannibals are on one side of a river that they wish to cross.",
                       "2.A boat is available that can hold at most two people and at leaskt one.",
                       "3.You must never leave a group of missionaries outnumbered by cannibals on the same bank."]

    for i, line in enumerate(explanationLine):
        msg = myfont.render(line, True, (0, 255, 0))
        msg_box = msg.get_rect()
        msg_box.center = (arena.center[0], arena.center[1] + i * LINE_HEIGHT)
        window.blit(msg, msg_box)
    pygame.display.flip()
    pygame.time.wait(WAIT_GAME_EXPLANATION)


def display_movement_count(window, movement_count):
    """
    Display the current movement count on the screen.

    Parameters:
    window: Pygame window object
    movement_count: Current movement count

    Returns:
    None
    """
    myfont = pygame.font.Font('freesansbold.ttf', MOVES_FONT_SIZE)
    text = myfont.render(f"Moves: {movement_count}", True, (0, 0, 0))
    window.blit(text, (10, 10))


def create_gamegraph():
    """
    Create the game graph representing possible states and transitions.

    Parameters:
    None

    Returns:
    gamegraph: Dictionary representing the game graph
    """
    gamegraph = {
                (3, 3, 1): {"m": (2, 3, 0), "c": (3, 2, 0), "2m": (1, 3, 0),
                            "2c": (3, 1, 0), "mc": (2, 2, 0)},
                (3, 2, 0): {"c": (3, 3, 1)},
                (3, 1, 0): {"c": (3, 2, 1), "2c": (3, 3, 1)},
                (2, 2, 0): {"m": (3, 2, 1), "c": (2, 3, 1), "mc": (3, 3, 1)},
                (3, 2, 1): {"m": (2, 2, 0), "c": (3, 1, 0),
                            "2m": (1, 2, 0), "2c": (3, 0, 0), "mc": (2, 1, 0)},
                (3, 0, 0): {"c": (3, 1, 1), "2c": (3, 2, 1)},
                (3, 1, 1): {"m": (2, 1, 0), "c": (3, 0, 0),
                            "2m": (1, 1, 0), "mc": (2, 0, 0)},
                (2, 2, 1): {"m": (1, 2, 0), "c": (2, 2, 0),
                            "2m": (0, 2, 0), "2c": (2, 0, 0), "mc": (1, 1, 0)},
                (1, 1, 0): {"m": (2, 1, 1), "c": (1, 2, 1),
                            "2m": (3, 1, 0), "2c": (1, 3, 0), "mc": (2, 2, 1)},
                (1, 1, 1): {"m": (0, 1, 0), "c": (1, 0, 0), "mc": (0, 0, 0)},
                (0, 3, 1): {"c": (0, 2, 0), "2c": (0, 1, 0)},
                (0, 2, 0): {"m": (1, 2, 1), "c": (0, 3, 1),
                            "2m": (2, 2, 1), "mc": (1, 3, 1)},
                (0, 1, 0): {"m": (1, 1, 1), "c": (0, 2, 1),
                            "2m": (2, 1, 1), "2c": (0, 3, 1), "mc": (1, 2, 1)},
                (0, 2, 1): {"c": (0, 1, 0), "2c": (0, 0, 0)},
                (2, 3, 0): "failure",
                (2, 3, 1): "failure",
                (1, 3, 0): "failure",
                (1, 3, 1): "failure",
                (1, 2, 0): "failure",
                (1, 2, 1): "failure",
                (2, 1, 0): "failure",
                (2, 1, 1): "failure",
                (1, 0, 0): "failure",
                (2, 0, 0): "failure",
                (2, 0, 1): "failure",
                (0, 0, 0): "success"}
    return gamegraph


def passengers(missionaries, cannibals, boat):
    """
    Define possible passenger configurations.

    Parameters:
    missionaries: List of missionary dictionaries
    cannibals: List of cannibal dictionaries
    boat: Dictionary representing the boat actor

    Returns:
    passengers: Dictionary representing possible passenger configurations
    """
    passengers = {
        "m1": [missionaries[0], boat],
        "m2": [missionaries[1], boat],
        "m3": [missionaries[2], boat],
        "c1": [cannibals[0], boat],
        "c2": [cannibals[1], boat],
        "c3": [cannibals[2], boat],
        "m1m2": [missionaries[0], missionaries[1], boat],
        "m1m3": [missionaries[0], missionaries[2], boat],
        "m2m3": [missionaries[1], missionaries[2], boat],
        "c1c2": [cannibals[0], cannibals[1], boat],
        "c1c3": [cannibals[0], cannibals[2], boat],
        "c2c3": [cannibals[1], cannibals[2], boat],
        "m1c1": [missionaries[0], cannibals[0], boat],
        "m1c2": [missionaries[0], cannibals[1], boat],
        "m1c3": [missionaries[0], cannibals[2], boat],
        "m2c1": [missionaries[1], cannibals[0], boat],
        "m2c2": [missionaries[1], cannibals[1], boat],
        "m2c3": [missionaries[1], cannibals[2], boat],
        "m3c1": [missionaries[2], cannibals[0], boat],
        "m3c2": [missionaries[2], cannibals[1], boat],
        "m3c3": [missionaries[2], cannibals[2], boat],
    }
    return passengers


def passengersCombination():
    """
    Define valid combinations of passengers.

    Parameters:
    None

    Returns:
    passengersCombination: Dictionary representing
    valid combinations of passengers
    """
    passengersCombination = {
        "m1": "m",
        "m2": "m",
        "m3": "m",
        "c1": "c",
        "c2": "c",
        "c3": "c",
        "m1m2": "2m",
        "m1m3": "2m",
        "m2m3": "2m",
        "c1c2": "2c",
        "c1c3": "2c",
        "c2c3": "2c",
        "m1c1": "mc",
        "m1c2": "mc",
        "m1c3": "mc",
        "m2c1": "mc",
        "m2c2": "mc",
        "m2c3": "mc",
        "m3c1": "mc",
        "m3c2": "mc",
        "m3c3": "mc"
    }
    return passengersCombination


def get_mouse_click(actors, events, arena,
                    boat_y_offset, clicked_actors, clickSound):
    """
    Handle mouse click events and update clicked actors.

    Parameters:
    actors: List of actor dictionaries
    events: List of Pygame events
    arena: Pygame Rect object representing the game arena
    boat_y_offset: Vertical offset for the boat position
    clicked_actors: List of currently clicked actors
    clickSound: Pygame Sound object for click sound

    Returns:
    clicked_actors: Updated list of clicked actors
    on_boat: Boolean indicating if an actor is on the boat
    """
    boat_objects_count = sum(
        actor["on_boat"]
        for actor in actors
        if actor["file"] != "boat.png")
    for event in events:
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and \
                event.button == MOUSE_BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            for actor in actors:
                if actor["rect"].collidepoint(mouse_pos):
                    clickSound.play()
                    if actor["file"] == "boat.png":
                        if actor not in clicked_actors:
                            clicked_actors.append(actor)
                        return clicked_actors, any(
                            actor["on_boat"]
                            for actor in actors
                            if actor["file"] != "boat.png")
                    elif not actor["on_boat"] and \
                            actor["file"] != "boat.png" and \
                            boat_objects_count < BOAT_MAX_CAPACITY:
                        for clicked_actor in clicked_actors:
                            if clicked_actor["file"] == "boat.png":
                                clicked_actors.remove(clicked_actor)
                        offset = sum(
                            actor["on_boat"]
                            for actor in actors
                            if actor["file"] != "boat.png"
                            and actor["on_boat"]) * BOAT_MOVE_STEP
                        if actor["rect"].midleft[0] > arena.centerx:
                            if actors[6]["right_side"]:
                                actor["on_boat"] = True
                                actor["rect"].midleft = (
                                    980+offset,
                                    arena.center[1] + boat_y_offset - 50)
                                if actor not in clicked_actors:
                                    clicked_actors.append(actor)
                            else:
                                continue
                        else:
                            if not actors[6]["right_side"]:
                                actor["on_boat"] = True
                                actor["rect"].midleft = (
                                    500+offset,
                                    arena.center[1] + boat_y_offset - 50)
                                if actor not in clicked_actors:
                                    clicked_actors.append(actor)
                            else:
                                continue
                        return clicked_actors, True
                    elif actor["on_boat"]:
                        actor["on_boat"] = False
                        if actor["rect"].midleft[0] > arena.centerx:
                            mirrored_x = (
                                actor["rect"].midleft[0] + actor["rect"].width)
                            actor["rect"].topleft = (
                                mirrored_x+50, actor["original_position"][1])
                            if actor in clicked_actors:
                                clicked_actors.remove(actor)

                        else:
                            actor["rect"].topleft = actor["original_position"]
                            if actor in clicked_actors:
                                clicked_actors.remove(actor)
                        for clicked_actor in clicked_actors:
                            if clicked_actor["file"] == "boat.png":
                                clicked_actors.remove(clicked_actor)
                        return clicked_actors, False
    return clicked_actors, None


def ferry(actors, step):
    """
    Perform the ferry action, moving the boat and actors.

    Parameters:
    actors: List of actor dictionaries
    step: Horizontal step for the boat movement

    Returns:
    done: Boolean indicating if the ferry action is completed
    """
    done = False
    for actor in actors:
        if actor["on_boat"] or actor["file"] == "boat.png":
            actor["rect"] = actor["rect"].move((step, 0))
            if actor["file"] == "boat.png" and not (
                            480 < actor["rect"].midleft[0] < 970):
                actor["rect"] = actor["rect"].move((-step, 0))
                actor["surf"] = pygame.transform.flip(
                                        actor["surf"], True, False)
                actor["right_side"] = not actor["right_side"]
                done = True
    return done
