from typing import List,Tuple

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
    def __init__(self,message : str):
        self.__K = {'clear' : "blockchains",'hex' : self.hexify('blockchains')} ## This the key, with clear and hex form. Note that we load it as a private variable, so it cannot be accessed outside this class
        self.message = {'clear': message,'hex':[self.hexify(hex) for hex in message]} ## This is where we load the messages. We load it as List[str] so we can store them in the same dictionnary

    def characterize(self,hexes:List[int]) -> str:
        return ''.join([chr(hex) for hex in hexes])
    def XOR_bitwise_encrypting(self,message : List[int]) -> List[int]:
        return [a^b for a,b in zip(message,self.__K['hex'] if len(message) == len(self.__K['hex']) else (lambda mod: self.__K['hex'] * mod[0] + self.__K['hex'] * mod[1])(divmod(len(message), len(self.__K["hex"]))))]