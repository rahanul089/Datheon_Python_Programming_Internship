"""
A simple chatbot that answers questions about hours, project submission
and certificates.

- Loads greetings and FAQ answers from sample_faq.json
- Matches user input using regex rules and keyword overlap
- One message can trigger multiple answers at once
- Type 'bye', 'exit' or 'quit' to leave
"""

import json
import os
import re
import sys

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_faq.json")
EXIT_WORDS = {"bye", "exit", "quit"}
CONFIDENCE_THRESHOLD = 0.34      # how much keyword overlap counts as a match

# Common words we ignore when comparing keywords
STOP_WORDS = {"a", "an", "the", "is", "are", "do", "does", "i", "my", "me", "you", "your",
              "we", "our", "to", "of", "for", "in", "on", "at", "and", "or", "what", "when",
              "how", "can", "will", "it", "be", "this", "that", "with", "about", "please"}

# Regex rules for specific topics: (name, pattern, index of FAQ answer)
INTENT_RULES = [
    ("hours",       re.compile(r"\b(hours?|open|opening|timings?|schedule|working time|operat\w*)\b"), 0),
    ("submission",  re.compile(r"\b(submit|submission|github|repo(sitory)?|upload|project)\b"), 1),
    ("certificate", re.compile(r"\b(certificate|certification|credential|verif\w*|qr)\b"), 2),
]

# Patterns for "help" and "thanks"
HELP_PATTERN = re.compile(r"\b(help|what can you do|options|menu)\b")
THANKS_PATTERN = re.compile(r"\b(thanks?|thank you|thx|appreciate)\b")

# Replies when the bot doesn't understand
FALLBACKS = [
    "Sorry, I didn't quite get that. Try asking about our hours, project submission or certificates.",
    "I'm not sure how to answer that yet. Type 'help' to see what I can do.",
]


def normalize(text):
    """Make text lowercase and remove punctuation so matching is easier."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def keywords(text):
    """Return the meaningful words in a sentence (skips stop words)."""
    return {w for w in normalize(text).split() if w not in STOP_WORDS}


def load_data(path=DATA_FILE):
    """Load the FAQ file. Exit with a message if it's missing or broken."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        greetings = [normalize(g) for g in data["greetings"]]
        faqs = data["faqs"]

        # Make sure every FAQ has the keys we need
        for item in faqs:
            item["question"], item["answer"]

        return greetings, faqs

    except FileNotFoundError:
        sys.exit(f"Error: data file not found: {path}")
    except (json.JSONDecodeError, KeyError, TypeError):
        sys.exit("Error: the FAQ JSON file is invalid (needs 'greetings' and 'faqs').")


def is_greeting(text, greetings):
    """Check if the message starts with one of the known greetings."""
    return any(text == g or text.startswith(g + " ") for g in greetings)


def find_answers(text, faqs):
    """Return every answer that matches the user's message (no duplicates)."""
    answers = []

    def add(ans):
        if ans not in answers:
            answers.append(ans)

    # 1. Check the regex rules
    for _, pattern, index in INTENT_RULES:
        if pattern.search(text) and index < len(faqs):
            add(faqs[index]["answer"])

    # 2. Check keyword overlap with every FAQ question
    user_kw = keywords(text)
    for item in faqs:
        q_kw = keywords(item["question"])
        if q_kw and len(user_kw & q_kw) / len(q_kw) >= CONFIDENCE_THRESHOLD:
            add(item["answer"])

    return answers


def bot_say(message):
    """Print a message as the bot."""
    print(f"Bot: {message}")


def chat():
    """Main chat loop."""
    greetings, faqs = load_data()
    state = "GREETING"
    fallback_count = 0

    bot_say("Hello! I'm the Datheon support assistant. Ask me about our hours, "
            "project submission or certificates. (Type 'bye' to exit.)")

    while state != "EXIT":
        # Read input safely (handle Ctrl+C and Ctrl+D)
        try:
            raw = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            bot_say("Goodbye!")
            break

        text = normalize(raw)

        # Ignore empty messages
        if not text:
            bot_say("Please type a question.")
            continue

        # 1. Exit if the user says bye/exit/quit
        if set(text.split()) & EXIT_WORDS and len(text.split()) <= 3:
            bot_say("Thanks for chatting. Goodbye!")
            state = "EXIT"

        # 2. First message is a greeting
        elif is_greeting(text, greetings) and state == "GREETING":
            bot_say("Hi there! How can I help you today?")
            state = "INTENT"

        # 3. User asked for help
        elif HELP_PATTERN.search(text):
            bot_say("I can answer questions about:\n"
                    + "\n".join(f"   - {f['question']}" for f in faqs))
            state = "INTENT"

        # 4. Otherwise, try to find answers
        else:
            state = "INTENT"
            answers = find_answers(text, faqs)

            if answers:
                fallback_count = 0
                bot_say("\n     ".join(answers))

                if THANKS_PATTERN.search(text):
                    bot_say("You're welcome!")

                state = "RESOLUTION"
                bot_say("Anything else I can help with?")

            elif THANKS_PATTERN.search(text):
                bot_say("You're welcome! Anything else?")

            else:
                # No match — use a fallback reply (alternate between them)
                bot_say(FALLBACKS[fallback_count % len(FALLBACKS)])
                fallback_count += 1


if __name__ == "__main__":
    chat()
