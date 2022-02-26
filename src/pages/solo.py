"""
Functions and other code belonging to the solo dame mode
"""


# AI difficult mode
def ai_mode(table, players_avatar):
    player1 = players_avatar[0]
    player2 = players_avatar[1]
    bestScore = float('-inf')  # negative infinity
    move = []

    for l in range(3):
        for c in range(3):
            # Is the spot available?
            if (table[l][c] == 0):
                table[l][c] = player2
                score = minimax(table, players_avatar, 0, False)
                #score = 1
                table[l][c] = 0
                if score > bestScore:
                    bestScore = score
                    move = [l, c]

    return move

#         X, O , tie
scores = {'X': -1, 'O': 1, 'tie': 0}

# Minimax AI function, to cycle all posibillities
def minimax(table, players_avatar, depth, isMaximizing):
    result = ai_winner()

    if result != None:
        return scores[result]

    player1 = players_avatar[0]
    player2 = players_avatar[1]

    if isMaximizing:
        bestScore = float('-inf')  # negative infinity
        for l in range(3):
            for c in range(3):
                # Is the spot available?
                if table[l][c] == 0:
                    table[l][c] = player2  # AI
                    score = minimax(depth + 1, False)  # call minimax recusively
                    table[l][c] = 0
                    bestScore = max(score, bestScore)  # find the best spot

        return bestScore  # return the best spot
    else:
        bestScore = float('inf')  # negative infinity
        for l in range(3):
            for c in range(3):
                # Is the spot available?
                if table[l][c] == 0:
                    table[l][c] = player1
                    score = minimax(depth + 1, True)  # call minimax recusively
                    table[l][c] = 0
                    bestScore = min(score, bestScore)  # find the best spot

        return bestScore # return the best spot

def ai_winner(table):
    winner = None

    # horizontal
    for l in range(3):
        if (table[l][0] == table[l][1] == table[l][2]) and table[l][0] != 0:
            winner = table[l][0]

    # Vertical
    for c in range(3):
        if (table[0][c] == table[1][c] == table[2][c]) and table[0][c] != 0:
            winner = table[0][c]

    # Diagonal
    if (table[0][0] == table[1][1] == table[2][2]) and table[0][0] != 0:
        winner = table[0][0]
    
    if (table[2][0] == table[1][1] == table[0][2]) and table[2][0] != 0:
        winner = table[2][0]

    openSpots = 0
    for l in range(3):
            for c in range(3):
                if (table[l][c] == 0):
                    openSpots += 1
        
    if (winner == None and openSpots == 0):
        return 'tie'
    else:
        return winner
