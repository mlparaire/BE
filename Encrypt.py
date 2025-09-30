# We import all the packages we need
from typing import List
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa as RSA
from cryptography.exceptions import InvalidSignature
from hashlib import sha256
from time import time
import os
import multiprocessing as mp
from binascii import hexlify ,unhexlify

# We define a custom type vector for our functions
type vector = List[int]

## This class will store all the values and function we need for the first part of  exercice 1
class Encrypt:
    ## We define the function hexify first, as we will use it on the key and the messages
    ## This function returns the unicode for every character of the string entered into a function
    ## and thus returns a List of integers
    def unicode_encoding(self,characters : str) -> vector:
        return [ord(char) for char in characters]

    ## We initiate the class with the key and the message
    def __init__(self,message : List[str]): # Note that we define message as str, not List[str]. But we can still load the two message as the same time
        self.__K = {'clear' : "blockchain",'hex' : self.unicode_encoding('blockchain')} ## This the key, with clear and hex form. Note that we load it as a private variable, so it cannot be accessed outside this class
        self.message = {'clear': message,'hex':[self.unicode_encoding(hex) for hex in message]} ## This is where we load the messages. We load it as List[str] so we can store them in the same dictionnary, and we transform them into hexbits format

    # we create a function to return go from unicode encoding to characters. We take each byte from the message and concatenate each characterized digit into a single string
    def characterize(self,hexes:vector) -> str:
        return ''.join([chr(hex) for hex in hexes])

    ## With this function, we perform the bitwise XOR.
    ## To make sure the key is always the same length as the message, we check if length are equal between the two
    ## If not, we compute the modulo division of both length. We then multiply the password by the quotient, and add the number of characters equals to the remainder
    ## The function returns the encrypted message in hexadecimal string
    def XOR_bitwise_encrypting(self,message : vector) -> str:
        return hexlify(bytes([a^b for a,b in zip(message,self.__K['hex'] if len(message) == len(self.__K['hex']) else (lambda mod: self.__K['hex'] * mod[0] + self.__K['hex'] * mod[1])(divmod(len(message), len(self.__K["hex"]))))])).decode('utf8')
    ## With this function, we reverse the bitwise XOR from the previous function
    ## Using the same length equalization technique for the key as the previous function
    ## We simply apply the bitwise XOR to the encrypted message, with the same key
    ## The function returns tbe decrypted message in plaintext
    def XOR_decode(self,encoded_string: str) -> str:
        return self.characterize([a ^ b for a, b in zip(list(unhexlify(encoded_string)), self.__K['hex'] if len(encoded_string) == len(self.__K['hex']) else (lambda mod: self.__K['hex'] * mod[0] + self.__K['hex'] * mod[1])(divmod(len(encoded_string), len(self.__K["hex"]))))])

## For the second part of first exercice, we create a new class. Because we won't need information from the first class, we don't need to make an inheritance class
## We call it PKE for Private-Public Key Encryption
class PKE:
    def __init__(self,message:str):
        self.__public_key_b = serialization.load_pem_public_key(bytes(open('public_key.pem').read().encode('utf8'))) # Here, we load the public key from Louis Bertucci's website. Note that we load it as a private variable
        if not {'private_key_paraire_22300561.pem', 'public_key_paraire_22300561.pem'}.issubset(os.listdir()): # Here, we check that we haven't created keys pairs for this exercice already
            self.__private_key = RSA.generate_private_key(public_exponent=65537,key_size=2048) # If not already create, we creat the private key. We also load it as a private variable
            self.public_key = self.__private_key.public_key() # We derive the public key from the private key
            open('private_key_paraire_22300561.pem', 'wb').write(self.__private_key.private_bytes(encoding=serialization.Encoding.PEM, format = serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())) # To save the newly created keys, we save them both inside distincts pem files
            open('public_key_paraire_22300561.pem', 'wb').write(self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format = serialization.PublicFormat.SubjectPublicKeyInfo))
        else: # Here, if we have already created they keys, we simply load them.
            self.__private_key = serialization.load_pem_private_key(open('private_key_paraire_22300561.pem', 'rb').read(), password=None)
            self.public_key = serialization.load_pem_public_key(bytes(open(
                'public_key_paraire_22300561.pem').read().encode('utf8')))
        self.message = message.encode()
    ## With the function RSA_public_key_encryption, we encrypt message as a string in hexadecimal form.
    ## To do so, we use Louis Bertucci's public key to encrypt our message. Only Louis Bertucci's private key will be able to decipher the message
    ## The function returns a string in hexadecimal form
    def RSA_public_key_encryption(self,message : bytes) -> str:
        return hexlify(self.__public_key_b.encrypt(message,padding=padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))).decode("utf8")
    ## With the function sign_message, we sign a message in plaintext using our private key
    ## The function returns both the message in hexadecimal form and the signature in a tuple
    def sign_message(self) -> tuple:
        return hexlify(self.message).decode(), hexlify(self.__private_key.sign(self.message,padding=padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),algorithm=hashes.SHA256())).decode()
    ## With the function check_signature, we check if the signature is correct with our public key
    ## To do so, we implement a try-except loop. If the public key verify our signature, the function return a message of succes
    ## However, if the public key raise a InvalidSignature exception, the function raise a ValueError
    def check_signature(self,message:str,signature :str):
        try:
            self.public_key.verify(unhexlify(signature),unhexlify(message),padding=padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),algorithm=hashes.SHA256())
            return "The message has been successfully verified with the signature"
        except InvalidSignature:
            raise ValueError(f'The signature could not be verified: Invalid signature')

## For the second question, we create a third class called Hash_func, that will be used to compute proof-of-work hashes
## Because we don't need any informations from the previous questions, we don't add an inheritance architecture
class Hash_func():
    def __init__(self):
        self.algoritm = sha256 ## Here, as the hashing function, we load sha256 from hashlib
        self.message = 'Paraire:"DigitalEconomics":' ## Here, we load the first part of the message

    ## With the function compute_hash, we seek to imitate a proof-of-work resolution
    ## We call the function with the complexity variable, that defines the number of liminary zeros in the hash
    ## The function returns a tuple with the message and the number of nonce, the hash and the time taken for the resolution

    def has_leading_zeros(self,digest: bytes, bits: int) -> bool:
        full_bytes = bits // 8
        remaining_bits = bits % 8

        if digest[:full_bytes] != b'\x00' * full_bytes:
            return False

        if remaining_bits > 0:
            next_byte = digest[full_bytes]
            return next_byte >> (8 - remaining_bits) == 0
        return True
    def compute_hash(self,complexity : int) -> tuple:
         ## Here, we define the prefix
        print(f'Computing for {complexity} 0')
        nonce = 0 ## Here, we define the number of nonce
        start_time = time() ## To compute the total time spent on the problem, we save the starting time
        # To check every hash until we find one that fits our needs, we use a while loop that stops whence a hash function with the correct liminary zeros is found.
        # nonce is incremented each time we fail to find a correct hash
#        while not(self.algoritm((self.message+str(nonce)).encode()).hexdigest().startswith(str('0' * complexity))):
        while True:
            if self.has_leading_zeros((digest := self.algoritm((self.message + str(nonce)).encode()).digest()), complexity):
                print(digest.hex())
                print(format(int.from_bytes(digest,"big"),'0256b'))
                break
            # Note that we use the walrus operator as to create and check the digest at the same time
            nonce += 1
        end_time = time() ## We note the end time
        return self.message+str(nonce),sha256((self.message + str(nonce)).encode()).hexdigest(),nonce,"Execution time ~ {0:.2f} seconds ".format(end_time-start_time),format(int.from_bytes(digest, "big"), "0256b"),complexity
    @classmethod
    def get_number_of_cpu(cls) -> str:
        return f'The numbre of CPU is {mp.cpu_count()}'
    def compute_hashes_increment(self,complexity:List[int]) -> tuple:
        for complex in complexity:
            yield self.compute_hash(complex)
