import os
import glob
import matplotlib.pyplot as plt
import numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def clean(cardString, deck):
    unwanted = ['[',']',"'",]

    for i in unwanted:      
        cardString = cardString.replace(i,"")
    cardString = cardString.replace("),", ")").replace(", ",",")

    for elements in cardString.split():
        a, b = elements.strip('()').split(',')
        deck.append((a, b))

    return deck

def unzip(cards):
    cards = list(zip(*cards))
    ranks = list(cards[1])
    colors = list(cards[0])
    ranks = [int(items) for items in ranks]
    colors = [int(items) for items in colors]

    return colors, ranks

def hint(hand, hintArray, match, hintType):
    if hintType == 1:
        #rank rows go from 0 - 4, not 1 - 5
        match -= 1
    #traverse through hand
    for cardIndex, cardValue in enumerate(hand):
        if hintType == 1:
            cardValue -= 1
        if cardValue == match:
            for row in range(0,5):
                #exclude row(color/rank) we are on
                if row != match:
                    hintArray[row][cardIndex] = 0
        else:
            hintArray[match][cardIndex] = 0
    return hintArray

def countHints(hintArray, index):
    hints = 0
    for rows in hintArray:
        if rows[index] == 0:
            hints += 1
    return hints

#when AI hints player
def updatePlayableCards():
    #board index(i) represents color, values represent rank
    for i, rank in enumerate(board):
        #find if color exists in player hand
        for k, color in enumerate(playerColors):
            if i == color:
                #if card is next in order
                if rank == playerRanks[k] - 1:
                    #set playableCard value to confidence of card at index k
                    playableCards[k] = countHints(playerColorHints, k)
                    playableCards[k] += countHints(playerRankHints, k)

    return playableCards

#a function called when a player hints or discards
#add +0/+1 to statistic, set playable cards to -1
def countCards(playableCards, didNotPlay):
    counted = []
    for confidence in playableCards:
        #do not want to count a the same confidence twice e.g. [5,5,5,-1,-1], +0/+1 goes into 5 ONE time
        if confidence not in counted:
            #+1 to denominator
            didNotPlay[confidence] += 1
            counted.append(confidence)
        #do not count index again until new info is found
        confidence = -1

    return playableCards, didNotPlay

def discard(handColors, handRanks, deckColors, deckRanks, colorHints, rankHints, index):
    #discard a card
    del handColors[index]
    del handRanks[index]

    #append from deck if not empty
    if len(deckColors) != 0 and len(deckRanks) != 0:
        handColors.append(deckColors[0])
        handRanks.append(deckRanks[0])
        del deckColors[0]
        del deckRanks[0]
   
    #update hints
    #for each row...
    for colors in colorHints:
        del colors[index]
        colors.append(1)
    for ranks in rankHints:
        del ranks[index]
        ranks.append(1)
       
    return handColors, handRanks, deckColors, deckRanks, colorHints, rankHints
if __name__ == "__main__":

    AIData = {}
    playerData = {}

    AIs = []
    beginnerIDs = []
    experiencedIDs = []

    difficulties =  ["any", "beg", "exp"]

    for difficulty in difficulties:
        playerData[f"{difficulty}"] = {}

        #order for player data moves list is hints, plays, discards, turns
        playerData[f"{difficulty}"]["moves"] = [0, 0, 0, 0]
        playerData[f"{difficulty}"]["colorHints"] = [0, 0, 0, 0, 0]
        playerData[f"{difficulty}"]["rankHints"] = [0, 0, 0, 0, 0]
        playerData[f"{difficulty}"]["combinedHints"] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        playerData[f"{difficulty}"]["couldPlay"] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        playerData[f"{difficulty}"]["didNotPlay"] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
 
    #check for survey files
    for filename in glob.glob('logs\survey*.log'):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:
                for line in f:
                    if "exp " in line:
                        exp = line.split(" ")
                        exp = exp[1]
                if exp == "new\n" or exp == "dabbling\n":
                    beginnerIDs.append(f"game{filename[11:-4]}")
                if exp == "intermediate\n" or exp == "expert\n":
                    experiencedIDs.append(f"game{filename[11:-4]}")
                f.close()
           
    #text file created from log, has same name
    for filename in glob.glob('decks\*.txt'):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:

            content = f.readlines()
       
            playerHand = []
            AIHand = []
            deck = []

            AIHand = clean(content[1], AIHand)
            playerHand = clean(content[2], playerHand)
            deck = clean(content[3], deck)

            playerColors, playerRanks = unzip(playerHand)
            AIColors, AIRanks = unzip(AIHand)
            deckColors, deckRanks = unzip(deck)
            filename = filename[6:]
            temp = filename.split(".")
            filename = temp[0]
           
            #finds matching log file
            path = f"logs\{filename}.log"

            #find AI type
            with open(path, 'r') as f:
                for line in f:
                    if "Treatment" in line:
                        AIType = line.split("'")
                        AIType = AIType[1]
                f.close()

            with open(path, 'r') as f:

                experience = "any"

                playerHints = 0
                playerPlays = 0
                playerDiscards = 0
                playerTurns = 0

                pColorConfidence = [0, 0, 0, 0, 0]
                pRankConfidence = [0, 0, 0, 0, 0]
                pCombinedConfidence = [0, 0, 0, 0, 0, 0, 0, 0, 0]
               
                #numerator
                couldPlay = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                #denominator
                didNotPlay = [0, 0, 0, 0, 0, 0, 0, 0, 0]

                #card is playable if > -1
                #values are how much we know about the playable card
                board = [0, 0, 0, 0, 0]
                playableCards = [-1, -1, -1, -1, -1]

                AIHints = 0
                AIPlays = 0
                AIDiscards = 0
                AITurns = 0
                   
                #confidence level from 0%, 25%, 50%, 75%, 100%
                AIColorConfidence = [0, 0, 0, 0, 0]
                AIRankConfidence = [0, 0, 0, 0, 0]
                AICombinedConfidence = [0, 0, 0, 0, 0, 0, 0, 0, 0]

                #unknown = -1
                #green = 0
                #yellow = 1
                #white = 2
                #blue = 3
                #red = 4

                #each row corresponds to a rank or color
                #columns correspond to the index of card
                playerColorHints = [[1, 1, 1, 1, 1] for i in range(5)]
                playerRankHints = [[1, 1, 1, 1, 1] for i in range(5)]
           
                AIColorHints = [[1, 1, 1, 1, 1] for i in range(5)]
                AIRankHints = [[1, 1, 1, 1, 1] for i in range(5)]

                #goes through each line in log file
                for line in f:
                    if "MOVE" in line:
                        info = line.split(": ")
                        sequence = info[1]
                        #sequence numbers get put into a list
                        sequence = sequence.split()

                        for index in range(6):
                            if sequence[index] == "None" or sequence[index] == "None\n":
                                sequence[index] = -1
                            else:
                                sequence[index] = int(sequence[index])
                   
                        #if players turn
                        if sequence[0] == 1:
                            playerTurns += 1
                            #player hints color to AI
                            if sequence[1] == 0:
                                playerHints += 1
                                AIColorHints = hint(AIColors, AIColorHints, sequence[4], 0)
                                playableCards, didNotPlay = countCards(playableCards, didNotPlay)
                               
                            #player hints rank to AI
                            if sequence[1] == 1:
                                playerHints += 1
                                AIRankHints = hint(AIRanks, AIRankHints, sequence[5], 1)  
                                playableCards, didNotPlay = countCards(playableCards, didNotPlay)

                            #play
                            if sequence[1] == 2:
                                playerPlays += 1

                                combined = 0
                                #go through each row of hints
                                temp = countHints(playerColorHints, sequence[2])
                                pColorConfidence[temp] += 1
                                combined += temp

                                temp = countHints(playerRankHints, sequence[2])
                                pRankConfidence[temp] += 1
                                combined += temp

                                pCombinedConfidence[combined] += 1

                                playerColors, playerRanks, deckColors, deckRanks, playerColorHints, playerRankHints = \
                                discard(playerColors, playerRanks, deckColors, deckRanks, playerColorHints, playerRankHints, sequence[2])

                                #if card was playable, add to numerator and denominator (+1/+1)
                                if playableCards[sequence[2]] != -1:
                                    couldPlay[playableCards[sequence[2]]] += 1
                                    didNotPlay[playableCards[sequence[2]]] += 1
                               
                                #delete card we just played from playableCards
                                del playableCards[sequence[2]]
                                playableCards.append(-1)
                       
                            #discard
                            if sequence[1] == 3:
                                playerDiscards += 1
                                playerColors, playerRanks, deckColors, deckRanks, playerColorHints, playerRankHints = \
                                discard(playerColors, playerRanks, deckColors, deckRanks, playerColorHints, playerRankHints, sequence[2])

                                del playableCards[sequence[2]]
                                playableCards.append(-1)
                                #Update playable cards, +0/+1
                                playableCards, didNotPlay = countCards(playableCards, didNotPlay)
                       
                        #AI turn
                        if sequence[0] == 0:
                            AITurns += 1
                       
                            #AI hints color to player
                            if sequence[1] == 0:
                                AIHints += 1
                                playerColorHints = hint(playerColors, playerColorHints, sequence[4], 0)
     
                            playableCards = updatePlayableCards()

                            #AI hints rank to player
                            if sequence[1] == 1:
                                AIHints += 1
                                playerRankHints = hint(playerRanks, playerRankHints, sequence[5], 1)

                            playableCards = updatePlayableCards()

                            #play
                            if sequence[1] == 2:
                                AIPlays += 1

                                #for calculating rank and color hints combined
                                combined = 0
                                #go through each row in hints
                                temp = countHints(AIColorHints, sequence[2])
                                AIColorConfidence[temp] += 1
                                combined += temp

                                temp = countHints(AIRankHints, sequence[2])
                                AIRankConfidence[temp] += 1
                                combined += temp

                                AICombinedConfidence[combined] += 1

                                AIColors, AIRanks, deckColors, deckRanks, AIColorHints, AIRankHints = \
                                discard(AIColors, AIRanks, deckColors, deckRanks, AIColorHints, AIRankHints, sequence[2])
                       
                            #discard
                            if sequence[1] == 3:
                                AIDiscards += 1
                                AIColors, AIRanks, deckColors, deckRanks, AIColorHints, AIRankHints = \
                                discard(AIColors, AIRanks, deckColors, deckRanks, AIColorHints, AIRankHints, sequence[2])

                    if "successfully" in line:
                        #reset board
                        board = []

                        temp = line.lower()
                        #remove characters and spaces from line
                        unwanted = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', " ", "\n", "!"]
                        for i in unwanted:
                            temp = temp.replace(i, "")
                        temp = temp[1:]
                        #create list of cards on board
                        temp = temp.split(",")

                        #update board
                        for items in temp:
                            board.append(int(items))
                           
                    if "Score" in line:
                        score = line.split()
                        score = score[1]

                if AIType not in AIs:
                    #order: hints, plays, discards, turns
                    #totals are initially set to 0
                    AIData[f"{AIType}Moves"] = [0, 0, 0, 0]
                    AIData[f"{AIType}ColorHints"] = [0, 0, 0, 0, 0]
                    AIData[f"{AIType}RankHints"] = [0, 0, 0, 0, 0]
                    AIData[f"{AIType}CombinedHints"] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    AIData[f"{AIType}Moves"][0] += AIHints
                    AIData[f"{AIType}Moves"][1] += AIPlays
                    AIData[f"{AIType}Moves"][2] += AIDiscards
                    AIData[f"{AIType}Moves"][3] += AITurns
                    for index in range (0, 5):
                        AIData[f"{AIType}ColorHints"][index] += AIColorConfidence[index]
                        AIData[f"{AIType}RankHints"][index] += AIRankConfidence[index]
                    for index in range (0, 9):
                        AIData[f"{AIType}CombinedHints"][index] += AICombinedConfidence[index]
                    AIs.append(AIType)
                else:
                    AIData[f"{AIType}Moves"][0] += AIHints
                    AIData[f"{AIType}Moves"][1] += AIPlays
                    AIData[f"{AIType}Moves"][2] += AIDiscards
                    AIData[f"{AIType}Moves"][3] += AITurns
                    for index in range (0, 5):
                        AIData[f"{AIType}ColorHints"][index] += AIColorConfidence[index]
                        AIData[f"{AIType}RankHints"][index] += AIRankConfidence[index]
                    for index in range (0, 9):
                        AIData[f"{AIType}CombinedHints"][index] += AICombinedConfidence[index]

                #any difficulty  
                playerData["any"]["moves"][0] += playerHints
                playerData["any"]["moves"][1] += playerPlays
                playerData["any"]["moves"][2] += playerDiscards
                playerData["any"]["moves"][3] += playerTurns
                for index in range (0, 5):
                    playerData["any"][f"colorHints"][index] += pColorConfidence[index]
                    playerData["any"][f"rankHints"][index] += pRankConfidence[index]
                for index in range (0, 9):
                    playerData["any"]["combinedHints"][index] += pCombinedConfidence[index]
                #did not play statistic
                for index in range (0, 9):
                    playerData["any"]["couldPlay"][index] += couldPlay[index]
                    playerData["any"]["didNotPlay"][index] += didNotPlay[index]
                   
                if filename in beginnerIDs or experiencedIDs:
                    if filename in beginnerIDs:
                        experience = "beg"
                    if filename in experiencedIDs:
                        experience = "exp"
                    playerData[f"{experience}"]["moves"][0] += playerHints
                    playerData[f"{experience}"]["moves"][1] += playerPlays
                    playerData[f"{experience}"]["moves"][2] += playerDiscards
                    playerData[f"{experience}"]["moves"][3] += playerTurns
                    for index in range (0, 5):
                        playerData[f"{experience}"][f"colorHints"][index] += pColorConfidence[index]
                        playerData[f"{experience}"][f"rankHints"][index] += pRankConfidence[index]
                    for index in range (0, 9):
                        playerData[f"{experience}"]["combinedHints"][index] += pCombinedConfidence[index]
                    #did not play statistic
                    for index in range (0, 9):
                        playerData[f"{experience}"]["couldPlay"][index] += couldPlay[index]
                        playerData[f"{experience}"]["didNotPlay"][index] += didNotPlay[index]

                #output statistics of a specific log file into its respective text file
                outFileName = f"results\{filename}.txt"
                outFile = open(outFileName, "w")
                outFile.write(f"\nAIType: {AIType}\n")
                outFile.write(f"Game finished with score of: {score}\n\n")
           
                outFile.write("Player turn percentages...\n")

                outFile.write(f"hints: {playerHints / playerTurns:.2f}\n")
                outFile.write(f"discards: {playerDiscards / playerTurns:.2f}\n")
                outFile.write(f"plays: {playerPlays / playerTurns:.2f}\n")

                if playerPlays > 0:
                    outFile.write("Confidence before playing a card (color): \n")
                    for index in range(0,5):
                        outFile.write(f'{25 * index}%: {pColorConfidence[index] / playerPlays:.2f}\n')

                    outFile.write("Confidence before playing a card (rank): \n")
                    for index in range(0,5):
                        outFile.write(f'{25 * index}%: {pRankConfidence[index] / playerPlays:.2f}\n')

                    outFile.write("Times we \"did the right thing\": \n")
                    for index in range(0,9):
                        if couldPlay[index] == 0 and didNotPlay[index] == 0:
                            outFile.write(f'{.25 * index}: 0.00\n')
                            continue
                        outFile.write(f'{.25 * index}: {couldPlay[index] / didNotPlay[index]:.2f}\n')
           
                outFile.write("\nAI turn percentages...\n")
                outFile.write(f"hints: {AIHints / AITurns:.2f}\n")
                outFile.write(f"discards: {AIDiscards / AITurns:.2f}\n")
                outFile.write(f"plays: {AIPlays / AITurns:.2f}\n")
           
                if AIPlays > 0:
                    outFile.write("Confidence before playing a card (color): \n")
                    for index in range(0,5):
                        outFile.write(f'{25 * index}%: {AIColorConfidence[index] / AIPlays:.2f}\n')

                    outFile.write("Confidence before playing a card (rank): \n")
                    for index in range(0,5):
                        outFile.write(f'{25 * index}%: {AIRankConfidence[index] / AIPlays:.2f}\n')
               
                outFile.close()

   
    #graphs
    chosenAI = []
    choices = input(f"Please choose 3 AI types from the list: {AIs}\n")
    for index in range (0,3):
        chosenAI.append(AIs[int(choices[index * 2]) - 1])

    choices = input("Please enter player difficulty (beg, exp, any): ")
   
    #order: hints, plays, discards, turns
    firstAI = []
    secondAI = []
    thirdAI = []

    hintStats = []
    playStats = []
    discardStats = []

    playerStats = []

    #turns(1) graph
    for index in range(0,3):
        firstAI.append(AIData[f"{chosenAI[0]}Moves"][index] / AIData[f"{chosenAI[0]}Moves"][3])
        secondAI.append(AIData[f"{chosenAI[1]}Moves"][index] / AIData[f"{chosenAI[1]}Moves"][3])
        thirdAI.append(AIData[f"{chosenAI[2]}Moves"][index] / AIData[f"{chosenAI[2]}Moves"][3])

    for index in range(0,3):
        playerStats.append(playerData[f"{choices}"]["moves"][index] / playerData[f"{choices}"]["moves"][3])

    #turns(2) graph
    for index in range(0,3):
        hintStats.append(AIData[f"{chosenAI[index]}Moves"][0] / AIData[f"{chosenAI[index]}Moves"][3])
        playStats.append(AIData[f"{chosenAI[index]}Moves"][1] / AIData[f"{chosenAI[index]}Moves"][3])
        discardStats.append(AIData[f"{chosenAI[index]}Moves"][2] / AIData[f"{chosenAI[index]}Moves"][3])

    hintStats.append(playerData[f"{choices}"]["moves"][0] / playerData[f"{choices}"]["moves"][3])
    playStats.append(playerData[f"{choices}"]["moves"][1] / playerData[f"{choices}"]["moves"][3])
    discardStats.append(playerData[f"{choices}"]["moves"][2] / playerData[f"{choices}"]["moves"][3])

    #hints graphs
    colorHintData = []
    rankHintData = []
    combinedHintData = []
    combinedHintDataPlayer = []
    didTheRightThing = []
    tempList = []

    #add AI color hints to graph
    for i in range (0,3):
        for j in range (0,5):
            tempList.append(AIData[f"{chosenAI[i]}ColorHints"][j] / AIData[f"{chosenAI[i]}Moves"][1])
        colorHintData.append(tempList)
        tempList = []

    #add AI rank hints to graph
    for i in range (0,3):
        for j in range (0,5):
            tempList.append(AIData[f"{chosenAI[i]}RankHints"][j] / AIData[f"{chosenAI[i]}Moves"][1])
        rankHintData.append(tempList)
        tempList = []
   
    #add AI combined hints to graph
    for i in range (0,3):
        for j in range (0, 9):
            tempList.append(AIData[f"{chosenAI[i]}CombinedHints"][j] / AIData[f"{chosenAI[i]}Moves"][1])
        combinedHintData.append(tempList)
        tempList = []

    #add player color hints to graph
    for i in range (0,5):
        tempList.append(playerData[f"{choices}"]["colorHints"][i] / playerData[f"{choices}"]["moves"][1])
    colorHintData.append(tempList)
    tempList = []

    #add player rank hints to graph
    for i in range(0,5):
        tempList.append(playerData[f"{choices}"]["rankHints"][i] / playerData[f"{choices}"]["moves"][1])
    rankHintData.append(tempList)
    tempList = []

    #add player combined hints to graph
    for i in range (0, 9):
        tempList.append(playerData[f"{choices}"]["combinedHints"][i] / playerData[f"{choices}"]["moves"][1])
    combinedHintData.append(tempList)
    tempList = []

    for i in range (0, 9):
        tempList.append(playerData["beg"]["combinedHints"][i] / playerData["beg"]["moves"][1])
    combinedHintDataPlayer.append(tempList)
    tempList = []

    for i in range (0, 9):
        tempList.append(playerData["exp"]["combinedHints"][i] / playerData["exp"]["moves"][1])
    combinedHintDataPlayer.append(tempList)
    tempList = []

    #add did not play stats to graph
    for i in range (0, 9):
        if playerData["beg"]["couldPlay"][i] == 0 and playerData["beg"]["didNotPlay"][i] == 0:
            continue
        tempList.append(playerData["beg"]["couldPlay"][i] / playerData["beg"]["didNotPlay"][i])
    didTheRightThing.append(tempList)
    tempList = []

    for i in range (0, 9):
        if playerData["exp"]["couldPlay"][i] == 0 and playerData["exp"]["didNotPlay"][i] == 0:
            continue
        tempList.append(playerData["exp"]["couldPlay"][i] / playerData["exp"]["didNotPlay"][i])
    didTheRightThing.append(tempList)
    tempList = []

    w = 0.1
    x = ['0', '0.25', '0.5', '0.75', '1']

    bar1 = np.arange(len(x))
    bar2 = [i+w for i in bar1]
    bar3 = [i+w for i in bar2]
    bar4 = [i+w for i in bar3]

    #color hint chart
    plt.bar(bar1, colorHintData[0], w ,label = f"{chosenAI[0]}")
    plt.bar(bar2, colorHintData[1], w ,label = f"{chosenAI[1]}")
    plt.bar(bar3, colorHintData[2], w ,label = f"{chosenAI[2]}")
    plt.bar(bar4, colorHintData[3], w ,label = "Player")

    plt.xlabel("Confidence Levels")
    plt.ylabel("Occurance Percentage")
    plt.title("Different Confidence Levels (Color)")
    plt.xticks(bar1 , x)
    plt.legend()

    plt.savefig(f'graphs\colorHints{choices.capitalize()}.png', dpi=300, bbox_inches='tight')

    plt.clf()

    #rank hint chart
    plt.bar(bar1, rankHintData[0], w ,label = f"{chosenAI[0]}")
    plt.bar(bar2, rankHintData[1], w ,label = f"{chosenAI[1]}")
    plt.bar(bar3, rankHintData[2], w ,label = f"{chosenAI[2]}")
    plt.bar(bar4, rankHintData[3], w ,label = "Player")
       
    plt.xlabel("Confidence Levels")
    plt.ylabel("Occurance Percentage")
    plt.title("Different AI Types Confidence Levels (Rank)")
    plt.xticks(bar1 , x)
    plt.legend()

    plt.savefig(f'graphs\\rankHints{choices.capitalize()}.png', dpi=300, bbox_inches='tight')

    plt.clf()

    x = []
    for i in np.arange (0, 2.25, 0.25):
        x.append(i)

    bar1 = np.arange(len(x))
    bar2 = [i+w for i in bar1]
    bar3 = [i+w for i in bar2]
    bar4 = [i+w for i in bar3]

    plt.bar(bar1, combinedHintData[0], w ,label = f"{chosenAI[0]}")
    plt.bar(bar2, combinedHintData[1], w ,label = f"{chosenAI[1]}")
    plt.bar(bar3, combinedHintData[2], w ,label = f"{chosenAI[2]}")
    plt.bar(bar4, combinedHintData[3], w ,label = "Player")

    plt.xlabel("Confidence Levels")
    plt.ylabel("Occurance Percentage")
    plt.title("Different Confidence Levels")
    plt.xticks(bar1 , x)
    plt.legend()

    plt.savefig(f'graphs\combinedHints{choices.capitalize()}.png', dpi=300, bbox_inches='tight')

    plt.clf()

    bar1 = np.arange(len(x))
    bar2 = [i+w for i in bar1]
    bar3 = [i+w for i in bar2]

    plt.bar(bar1, combinedHintDataPlayer[0], w ,label = "Beginner")
    plt.bar(bar2, combinedHintDataPlayer[1], w ,label = "Experienced")

    plt.xlabel("Confidence Levels")
    plt.ylabel("Occurance Percentage")  
    plt.title("Different Confidence Levels")
    plt.xticks(bar1 , x)
    plt.legend()

    plt.savefig(f'graphs\combinedHintsPlayer.png', dpi=300, bbox_inches='tight')

    plt.clf()

    #statisitic of when cards were not played
    plt.bar(bar1, didTheRightThing[0], w ,label = "Beginner")
    plt.bar(bar2, didTheRightThing[1], w ,label = "Experienced")
       
    plt.xlabel("Confidence Levels")
    plt.ylabel("Occurance Percentage")  
    plt.title("Times We Did the Right Thing")
    plt.xticks(bar1 , x)
    plt.legend()

    plt.savefig(f'graphs\didTheRightThing.png', dpi=300, bbox_inches='tight')

    plt.clf()

    #AI turn chart

    x = ['Hints', 'Plays', 'Discards']

    bar1 = np.arange(len(x))
    bar2 = [i+w for i in bar1]
    bar3 = [i+w for i in bar2]
    bar4 = [i+w for i in bar3]

    plt.bar(bar1, firstAI, w ,label = f"{chosenAI[0]}")
    plt.bar(bar2, secondAI, w ,label = f"{chosenAI[1]}")
    plt.bar(bar3, thirdAI, w ,label = f"{chosenAI[2]}")
    plt.bar(bar4, playerStats, w ,label = "Player")

    plt.xlabel("Turns")
    plt.ylabel("Occurance Percentage")
    plt.title("AI and Player Turns")
    plt.xticks(bar1 , x)
    plt.legend()

    plt.savefig(f'graphs\\turns{choices.capitalize()}(1).png', dpi=300, bbox_inches='tight')

    plt.clf()

    x = [f'{chosenAI[0]}', f'{chosenAI[1]}', f'{chosenAI[2]}', 'Player']

    bar1 = np.arange(len(x))
    bar2 = [i+w for i in bar1]
    bar3 = [i+w for i in bar2]

    plt.bar(bar1, hintStats, w ,label = "Hints")
    plt.bar(bar2, playStats, w ,label = "Plays")
    plt.bar(bar3, discardStats, w ,label = "Discards")

    plt.xlabel("Turns")
    plt.ylabel("Occurance Percentage")
    plt.title("AI and Player Turns")
    plt.xticks(bar1 , x)
    plt.legend()

    plt.savefig(f'graphs\\turns{choices.capitalize()}(2).png', dpi=300, bbox_inches='tight')

    plt.clf()