import copy     #NOTE:(Roy) Dont use because of time issues!
import sys
import time

from queue import PriorityQueue

INPUT_FILENAME = "rh.txt"
OUTPUT_FILENAME = "ans_with_cost_2.txt"

RED_CAR_EXIT_INDEX = 17

START_LINE = 8          # staring line in rh.txt
SAMPLES = 40

MAX_TIME = 5            # max time per board
BOARD_LENGTH = 6

(
    HORIZ,
    VERT
)=range(2)


# Utilities

def read_file(filename=INPUT_FILENAME):
    with open(filename, 'r') as fileobj:
        data = fileobj.read().split('\n')

    # return data in file
    return data[START_LINE : START_LINE + SAMPLES]

def write_file(stats, filename=OUTPUT_FILENAME):
    with open(filename, 'a+') as fileobj:
        fileobj.write(stats)


def dict_to_str(d):
    s = ""
    for k, v in d.items():
        s += "%s:\t%s\n" % (k, v)
    return s + "\n\n"


# Board object
# NOTE(Roy): Don't use objects for cars, Python OOP is expensive!

class Board(object):
    def __init__(self, board_string, moves):
        self._board_str = board_string
        self._moves = moves
        self._cars = {}

        # create dict out of the cars
        for index, tile in enumerate(list(self._board_str)):
            if tile is not ".":
                if tile not in self._cars.keys():
                    self._cars[tile] = [[]]

                self._cars[tile][0].append(index)

        for car, car_info in self._cars.items():
            # compare two first instances of
            if car_info[0][0] + 1 == car_info[0][1]:
                car_info.append(HORIZ)
            else:
                car_info.append(VERT)

        self._cost = self.cost_2()

    def __repr__(self):
        s = "     1 2 3 4 5 6 \n   +-------------+\n"
        for i in range(BOARD_LENGTH):
            s += (' ' + str(i+1) + " | ")
            for j in range(BOARD_LENGTH):
                s += ('' + self.get_tile((i, j)) + " ")
            if i == 2:
                s += ("  ==>\n")
            else:
                s += ("|\n")
            i+=1
        s += "   +-------------+ "
        return s

    def get_tile(self, loc):
        return self._board_str[loc[0] * BOARD_LENGTH + loc[1]]

    def to_loc(self, pos):
        return (int(pos / 6), pos % 6)

    def cost(self):
        # return all blocking cars in front
        return sum([
            1 for index in range((self._cars["X"][0][-1] + 1), RED_CAR_EXIT_INDEX + 1)
            if self._board_str[index] != "."
        ])

    def cost_2(self):
        # return the sum of sizes of all the blocking cars
        return sum([
            len(self._cars[self._board_str[index]][0])
            for index in range((self._cars["X"][0][-1] + 1), RED_CAR_EXIT_INDEX + 1)
            if self._board_str[index] != "."
        ])

    # Not to compare states! this is to compare states_we_visited
    # heurisitc value - used by PriorityQueue
    def __eq__(self, other):
        return self._cost == other._cost

    def __lt__(self, other):
        return self._cost < other._cost

    def final_state(self):
        if self._board_str[RED_CAR_EXIT_INDEX] is "X":
            return True
        return False

    def next_layer(self):
        next_layer = []
        for car_name, car_info in self._cars.items():
            locations = car_info[0]
            start_loc = self.to_loc(locations[0])
            end_loc = self.to_loc(locations[-1])

            # Horizntal movement
            if car_info[1] == HORIZ:
                # check right movement
                curr_board = self._board_str

                for move_len, new_end in enumerate(
                    range(end_loc[1] + 1, BOARD_LENGTH)
                ):
                    # empty?
                    if self.get_tile((end_loc[0], new_end)) != ".":
                        break

                    # add possible move
                    new_move = car_name + "R" + str(move_len + 1)

                    # write new board
                    new_board = list(curr_board)
                    new_board[locations[0] + move_len] = "."
                    new_board[locations[-1] + move_len + 1] = car_name
                    curr_board = "".join(new_board)

                    # add to states
                    next_layer.append(Board(curr_board, self._moves + [new_move]))

                # check left movement
                curr_board = self._board_str

                for move_len, new_end in enumerate(
                    range(start_loc[1] - 1, -1, -1)
                ):
                    # empty?
                    if self.get_tile((end_loc[0], new_end)) != ".":
                        break

                    # add possible move
                    new_move = car_name + "L" + str(move_len + 1)

                    # write new board
                    new_board = list(curr_board)
                    new_board[locations[-1] - move_len] = "."
                    new_board[locations[0] - move_len - 1] = car_name
                    curr_board = "".join(new_board)

                    # add to states
                    next_layer.append(Board(curr_board, self._moves + [new_move]))

            # Vertical movement
            else:
                # check down movement
                curr_board = self._board_str

                for move_len, new_end in enumerate(
                    range(end_loc[0] + 1, BOARD_LENGTH)
                ):
                    # empty?
                    if self.get_tile((new_end, end_loc[1])) != ".":
                        break

                    # add possible move
                    new_move = car_name + "D" + str(move_len + 1)

                    # write new board
                    new_board = list(curr_board)
                    new_board[locations[0] + BOARD_LENGTH * move_len] = "."
                    new_board[locations[-1] + (BOARD_LENGTH) * (move_len + 1)] = car_name
                    curr_board = "".join(new_board)

                    # add to states
                    next_layer.append(Board(curr_board, self._moves + [new_move]))

                # check up movement
                curr_board = self._board_str

                for move_len, new_end in enumerate(
                    range(start_loc[0] - 1, -1, -1)
                ):
                    # empty?
                    if self.get_tile((new_end, end_loc[1])) != ".":
                        break

                    # add possible move
                    new_move = car_name + "U" + str(move_len + 1)

                    # write new board
                    new_board = list(curr_board)
                    new_board[locations[-1] - BOARD_LENGTH * move_len] = "."
                    new_board[locations[0] - (BOARD_LENGTH) * (move_len + 1)] = car_name
                    curr_board = "".join(new_board)

                    # add to states
                    next_layer.append(Board(curr_board, self._moves + [new_move]))

        return next_layer



# MAIN FUNCTIONS

def board_solver(board_str, board_num):
    # Init board stats
    stats = {
        "Puzzle number" : board_num,
        "solved" : False,
    }
    board_time = time.time()
    total_branches = 0
    expanded_nodes = 0
    total_cost = 0

    # Init board variables
    initial_state = Board(board_str, [])
    queue_states = PriorityQueue()
    queue_states.put(initial_state)
    visited_boards = []

    while (time.time() - board_time) < MAX_TIME:
        curr_state = queue_states.get()
        expanded_nodes += 1
        total_cost += curr_state._cost

        # check if final state
        if curr_state.final_state():
            stats["solved"] = True
            stats["search time"] = time.time() - board_time
            stats["solution"] = curr_state._moves

            # NOTE(Roy) : We found that using this formula doesnt
            # give the expected results
            # stats["branching factor"] = (
            #    len(visited_boards)**(1.0/len(stats["solution"]))
            #)
            stats["branching factor"] = total_branches / expanded_nodes
            stats["avg. function"] = total_cost / expanded_nodes

            # depth heuristics
            depths = []
            while not queue_states.empty():
                depths.append(len(queue_states.get()._moves))

            stats["avg depth"] = sum(depths) / len(depths)
            stats["min depth"] = min(depths)
            stats["max depth"] = max(depths)

            break

        # otherwise expand
        else:
            for new_state in curr_state.next_layer():
                total_branches += 1
                if new_state._board_str not in visited_boards:
                    visited_boards.append(new_state._board_str)
                    queue_states.put(new_state)

    return stats


def main():
    # init overall stats
    overall_time = time.time()
    total_wins = 0

    # loop over all the boards
    for index, board in enumerate(read_file()):
        # handle the current board
        stats = board_solver(board, index + 1)

        # document
        write_file(dict_to_str(stats))
        total_wins += stats["solved"]

    # Output the Total time
    write_file(str(
        "\n\nTotal time:\t" + str(time.time() - overall_time)
        + "\nTotal solved:\t" + str(total_wins) + "\n\n"
    ))


if __name__ == "__main__":
    main()
