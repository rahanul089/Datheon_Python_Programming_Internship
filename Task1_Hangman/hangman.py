"""
Hangman Word Guessing Game (Console)
------------------------------------
- Picks a random word from words.txt (the downloaded English word list),
  falling back to a built-in list if the file is missing.
- 6 incorrect guesses allowed, with ASCII gallows art for each stage.
- Tracks guessed letters; repeated guesses never cost an attempt.
"""

import random
import os

MAX_MISTAKES = 6
WORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")
FALLBACK_WORDS = ["python", "keyboard", "internship", "algorithm", "variable",
                  "function", "database", "compiler", "software", "network"]

# ASCII art: index = number of incorrect guesses (0..6)
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
    """Load alphabetic words of at least min_len letters; fall back if needed."""
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
    """Return e.g. '_ a _ h o n' based on correctly guessed letters."""
    return " ".join(ch if ch in guessed else "_" for ch in secret)


def get_guess(guessed):
    """Prompt until the player enters a single new letter."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter exactly one letter (a-z).")
        elif guess in guessed:
            print(f"You already guessed '{guess}'. Try another letter.")
        else:
            return guess


def play_round(secret):
    """Run one game. Returns True if the player wins."""
    guessed = set()
    mistakes = 0

    while mistakes < MAX_MISTAKES:
        print(STAGES[mistakes])
        print(f"\nWord:    {masked_word(secret, guessed)}")
        print(f"Guessed: {' '.join(sorted(guessed)) or '-'}")
        print(f"Attempts left: {MAX_MISTAKES - mistakes}\n")

        guess = get_guess(guessed)
        guessed.add(guess)

        if guess in secret:
            print(f"Good guess! '{guess}' is in the word.")
            if all(ch in guessed for ch in secret):
                print(f"\n*** VICTORY! The word was '{secret}'. ***")
                return True
        else:
            mistakes += 1
            print(f"Sorry, '{guess}' is not in the word.")

    print(STAGES[MAX_MISTAKES])
    print(f"\n*** DEFEAT! The word was '{secret}'. ***")
    return False


def main():
    words = load_words()
    print("=== HANGMAN ===")
    wins = losses = 0

    while True:
        if play_round(random.choice(words)):
            wins += 1
        else:
            losses += 1
        print(f"Score - Wins: {wins} | Losses: {losses}")
        if input("\nPlay again? (y/n): ").strip().lower() != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
