from typing import Optional

import numpy as np
from numba import njit
from rich.console import Console

VALUE = 0
SUIT = 1
TOTAL_CARDS = 2

PRETTY_VALUES = {
    0: "A",
    1: "2",
    2: "3",
    3: "4",
    4: "5",
    5: "6",
    6: "7",
    7: "8",
    8: "9",
    9: "10",
    10: "J",
    11: "Q",
    12: "K",
}

PRETTY_SUITS = {0: "♣", 1: "♠", 2: "♥", 3: "♦"}

SUIT_STYLES = {
    0: "bold black on bright_white",
    1: "bold black on bright_white",
    2: "bold dark_red on bright_white",
    3: "bold dark_red on bright_white",
}

NEW_DECK = np.array([(face, suit) for face in range(13) for suit in range(4)], np.uint8)

console = Console()


def print_current_state(
    game,
    game_index,
    card_being_checked: Optional[int] = None,
    last_stacked: Optional[int] = None,
):
    total = game[0][TOTAL_CARDS]
    index = 0
    board = []

    while total > 0:
        value = PRETTY_VALUES[game[index][VALUE]]
        suit = PRETTY_SUITS[game[index][SUIT]]
        style = SUIT_STYLES[game[index][SUIT]]
        total = game[index][TOTAL_CARDS]
        selection = ""
        stacked = ""
        if card_being_checked == index:
            selection = "[default on blue] [/default on blue]"
        if last_stacked == index:
            stacked = "[default on red] [/default on red]"
        board.append(
            f"{stacked}{selection}"
            f"[{style}] {value}{suit} [/{style}]"
            f"{selection}{stacked}"
            f"([green]{total}[/green])"
        )
        index += 1
        if index > 51:
            break
        total = game[index][TOTAL_CARDS]

    console.print(" ".join(board))
    console.print(f"Number of active cards: {game_index + 1}")


@njit
def rank_match(array: np.array, index1: int, index2: int):
    return array[index1][VALUE] == array[index2][VALUE]


@njit
def suit_match(array: np.array, index1: int, index2: int):
    return array[index1][SUIT] == array[index2][SUIT]


@njit
def rank_or_suit_match(array: np.array, index1: int, index2: int) -> bool:
    return rank_match(array, index1, index2) or suit_match(array, index1, index2)


@njit
def move_card(array: np.array, new_index: int, old_index: int):
    array[new_index][VALUE] = array[old_index][VALUE]
    array[new_index][SUIT] = array[old_index][SUIT]
    array[new_index][TOTAL_CARDS] += array[old_index][TOTAL_CARDS]

    array[old_index][VALUE] = 0
    array[old_index][SUIT] = 0
    array[old_index][TOTAL_CARDS] = 0


@njit
def remove_card(array: np.array, index):
    array[index][VALUE] = 0
    array[index][SUIT] = 0
    array[index][TOTAL_CARDS] = 0


@njit
def shift(array, index, empty_space=1):
    card_total = array[index + empty_space][TOTAL_CARDS]

    while card_total > 0:
        move_card(array, index, index + empty_space)
        index += 1
        card_total = array[min(index + empty_space, 51)][TOTAL_CARDS]


@njit
def get_shuffled_deck() -> np.array:
    deck = np.copy(NEW_DECK)
    np.random.shuffle(deck)
    return deck
