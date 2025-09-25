from Encrypt import Encrypt
from operator import xor
#Question 1

## We load the class Encrypt from the file Encrypt.py, and we initiate with the messages from the exercice
enc = Encrypt(["bitcoin","This is such a great class"])

## The key has already been transformed into digits, and we need to do the same with the function hexify
## to the messages from the exercice


#print(enc.message['hex'][1])
message = enc.XOR_bitwise_encrypting(enc.message['hex'][1])

# FOr commit