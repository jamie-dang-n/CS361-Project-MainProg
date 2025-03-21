# import necessary packages
import requests
import textwrap
import json
import zmq

#CONSTANTS
FIRST_LEVEL_PARAMS = ['index', 'name', 'level', 'url']
SECOND_LEVEL_PARAMS = ['index', 'name', 'url', 'desc', 'higher_level', 'range', 'components', 'material', 'area_of_effect', 'ritual', 'duration', 'concentration', 'casting_time', 'level', 'attack_type', 'damage', 'school', 'classes', 'subclasses', 'url']
DESC_LENGTH = 70

# MAIN Program & Helpers Functions ----------------------------------------------------------------------------
# Prints out the title of the program with a short sentence describing the application
def printTitle():
    print("______ _   _______   _____        _____            _ _ _                 _    ")
    print("|  _  \\ \\ | |  _  \\ |  ___|      /  ___|          | | | |               | |   ")
    print("| | | |  \\| | | | | |___ \\  ___  \\ `--. _ __   ___| | | |__   ___   ___ | | __")
    print("| | | | . ` | | | |     \\ \\/ _ \\  `--. \\ '_ \\ / _ \\ | | '_ \\ / _ \\ / _ \\| |/ /")
    print("| |/ /| |\\  | |/ /  /\\__/ /  __/ /\\__/ / |_) |  __/ | | |_) | (_) | (_) |   < ")
    print("|___/ \\_| \\_/___/   \\____/ \\___| \\____/| .__/ \\___|_|_|_.__/ \\___/ \\___/|_|\\_\\")
    print("                                       | |                                    ")
    print("                                       |_|                                    ")
    print("\nEasily search for DND5e spells for all your campaign needs!")
    print("\nThis application will only run with an active internet connection.")

# Print out main menu options
def printMenuOptions():
    print("\nAPPLICATION FUNCTIONS")
    print("6: Roll a dice (with or without modifiers)")
    print("5: Add a custom spell to Bookmarks/Edit a bookmarked spell")
    print("4: View Bookmarks")
    print("3: Search for a spell with exact spell name.") # (ex. Search for 'shocking grasp', 'fireball', etc.)
    print("2: Search for a spell by a keyword within the spell's name.") # (ex. Searching 'acid' returns all entries with 'acid' associated in the name.)
    print("1: Help Manual.")
    print("0: Quit.\n")

# Get user input for any integer input
def getIntegerInput(prompt, minVal, maxVal):
    userInput = -1
    invalidInput = True
    while (invalidInput):
        try:
            userInput = int(input(prompt))
            if (userInput < minVal or userInput > maxVal):
                print("Invalid Input. Please enter a valid option!")
            else:
                invalidInput = False
        except ValueError:
            print("Invalid Input. Please enter an integer!")
    return userInput

# Option 3 implementation: Search for a spell in the API by spell name 
# (print 1 spell)
# Code citation: Referenced "GeeksForGeeks"
def searchSpellName():
    # API endpoint URL
    url = "https://www.dnd5eapi.co/api/spells/"

    # get user input
    userSpell = input("Enter a spell name: ")

    # format user input into lowercase, dashed form
    userSpell = userSpell.lower()
    userSpell = userSpell.replace(" ", "-")

    # update URL for API call
    url = url + userSpell

    # do an API call to dnd5eapi, given a spell name
    try:
        response = requests.get(url)

        if (response.status_code) == 200:
            spell = response.json()
            return spell
        else:
            print("\nError: Spell not found with response code", response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        # handle network-related errors/exceptions
        print("Error: ", e)
        return None

# Option 2 implementation: search for spells in the API by keyword in spell name 
# (possibly print many spells)
def searchKeyWord(bookmarks):
    matchedIndices = [] # initialize empty array of matched indices
    matchedNames = [] # initialize empty array of matched names
    numMatches = 0

    # API endpoint URL
    url = "https://www.dnd5eapi.co/api/spells/"

    # get user input for key word
    keyWord = input("Enter a key word to search for: ")

    # find all matching keywords
    # format user input into lowercase form
    keyWord = keyWord.lower()
    keyWord = keyWord.replace(" ", "+")

    # Find spells that match the key word in name field
    try:
        allSpellsURL = url + "?"
        currURL = allSpellsURL + "name=" + keyWord
        currResponse = requests.get(currURL)
        if currResponse.status_code == 200:
            matchingSpells = currResponse.json()
            for spell in matchingSpells['results']:
                if spell['index'] not in matchedIndices:
                    # only match spells that have not already been matched
                    matchedIndices.append(spell['index'])
                    matchedNames.append(spell['name'])
                    numMatches += 1
        else:
            print("Error: No response with response code", currResponse.status_code)
    except requests.exceptions.RequestException as e:
        # handle network-related errors/exceptions
        print("Error: ", e)
        return None

    # display the name of every matching spell found
    if numMatches == 0:
        print("\nNo matches were found.")
    else: 
        print("\nMatches were found.")
        printNumberedMatches(matchedNames)

        # give user decision to read more about a spell or return to main menu
        userChoice = subSpellMenu()
        while (userChoice == 1):
            try:
                # Choose a spell to examine further
                spellChoice = getSpellChoice(numMatches, matchedNames)
                try: 
                    # get spell by index
                    spellToPrintURL = url + matchedIndices[spellChoice - 1]
                    spellToPrintResp = requests.get(spellToPrintURL)
                    if spellToPrintResp.status_code == 200:
                        spellToPrint = spellToPrintResp.json()
                        printSpell(spellToPrint)
                        # ask user if they want to add this spell to a bookmarks list
                        addSpell(spellToPrint, bookmarks)
                    else:
                        print("Error: spell could not be displayed.")
                except requests.exceptions.RequestException as e:
                    # handle network-related errors/exceptions
                    print("Error: ", e)
                    return None
                userChoice = subSpellMenu()
            except ValueError:
                print("\nInvalid Input. Please enter an integer!")    

# Get user's spell choice from sub-menu in Option 2
def getSpellChoice(numMatches, matchedNames):
    print("\nSelect a spell from the given indices.")
    printNumberedMatches(matchedNames)
    spellChoiceString = "\nSpell selection [1 to " + str(numMatches) + "]: "
    spellChoice = int(input(spellChoiceString))
    while (spellChoice < 1 or spellChoice > numMatches):
        print("\nInvalid Input. Please enter a valid option!")
        printNumberedMatches(matchedNames)
        spellChoiceString = "\nSpell selection [1 to " + str(numMatches) + "]: "
        spellChoice = int(input(spellChoiceString))
    return spellChoice

# Print out matched spells with indexing for Option 2
def printNumberedMatches(matchedNames):
    i = 1
    for match in matchedNames:
        print(i, ": ", match)
        i += 1
    
# Display spell sub menu options and get user input for sub menu
def subSpellMenu():
    print("\nSPELL OPTIONS")
    print("1: Enter spell index to view more details about that spell")
    print("0: Return to main menu\n")
    userInput = getIntegerInput("Select an option [1 or 0]: ", 0, 1)
    return userInput

# Print a line for ease of reading
def printLine():
    print("-----------------------------------------------------------------------------")

# Option 1: Display help menu
def showHelpMenu():
    print("""Help Manual
          
This program supports searching the DND5e API for particular spells
based on spell name or a particular keyword. In depth descriptions follow.

Option 6: Roll a dice (with or without modifiers)
You can roll a dice with any number of faces between 1 and 10000.
You can also add and subtract modifiers, where the modifier can
take any value between 1 and 10000.

Option 5: Add a custom spell to Bookmarks/Edit a bookmarked spell
This is where you can create a custom spell or edit a spell in your
bookmarks. You have full control over the given fields.
          
Option 4: View Bookmarks
This is where you can quickly access and view your saved spells, 
including spells you've edited/spells that you've custom-made.
          
Option 3: Search for a spell with exact spell name
If the user already knows the name of a particular spell they want
to view the details of, input '3' from the main menu and type in
the name of a spell, like 'Shocking Grasp'. Information about the
spell will appear in the console. 
The console will also prompt you to add the spell to your bookmarks,
where you can refer to them later.
          
Option 2: Search for a spell by a keyword within the spell's name
If you cannot recall the name of a spell, no worries! This option
allows you to find a spell based on a 'key word' that may appear
in the spell's name. Input '2' from the main menu and type in your 
desired key word. The application will search and display any spell 
that has a match to the keyword in the name. For example, searching
'acid' should display any spell whose name has 'acid' in it.
The console will also prompt you to add the spell to your bookmarks,
where you can refer to them later.
NOTE: This search option will take slightly longer than the first,
because you will have to select a spell to examine it further, as opposed
to searching and printing out only 1 spell (as the first option does).
          
Option 1: Help Manual
This is the current option you have chosen. Inputting '1' in the main
menu will always bring you back to this help manual, where you can learn
more about the commands this application allows.""")

# Print select (programmer-specified) data from a single spell
def printSpell(spell):
    printLine()

    print("Name: ", spell['name'])
    spellDesc = textwrap.wrap(spell['desc'][0], width=DESC_LENGTH)

    print("\nDescription: ")
    for line in spellDesc:
        print(line)

    if (spell['higher_level']):
        print("\nHigher level: ")
        levelDesc = textwrap.wrap(spell['higher_level'][0], width=DESC_LENGTH)
        for line in levelDesc:
            print(line)

    print("\nRange: ", spell['range'])
    print("Casting time: ", spell['casting_time'])
    print("Duration: ", spell['duration'])
    print("Level: ", spell['level'])

    if (spell['concentration']):
        print("\nConcentration: Necessary")
    else:
        print("\nConcentration: Not necessary")
    if 'attack_type' in spell:
        print("Attack type: ", spell['attack_type'])
    if ("damage" in spell):
        print("Damage type: ", spell['damage']['damage_type']['name'])
        if 'damage_at_slot_level' in spell['damage']:
            print("\nDamage at slot level:")
            numSlots = 0
            for slot in (spell['damage']['damage_at_slot_level']):
                print("Slot level", 
                        slot, 
                        ":", 
                        spell['damage']['damage_at_slot_level'][slot])
                numSlots += 1
            if numSlots == 0:
                print("No information for damage at slot levels.")
        if 'damage_at_character_level' in spell['damage']:
            print("\nDamage at character level:")
            numLevels = 0
            for level in (spell['damage']['damage_at_character_level']):
                print("Character level ", 
                        level, 
                        ":",
                        spell['damage']['damage_at_character_level'][level])
                numLevels += 1
            if numLevels == 0:
                print("No information for damage at character levels")

    print("\nSchool of Magic: ", spell['school']['name'])
    for spell_class in spell['classes']:
        print("Class(es): ", spell_class['name'])
    printLine()

# Signal all microservices to quit
# Can force terminate in powershell with taskkill /F /IM python.exe
def exitMicroservices():
    # send the exit input to all the microservices
    generateSpell(None, 0, None, None)
    accessBookmarkMods("", "", 0)
    getSortOption(None, 0)
    accessDiceRoller(0, None, None, None)

# -------------------------------------------------------------------------------------------------------------

# MICROSERVICE A ----------------------------------------------------------------------------------------------
# Sort the bookmarks list
def getSortOption(bookmarks, sortChoice):
    # interact with microservice A
    context = zmq.Context()

    # socket to talk to server
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    if (sortChoice == 0):
        # exit the microservice
        exit_message = json.dumps({"end_program": True})
        socket.send_string(exit_message)
        dummy_msg = socket.recv() # receive the sent message so the microservice can actually terminate
    else:
        # form dictionary request
        dict = {
            "sort_by": None,
            "descending": None,
            "class_name": None,
            "bookmarks": True,
            "spell_list": bookmarks
        }
        if (sortChoice == 1):
            dict['sort_by'] = "level"
            print("SORTING TYPE")
            print("2: Sort spells by level descending")
            print("1: Sort spells by level ascending\n")
            sortingType = getIntegerInput("Select an option [1 or 2]: ", 1, 2)
            if (sortingType == 1):
                dict['descending'] = False
            else:
                dict['descending'] = True
        elif (sortChoice == 2):
            dict['sort_by'] = "name"
        elif (sortChoice == 3):
            dict['sort_by'] = "class"
            classType = input("Enter the class you want to sort by: ")
            dict['class_name'] = classType

        # send the request
        message = json.dumps(dict)
        socket.send_string(message)
        result = socket.recv_string()
        try: 
            spell_data = json.loads(result)
            if spell_data == []:
                # if no spells returned, class name was invalid
                print("Class not found.")
            else:
                # iterate through the response, printing out each spell
                for spell in spell_data:
                    printSpell(spell)
        except json.JSONDecodeError:
            print("Error: Could not decode server resonse")
# -------------------------------------------------------------------------------------------------------------

# MICROSERVICE B ----------------------------------------------------------------------------------------------
# Get option to add a spell to bookmarks
def addSpell(spell, bookmarks):
    addOption = getIntegerInput("Would you like to add this spell to your bookmarks [1 = yes, 0 = no]?: ", 0, 1)
    if (addOption == 1):
        bookmarks[:] = accessBookmarkMods(spell, bookmarks, 1) # set option to 1 to add the spell

# Get option + confirmation to remove a spell from bookmarks
def removeSpell(spell, bookmarks):
    removeOption = getIntegerInput("Would you like to remove this spell from your bookmarks [1 = yes, 0 = no]?: ", 0, 1)
    if (removeOption == 1):
        print("WARNING: Removing the spell will delete it from your bookmarks. Please confirm that you want to delete it.")
        removeOption = getIntegerInput("Would you like to remove this spell from your bookmarks [1 = yes, 0 = no]?: ", 0, 1)
        if (removeOption == 1):
            bookmarks[:] = accessBookmarkMods(spell, bookmarks, 2) # set option to 2 to remove the spell
    
# Interaction with the bookmark_mods.py microservice: add/remove spells
def accessBookmarkMods(spell, bookmarks, option):
    # interact with microservice B
    context = zmq.Context()

    # socket to talk to server
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5553")

    # form dictionary request
    dict = {
        "json_array": bookmarks,
        "json_object": spell,
        "option": option
    }
    jsonInput = json.dumps(dict, default=str)

    # send request
    socket.send_string(jsonInput)

    # receive response
    message = socket.recv()
    if (len(message) != 0):
        decoded = message.decode('utf-8')
        jsonLoaded = json.loads(decoded)
        return jsonLoaded
    return bookmarks # return original list if nothing was done
    
# Print out name of spells in bookmarks list
def viewBookmarks(bookmarks):
    if not bookmarks: # check if list is empty
        print("You have no spells saved yet!")
    else:
        print("\nBookmarks")
        for i, spell in enumerate(bookmarks, start=1):
            print(f"{i}: {bookmarks[i-1]['name']}")
    
# Display and get options for the bookmarks submenu (view a spell's details or delete it)
def bookmarksSubmenu(bookmarks):
    option = 1
    while (option > 0):
        viewBookmarks(bookmarks)
        if (len(bookmarks) > 0):
            print("\nBOOKMARK OPTIONS")
            print("3: Choose a sorting option to sort bookmarked spells by")
            print("2: Enter spell index to delete the spell")
            print("1: Enter spell index to view more details about that spell")
            print("0: Return to main menu\n")
            option = getIntegerInput("Select an option [0, 1, 2, or 3]: ", 0, 3)
            if (option == 1):
                viewBookmarks(bookmarks)
                getBookmarkedSpell(bookmarks, "\nSelect the index of a bookmarked spell to view it in more detail.")
            elif (option == 2):
                viewBookmarks(bookmarks)
                selectedSpell = getBookmarkedSpell(bookmarks, "\nSelect the index of a bookmarked spell to delete.")
                removeSpell(bookmarks[selectedSpell], bookmarks)
            elif (option == 3):
                print("\nSORTING OPTIONS")
                print("3: Sort spells by class, alphabetically")
                print("2: Sort spells by name, alphabetically")
                print("1: Sort spells by level, ascending or descending")
                print("0: Return to Bookmarks Options\n")
                sortChoice = getIntegerInput("Select an option [0, 1, 2, or 3]: ", 0, 3)
                getSortOption(bookmarks, sortChoice)
                
        else:
            option = 0

# Retrieve a spell index from spell selection in bookmarks
def getBookmarkedSpell(bookmarks, prompt):
    print(prompt)
    numSpells = len(bookmarks)
    spellChoiceString = "\nSpell selection [1 to " + str(numSpells) + "]: "
    selectedSpell = getIntegerInput(spellChoiceString, 1, numSpells) - 1
    printSpell(bookmarks[selectedSpell])
    return selectedSpell
# -------------------------------------------------------------------------------------------------------------

# MICROSERVICE C ----------------------------------------------------------------------------------------------
# get user input for spell fields
def getSpellFields():
    # Collect basic field values as simple key-value pairs
    spellFields = {}
    print("\n") # blank line for formatting
    
    # Get basic field values
    for key in ['name', 'level', 'range', 'casting_time', 'duration', 'attack_type']:
        value = input(f"Enter a value for the field '{key}': ")
        spellFields[key] = value

    # Handle description
    desc = input("Enter the spell description: ")
    spellFields['desc'] = desc

    # Handle higher level effects
    higher_level = input("Enter higher level effects (leave empty if none): ")
    if higher_level:
        spellFields['higher_level'] = higher_level
    else:
        spellFields['higher_level'] = ""

    # Handle concentration
    concentration = input("Does this spell require concentration? (yes/no): ").lower()
    spellFields['concentration'] = concentration

    # Handle ritual
    ritual = input("Is this spell a ritual? (yes/no): ").lower()
    spellFields['ritual'] = ritual

    # Handle components
    components_input = input("Enter components (separate with commas, e.g., V,S,M): ")
    spellFields['components'] = components_input

    # Handle damage type and scaling
    has_damage = input("Does this spell deal damage? (yes/no): ").lower()
    spellFields['has_damage'] = has_damage
    
    if has_damage == 'yes':
        damage_type = input("Enter damage type (e.g. Fire, Cold, etc.): ")
        spellFields['damage_type'] = damage_type
        
        # Handle damage scaling
        scaling_type = input("Does damage scale with slot level or character level? (slot/character): ")
        spellFields['scaling_type'] = scaling_type
        
        if scaling_type in ['slot', 'character']:
            levels = input(f"Enter {scaling_type} levels to define (comma separated, e.g., 1, 5, 11): ")
            spellFields['scaling_levels'] = levels
            
            # Collect damage values for each level
            damage_values = {}
            for level in levels.split(','):
                level = level.strip()
                damage = input(f"Enter damage for {scaling_type} level {level}: ")
                damage_values[level] = damage
            
            spellFields['damage_values'] = json.dumps(damage_values)  # Convert to JSON string

    # Handle school of magic
    school = input("Enter school of magic: ")
    spellFields['school'] = school

    # Handle classes
    classes_input = input("Enter classes that can use this spell (comma separated): ")
    spellFields['classes'] = classes_input

    return spellFields

def generateSpell(spellFields, option, bookmarks, spellToEdit):
    # interact with microservice C
    context = zmq.Context()

    # socket to talk to server
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5554")

    # form dictionary request
    dict = {
        "option": option,
        "json_array": bookmarks,
        "json_object": spellToEdit,
        "spell_fields": spellFields  # Send the collected fields directly
    }
    jsonInput = json.dumps(dict, default=str)

    # send request
    socket.send_string(jsonInput)

    # receive response
    message = socket.recv()
    if (len(message) != 0):
        decoded = message.decode('utf-8')
        jsonLoaded = json.loads(decoded)
        return jsonLoaded # this will be a new set of bookmarks with the edited spell
    return bookmarks  # Return original bookmarks if no response

def newSpellSubmenu():
    print("\nNEW SPELL OPTIONS")
    print("2: Edit an existing spell in your bookmarks list")
    print("1: Create an entirely new spell")
    print("0: Return to main menu\n")
    option = getIntegerInput("Select an option [0, 1, or 2]: ", 0, 2)
    return option

def getSpellToEdit(bookmarks):
    viewBookmarks(bookmarks)
    spellEditIndex = getBookmarkedSpell(bookmarks, "\nSelect a spell to edit")
    return bookmarks[spellEditIndex]
# -------------------------------------------------------------------------------------------------------------
# MICROSERVICE D ----------------------------------------------------------------------------------------------
def accessDiceRoller(option, n, m, operator):
    # interact with microservice C
    context = zmq.Context()

    # socket to talk to server
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5552")

    # form dictionary request
    dict = {
        "option": option,
        "n": n,
        "operation": operator,
        "m": m
    }
    jsonInput = json.dumps(dict, default=str)

    # send request
    socket.send_string(jsonInput)

    # receive response
    result = socket.recv()
    dice_roll = int.from_bytes(result, byteorder='big')
    
    return dice_roll

def getDiceData():
    n = getIntegerInput("Enter the number of faces on the dice to roll (max number of faces is 10000): ", 0, 10000)
    isModified = None
    while (isModified != "yes" and isModified != "no"):
        isModified = input("Do you want to add a modifier to this dice roll? (yes/no): ").lower()
        if (isModified == "yes"):
            option = 2
            invalidOperator = True
            while (invalidOperator):
                operator = input("Do you want to add/subtract to the dice roll? (+/-): ")
                if (operator == "+" or operator == "-"):
                    invalidOperator = False
                else:
                    print("Invalid input. Please enter + or -")
            m = getIntegerInput("Enter the value of the modifier (max modifier is 10000): ", 0, 10000)
        elif (isModified == "no"):
            option = 1
            m = None
            operator = None
        else: 
            print("Invalid input. Please enter \"yes\" or \"no\".")
    
    return accessDiceRoller(option, n, m, operator)
    
# -------------------------------------------------------------------------------------------------------------
# Program Driver
def main():
    # variables
    bookmarks = []
    userInput = -1
    confirmQuit = -1

    # Display Title
    printTitle()

    # User input loop
    while (confirmQuit != 0):
        printMenuOptions()
        userInput = getIntegerInput("Choose an option [0, 1, 2, 3, 4, 5, 6]: ", 0, 6)
        if (userInput == 6):
            dice_roll = getDiceData()
            print(f"\nYour dice roll result is: {dice_roll}")
        elif (userInput == 5):
            option = newSpellSubmenu()
            if (option > 0):
                if (option == 1):
                    # Get user input for spell fields
                    customSpell = getSpellFields()
                    # Send to microservice for processing
                    bookmarks = generateSpell(customSpell, option, bookmarks, None)
                elif (option == 2):
                    # select some spell to edit
                    if (len(bookmarks) > 0):
                        spellToEdit = getSpellToEdit(bookmarks)
                        # Get user input for updated fields
                        spellEdits = getSpellFields()
                        # Send to microservice for processing
                        bookmarks = generateSpell(spellEdits, option, bookmarks, spellToEdit)
                    else:
                        print("No spells are in your bookmarks to edit.")
        elif (userInput == 4):
            bookmarksSubmenu(bookmarks)
        elif (userInput == 3):
            spell = searchSpellName()
            if (spell):
                # if a spell was returned, print it
                print("\nSpell found!\n")
                printSpell(spell)
                # ask user if they want to add this spell to a bookmarks list
                addSpell(spell, bookmarks)
        elif (userInput == 2):
            searchKeyWord(bookmarks)
        elif (userInput == 1):
            printLine()
            showHelpMenu()
            printLine()
        else:
            confirmQuit = input("Enter 0 to confirm that you want to quit, otherwise enter any value to return to main menu: ")
            try:
                confirmQuit = int(confirmQuit)
            except ValueError:
                confirmQuit = -1
            if (confirmQuit == 0):
                exitMicroservices()
                print("\nProgram closed.")

if __name__ == "__main__":
    main()