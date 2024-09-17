from random import randint

def getRandomID():  # Generate a random ID between 1 and 1000000000 used for generation database IDs
    minID = 1
    maxID = 1000000000
    return randint(minID, maxID)