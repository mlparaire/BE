from P2PKH import P2PKH

# We load the needed keys and addresses from Louis Bertucci
__PUBLIC_KEY_FROM_BERTUCCI = "02019662a808d4a0df7e8c1ee8b26646e59cfaa92ebd906bde14b4bda5113fa2a9"
__FIRST_ADDRESS_FROM_BERTUCCI = "mreLpAzPWBtdwBC9NMEsBy1jkQ3phjy1Eh"
__SECOND_ADDRESS_FROM_BERTUCCI = "msfTfNj6FicTNBShCJBhoxvhHoM794cKsZ"

# We load the P2PKH class from P2PKH.py

Wallet = P2PKH(__PUBLIC_KEY_FROM_BERTUCCI,__FIRST_ADDRESS_FROM_BERTUCCI,__SECOND_ADDRESS_FROM_BERTUCCI)

# Exercice 1 - Simple P2PKH
transaction,txid = Wallet.send_to_address(0.00055)
result = Wallet.broadcast(transaction)
if result:
    print(f'The transaction was successfully broadcasted with transaction id :{result}')
# The transaction was was successfully broadcasted with transaction id 1e440bfd940dde41413172055a88db50b0bffe2e0b3b09937ddf58676c7b99ea

# Exercice 2 - MultiSignature

## Question 1
signature = Wallet.two_of_two_transaction(0.0042,Wallet.first_address,True)
print(f"The signed transaction script is {signature[0]} \nThe signature is {signature[1]}\nThe multi_signature_script is {signature[2]}")

## Question 2

signature = Wallet.two_of_two_transaction(0.0042,Wallet.second_address,False)
print(f"The unsigned transaction script is {signature[0]} \nThe signature is {signature[1]}\nThe multi_signature_script is {signature[2]}")



# tb1qerzrlxcfu24davlur5sqmgzzgsal6wusda40er 0.00191516
# tb1qerzrlxcfu24davlur5sqmgzzgsal6wusda40er 0.00193993
# tb1qerzrlxcfu24davlur5sqmgzzgsal6wusda40er 0.00152634