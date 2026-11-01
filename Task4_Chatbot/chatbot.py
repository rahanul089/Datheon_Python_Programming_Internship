"""
Rule-Based Interactive Terminal Assistant / Chatbot
---------------------------------------------------
- Loads greetings and FAQs from a JSON dataset (sample_faq.json).
- Normalizes input (lowercase, strip punctuation/whitespace).
- Multi-intent recognition: regex rules for business hours, internship
  submission, certificates, thanks and help, plus keyword-overlap matching
  against every FAQ question (with a confidence threshold).
  One message can trigger several intents ("hours and certificate?").
- Conversation state: GREETING -> INTENT -> RESOLUTION -> EXIT
- Fallback replies for unrecognized queries; exit with 'bye', 'exit' or 'quit'.
- Error handling for a missing/invalid JSON file, Ctrl+C and Ctrl+D.
"""

import json
import os
import re
import sys

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_faq.json")
EXIT_WORDS = {"bye", "exit", "quit"}
CONFIDENCE_THRESHOLD = 0.34      # share of a FAQ question's keywords that must match
STOP_WORDS = {"a", "an", "the", "is", "are", "do", "does", "i", "my", "me", "you", "your",
              "we", "our", "to", "of", "for", "in", "on", "at", "and", "or", "what", "when",
              "how", "can", "will", "it", "be", "this", "that", "with", "about", "please"}

# Regex intent rules: (intent name, pattern, answer index in FAQ list or fixed text)
INTENT_RULES = [
    ("hours",       re.compile(r"\b(hours?|open|opening|timings?|schedule|working time|operat\w*)\b"), 0),
    ("submission",  re.compile(r"\b(submit|submission|github|repo(sitory)?|upload|project)\b"), 1),
    ("certificate", re.compile(r"\b(certificate|certification|credential|verif\w*|qr)\b"), 2),
]
HELP_PATTERN = re.compile(r"\b(help|what can you do|options|menu)\b")
THANKS_PATTERN = re.compile(r"\b(thanks?|thank you|thx|appreciate)\b")

FALLBACKS = [
    "Sorry, I didn't quite get that. Try asking about our hours, project submission or certificates.",
    "I'm not sure how to answer that yet. Type 'help' to see what I can do.",
]


def normalize(text):
    """Lowercase, replace punctuation with spaces and collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def keywords(text):
    return {w for w in normalize(text).split() if w not in STOP_WORDS}


def load_data(path=DATA_FILE):
    """Load the FAQ dataset; exit with a friendly message if it is unusable."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        greetings = [normalize(g) for g in data["greetings"]]
        faqs = data["faqs"]
        for item in faqs:
            item["question"], item["answer"]          # validate keys
        return greetings, faqs
    except FileNotFoundError:
        sys.exit(f"Error: data file not found: {path}")
    except (json.JSONDecodeError, KeyError, TypeError):
        sys.exit("Error: the FAQ JSON file is invalid (needs 'greetings' and 'faqs').")


def is_greeting(text, greetings):
    return any(text == g or text.startswith(g + " ") for g in greetings)


def find_answers(text, faqs):
    """Return a list of distinct answers matched by regex rules and keyword overlap."""
    answers = []

    def add(ans):
        if ans not in answers:
            answers.append(ans)

    for _, pattern, index in INTENT_RULES:           # regex-based intents
        if pattern.search(text) and index < len(faqs):
            add(faqs[index]["answer"])

    user_kw = keywords(text)                          # keyword-overlap fallback
    for item in faqs:
        q_kw = keywords(item["question"])
        if q_kw and len(user_kw & q_kw) / len(q_kw) >= CONFIDENCE_THRESHOLD:
            add(item["answer"])
    return answers


def bot_say(message):
    print(f"Bot: {message}")


def chat():
    greetings, faqs = load_data()
    state, fallback_count = "GREETING", 0
    bot_say("Hello! I'm the Datheon support assistant. Ask me about our hours, "
            "project submission or certificates. (Type 'bye' to exit.)")

    while state != "EXIT":
        try:
            raw = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            bot_say("Goodbye!")
            break

        text = normalize(raw)
        if not text:
            bot_say("Please type a question.")
            continue

        if set(text.split()) & EXIT_WORDS and len(text.split()) <= 3:
            bot_say("Thanks for chatting. Goodbye!")
            state = "EXIT"
        elif is_greeting(text, greetings) and state == "GREETING":
            bot_say("Hi there! How can I help you today?")
            state = "INTENT"
        elif HELP_PATTERN.search(text):
            bot_say("I can answer questions about:\n"
                    + "\n".join(f"   - {f['question']}" for f in faqs))
            state = "INTENT"
        else:
            state = "INTENT"
            answers = find_answers(text, faqs)
            if answers:                                # RESOLUTION
                fallback_count = 0
                bot_say("\n     ".join(answers))
                if THANKS_PATTERN.search(text):
                    bot_say("You're welcome!")
                state = "RESOLUTION"
                bot_say("Anything else I can help with?")
            elif THANKS_PATTERN.search(text):
                bot_say("You're welcome! Anything else?")
            else:
                bot_say(FALLBACKS[fallback_count % len(FALLBACKS)])
                fallback_count += 1


if __name__ == "__main__":
    chat()
