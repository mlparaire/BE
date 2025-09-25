from typing import List,Dict,Tuple
from binascii import hexlify,unhexlify

# type Vector = List[float]
#type Address = tuple[str,int]

## This class will store all the values we need for this exercice and the functions we need
class Encrypt:
    ## We define the function hexify first, as we will use it on the key
    ## This function returns the unicode for every character of the string entered into a function
    ## and thus returns a List of integers
    def hexify(self,characters : str) -> List[int]:
        return [ord(char) for char in characters]

    # Because the key and message vary in length, we need to create the function that fill the difference
    def remainder_for_key(func):
        def check_key_length(self,message : List[int]) -> Tuple[List[int],List[int]]:
            return func(self,message,self.__K['hex'] if len(message) == len(self.__K['hex']) else (lambda rem: self.__K['hex']*rem[0]+self.__K['hex'][:rem[1]])(divmod(len(message),len(self.__K['hex']))))
        return check_key_length

    ## We initiate the class
    def __init__(self,message : List[str]):
        self.__K = {'clear' : "blockchain",'hex' : self.hexify('blockchain')} ## This the key, with clear and hex form. Note that we load it as a private variable, so it cannot be accessed outside this class
        self.message = {'clear': message, 'hex' : [self.hexify(char) for char in [mess for mess in message]]} ## This is where we load the messages. We load it as List[str] so we can store them in the same List
    def characterize(self,hexes:List[int]) -> str:
        return ''.join([chr(hex) for hex in hexes])
    @remainder_for_key
    def XOR_bitwise_encrypting(self, message : List[int],key:List[int]) -> List[int]:
        return [m^k for m,k in zip(message,key)]
