# Telegram bot helping to win at Wordle puzzles (https://www.nytimes.com/games/wordle/index.html)  

## Deployment:
- Clone/download GitHub repo.
- Create and activate virtual environment in the repo directory.
- Install dependencies from requirements.txt into the activated virtual environment.
- Rename the ".env.example" to ".env" and fill it with values.
- Run "python main.py" (Windows, Linux) or "python3 main.py" (Mac) in the terminal with the activated virtual environment.

That's it, the bot is up and running!

## How to play:

Example of user input (one word at a time):

    Fundi?
    ra?the

This means:
- Letter 'f' was guessed and it's in the 1st position
(are in capital case).

- Letters 'a' and 'i' are present in the solution,
but not in the 2nd and 5th position, respectively
(are followed by question mark).

- Letters
'u', 'n', 'd', 'r', 't', 'h' and 'e'
are missing from the solution (are in lower case).