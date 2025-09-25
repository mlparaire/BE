from typing import List

# type Vector = List[float]
#type Address = tuple[str,int]

## This class will store all the values we need for this exercice and the functions we need
class Encrypt:
    ## We define the function hexify first, as we will use it on the key
    ## This function returns the unicode for every character of the string entered into a function
    ## and thus returns a List of integers
    def hexify(self,characters : str) -> List[int]:
        return [ord(char) for char in characters]

    ## We initiate the class
    def __init__(self,message : List[str]):
        self.__K = {'clear' : "blockchains",'hex' : self.hexify('bitcoin')} ## This the key, with clear and hex form. Note that we load it as a private variable, so it cannot be accessed outside this class
        self.message = {'clear': message} ## This is where we load the messages. We load it as List[str] so we can store them in the same dictionnary

    def characterize(self,hexes:List[int]) -> str:
        return ''.join([chr(hex) for hex in hexes])
