# Telegram bot helping to win at Wordle puzzles (https://www.nytimes.com/games/wordle/index.html)  

## Deployment:
- Clone/download GitHub repo.
- Create and activate virtual environment in the repo directory.
- Install dependencies from requirements.txt into the activated virtual environment.
- Rename the ".env.example" to ".env" and fill it with values.
- Run "python main.py" (Windows, Linux) or "python3 main.py" (Mac) in the terminal with the activated virtual environment.

That's it, the bot is up and running!

## HOW TO USE THE WORDLE BOT:

Example of user input:

    Fundi? ra?the

This means:
- Two attempts were made: words 'fundi' and 'rathe'.

- Letters in capital case designate the letters 
revealed in their correct positions. 
In this example, letter 'f' is in the 1st position in the solution.

- Letters followed by '?' are revealed in incorrect positions. 
In the example letters 'i' and 'a' are present in the solution,
but not in the 5th and 2nd positions, respectively.

- All the other letters, that are in the lower case and not followed by '?', 
are missing from the solution.
In the example, it's letters 'u', 'n', 'd', 'r', 't', 'h' and 'e'.