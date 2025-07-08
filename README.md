# HanabiAnalysis

For my senior project, I independently developed a Python script that analyzed log files from 'Hanabi' games played between a human and three different AI types. While my professor provided the overall direction for the project, I wrote the code myself with minimal assistance. My script visualized behavioral differences between the AI types using bar graphs generated with Python’s matplotlib library. You can see the results of my analysis here:

📄 [Read the AI Behavior Analysis Report](./hanabi-analysis-results.pdf)

Directions for running my project:

1. Have hanabi game logs in a directory called "logs"

2. Have HanabiAnalysis.py and DeckRandomizer.py in the same directory "logs" is located

3. Run DeckRandomizer.py on python 2.7 to make a randomized deck + starting hands. Files will be placed into a directory called "decks".

4. Run HanabiAnalyzer.py using python versions 3.0 and up. Each log file should have a matching deck file created by DeckRandomizer.py

5. Pick 3 AI's to analyze after executing the code separated by space e.g. intentional outer full

6. Pick which difficulty you would like to observe, beg or exp


