import random
import sys
import string
import colorama
from colorama import Fore
from colorama import Style
colorama.init(autoreset=True)

"""Nested dictionaries containing various levels of difficulty. Each dictionary contains the x and y axis of the game-board and the number of 
mines that will populate the grid. This is based on the level of difficulty the player would like to play"""
difficulty_dictionaries = {
    1 : {
        "difficulty": "Beginner",
        "x_axis": 8, 
        "y_axis": 8, 
        "mine_no": 10
    },
    2 : {
        "difficulty": "Intermediate",
        "x_axis": 16, 
        "y_axis": 16, 
        "mine_no": 40
    },
    3 : {
        "difficulty": "Expert",
        "x_axis": 26, 
        "y_axis": 16, 
        "mine_no": 90
    }
}   

   #String of uppercase letters to use at the top of the player board.
''' Empty lists to be filled with: 
    co-ordinates on the hidden-board that have been revealed during game play; 
    co-ordinates that the player has flagged as mines; co-ordinates of mines'''
checked_h_co_ords = []
flagged_co_ords = []
mines_lst = [] 
play = True

def set_difficulty():
    """Asks the user to select the difficultly level they would like to play and returns the dictionary of the corresponding difficulty. 
    This dictionary is used to set the player-board and hidden-board"""
    print ("Please select difficulty level by entering either 1, 2 or 3 based on the corresponding difficulty")
    #for loop to cycle through dictionaries 
    for x in range(1,len(difficulty_dictionaries)+1):
        print(f"""{x}. {difficulty_dictionaries[x]['difficulty']}: {difficulty_dictionaries[x]['x_axis']}x{difficulty_dictionaries[x]['y_axis']} grid, {difficulty_dictionaries[x]['mine_no']} mines""")
    while True: #An infinite loop to ensure valid input - this will only end when the input meets the specified criteria
        try: 
            diff_input = int(input())
            if diff_input >= 4: #The specified criteria - the input is between 1 and 3 
                print("Please enter a number between 1 and 3")
            else: 
                break
        except ValueError: #If no value is entered or the wrong type is entered
            print("Please enter a valid number between 1 and 3")
    return difficulty_dictionaries[diff_input]

def set_mines_array():
    """Creates a list of unique co-ordinates for the mines to be placed on the hidden-board. 
    Number of mines and x & y ranges are based on the selected difficulty dictionary"""
    while len(mines_lst) < diff_dict["mine_no"]:
        mines_lst.append([random.randint(0, diff_dict["x_axis"] - 1), random.randint(0, diff_dict["y_axis"] - 1)])
        if mines_lst[-1] in mines_lst[0:-1]: #If this co-ordinate is already in the mines_lst then it is removed from the list 
            mines_lst.pop()
    return mines_lst 

def set_h_xr(x_co_ord):
    """Creates the range along the x-axis, of the hidden-board, that other definitions will use to iterate through. 
    The range is dependent on the placement of the co-ordinate along the x-axis"""
    if x_co_ord == 0:
        xr = iter(range(x_co_ord, x_co_ord + 2)) #If the co-ord is against the left edge the then x-axis range is x co-ordinate -> co-ordinate + 1  
    elif x_co_ord == diff_dict["x_axis"] - 1:
        xr = iter(range(x_co_ord - 1, x_co_ord + 1)) #If the co-ord is against the right edge then the x-axis range is x co-ordinate - 1 -> co-ordinate
    else: 
        xr = iter(range(x_co_ord - 1, x_co_ord + 2)) #If the co-ord is away from both edges then the x-axis range is x co-ordinate - 1 -> co-ordinate + 1
    return xr

def set_h_yr(y_co_ord):
    """Creates the range along the y-axis, of the hidden-board, that other definitions will use to iterate through. 
    The range is dependent on the placement of the co-ordinate along the y-axis"""
    if y_co_ord == 0:
        yr = iter(range(y_co_ord, y_co_ord + 2)) #If the co-ord is against the top edge the then y-axis range is y co-ordinate -> co-ordinate + 1 
    elif y_co_ord == diff_dict["y_axis"] - 1:
        yr = iter(range(y_co_ord - 1, y_co_ord + 1)) #If the co-ord is against the bottom edge then the y-axis range is y co-ordinate - 1 -> co-ordinate
    else: 
        yr = iter(range(y_co_ord - 1, y_co_ord + 2)) #If the co-ord is away from both edges then the y-axis range is y co-ordinate - 1 -> co-ordinate + 1
    return yr

def set_p_axis_ranges(h_co_ord, p_co_ord): 
    """Sets the initial points of the x & y-axies ranges, of the player board, that other definitions will use to iterate through. 
    The range is dependent on the placement of the co-ordinate along the x & y-axies"""
    p_x = p_co_ord[0]-2 if h_co_ord[0] == 0 else p_co_ord[0] - 4
    p_y = p_co_ord[1]-2 if h_co_ord[1] == 0 else p_co_ord[1] - 4
    return (p_x, p_y)

def set_hidden_board():
    """Creates the hidden-board that contains the locations of the mines, as well as the values that sit around the mines, to 
    indicate if a mine is near"""
    hidden_board = init_h_board() #Creates a hidden board filled with 0s based on the x & y ranges from the difficulty dictionary
    hidden_board = set_h_board_mines(hidden_board) #Places the mines at the co-ordinates specified in `mines_lst`
    hidden_board = set_h_board_values(hidden_board) #Sets the counters for the squares around the mines
    return hidden_board

def init_h_board():
    """Creates a hidden-board filled with 0s based on the x & y ranges from the selected difficulty dictionary
    ie 
    0000000
    0000000
    0000000
    0000000
    """
    hidden_board = []
    for set_hidden_y in range(diff_dict["y_axis"]):
        hidden_board.append([]) #Adds a new line for each row along the y-axis
        for set_hidden_x in range(diff_dict["x_axis"]): 
            hidden_board[set_hidden_y].append(0) #Adds a 0 for each square along the x-axis
    return hidden_board

def set_h_board_mines(hidden_board):
    """Populates the board with the mines at the co-ordinates in `mines_lst`"""
    for mines in mines_lst:
        hidden_board[mines[1]][mines[0]] = "x"
    return hidden_board

def set_h_board_values(hidden_board):
    """Increments counters in the squares around the mines to show how many mines are in the immediate squares around a given square
    ie 
    111112x
    2x21x21
    2x31210
    111x100
    """
    for mines in mines_lst: #For each co-ordinate that contains a mine
        for x in set_h_xr(mines[0]): #Iiterates through the x-axis range set in set_h_xr()     
            for y in set_h_yr(mines[1]): #Iterates through the y-axis range set in set_h_yr()
                if hidden_board[y][x] =="x": #If the square around the selected mine also contains a mine do not change that square
                    continue
                hidden_board[y][x] += 1 #Add 1 to the counter within the sqaure 
    return hidden_board

def set_user_board():
    """Sets the `grid` list, which contains all the information to print the player-board. It is initially an empty board that prints as below
    + - + - + - + - + 
    |   |   |   |   | 
    + - + - + - + - + 
    |   |   |   |   |   
    + - + - + - + - + 
    As squares get clicked on by the player, the `grid` list is updated with the corresponding hidden-board values, which prints as below
    + - + - + - + - + 
    | 2 |   | 2 | 1 | 
    + - + - + - + - + 
    | 2 |   | 3 | 1 |   
    + - + - + - + - + 
    """
    grid = [' ']
    for set_x in range(diff_dict["x_axis"]):
        grid.append(ALPHABET[set_x]) #Sets the alphabet to sit at the top of the board, as a grid reference, which will be used to select squares (eg A5)
    grid[0] = (" ".join(grid)) #Code to concatinate the alphabet into one string with whitespace 
    del grid[1:] #

    grid.append(" " + "+" + ("-+")*(diff_dict["x_axis"]))
    for set_y in range(diff_dict["y_axis"]):
        grid.append(" |" + (" " + "|")*diff_dict["x_axis"]) 
        grid.append(" +" + ("-+")*diff_dict["x_axis"]) #Code to fill `grid` with the strings for the player board
    return(grid)

def print_grid():
    """Prints the player-board to the terminal. This is called at the beginning of play, and then after each time the player enters a square 
    selection. The player-board will update, with the values of the hidden-board, after each selection. The revealed different numbers 
    are printed in different colours to aid with player readability
    """
    for number, row in enumerate(grid, 0): #Shifts through rows instead of items
        if number % 2 == 1 or number == 0: #Only for rows that contain squares 
            print("  ", end='') #Numbers are printed in white, down the side of the board, as a grid reference
        else:
            print(f"{Fore.WHITE + Style.BRIGHT}{number//2} ", end='') if number//2 < 10 else print(f"{Fore.WHITE + Style.BRIGHT}{number//2}", end='') 
            #Leaves a double space for numbers below 10 and a single space for numbers above 10
        for item in row:
            if item in '+-|':  
                colour = Fore.WHITE + Style.BRIGHT #Prints the grid in white
            elif item == '1':
                colour = Fore.BLUE + Style.BRIGHT #Prints all numbers, within the player board, in different colours    
            elif item == '2': 
                colour = Fore.GREEN + Style.BRIGHT
            elif item == '3': 
                colour = Fore.RED + Style.BRIGHT
            elif item == '4': 
                colour = Fore.YELLOW + Style.BRIGHT
            elif item == '5': 
                colour = Fore.MAGENTA + Style.BRIGHT
            elif item == '6':
                colour = Fore.CYAN + Style.BRIGHT   
            elif item == '7': 
                colour = Fore.BLUE + Style.BRIGHT
            elif item == '8': 
                colour = Fore.GREEN + Style.BRIGHT                       
            else:
                colour = Fore.WHITE + Style.BRIGHT
            print(f"{colour}{item}", end=' ') # `end=' '`` prints without a new line 
        print() # go to next line
    return

def click_square():
    """Asks the user for input on which square they are selecting, ensuring that input is valid and determining
    whether the user would like to flag the square as containing a mine"""
    print("Please enter grid co-ordinates. \nIf you would like to flag a mine please type fl before entering your co-ordinates")
    while True: #A loop to ensure that the user enters a valid co-ordinate or flag + co_ordinate 
        flag = False 
        square = input().upper() #Full input is capitalised to account for if a mine is flagged or not
        if len(square) > 3: #If the user wants to flag a mine then the input will be 4 or 5 characters long
            flag = square[:2] #The input is split to keep `square` as 2 characters
            square = square[2:]
        if flag and flag != "FL" or len(square) not in [2, 3] or square[0] not in ALPHABET or not square[1:].isdigit(): #If the user enters anything other than fl while trying to flag a mine
            if flag and flag != "FL":#if square doesn't contain exactly 2 charaters, if the first character doesn't match an element in ALPHABET, or the second character isn't a number
                print("If you would like to flag a square as a mine please type 'fl' before you enter your co-ordinates.")
            if len(square) not in [2, 3] or square[0] not in ALPHABET or not square[1:].isdigit():
                print("Please enter grid co-ordinates in the format letter-number (eg b7).")
        else: break 
    if flag: #If flag is truthy then the user must want to flag the square 
        flag_square(square) #If the user wants to flag the selected square then flag_sqare() is called and fed the co-ordinates
    else:
        test_square(square) #If the user is not flagging a mine then test_square() is called and fed the co-ordinates
    return 

def board_callup(square_x, square_y):
    """Each time the user clicks a new square, a list is created containing the co-ordinates of the square on the player-board as well as the 
    corresponding co-ordinates of the hidden-board. A counter is initialised that reflects how many co-ordinates are in the queue to be checked.
    For squares that contian a 0, on the hidden-board, all the squares around them need to be revealed therefore the co-ordinates of those sqaures
    will be added to the list and the counter will be incremented"""
    co_ord_no = 1 #A counter. Each time a new square is selected by the user this should reset to 1
    hidden_x = ALPHABET.index(square_x) #The index postion of the letter part of the co-ordinate, within ALPHABET, matches the hidden grid x position
    hidden_y = square_y - 1 #The number part of the co-ordinates, entered by the user minus 1, corresponds to the hidden grid y position 
    player_x = grid[0].index(square_x) #The index postition of the letter part of the co-ordinate, within grid[0] (the alphabet with " " between letters), matches the index of the player grid x position
    player_y = square_y*2 #The number part of the co-ordinates, entered by the user times by 2, corresponds to the player grid y position
    return [co_ord_no, hidden_x, hidden_y, player_x, player_y] #Counter, and both hidden and player x & y co-ordinates, are returned as a list

def test_square(square):
    """Function for handling game play. Both the hidden and player x & y co-ordinates are spliced out from the list generated in `boad_callup()` into
    separate hidden and player co-ordinates lists. `h_co_ords` is used to determine what value on the hidden-board corresponds to the selected 
    sqaure. If this is a mine then the game is lost and the script is exited. If this is not a mine then the hidden-board value is inserted into the 
    `grid` list, in the corresponding player-board square. If the hidden-board value is a 0 then all the squares around that 
    square are also checked. The hidden-board co-ordinates are added to `checked_h_co_ords` to keep track of all checked squares."""
    init_co_ords = board_callup(square[0],int(square[1:])) #Hidden co-ordinates, and corresponding player board co-ordinates, are found
    h_co_ord = init_co_ords[1:3]
    p_co_ord = init_co_ords[3:]
    
    if hidden_board[h_co_ord[1]][h_co_ord[0]] == "x": #If the user has clicked on a square that contains a mine then the game is lost
        game_interaction(2)
        sys.exit()
    elif hidden_board[h_co_ord[1]][h_co_ord[0]] == "$": #If the user has flagged a square as a mine then the program should leave this flag in place
        pass
    else:
        grid[p_co_ord[1]] = (grid[p_co_ord[1]][:p_co_ord[0]] + str(hidden_board[h_co_ord[1]][h_co_ord[0]]) + grid[p_co_ord[1]][p_co_ord[0] + 1:])
        #Player board y position is used to find the correct list within `grid` to insert the corresponding hidden board value. This list is 
        #spliced at the point of the player board x postion and the hidden board value is inserted
        checked_h_co_ords.append(str(h_co_ord[0]) + ", " + str(h_co_ord[1])) #The hidden board co-ordinates corresponding to the selected square are appended to `checked_h_co_ords`

        if hidden_board[h_co_ord[1]][h_co_ord[0]] == 0:
            while init_co_ords[0] != 0: #The loop keeps running while the counter within `init_co_ord` hasn't reached 0
                init_co_ords = turn_3x3(init_co_ords)
    return 

def turn_3x3(grid_co_ords):
    """Game play for when the user selects a grid with no mines nearby. All squares around it are also revealed until squares with mines nearby
    are revealed eg
    + - + - + - + - + - + 
    | 2 | 2 | 0 | 1 |   |
    + - + - + - + - + - +
    | 2 | 0 | 0 | 1 |   |
    + - + - + - + - + - +
    `grid_co_ords` is used to store all the player-board co-ordinates that are to be checked and their corresponding hidden-board co-ordinates.
    The first index of the list contains a counter of the number of squares that are to be checked. As these co-ordinates are checked they 
    are removed from the list and the counter is decremented. All checked co-ordinates are appended to checked_h_co_ords"""

    h_co_ord = grid_co_ords[1:3] #The first co-ordinates in line (after the counter) are the hidden-board co-ordinates 
    p_co_ord = grid_co_ords[grid_co_ords[0]*2 + 1:grid_co_ords[0]*2 + 3] #The counter is used as a multiplier to select the next player co-ordinates
    
    del_sq_indices = [1, 2, grid_co_ords[0]*2 + 1, grid_co_ords[0]*2 + 2] #The indices of these co-ordinates are then added to a list
    for index in sorted(del_sq_indices, reverse = True): #reversed, so that it doesn't change the remaining indices as an index is deleted 
        del grid_co_ords[index] #All of the indices are deleted

    grid_co_ords[0] -= 1 #and the counter is decremented

    p_axis_ranges = set_p_axis_ranges(h_co_ord, p_co_ord) #The initial player co-ordinates along the x & y - axies are set  
    h_xr = set_h_xr(h_co_ord[0]) #The hidden co-ordinate sets the range of the x-axis
    p_x = p_axis_ranges[0] #The initial player-board x-axis co-ordinate that is to be incremented through
    for h_x in h_xr: #As the hidden-board co-ordinates increment through their range 
        p_x += 2 #then the player-board co-ordinates increment by 2 to take into account the grid
        h_yr = set_h_yr(h_co_ord[1]) #The same process to set the co-ordinates along the x-axis is completed for the y-axis
        p_y = p_axis_ranges[1]
        for h_y in h_yr:
            checked = False #Each time a new co-ordinate is selected, `checked` is set to False
            p_y += 2
            if h_x == h_co_ord[0] and h_y == h_co_ord[1]: #Skips turning the centre square as this is done in previous function and doesn't need repeating
                continue
            if grid[p_y][p_x] == "$": #If the user has flagged a square that isn't a mine, the program should leave this flag in place
                continue
            else:
                for co_ord in checked_h_co_ords: #Iterates through all the co-ordinates in `checked_h_co_ords`
                    if str(h_x) + ", " + str(h_y) == co_ord: #If the string of the current co-ordinate matches any in `checked_h_co_ords`
                        checked = True #`checked` is set to True 
                if checked: #This is done so that the following code within `else` isn't executed for all co-ordinatess in `checked_h_co-ords`
                    continue
                else:
                    grid[p_y] = (grid[p_y][:p_x] + str(hidden_board[h_y][h_x]) + grid[p_y][p_x + 1:])  
                    #Player-board y-position is used to find the correct list within `grid` to insert the corresponding hidden-board value. 
                    # This list is spliced at the point of the player-board x-postion and the hidden-board value is inserted
                    checked_h_co_ords.append(str(h_x) + ", " + str(h_y)) #The hidden-board co-ordinates corresponding to the selected square are appended to `checked_h_co_ords`
                    
                    if hidden_board[h_y][h_x] == 0: #If the current co-ordinate contains a 0
                        grid_co_ords.insert(grid_co_ords[0]*2 + 1, h_x) #the hidden-board x-co-ordinate is inserted, using the counter of co-ordinates currently in `grid_co_ords` as a multipler for the index
                        grid_co_ords.insert(grid_co_ords[0]*2 + 2, h_y) #the hidden-board y-co-ordinate is inserted, using the counter of co-ordinates currently in `grid_co_ords` as a multipler for the index
                        grid_co_ords.append(p_x) #the player-board x-co-ordinate appended
                        grid_co_ords.append(p_y) #the player-board y-co-ordinate appended
                        grid_co_ords[0] += 1 #the counter of co-ordinates to be checked is incremented by 1 
    return(grid_co_ords)

def flag_square(square):
    """Flags an individual square as a potential mine. A square that is flagged as a mine will be updated with a '$' """
    init_co_ords = board_callup(square[0],int(square[1:])) #Hidden-board, and corresponding player-board, co-ordinates are found
    h_co_ord = init_co_ords[1:3]
    p_co_ord = init_co_ords[3:]
    grid[p_co_ord[1]] = (grid[p_co_ord[1]][:p_co_ord[0]] + "$" + grid[p_co_ord[1]][p_co_ord[0] + 1:]) #A '$' marker is entered into the appropriate position within `grid`
    flagged_co_ords.append(h_co_ord) #The hidden-board co-ordinates are added to `flagged_co_ords`
    return

def game_interaction(game_flow):
    """"""
    if game_flow == 1:
        print ("*Welcome to Minesweeper! Where the aim of the game is to reveal all the squares while avoidingcmd all of the hidden mines!*\n*Click on a sqaure by typing in its co_ordinates (eg a5) and pressing enter*\n*This will reveal if there is a mine in that location or in the sqaures around it*\n*If a revealed square has a number in it then this shows how many mines are in the squares around that square*\n*You can flag the squares where you believe there to be a mine by typing in 'fl' before the co-ordinate (eg flh3)\n*If you click on a mine then the game is lost. The game is won when all of the mines are flagged or all of the squares not containing a mine are revealed*\n***Good Luck!!***")
    if game_flow == 2:
        print(f"Ouch! You found a mine! {Style.BRIGHT}GAME OVER!!")
    if game_flow == 3:
        print(f"Congratulations!! You {Style.BRIGHT}WIN!!")
    return


"""Game initialisation: Prints game instructions; asks the user for the difficulty level; initialises the empty player-grid; sets the location
of the mines; creates the hidden-board of mines and corresponding proximity values; and prints the empty player-grid"""
game_interaction(1)
diff_dict = set_difficulty()
grid = set_user_board()
mines_lst = set_mines_array()
hidden_board = set_hidden_board()
print_grid()

"""The game will contine until the co-ordinates in `flagged_co-ords` matches those in `mines_lst` or the number of elements in `checked_h_co_ords` 
is equal to the number of non-mine squares on the board. Game play can also be ended early by clicking on a mine within `click_square`"""
while sorted(flagged_co_ords) != sorted(mines_lst) and len(checked_h_co_ords) != diff_dict["x_axis"]*diff_dict["y_axis"] - diff_dict["mine_no"]:
    click_square() #The user is asked to input their square choice, the player-board is updated with the data from the hidden-board
    print_grid() #The updated player-grid is printed
game_interaction(3) #If the player makes it out of the while loop then they have won! 
