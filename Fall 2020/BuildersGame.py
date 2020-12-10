#Author: Zach Gee
#Date: 11/19/2020
#Description: Create a class called BuildersGame that initiates a 5-square by 5-square boardgame where two players take turns moving around the board and building towers. The first player to be on top of a 3-story tower or to have their opponent have no more valid moves wins.

class BuildersGame:
    """Creates game object that initiates blank 5x5 board, has get_current_state getter method, method to print the board, method for initial placement of builders for each player, and method to move and build and determine if player is a winner."""

    def __init__(self):
        """Initiates game with current state of 'UNFINISHED', starts at x's turn, and keeps track of builder locations and board tower levels."""

        self._current_state = 'UNFINISHED'
        self._turn = 'x'
        self._made_initial_placement = []
        self._builder_locations = {
            'x' : [],
            'o' : []
        }
        self._board = []
        for i in range(5):
            self._board.append([])
            for j in range(5):
                self._board[i].append([0,''])

    def get_current_state(self):
        """Returns _current_state"""

        return self._current_state

    def print_board(self):
        """Prints board for testing purposes"""

        for row in self._board:
            print(row)

    def initial_placement(self, build_1_row, build_1_col, build_2_row, build_2_col, player):
        """Places player's initial builder placements. Can only be used once and before any other moves."""

        if (0 <= build_1_row <= 4 and 0 <= build_1_col <= 4 and 0 <= build_2_row <= 4 and 0 <= build_2_col <= 4 and
                self._turn == player and
                player not in self._made_initial_placement and
                self._board[build_1_row][build_1_col][1] == '' and
                self._board[build_2_row][build_2_col][1] == '' and
                not (build_1_row == build_2_row and build_1_col == build_2_col) and
                player in ['x','o']):
            self._board[build_1_row][build_1_col][1] = player
            self._builder_locations[player].append([build_1_row,build_1_col])
            self._board[build_2_row][build_2_col][1] = player
            self._builder_locations[player].append([build_2_row, build_2_col])
            self._made_initial_placement.append(player)

            # Make it next player's turn
            if self._turn == 'x':
                self._turn = 'o'
            elif self._turn == 'o':
                self._turn = 'x'

            return True

        return False

    def make_move(self, to_move_row, to_move_col, move_to_row, move_to_col, build_row, build_col):
        """If input valid, moves player's builder and builds designated adjacent tower by 1 level. Checks if player has won game."""

        if (0 <= to_move_row <= 4 and 0 <= to_move_col <= 4 and 0 <= move_to_row <= 4 and 0 <= move_to_col <= 4 and 0 <= build_row <= 4 and 0 <= build_col <= 4 and
                self._current_state == 'UNFINISHED' and
                len(self._made_initial_placement) == 2 and
                self._board[to_move_row][to_move_col][1] == self._turn and
                (self._board[move_to_row][move_to_col][0] <= self._board[to_move_row][to_move_col][0] + 1) and
                self._board[build_row][build_col][0] <= 3 and
                self._board[move_to_row][move_to_col][1] == '' and
                (self._board[build_row][build_col][1] == '' or [build_row,build_col] == [to_move_row,to_move_col]) and
                abs(move_to_row - to_move_row) <= 1 and abs(move_to_col - to_move_col) <= 1 and
                abs(build_row - move_to_row) <= 1 and abs(build_col - move_to_col) <= 1 and
                [to_move_row,to_move_col] != [move_to_row,move_to_col]):
            #Save builder new location and remove old location
            self._board[move_to_row][move_to_col][1] = self._turn
            self._board[to_move_row][to_move_col][1] = ''
            self._builder_locations[self._turn].append([move_to_row,move_to_col])
            self._builder_locations[self._turn].remove([to_move_row,to_move_col])

            #Build tower level
            self._board[build_row][build_col][0] += 1

            #Check if move resulted in a win
            next_turn = ''
            if self._turn == 'x':
                next_turn = 'o'
            elif self._turn == 'o':
                next_turn = 'x'

            all_inaccessible = True
            for builder in self._builder_locations[next_turn]:
                for i in range(builder[0]-1,builder[0]+2):
                    for j in range(builder[1]-1,builder[1]+2):
                        if 0 <= i <= 4 and 0 <= j <= 4 and [i,j] != [builder[0],builder[1]]:
                            if self._board[i][j][1] == '' and self._board[i][j][0] <= self._board[builder[0]][builder[1]][0] + 1:
                                for k in range(i-1,i+2):
                                    for l in range(j-1,j+2):
                                        if 0 <= k <= 4 and 0 <= l <= 4 and [k,l] != [i,j]:
                                            if (self._board[k][l][1] == '' or [k,l] == [builder[0],builder[1]]) and self._board[k][l][0] <= 3:
                                                all_inaccessible = False

            if self._board[move_to_row][move_to_col][0] == 3 or all_inaccessible == True:
                self._current_state = self._turn.upper() + '_WON'

            #Make it next player's turn
            if self._turn == 'x':
                self._turn = 'o'
            elif self._turn == 'o':
                self._turn = 'x'

            return True

        return False

