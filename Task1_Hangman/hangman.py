"""
Hangman Word Guessing Game (Console)
------------------------------------
Guess the hidden word one letter at a time.
You get 6 wrong guesses before the game ends.
"""

import random
import os

MAX_MISTAKES = 6
WORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")

# Words to use if words.txt is missing
FALLBACK_WORDS = ["python", "keyboard", "internship", "algorithm", "variable",
                  "function", "database", "compiler", "software", "network"]

# Gallows drawing for each stage (0 = no mistakes, 6 = game over)
STAGES = [
    """
     -----
     |   |
         |
         |
         |
         |
    =========""",
    """
     -----
     |   |
     O   |
         |
         |
         |
    =========""",
    """
     -----
     |   |
     O   |
     |   |
         |
         |
    =========""",
    """
     -----
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    """
     -----
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    """
     -----
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    """
     -----
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========""",
]


def load_words(path=WORD_FILE, min_len=4):
    """Read words from the file, or use the fallback list if it's missing."""
    try:
        with open(path, encoding="utf-8") as f:
            words = [w.strip().lower() for w in f
                     if w.strip().isalpha() and len(w.strip()) >= min_len]
        if words:
            return words
    except OSError:
        print(f"(Word file '{path}' not found - using built-in words.)")
    return FALLBACK_WORDS


def masked_word(secret, guessed):
    """Show the word with guessed letters filled in, like 'p _ t _ _ _'."""
    return " ".join(ch if ch in guessed else "_" for ch in secret)


def get_guess(guessed):
    """Ask the player for a letter until they give a valid new one."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter exactly one letter (a-z).")
        elif guess in guessed:
            print(f"You already guessed '{guess}'. Try another letter.")
        else:
            return guess


def play_round(secret):
    """Play one game. Returns True if the player wins, False if they lose."""
    guessed = set()
    mistakes = 0

    while mistakes < MAX_MISTAKES:
        # Show the current game state
        print(STAGES[mistakes])
        print(f"\nWord:    {masked_word(secret, guessed)}")
        print(f"Guessed: {' '.join(sorted(guessed)) or '-'}")
        print(f"Attempts left: {MAX_MISTAKES - mistakes}\n")

        guess = get_guess(guessed)
        guessed.add(guess)

        if guess in secret:
            print(f"Good guess! '{guess}' is in the word.")
            # Check if all letters are guessed
            if all(ch in guessed for ch in secret):
                print(f"\n*** VICTORY! The word was '{secret}'. ***")
                return True
        else:
            # Wrong guess, count a mistake
            mistakes += 1
            print(f"Sorry, '{guess}' is not in the word.")

    # Out of guesses, player loses
    print(STAGES[MAX_MISTAKES])
    print(f"\n*** DEFEAT! The word was '{secret}'. ***")
    return False


def main():
    words = load_words()
    print("=== HANGMAN ===")
    wins = losses = 0

    while True:
        # Play a round and update the score
        if play_round(random.choice(words)):
            wins += 1
        else:
            losses += 1
        print(f"Score - Wins: {wins} | Losses: {losses}")

        # Ask if the player wants another round
        if input("\nPlay again? (y/n): ").strip().lower() != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
