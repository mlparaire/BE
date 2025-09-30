from Encrypt import Encrypt,PKE,Hash_func

#Exercice 1

# Question 1

## For this question, all of the bitwise operations will be computed within the class Encrypt.
## This way, we can use private variables so to safely contains the private key

## We load the class Encrypt from the file Encrypt.py, and we initiate with the messages from the exercice
enc = Encrypt(["bitcoin","This is such a great class"])

# We load the first message from the class, and apply a bitwise XOR
first_message = enc.XOR_bitwise_encrypting(enc.message['hex'][0])
print(f'The first message, when encoded in hexadecimal form is : {first_message}')
# We load the second message from the class, and apply a bitwise XOR
second_message = enc.XOR_bitwise_encrypting(enc.message['hex'][1])
print(f'The second message, where encoded in hexadecimal form is: {second_message}')

# To check whether we can decipher our encrypted message, we perform a new bitwise XOR with the same key to the cyphertext
print(f'The first message, when decoded is: {enc.XOR_decode(first_message)}')
print(f'The first message, when decoded is: {enc.XOR_decode(second_message)}')


# Question 2
# We load the class PKE, that contains all public and private keys, with a message that will be used for part 3
pke = PKE("The message is fragments.lameness.clowns")

## Part 1
# We use the class function RSA_public_key_encryption to encrypt a message
__SECRET_MESSAGE = open('secret_message.txt').read()
message_for_b = pke.RSA_public_key_encryption(b"Dear Professor Bertucci\n, here's my message: Les sanglots longs des violons de l'automne \n blessent mon coeur d'un langueur monotone")
print(f'The message, in hexadecimal form is:\n{message_for_b}')

## Part 2
# The pair of keys is generated when the function PKE is loaded

## Part 3
# We extract the message from initialisation with its signature from the private key in two variables
message, signature = pke.sign_message()
print(f'The message is {message}\nThe signature is {signature}')
print(f'We now verify the signature')
# We verify the signature with our public key inside the class PKE
try:
    # If the signature checks out, we print a success message
    print(f"\033[92m{pke.check_signature(message=message,signature=signature)}\033[0m")
except ValueError as e:
    # If not, we print an error message
    print(f"\033[91m{e}\033[0m")

## Part 4
# Using the message in the initialisation of PKE class, we encrypt it using the encryption function with Louis Bertucci's class
message = pke.RSA_public_key_encryption(pke.message)
print(message)

# Question 2
print('Question 2 \n')
# We load the class Hash_func, that contains the hashing SHA256 algorithm
hash = Hash_func()
# We attempt to compute hashes that meets 5 and 10 liminary zeros, and save the result
response,second_response= hash.compute_hash(5),hash.compute_hash(10)
with open('Exercice_2_answer_Paraire_22300561.txt','wb') as ex:
    ex.write(b'For the computation of a proof of work with 5 leading zeros, the results are :\n')
    ex.write((("Message M = "+response[0]+'\nHash = '+response[1]+'\nNumber of nonce = '+str(response[2])+"\n"+response[3]+ "\nBytes:" + response[4]).encode()))
    ex.write(b'\n\n')
    ex.write(b'For the computation of a proof of work with 10 leading zeros, the results are :\n')
    ex.write((("Message M = " + second_response[0] + '\nHash = ' + second_response[ 1] + '\nNumber of nonce = ' + str(second_response[2]) + "\n" + second_response[3] + "\nBytes:" + second_response[4]).encode()))
    ex.close()

## Question 3

print(hash.get_number_of_cpu())
## To see how fast can we go with computing bits, we can try to increment complexity with leading zeros
y = hash.compute_hashes_increment(list(range(100)))
with open('incrementation.txt','wb') as an:
    for i in y:
        an.write((("Leading zeros = "+ str(i[5])+"\nMessage M = " + i[0] + '\nHash = ' + i[1] + '\nNumber of nonce = ' + str(i[2]) + "\n" + i[3] + "\nBytes:" +i[4]).encode()))
        an.write(b'\n\n')
    an.close()

## When we look at the transcript, we see that the computer starts to lag at the 25 leading zeros.

## It then takes exponentially more time to compute the next number of leading zero
