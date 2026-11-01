# Datheon Python Programming Internship

Portfolio projects completed for the Datheon self-paced Python Programming Internship.
All tasks use Python 3 and the standard library only (`yfinance` is optional in Task 2).

## Repository Structure

```
Datheon_Python_Programming_Internship/
├── README.md
├── Task1_Hangman/
│   ├── hangman.py
│   └── words.txt
├── Task2_Portfolio_Tracker/
│   ├── portfolio.py
│   └── portfolio_summary.csv      (sample output)
├── Task3_File_Organizer/
│   └── organizer.py
└── Task4_Chatbot/
    ├── chatbot.py
    └── sample_faq.json
```

## Task 1 - Hangman Word Guessing Game (Console)
Terminal Hangman with 6 attempts, ASCII gallows art, masked word display, guessed-letter
tracking, no penalty for repeated guesses, input validation, replay and score counter.
```bash
cd Task1_Hangman && python hangman.py
```

## Task 2 - Stock Portfolio Performance Tracker
Enter tickers, buy prices and share quantities (stored in a dictionary). The script gets live
prices via `yfinance` if installed (otherwise asks for the current price), then calculates
invested capital, current value and gain/loss % per holding and overall. Results are printed as
a formatted table and appended with a timestamp to `portfolio_summary.csv` (csv module).
If the S&P 500 dataset is saved as `sp500.csv` next to the script, tickers are validated
and company names added.
```bash
cd Task2_Portfolio_Tracker
pip install yfinance   # optional, for live prices
python portfolio.py
```

## Task 3 - Automated File Organizer & Cleanup Utility
Sorts a cluttered folder into Documents, Images, Videos, Audio, Archives, Code and Others
using an extension mapping, `os.scandir()` and `shutil.move()`. Handles naming collisions
(`report.pdf` -> `report_1.pdf`), `PermissionError` / `FileExistsError`, writes `organizer.log`,
and prints an execution summary. Includes a `--dry-run` preview mode.
```bash
cd Task3_File_Organizer
python organizer.py --dry-run          # preview Downloads folder
python organizer.py "path/to/folder"   # organize a specific folder
```

## Task 4 - Rule-Based Interactive Terminal Assistant / Chatbot
A support chatbot that loads greetings and FAQs from `sample_faq.json`, normalizes input
(lowercase, punctuation stripped), and recognizes multiple intents in one message using
regular expressions plus keyword-overlap matching with a confidence threshold. It tracks
conversation state (greeting -> intent -> resolution -> exit), gives graceful fallbacks for
unknown queries, and exits cleanly on `bye`, `exit` or `quit` (also handles Ctrl+C / Ctrl+D
and a missing or invalid JSON file).
```bash
cd Task4_Chatbot && python chatbot.py
```
