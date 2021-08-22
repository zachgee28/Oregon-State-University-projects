# Author: Zach Gee
# Date: 3/4/2021
# Description: Program simulates a slightly simplified version of the game Janggi.
#               See rules at https://en.wikipedia.org/wiki/Janggi

class JanggiGame:
    """
    Holds the general data and methods of the game. Keeps track of the game board, the Piece objects that are still
    active (not captured), the game's state (unfinished or won), and whose turn it is. The class is responsible for
    determining if a player is in check or checkmated, moving the Pieces, and displaying the game board. It must
    interact with all of the classes inherited from Piece, as the Piece objects are what occupy the game board
    """

    def __init__(self):
        """
        Creates an instance of a Janggi game. Sets up the game board with all the pieces at their starting locations.
        Begins game on Blue's turn.
        """

        self._turn = 'blue'
        self._active_pieces = {'blue': [], 'red': []}
        self._game_state = 'UNFINISHED'
        self._board = [['' for j in range(10)] for i in range(9)]

        # add pieces to the board
        self.add_piece('red', Chariot, 'a1')
        self.add_piece('red', Elephant, 'b1')
        self.add_piece('red', Horse, 'c1')
        self.add_piece('red', Guard, 'd1')
        self.add_piece('red', Guard, 'f1')
        self.add_piece('red', Elephant, 'g1')
        self.add_piece('red', Horse, 'h1')
        self.add_piece('red', Chariot, 'i1')
        self.add_piece('red', General, 'e2')
        self.add_piece('red', Cannon, 'b3')
        self.add_piece('red', Cannon, 'h3')
        self.add_piece('red', Soldier, 'a4')
        self.add_piece('red', Soldier, 'c4')
        self.add_piece('red', Soldier, 'e4')
        self.add_piece('red', Soldier, 'g4')
        self.add_piece('red', Soldier, 'i4')
        self.add_piece('blue', Chariot, 'a10')
        self.add_piece('blue', Elephant, 'b10')
        self.add_piece('blue', Horse, 'c10')
        self.add_piece('blue', Guard, 'd10')
        self.add_piece('blue', Guard, 'f10')
        self.add_piece('blue', Elephant, 'g10')
        self.add_piece('blue', Horse, 'h10')
        self.add_piece('blue', Chariot, 'i10')
        self.add_piece('blue', General, 'e9')
        self.add_piece('blue', Cannon, 'b8')
        self.add_piece('blue', Cannon, 'h8')
        self.add_piece('blue', Soldier, 'a7')
        self.add_piece('blue', Soldier, 'c7')
        self.add_piece('blue', Soldier, 'e7')
        self.add_piece('blue', Soldier, 'g7')
        self.add_piece('blue', Soldier, 'i7')

    def add_piece(self, color, piece_type, location):
        """
        Adds a piece to the board and _active_pieces
        :param color: 'red' or 'blue' as the player
        :param piece_type: what kind of Piece object (ie. Chariot)
        :param location: where to place piece on board in algebraic notation (ie. 'd4')
        :return: none
        """

        coordinates = self.translate_to_grid(location)
        piece_to_add = piece_type(color, coordinates)
        self._board[coordinates[0]][coordinates[1]] = piece_to_add
        self._active_pieces[color].append(piece_to_add)
        return

    def get_game_state(self):
        """
        Returns the state of the game ('UNFINISHED', 'RED_WON', or 'BLUE_WON')
        """

        return self._game_state

    def is_in_check(self, color):
        """
        Determines if a player is in check.
        :param color: Takes in either 'red' or 'blue' as the player
        :return: True if the player is in check, False if they are not
        """

        for piece in self._active_pieces[color]:
            if type(piece) == General:
                return piece.get_in_check()

    def make_move(self, move_from, move_to):
        """
        Attempts to make a move for a player's piece. Must interact with the piece to determine if the move is valid.
        :param move_from: coordinates of piece's starting location
        :param move_to: coordinates of piece's ending location
        :return: True if the move succeeded, False if the move cannot be done.
        """

        from_coordinates = self.translate_to_grid(move_from)
        to_coordinates = self.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]
        value_at_from = self._board[from_col][from_row]
        value_at_to = self._board[to_col][to_row]

        # if player passes the same square value for both move_from and move_to, then they are passing their turn
        # which they however cannot do if they are in check
        if not self.is_in_check(self._turn) and move_from == move_to:
            if self._turn == 'red':
                self._turn = 'blue'
            else:
                self._turn = 'red'
            return True

        # if game isn't over yet and move_from location holds a piece
        if (self.get_game_state() == 'UNFINISHED' and issubclass(type(value_at_from), Piece) and
                # and that piece belongs to the player whose turn it is
                self._turn == value_at_from.get_color() and
                # and the movement pattern is valid for that piece
                value_at_from.validate_move(move_from, move_to, self._board)):
            # if there's a piece belonging to the player whose turn it is at move_to (attempting to capture own piece)
            if issubclass(type(value_at_to), Piece) and self._turn == value_at_to.get_color():
                return False
            else:
                # Make the move
                # if move_to holds an opposing piece, it gets captured
                if issubclass(type(value_at_to), Piece):
                    self.remove_piece(value_at_to)
                value_at_from.set_location(move_to)
                self._board[to_col][to_row] = value_at_from
                self._board[from_col][from_row] = ''
                # whether the player was already in check or this move placed them in check, they cannot now be in check
                if type(self.is_a_player_in_check(self._turn)) is General and self.is_a_player_in_check(self._turn).get_color() == self._turn:
                    # Revert the move and return False since the player did not bring themself out of check
                    self._board[from_col][from_row] = value_at_from
                    self._board[to_col][to_row] = value_at_to
                    value_at_from.set_location(move_from)
                    if issubclass(type(value_at_to), Piece):
                        self._active_pieces[value_at_to.get_color()].append(value_at_to)
                    return False
                # the player either already wasn't or now isn't in check, so set its General to not in check
                self.get_general(self._turn).set_in_check(False)
                # if opposing general was put in check, set its in_check status to True and see if checkmate
                if type(self.is_a_player_in_check(self._turn)) is General:
                    self.is_a_player_in_check(self._turn).set_in_check(True)
                    if self.checkmate(self.is_a_player_in_check(self._turn)):
                        if self._turn == 'red':
                            self._game_state = 'RED_WON'
                        else:
                            self._game_state = 'BLUE_WON'
                # turn complete, change to other player's turn
                if self._turn == 'red':
                    self._turn = 'blue'
                else:
                    self._turn = 'red'
                return True
        return False

    @staticmethod
    def translate_to_grid(location):
        """
        Converts a board location in algebraic notation to form usable with other functions (ie. from 'c7' to [2,6])
        :param location: board location in algebraic notation (ie. 'c7')
        :return: board location in a list coordinate (ie. [2,6])
        """

        columns = 'abcdefghi'
        return [int(columns.index(location[0].lower())), int(location[1:])-1]

    @staticmethod
    def translate_to_algebraic(location):
        """
        Converts a board location in list coordinates to algebraic notation (ie. from [2,6] to 'c7')
        :param location: board location in list coordinates (ie. [2,6]
        :return: board location in algebraic notation (ie. 'c7')
        """

        columns = 'abcdefghi'
        return columns[location[0]] + str(location[1] + 1)

    def get_general(self, color):
        """
        Receives a player's color and returns their General
        :param color: 'red' or 'blue'
        :return: a General object
        """

        for piece in self._active_pieces[color]:
            if type(piece) is General:
                return piece

    def can_checkmate(self, color):
        """
        Iterates through the passed player's pieces to see if they can checkmate the opposing player's general
        :param color: 'red' or 'blue' as the player
        :return: True if the player is in position to checkmate on their next turn, False otherwise
        """

        if color == 'red':
            opposing_color = 'blue'
        else:
            opposing_color = 'red'
        general_location = None

        for piece in self._active_pieces[opposing_color]:
            if type(piece) is General:
                general_location = self.translate_to_algebraic(piece.get_location())
                break
        for piece in self._active_pieces[color]:
            piece_location = self.translate_to_algebraic(piece.get_location())
            if piece.validate_move(piece_location, general_location, self._board):
                return True
        return False

    def is_a_player_in_check(self, color):
        """
        Determines if either player is in check. Checks first if the passed player (color parameter) is in check and only
        passes that General object even if both players' Generals are in check because this signifies that the current
        player is attempting an invalid move as they cannot place themself in check.
        :param color: 'red' or 'blue'
        :return: False if neither player is in check, or the General object of the player that is in check.
        """

        current_player = color
        if current_player == 'red':
            opposing_player = 'blue'
        else:
            opposing_player = 'red'

        if self.can_checkmate(opposing_player):
            return self.get_general(current_player)

        if self.can_checkmate(current_player):
            return self.get_general(opposing_player)

        return False

    def checkmate(self, general_object):
        """
        Iterates through the passed General's team's pieces and sees if any can make a move that will
        bring the General out of check.
        :param general_object: General object of the player we are determining is checkmated
        :return: True if the player is checkmated, False otherwise
        """

        # iterate through each piece on General's team
        for value_at_from in self._active_pieces[general_object.get_color()]:
            from_col = value_at_from.get_location()[0]
            from_row = value_at_from.get_location()[1]
            move_from = [from_col,from_row]

            for move_to in value_at_from.possible_moves(self._board):
                to_col = move_to[0]
                to_row = move_to[1]
                value_at_to = self._board[to_col][to_row]


                # if there's a piece of the same color at move_to (attempting to capture own piece)
                if issubclass(type(value_at_to), Piece) and general_object.get_color() == value_at_to.get_color():
                    continue
                else:
                    # Make the move
                    # if move_to holds an opposing piece, it gets captured
                    if issubclass(type(value_at_to), Piece):
                        self.remove_piece(value_at_to)
                    value_at_from.set_location(move_to)
                    self._board[to_col][to_row] = value_at_from
                    self._board[from_col][from_row] = ''
                    # if the General is no longer in check
                    if self.is_a_player_in_check(general_object.get_color()) != general_object:
                        # Revert the move and return False
                        self._board[from_col][from_row] = value_at_from
                        self._board[to_col][to_row] = value_at_to
                        value_at_from.set_location(move_from)
                        if issubclass(type(value_at_to), Piece):
                            self._active_pieces[value_at_to.get_color()].append(value_at_to)
                        return False
                    # Revert the move and move on to checking next move
                    self._board[from_col][from_row] = value_at_from
                    self._board[to_col][to_row] = value_at_to
                    value_at_from.set_location(move_from)
                    if issubclass(type(value_at_to), Piece):
                        self._active_pieces[value_at_to.get_color()].append(value_at_to)

        return True

    def remove_piece(self, piece):
        """
        Removes passed Piece object from the active pieces list of the game board.
        :param piece: Piece object to be removed
        :return: none
        """

        self._active_pieces[piece.get_color()].remove(piece)

    def display_board(self):
        """
        Prints a representation of the state of the game board.
        """

        for i in range(len(self._board[0])):
            row = ''
            for j in range(len(self._board)):
                if self._board[j][i] == '':
                    row += '  -  '
                else:
                    row += ' '+str(self._board[j][i])+' '
            print(row)
        print('............................................')


class Piece:
    """
    Is the parent class of all the various piece classes that constitute the pieces of the game. Each Piece holds
    the team's color, the piece type (for printing/debugging purposes), and its location on the game board. Each
    piece will be able to return a list of all its possible moves at any given time to be passed to the JanggiGame
    class for determining if a player is checkmated.
    """

    def __init__(self, color, location):
        """
        Initiates the Piece object for the designated player at the designated location on the game board.
        :param color: 'red' or 'blue' as the player
        :param location: game board coordinate to place the piece (ie. [3,7])
        """

        self._color = color
        self._piece_type = None
        self._location = location

    def __repr__(self):
        """
        Sets the Piece objects representation to a compact readable form, mainly used for JanggiGame's
        display_board method.
        :return: Piece object's repr() (ie. 'BGe' for blue player's General)
        """

        return self._color[0].upper() + self._piece_type

    def get_color(self):
        """
        Returns _color data member value.
        """

        return self._color

    def get_location(self):
        """
        Returns _location value
        """

        return self._location

    def set_location(self, location):
        """
        Sets the Piece's location on the game board.
        :param location: Coordinates on game board to move Piece to (ie. [3,7])
        :return: none
        """

        if type(location) is list:
            location_as_list = location
        else:
            location_as_list = JanggiGame.translate_to_grid(location)

        self._location = location_as_list

    def validate_move(self, move_from, move_to, board):
        """
        Each piece will have its own validation method to confirm the proposed movement pattern is valid.
        :param move_from: starting location (ie. 'd1')
        :param move_to: ending location (ie. 'd2')
        :param board: the JanggiGame instance's board value
        :return: True if move is valid, False otherwise
        """

        pass

    def possible_moves(self, board):
        """
        Returns list of all possible moves the Piece can make.
        :param board: JanggiGame instance's _board value
        :return: List in coordinates (ie. [[3,7], [5,2], [6,6])
        """

        coordinate_list = []
        algebraic_from = JanggiGame.translate_to_algebraic(self._location)
        for i, col in enumerate(board):
            for j, row in enumerate(col):
                algebraic_to = JanggiGame.translate_to_algebraic([i,j])
                if self.validate_move(algebraic_from,algebraic_to,board) is True:
                    coordinate_list.append([i,j])

        return coordinate_list


class General(Piece):
    """
    Inherits all data members and methods from Piece class and creates an object representing the general. It
    also determines if a move passed to it from the JanggiGame class is valid for this piece type.
    """

    def __init__(self, color, location):
        """
        Inherits from Piece, but amends value for piece type to readable form used for JanggiGame's display_board method
        """

        super().__init__(color, location)
        self._piece_type = 'Ge'
        self._in_check = False

    def validate_move(self, move_from, move_to, board):
        """
        Validates the proposed move for the piece. A General can move only one space at a time, and must stay within the
        confines of the palace (box confined by d1-f1-d3-f3 for red, and d10-f10-d8-f8 for blue)
        :param move_from: starting location (ie. d1)
        :param move_to: ending location (ie. d2)
        :param board: not used for General, but is necessary place holder as board needed in validate_move for other pieces
        :return: True if move is valid, False otherwise
        """

        from_coordinates = JanggiGame.translate_to_grid(move_from)
        to_coordinates = JanggiGame.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]

        if self._color == 'red':
            # if destination within the palace:
            if (to_col in range(3,6) and to_row in range(3) and
                # and the move is 1 horizontal or 1 vertical:
                (((abs(to_col-from_col) == 1 and to_row-from_row == 0) or
                (to_col-from_col == 0 and abs(to_row-from_row) == 1)) or
                # or the move is one diagonal:
                ((from_coordinates == [4,1] and to_coordinates in [[3,0],[3,2],[5,0],[5,2]]) or
                (from_coordinates in [[3,0],[3,2],[5,0],[5,2]] and to_coordinates == [4,1]))
                )
            ):
                return True
            else:
                return False

        if self._color == 'blue':
            # if destination within the palace:
            if (to_col in range(3,6) and to_row in range(7,10) and
                # and the move is 1 horizontal or 1 vertical:
                (((abs(to_col-from_col) == 1 and to_row-from_row == 0) or
                (to_col-from_col == 0 and abs(to_row-from_row) == 1)) or
                # or the move is one diagonal:
                ((from_coordinates == [4,8] and to_coordinates in [[3,7],[3,9],[5,7],[5,9]]) or
                (from_coordinates in [[3,7],[3,9],[5,7],[5,9]] and to_coordinates == [4,8]))
                )
            ):
                return True
            else:
                return False

    def get_in_check(self):
        """
        Returns the General's in_check status.
        """

        return self._in_check

    def set_in_check(self, state):
        """
        Sets the General's in_check status to True or False.
        :param state: True or False
        :return: none
        """

        self._in_check = state


class Guard(Piece):
    """
    Inherits all data members and methods from Piece class and creates an object representing a guard. It
    also determines if a move passed to it from the JanggiGame class is valid for this piece type.
    """

    def __init__(self, color, location):
        """
        Inherits from Piece, but amends value for piece type to readable form used for JanggiGame's display_board method
        """

        super().__init__(color, location)
        self._piece_type = 'Gu'

    def validate_move(self, move_from, move_to, board):
        """
        Validates the proposed move for the piece. A guard can only move one space at a time within the confines of its
        fortress (just like a General).
        :param move_from: starting location (ie. d1)
        :param move_to: ending location (ie. d2)
        :param board: not used for Guard, but is necessary place holder as board needed in validate_move for other pieces
        :return: True if move is valid, False otherwise
        """

        from_coordinates = JanggiGame.translate_to_grid(move_from)
        to_coordinates = JanggiGame.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]

        if self._color == 'red':
            # if destination within the palace:
            if (to_col in range(3, 6) and to_row in range(3) and
                    # and the move is 1 horizontal or 1 vertical:
                    (((abs(to_col - from_col) == 1 and to_row - from_row == 0) or
                      (to_col - from_col == 0 and abs(to_row - from_row) == 1)) or
                     # or the move is one diagonal:
                     ((from_coordinates == [4, 1] and to_coordinates in [[3, 0], [3, 2], [5, 0], [5, 2]]) or
                      (from_coordinates in [[3, 0], [3, 2], [5, 0], [5, 2]] and to_coordinates == [4, 1]))
                    )
            ):
                return True
            else:
                return False

        if self._color == 'blue':
            # if destination within the palace:
            if (to_col in range(3, 6) and to_row in range(7, 10) and
                    # and the move is 1 horizontal or 1 vertical:
                    (((abs(to_col - from_col) == 1 and to_row - from_row == 0) or
                      (to_col - from_col == 0 and abs(to_row - from_row) == 1)) or
                     # or the move is one diagonal:
                     ((from_coordinates == [4, 8] and to_coordinates in [[3, 7], [3, 9], [5, 7], [5, 9]]) or
                      (from_coordinates in [[3, 7], [3, 9], [5, 7], [5, 9]] and to_coordinates == [4, 8]))
                    )
            ):
                return True
            else:
                return False


class Horse(Piece):
    """
    Inherits all data members and methods from Piece class and creates an object representing a horse. It
    also determines if a move passed to it from the JanggiGame class is valid for this piece type.
    """

    def __init__(self, color, location):
        """
        Inherits from Piece, but amends value for piece type to readable form used for JanggiGame's display_board method
        """

        super().__init__(color, location)
        self._piece_type = 'Ho'

    def validate_move(self, move_from, move_to, board):
        """
        Validates the proposed move for the piece. A horse moves one space in any direction and then one space diagonally.
        It does not jump, so the move is invalid if another piece is in the way.
        :param move_from: starting location (ie. d1)
        :param move_to: ending location (ie. d2)
        :param board: the passing JanggiGame instance's _board value
        :return: True if move is valid, False otherwise
        """

        from_coordinates = JanggiGame.translate_to_grid(move_from)
        to_coordinates = JanggiGame.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]

        # if destination within the board
        if (to_col in range(9) and to_row in range(10) and
        # and the move is 1 up/down/left/right (with no other piece here) and then 1 farther out diagonally
            ((to_row - from_row == -2 and abs(to_col - from_col) == 1 and board[from_col][from_row - 1] == '') or
             (to_row - from_row == 2 and abs(to_col - from_col) == 1 and board[from_col][from_row + 1] == '') or
             (to_col - from_col == -2 and abs(to_row - from_row) == 1 and board[from_col - 1][from_row] == '') or
             (to_col - from_col == 2 and abs(to_row - from_row) == 1 and board[from_col + 1][from_row] == '')
            )
        ):
            return True
        else:
            return False


class Elephant(Piece):
    """
    Inherits all data members and methods from Piece class and creates an object representing an elephant. It
    also determines if a move passed to it from the JanggiGame class is valid for this piece type.
    """

    def __init__(self, color, location):
        """
        Inherits from Piece, but amends value for piece type to readable form used for JanggiGame's display_board method
        """

        super().__init__(color, location)
        self._piece_type = 'El'

    def validate_move(self, move_from, move_to, board):
        """
        Validates the proposed move for the piece. An elephant moves one space in any direction and then two spaces
        diagonally. It does not jump, so is blocked if another piece is in the way.
        :param move_from: starting location (ie. d1)
        :param move_to: ending location (ie. d2)
        :param board: the passing JanggiGame instance's _board value
        :return: True if move is valid, False otherwise
        """

        from_coordinates = JanggiGame.translate_to_grid(move_from)
        to_coordinates = JanggiGame.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]

        # if destination within the board
        if to_col in range(9) and to_row in range(10):
            # if destination is 1 up and diagonally to the left
            if to_col - from_col == -2 and to_row - from_row == -3 and board[from_col][from_row - 1] == '' and board[from_col - 1][from_row - 2] == '':
                return True
            # if destination is 1 up and diagonally to the right
            if to_col - from_col == 2 and to_row - from_row == -3 and board[from_col][from_row - 1] == '' and board[from_col + 1][from_row - 2] == '':
                return True
            # if destination is 1 down and diagonally to the left
            if to_col - from_col == -2 and to_row - from_row == 3 and board[from_col][from_row + 1] == '' and board[from_col - 1][from_row + 2] == '':
                return True
            # if destination is 1 down and diagonally to the right
            if to_col - from_col == 2 and to_row - from_row == 3 and board[from_col][from_row + 1] == '' and board[from_col + 1][from_row + 2] == '':
                return True
            # if destination is 1 left and diagonally up
            if to_col - from_col == -3 and to_row - from_row == -2 and board[from_col - 1][from_row] == '' and board[from_col - 2][from_row - 1] == '':
                return True
            # if destination is 1 left and diagonally down
            if to_col - from_col == -3 and to_row - from_row == 2 and board[from_col - 1][from_row] == '' and board[from_col - 2][from_row + 1] == '':
                return True
            # if destination is 1 right and diagonally up
            if to_col - from_col == 3 and to_row - from_row == -2 and board[from_col + 1][from_row] == '' and board[from_col + 2][from_row - 1] == '':
                return True
            # if destination is 1 right and diagonally down
            if to_col - from_col == 3 and to_row - from_row == 2 and board[from_col + 1][from_row] == '' and board[from_col + 2][from_row + 1] == '':
                return True
        return False


class Chariot(Piece):
    """
    Inherits all data members and methods from Piece class and creates an object representing a chariot. It
    also determines if a move passed to it from the JanggiGame class is valid for this piece type.
    """

    def __init__(self, color, location):
        """
        Inherits from Piece, but amends value for piece type to readable form used for JanggiGame's display_board method
        """

        super().__init__(color, location)
        self._piece_type = 'Ch'

    def validate_move(self, move_from, move_to, board):
        """
        Validates the proposed move for the piece. A Chariot can move unlimited spaces horizontally or vertically until
        it hits a wall or another piece. It can move along the diagonals in the fortresses as well.
        :param move_from: starting location (ie. d1)
        :param move_to: ending location (ie. d2)
        :param board: the passing JanggiGame instance's _board value
        :return: True if move is valid, False otherwise
        """

        from_coordinates = JanggiGame.translate_to_grid(move_from)
        to_coordinates = JanggiGame.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]

        # if destination within the board and the move is strictly horizontal or vertical
        if to_col in range(9) and to_row in range(10) and (to_col == from_col or to_row == from_row):
            # if move is to the left
            if to_col < from_col:
                # make sure no other piece lies between to and from
                for col in range(to_col + 1, from_col):
                    if board[col][to_row] != '':
                        return False
                return True
            # if move is to the right
            if to_col > from_col:
                # make sure no other piece lies between to and from
                for col in range(from_col + 1, to_col):
                    if board[col][to_row] != '':
                        return False
                return True
            # if move is upward
            if to_row < from_row:
                # make sure no other piece lies between to and from
                for row in range(to_row + 1, from_row):
                    if board[to_col][row] != '':
                        return False
                return True
            # if move is downward
            if to_row > from_row:
                # make sure no other piece lies between to and from
                for row in range(from_row + 1, to_row):
                    if board[to_col][row] != '':
                        return False
                return True

            return False

        # if moving along the diagonals in the red palace
        if from_coordinates in [[3,0],[3,2],[5,0],[5,2]] and to_coordinates in [[3,0],[3,2],[5,0],[5,2]] and board[4][1] == '':
            return True
        if from_coordinates in [[3,0],[3,2],[5,0],[5,2]] and to_coordinates == [4,1]:
            return True
        if from_coordinates == [4,1] and to_coordinates in [[3,0],[3,2],[5,0],[5,2]]:
            return True

        # if moving along the diagonals in the blue palace
        if from_coordinates in [[3,7],[3,9],[5,7],[5,9]] and to_coordinates in [[3,7],[3,9],[5,7],[5,9]] and board[4][8] == '':
            return True
        if from_coordinates in [[3,7],[3,9],[5,7],[5,9]] and to_coordinates == [4,8]:
            return True
        if from_coordinates == [4,8] and to_coordinates in [[3,7],[3,9],[5,7],[5,9]]:
            return True

        return False


class Cannon(Piece):
    """
    Inherits all data members and methods from Piece class and creates an object representing a cannon. It
    also determines if a move passed to it from the JanggiGame class is valid for this piece type.
    """

    def __init__(self, color, location):
        """
        Inherits from Piece, but amends value for piece type to readable form used for JanggiGame's display_board method
        """

        super().__init__(color, location)
        self._piece_type = 'Ca'

    def validate_move(self, move_from, move_to, board):
        """
        Validates the proposed move for the piece. A cannon moves horizontally or vertically in any direction, but can
        only do so if another piece (that is NOT a cannon) is in the way. It cannot hop over or capture another cannon.
        :param move_from: starting location (ie. d1)
        :param move_to: ending location (ie. d2)
        :param board: the passing JanggiGame instance's _board value
        :return: True if move is valid, False otherwise
        """

        from_coordinates = JanggiGame.translate_to_grid(move_from)
        to_coordinates = JanggiGame.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]

        # a cannon cannot capture another cannon
        if type(board[to_col][to_row]) == Cannon:
            return False

        # if destination within the board and the move is strictly horizontal or vertical
        if to_col in range(9) and to_row in range(10) and (to_col == from_col or to_row == from_row):
            # if move is to the left
            if to_col < from_col:
                # make sure there is exactly one intervening piece that's not a cannon
                piece_count = 0
                for col in range(to_col + 1, from_col):
                    if type(board[col][to_row]) == Cannon:
                        return False
                    if issubclass(type(board[col][to_row]), Piece):
                        piece_count += 1
                if piece_count == 1:
                    return True
            # if move is to the right
            if to_col > from_col:
                # make sure there is exactly one intervening piece that's not a cannon
                piece_count = 0
                for col in range(from_col + 1, to_col):
                    if type(board[col][to_row]) == Cannon:
                        return False
                    if issubclass(type(board[col][to_row]), Piece):
                        piece_count += 1
                if piece_count == 1:
                    return True
            # if move is upward
            if to_row < from_row:
                # make sure there is exactly one intervening piece that's not a cannon
                piece_count = 0
                for row in range(to_row + 1, from_row):
                    if type(board[to_col][row]) == Cannon:
                        return False
                    if issubclass(type(board[to_col][row]), Piece):
                        piece_count += 1
                if piece_count == 1:
                    return True
            # if move is downward
            if to_row > from_row:
                # make sure there is exactly one intervening piece that's not a cannon
                piece_count = 0
                for row in range(from_row + 1, to_row):
                    if type(board[to_col][row]) == Cannon:
                        return False
                    if issubclass(type(board[to_col][row]), Piece):
                        piece_count += 1
                if piece_count == 1:
                    return True
            return False

        # for moving diagonally in the red palace
        if (from_coordinates in [[3,0],[3,2],[5,0],[5,2]] and to_coordinates in [[3,0],[3,2],[5,0],[5,2]] and
                type(board[4][1]) != Cannon and issubclass(type(board[4][1]), Piece)):
            return True

        # for moving diagonally in the blue palace
        if (from_coordinates in [[3,7],[3,9],[5,7],[5,9]] and to_coordinates in [[3,7],[3,9],[5,7],[5,9]] and
                type(board[4][8]) != Cannon and issubclass(type(board[4][8]), Piece)):
            return True

        return False


class Soldier(Piece):
    """
    Inherits all data members and methods from Piece class and creates an object representing a soldier. It
    also determines if a move passed to it from the JanggiGame class is valid for this piece type.
    """

    def __init__(self, color, location):
        """
        Inherits from Piece, but amends value for piece type to readable form used for JanggiGame's display_board method
        """

        super().__init__(color, location)
        self._piece_type = 'So'

    def validate_move(self, move_from, move_to, board):
        """
        Validates the proposed move for the piece. The Soldier can only move one space forward or to the side at a time.
        However it can also move forward diagonally within a fortress.
        :param move_from: starting location (ie. d1)
        :param move_to: ending location (ie. d2)
        :param board: not used for Soldier, but is necessary place holder as board needed in validate_move for other pieces
        :return: True if move is valid, False otherwise
        """

        from_coordinates = JanggiGame.translate_to_grid(move_from)
        to_coordinates = JanggiGame.translate_to_grid(move_to)
        from_col = from_coordinates[0]
        from_row = from_coordinates[1]
        to_col = to_coordinates[0]
        to_row = to_coordinates[1]

        # for red soldiers (who can only move downward or to the side)
        if self.get_color() == 'red':
            # if destination within the board and the move is strictly one downward or to the side
            if (to_col in range(9) and to_row in range(10) and
                    ((abs(to_col - from_col) == 1 and to_row == from_row) or (to_col == from_col and to_row - from_row == 1))):
                return True
            # if moving diagonally within the blue palace
            if from_coordinates in [[3,7],[5,7]] and to_coordinates == [4,8]:
                return True
            if from_coordinates == [4,8] and to_coordinates in [[3,9],[5,9]]:
                return True

            return False

        # for blue soldiers (who can only move upward or to the side)
        if self.get_color() == 'blue':
            # if destination within the board and the move is strictly one upward or to the side
            if (to_col in range(9) and to_row in range(10) and
                    ((abs(to_col - from_col) == 1 and to_row == from_row) or (to_col == from_col and to_row - from_row == -1))):
                return True
            # if moving diagonally within the red palace
            if from_coordinates in [[3, 2], [5, 2]] and to_coordinates == [4, 1]:
                return True
            if from_coordinates == [4, 1] and to_coordinates in [[3, 0], [5, 0]]:
                return True

            return False

        return False


def main():
    """
    Place test code here.
    """

    game = JanggiGame()
    game.display_board()
    print(game.make_move('a7','a6'))
    print(game.make_move('h1','g3'))
    print(game.make_move('a10','a7'))
    print(game.make_move('b1','d4'))
    print(game.make_move('a7','b7'))
    print(game.make_move('c1','a2'))
    print(game.make_move('b7','b3'))
    print(game.make_move('h3','b3'))
    print(game.make_move('e7','e6'))
    print(game.make_move('i1','h1'))
    print(game.make_move('i7','h7'))
    print(game.make_move('a2','b4'))
    print(game.make_move('b10','d7'))
    print(game.make_move('b4','a6'))
    print(game.make_move('i10','i9'))
    print(game.make_move('a6','b8'))
    print(game.make_move('c10','b8'))
    print(game.make_move('b3','b9'))
    print(game.make_move('i9','i6'))
    print(game.make_move('a1','b1'))
    print(game.make_move('b8','c6'))
    print(game.make_move('b1','b8'))
    print(game.make_move('h8','h1'))
    print(game.make_move('g3','h1'))
    print(game.make_move('e6','d6'))
    print(game.make_move('h1','g3'))
    print(game.make_move('d6','d5'))
    print(game.make_move('d4','b1'))
    print(game.make_move('i6','e6'))
    print(game.make_move('i4','i5'))
    print(game.make_move('c6','d4'))
    print(game.make_move('c4','d4'))
    print(game.make_move('d5','d4'))
    print(game.make_move('g4','f4'))
    print(game.make_move('d4','e4'))
    print(game.make_move('f4','e4'))
    print(game.make_move('e6','e4'))
    print(game.make_move('g3','e4'))
    print(game.make_move('h10','i8'))
    print(game.make_move('e4','f6'))
    print(game.make_move('g7','g6'))
    print(game.make_move('b1','d4'))
    print(game.make_move('g6','f6'))
    print(game.make_move('d4','f7'))
    print(game.make_move('d7','f4'))
    print(game.make_move('f7','c9'))
    print(game.make_move('d10','d9'))
    print(game.make_move('a4','a5'))
    print(game.make_move('f6','f5'))
    print(game.make_move('g1','e4'))
    print(game.make_move('c7','c6'))
    print(game.make_move('b8','i8'))
    print(game.make_move('f5','e5'))
    print(game.make_move('e4','g1'))
    print(game.make_move('e5','d5'))
    print(game.make_move('i8','i9'))
    print(game.make_move('f10','f9'))
    print(game.make_move('a5','a6'))
    print(game.make_move('d5','d4'))
    print(game.make_move('a6','a7'))
    print(game.make_move('d4','d3'))
    print(game.make_move('e2','d3'))
    print(game.make_move('e9','e8'))
    print(game.make_move('i9','f9'))
    print(game.make_move('h7','h6'))
    print(game.make_move('a7','b7'))
    print(game.make_move('g10','e7'))
    print(game.make_move('f9','f7'))
    print(game.make_move('d9','d10'))
    print(game.make_move('f7','e7'))
    print(game.make_move('e8','f8'))
    print(game.make_move('b7','c7'))
    print(game.make_move('h6','h5'))
    print(game.make_move('e7','e10'))
    print(game.make_move('h5','h4'))
    print(game.make_move('c7','d7'))
    print(game.make_move('h4','h3'))
    print(game.make_move('d7','e7'))
    print(game.make_move('h3','h2'))
    print(game.make_move('e7','f7'))
    game.display_board()
    print('Red in check: '+str(game.is_in_check('red')))
    print('Blue in check: '+str(game.is_in_check('blue')))
    print(game.get_game_state())


if __name__ == '__main__':
    main()
