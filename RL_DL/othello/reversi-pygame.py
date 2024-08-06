import pygame, sys
pygame.init()

import numpy as np

# global variables
WIDTH, HEIGHT = 560, 560
MESSAGE_MARGIN = 40
yellow = (255, 227, 56)
green = (0, 128, 0)
white = (255, 255, 255)
black = (0, 0, 0)
boardcolor = [white, black]
playercolor = [ None, yellow, green ] # border color of selected cells
font = pygame.font.SysFont("comicsans",24)

# create window
screen = pygame.display.set_mode((WIDTH, HEIGHT+MESSAGE_MARGIN))
pygame.display.set_caption("REVERSI")

# chess piece
# 1: rook
# 2: knight
# 3: bishop
# 4: king
# 5: queen
# 6: pawn

# player
# 1: yellow player 1 (or human player), who moves first
# 2: green player 2 (or AI)

# board color (checker pattern)
bgcolor = np.array([
    [  0,  1,  0,  1,  0,  1,  0,  1 ],
    [  1,  0,  1,  0,  1,  0,  1,  0 ],
    [  0,  1,  0,  1,  0,  1,  0,  1 ],
    [  1,  0,  1,  0,  1,  0,  1,  0 ],
    [  0,  1,  0,  1,  0,  1,  0,  1 ],
    [  1,  0,  1,  0,  1,  0,  1,  0 ],
    [  0,  1,  0,  1,  0,  1,  0,  1 ],
    [  1,  0,  1,  0,  1,  0,  1,  0 ]
], dtype=np.int16)

# game state
state = np.array([
    [  0,  0,  0,  0,  0,  0,  0,  0 ],
    [  0,  0,  0,  0,  0,  0,  0,  0 ],
    [  0,  0,  0,  0,  0,  0,  0,  0 ],
    [  0,  0,  0,  1,  2,  0,  0,  0 ],
    [  0,  0,  0,  2,  1,  0,  0,  0 ],
    [  0,  0,  0,  0,  0,  0,  0,  0 ],
    [  0,  0,  0,  0,  0,  0,  0,  0 ],
    [  0,  0,  0,  0,  0,  0,  0,  0 ]
], dtype=np.int16)

# player turn (1 or 2)
current_player = 1

# selected cell
selected_cell = None

# create a surface object, image is drawn on it.
CELL_WIDTH, CELL_HEIGHT = WIDTH/8, HEIGHT/8


def _message_margin(txt, backgr, textcol):
    rect = pygame.Rect( (0, HEIGHT), (WIDTH, MESSAGE_MARGIN) )
    pygame.draw.rect(screen, backgr, rect)
    pos_text = font.render(txt, True, textcol)
    pos_rect = pos_text.get_rect()
    pos_rect.center = ( WIDTH/2, HEIGHT + MESSAGE_MARGIN/2 )
    screen.blit(pos_text, pos_rect)

# show the message (turn, win, tie) on the bottom of screen
def show_msg():
    if is_gameover:
        if tie:
            txt = "Tie!"
        else:
            if winner == 1: # turn of yellow
                txt = "Yellow Wins!"
            else:
                txt = "Green Wins!"

    else:
        if current_player == 1: # turn of yellow
            txt = "Yellow's Turn"
        else:
            txt = "Green's Turn"
    _message_margin(txt, black, white)

def draw_board(surf, state):
    for i in range(8): # index of row
        for j in range(8): # index of col
            # locate a rect at i-th row and j-th col
            rect = pygame.Rect(
                (j * CELL_WIDTH, i * CELL_HEIGHT), (CELL_WIDTH, CELL_HEIGHT))
            pygame.draw.rect(surf, boardcolor[bgcolor[i, j]], rect)

    for i in range(8): # index of row
        for j in range(8): # index of col
            if state[i, j] == 0:
                continue

            center = (j * CELL_WIDTH + CELL_WIDTH/2, i * CELL_HEIGHT + CELL_HEIGHT/2)
            pygame.draw.circle(surf, playercolor[state[i, j]], center, WIDTH/16, width=0)

def cell_coord(pos):
    # get row and col & return
    # note that y -> row number, x -> col number
    return (int(pos[1] / CELL_HEIGHT), int(pos[0] / CELL_WIDTH))

# return all possible actions that player can takes
def possible_moves(player):
    ret = list()
    opponent = 3 - player
    print("player:", player, "opponent:", opponent)
    for i in range(8):
        for j in range(8):
            # if occupied, skip
            if state[i, j] > 0:
                continue

            # if there is any adjacent cell occupied by oppenent
            # (u, v) is the relative position of eight adjacent cells
            # and also the direction to examine if any opponent piece
            # flipped over
            # (u, v) is
            # (-1, -1) ( -1,  0) (-1,  1)
            # ( 0, -1) (  0,  0) ( 0,  1)
            # ( 1, -1) (  1,  0) ( 1,  1)
            # e.g.,                  
            #          (i-1, j+1) -> opponent
            #    (i, j) -> player
            # -> examine diagonal direction of up and right
            #    (i-1,j+1), (i-2,j+2), (i-3,j+3), ...
            for u in [-1, 0, 1]:
                for v in [-1, 0, 1]:
                    if (u != 0 or v != 0) and \
                        (i+u>=0 and i+u<8) and \
                            (j+v>=0 and j+v<8) and \
                                state[i+u,j+v] == opponent:
                        
                        # examine if there is a player's piece
                        # and thus the opponent's pieces between
                        # (i,j) and (i+d*u,j+d*v) can be
                        # flipped over
                        for d in range(1,8):
                            if (i+d*u<0 or i+d*u>=8) or \
                                (j+d*v<0 or j+d*v>=8):
                                break

                            if state[i+d*u,j+d*v] == player:
                                ret.append((i, j))
                            elif state[i+d*u,j+d*v] == opponent:
                                continue
                            else:
                                break
    ret = list(dict.fromkeys(ret))
    print(ret)
    return ret

# flip pieces between the new piece placed and the piece with the same color
# vertically, horizontally and diagonally
def flip_piece(player, pos, state=state):

    # assume that the cell of pos is empty
    state[pos] = player

    n_flipped = 0

    # find target vertical toward top
    for i in range (-1, -8, -1):
        # out of board
        if pos[0] + i < 0:
            break

        # if empty, stop proving
        if state[pos[0] + i, pos[1]] == 0:
            break

        # found
        if state[pos[0] + i, pos[1]] == player:
            for j in range (-1, i, -1):
                state[pos[0] + j, pos[1]] = player
                n_flipped += 1
            break

    # find target vertical toward bottom
    for i in range (1, 8):
        # out of board
        if pos[0] + i >= 8:
            break

        # if empty, stop proving
        if state[pos[0] + i, pos[1]] == 0:
            break

        # found
        if state[pos[0] + i, pos[1]] == player:
            for j in range (1, i):
                state[pos[0] + j, pos[1]] = player
                n_flipped += 1
            break

    # find target horizon toward left
    for i in range (-1, -8, -1):
        # out of board
        if pos[1] + i < 0:
            break

        # if empty, stop proving
        if state[pos[0], pos[1] + i] == 0:
            break

        # found
        if state[pos[0], pos[1] + i] == player:
            for j in range (-1, i, -1):
                state[pos[0], pos[1] + j] = player
                n_flipped += 1
            break
 
     # find target horizon toward right
    for i in range (1, 8):
        # out of board
        if pos[1] + i >= 8:
            break

        # if empty, stop proving
        if state[pos[0], pos[1] + i] == 0:
            break

        # found
        if state[pos[0], pos[1] + i] == player:
            for j in range (1, i):
                state[pos[0], pos[1] + j] = player
                n_flipped += 1
            break

    # find target diagonal toward top & left 
    for i in range (-1, -8, -1):
        # out of board
        if pos[0] + i < 0 or pos[1] + i < 0:
            break

        # if empty, stop proving
        if state[pos[0] + i, pos[1] + i] == 0:
            break

        # found
        if state[pos[0] + i, pos[1] + i] == player:
            for j in range (-1, i, -1):
                state[pos[0] + j, pos[1] + j] = player
                n_flipped += 1
            break

    # find target diagonal toward bottom & right 
    for i in range (1, 8):
        # out of board
        if pos[0] + i >= 8 or pos[1] + i >= 8:
            break

        # if empty, stop proving
        if state[pos[0] + i, pos[1] + i] == 0:
            break

        # found
        if state[pos[0] + i, pos[1] + i] == player:
            for j in range (1, i):
                state[pos[0] + j, pos[1] + j] = player
                n_flipped += 1
            break

    # find target diagonal toward top & right 
    for i in range (-1, -8, -1):
        # out of board
        if pos[0] + i < 0 or pos[1] - i >= 8:
            break

        # if empty, stop proving
        if state[pos[0] + i, pos[1] - i] == 0:
            break

        # found
        if state[pos[0] + i, pos[1] - i] == player:
            for j in range (-1, i, -1):
                state[pos[0] + j, pos[1] - j] = player
                n_flipped += 1
            break

    # find target diagonal toward bottom & right 
    for i in range (1, 8):
        # out of board
        if pos[0] + i >= 8 or pos[1] - i < 0:
            break

        # if empty, stop proving
        if state[pos[0] + i, pos[1] - i] == 0:
            break

        # found
        if state[pos[0] + i, pos[1] - i] == player:
            for j in range (1, i):
                state[pos[0] + j, pos[1] - j] = player
                n_flipped += 1
            break

    return n_flipped

# examine if the board is full
def game_over():
    return all([ False if state[i, j] == 0 else True for i in range(8) for j in range(8) ])

# return true if player wins
def win(player):
    global tie
    opponent = 3 - player
    ptr1 = np.sum([1 if state[i, j] == player else 0 for i in range(8) for j in range(8) ])
    ptr2 = np.sum([1 if state[i, j] == opponent else 0 for i in range(8) for j in range(8) ])
    if ptr1 == ptr2:
        tie = True
    return True if ptr1 > ptr2 else False

is_gameover = False
winner = 0
tie = False
running = True

while running:
    pygame.time.delay(200)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not is_gameover:
            # calculate the clicked piece
            idx = cell_coord(pygame.mouse.get_pos())

            # clicked out of board such as message box
            if (idx[0] <  0 or idx[0] >= 8) or (idx[1] < 0 or idx[1] >= 8):
                break

            if idx in possible_moves(current_player):
                n_flipped = flip_piece(current_player, idx)

                # examine if the game is over
                if game_over():
                    is_gameover = True
                    winner = 1 if win(1) else 2
                    break

                # switch player for the next turn
                current_player = 1 if current_player == 2 else 2

                # if no possible moves for the current player
                if len(possible_moves(current_player)) == 0:
                    current_player = 1 if current_player == 2 else 2
                    
                    # if no possible moves again
                    if len(possible_moves(current_player)) == 0:
                        is_gameover = True
                        winner = 1 if win(1) else 2
                        break
                


    draw_board(screen, state)
    show_msg()
    pygame.display.update()


pygame.quit()
sys.exit()