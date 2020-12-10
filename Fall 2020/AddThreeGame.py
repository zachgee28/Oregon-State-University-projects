#Author: Zach Gee
#Date: 11/12/2020
#Description: Create AddThreeGame class that allows two players to play a game in which they alternately choose numbers from 1-9. They may not choose a number that has already been selected by either player. If at any point exactly three of the player's numbers sum to 15, then that player has won. If all numbers from 1-9 are chosen, but neither player has won, then the game ends in a draw.

class AddThreeGame:
    """Allows two players to play a game in which they alternately choose numbers from 1-9. They may not choose a number that has already been selected by either player. If at any point exactly three of the player's numbers sum to 15, then that player has won. If all numbers from 1-9 are chosen, but neither player has won, then the game ends in a draw."""

    def __init__(self):
        """Initializes an instance of the game with data members describing who chose which numbers, the current state, and whose turn it is"""

        self._nums_chosen = {"first" : [], "second" : []}
        self._current_state = "UNFINISHED"
        self._turn = "first"

    def get_current_state(self):
        """returns self._current_state"""

        return self._current_state

    def make_move(self, player, num):
        """Takes in 'first' or 'second' as valid player argument and an integer 1-9 as valid num argument. If it's the correct player's turn and num hasn't been played and game is 'UNFINISHED', then complete the move and update data members accordingly."""

        if self._turn == player and 1 <= num <= 9 and num not in self._nums_chosen["first"] and num not in self._nums_chosen["second"] and self._current_state == "UNFINISHED":
            self._nums_chosen[player].append(num)

            if len(self._nums_chosen[player]) >= 3:
                for i in range(len(self._nums_chosen[player])):
                    for j in range(i+1, len(self._nums_chosen[player])):
                        for k in range(j+1, len(self._nums_chosen[player])):
                            if self._nums_chosen[player][i] + self._nums_chosen[player][j] + self._nums_chosen[player][k] == 15:
                                self._current_state = player.upper() + "_WON"

            if len(self._nums_chosen["first"]) + len(self._nums_chosen["second"]) == 9 and self._current_state == "UNFINISHED":
                self._current_state = "DRAW"

            if self._turn == "first":
                self._turn = "second"
            elif self._turn == "second":
                self._turn = "first"

            return True

        else:
            return False
