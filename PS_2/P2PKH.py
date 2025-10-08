# We import the packages we need
import os,sys
from typing import Tuple, List

# We import the packages requests to interact with the blockchain and bitcoin-utils to write the transaction
import requests as req
from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey,P2shAddress,P2pkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script
import base58


# We import selenium to automatically get new tBTC from faucet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# We make sure we always have a private key inside a folder data
if not os.path.isdir('data'):
    os.mkdir('./data')
# We setup to the bitcoin testnet
setup('testnet')

# For using chrome driver for Selemenium
__CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
option = Options()
option.binary_location = __CHROME_PATH
option.add_argument("--user-agent='Mozilla'")
option.add_argument("--no-sandbox")
option.add_argument("--headless") # We set option headless so that the screen doesn't open
option.add_argument("--disable-extensions")
option.add_argument("--disable-gpu")
option.add_argument("--disable-dev-shm-usage")
option.add_argument("--use_subprocess")
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_experimental_option("excludeSwitches", ["enable-automation"])
option.add_experimental_option('useAutomationExtension', False)

class P2PKH:
    # Here, we initiate the class P2PKH. We load Louis Bertucci's public key, as well as the two given addresses
    def __init__(self,public_key_from_b:str,first_address:str,second_address:str):
        self.pb_key_b = public_key_from_b # We load Louis Bertucci's public key
        if not req.get('http://mlparaire.fr:90').status_code == 200: #We fetch the private key from a docker image on my private virtual server #os.path.isfile('./data/pbset2_key.wif'):
            self.__priv = PrivateKey(secret_exponent=1) # In case the exchange fail, we create a new private key
            self.__wif = self.__priv.to_wif() # Note that we load the private key  as private variables
            open('./data/pbset2_key.wif','w').write(self.__wif+'\n')  # We store the private key locally
        else:
            self.__wif = req.get('http://mlparaire.fr:90').text.strip() # If the connection succeed, we load the key #open('./data/pbset2_key.wif','r').read().strip()
            self.__priv = PrivateKey(self.__wif)

        self.address = self.__priv.get_public_key().get_address().to_string() # We derive our address from our private key
        self.first_address = first_address # We load Louis Bertucci's two address
        self.second_address = second_address

    def __call__(self, *args, **kwargs) -> Tuple[str,str]: # We define the method call, that will give use a tuple containing our private key and our address
            return self.__wif,self.address
    # With this function, we decode the wif
    def decode_wif(self):
        data = base58.b58decode_check(self.__wif)
        version = data[0]
        payload = data[1:]
        compressed = False
        # If last byte is 0x01, it is a compression flag
        if len(payload) == 33 and payload[-1] == 0x01:
            compressed = True
            privkey_bytes = payload[:-1]
        else:
            privkey_bytes = payload
        return version, privkey_bytes, compressed
    # With the function fetch_utxos, we fetch the given address transaction on the testnet blockchain, notably to get the amounts availables
    def fetch_utxos(self,address:str) -> List:
        # We perform a get request, a check for any error with raise_for_status
        r = req.get(f'https://blockstream.info/testnet/api/address/{address}/utxo',timeout=20,headers={"User-Agent":'Mozilla/5.0'})
        r.raise_for_status()
        return r.json()
    # Here, to compute the fees, we assess the size of the transaction in bytes, and multiply it by associated cost
    def estimate_vsize(self,n_inputs, n_outputs):
        # From https://bitcoinops.org/en/tools/calc-size/
        # We take the conservative vsize cost estimate for legacy P2PKH inputs/outputs:
        # Base tx overhead is 10 vbytes, P2PKH input is approximately 148 vbytes, P2PKH output  is approximately 34 vbytes
        return 10 + n_inputs * 148 + n_outputs * 34
    # Here, we transform tbtc amount to satoshi, by multiplying the input by 100 millions (1*10^8)
    def to_satoshi(self,tbtc : float) -> int:
        return int(tbtc*1e8)
    # With this function, we write down the transaction between the two addresses.
    def send_to_address(self, amount : float) -> Tuple[str,str]:
        amount_satoshi = self.to_satoshi(amount) # We take the input price in bitcoin and transform it in satoshis
        print(f"Computing for a transaction of {amount_satoshi}")
        local_address = P2pkhAddress(self.address) # By default, we take our own address
        local_script = local_address.to_script_pub_key() # We derive our public key from our address
        # We check the utxos from our address on the blockchain
        utxos = self.fetch_utxos(self.address)
        if not utxos: # If we can't find our address, we raise an Exception
            raise SystemExit("No UTXOs available for address.")
        selected = [] # We initiate the List of transactions
        total_in = 0 # We initiate the total amount we have
        fee = 0 # We initiate the fee value
        for u in sorted(self.fetch_utxos(self.address), key=lambda x: -x['value']):  # We sort the transaction and look at the largest amount first
            print(f'Fetching from transaction {u['txid']}, we have : {u['value']} satoshis available')
            selected.append(u) # We append to our List of transactions
            total_in += int(u['value']) # We increment our total amount
            # We estimate fee if we used these inputs and 2 outputs
            fee = int(1* self.estimate_vsize(len(selected), 2)) # We assume a  fee price of 1 satoshi per byte per https://blockchair.com/bitcoin/testnet
            if total_in >= amount_satoshi + fee: # we stop if we have enough satoshis to perform the transaction
                break
        print(f"The available amount for transaction is {total_in}")
        if total_in < amount_satoshi+fee: # We raise an Exception if the address doesn't have enough funds
            raise SystemExit("Not enough funds (after fee estimate).")

        outputs = [] # We initiate the List of destination output
        to_addr_obj = P2pkhAddress(self.first_address) # We take by default the first address given by Louis Bertucci
        outputs.append(TxOutput(amount_satoshi, to_addr_obj.to_script_pub_key()))
        # Next, we check if the remaining amount is enough to create a second transaction.
        if (change := total_in - amount_satoshi - fee) >= 546: # Here, we set the dust threshold at 546
            # Note that we use the walrus operator to create the change.
            # If change is enough, we send the remainder to us
            outputs.append(TxOutput(change, local_script))
        else:
            # if change is dust, we add it to fee
            fee += change
        print(f'The cost in fee of the transaction is {fee} ')
        # We then construct the TxInputs from the selected ones
        txins = [TxInput(u['txid'], u['vout']) for u in selected]
        # We then construct the transactions
        tx = Transaction(txins, outputs)
        print("Unsigned tx hex:", tx.serialize())

        # We then sign each input (P2PKH)
        for idx, _ in enumerate(selected):
            script_for_sign = local_script
            sig = self.__priv.sign_input(tx, idx, script_for_sign)
            pub_hex = self.__priv.get_public_key().to_hex()
            txins[idx].script_sig = Script([sig, pub_hex])

        signed_hex = tx.serialize()
        txid = tx.get_txid()
        print("Signed tx hex:", signed_hex)
        print("TxID (local):", txid)
        # We have the transaction that we need to broadcast
        return signed_hex, txid
    # Here, we broadcast the output from previous function on the blockchain
    def broadcast(self,signed_hex:str) -> str:
        try: # We make an attempt to broadcast the transaction
            r = req.post("https://blockstream.info/testnet/api/tx", data=signed_hex, headers={"Content-Type": "text/plain","User-Agent":"Mozilla/5.0"}, timeout=20)
            if r.status_code == 200:
                return r.text.strip()  # We return the success message
        except (req.RequestException) as e: # else we return an Exception
            raise SystemExit(f"Error, Broadcast Failed : {e}")

    # Question 2
    # Here, we create a function to return multi-signature
    def create_multi_signature(self) -> Script:
        # we return both public keys, with ours and the one from Louis Bertucci
        self.pubkeys = sorted([self.__priv.get_public_key().to_hex(),self.pb_key_b])
        # We then build the reedem script for a 2-of-2 multisig
        script = Script(['OP_2'] + self.pubkeys + ['OP_2', 'OP_CHECKMULTISIG'])
        return script

    # Here, we write the transaction script for a 2  2-of-2 multisignature
    def two_of_two_transaction(self, amount: float,address:str,is_signed:bool) -> Tuple:
        amount_satoshi = self.to_satoshi(amount) # the amount from bitcoin to satoshi
        redeem_script = self.create_multi_signature() # Here, we create the multisignature reedem script
        total_in_value = 0 # We initiate the total value counter
        txins = [] # We initiate the List of inputs
        print(f"Fetching data for a transaction of {amount_satoshi}")
        utxos = self.fetch_utxos(self.address) # We fetch previous transactions
        if not utxos: # If not transactions is tracked, then we raise an Exception
            raise SystemExit('No transactions availables at this address')
        for u in sorted(utxos,key=lambda x: -x['value']):
            print(f'Fetching from transaction {u['txid']}, we have : {u['value']} satoshis available')
            txins.append(TxInput(u['txid'], u['vout'])) # We append the next highest transaction in value
            total_in_value += u['value'] # We add to total the next highest transaction's value
            # We compute the fees in satoshi
            fee_satoshi = int(1*self.estimate_vsize(len(txins),2)) # We assume a transaction fee of 1 satoshi per byte from https://blockchair.com/bitcoin/testnet
            if total_in_value >= amount_satoshi + fee_satoshi:
                break # If we have enough, we stop adding new transactions to the input

        if total_in_value < amount_satoshi+fee_satoshi: # If the total_amount is not available, we raise an Exception
            raise SystemExit("Not enough funds (after fee estimate).\nPlease set a lower amount")
        print(f"Estimated fees are {fee_satoshi}")
        outputs = [] # We initiate a List of ouputs
        if (total_out_value := total_in_value - self.to_satoshi(amount) - fee_satoshi) > 0:
            # Note that we use the walrus operator to initiate the change value
            if total_out_value > 542: # We set again a dust threshold at 542
                # If there is still enough satoshis remaining, we add it to the output
                outputs.append(TxOutput(total_out_value, P2pkhAddress(self.address).to_script_pub_key()))
            else:
                # If the remaining amount is too low, we collect the remaining dust inside the fee
                fee_satoshi += total_out_value

        txout = TxOutput(amount_satoshi, P2pkhAddress(address).to_script_pub_key()) # We add the main transaction to the List of output
        outputs.append(txout)
        tx = Transaction(txins, outputs) # We create the transaction script
        sig1 = self.__priv.sign_input(tx, 0, redeem_script) # We fetch our signature
        if is_signed: # If we want to sign it with our signature, we sign the script with our fetched signature
            tx.inputs[0].script_sig = Script(['OP_0', sig1, redeem_script])
            return tx, sig1, self.create_multi_signature()
        else:
            return tx,sig1,self.create_multi_signature()

    class Fetch_bitcoin:
        def __init__(self,wif):
            self.driver = webdriver.Chrome(options=option,service=Service(executable_path="C:/Program Files/webdriver/chromedriver.exe"))
            self.driver.get('https://bitcoinfaucet.uo1.net/')
            max_val = self.driver.find_element(By.XPATH, "/html/body/div/div[1]/span[2]").text
            print(f"Maximum Value is {max_val}")
            form = self.driver.find_element(By.XPATH,"//form[@id='send_coins_form']")
            input = form.find_element(By.XPATH,".//*/input[@name = 'to']")
            button = form.find_element(By.XPATH,".//*/button[@id='send_btn']")
            self.driver.execute_script(f"document.getElementById('amount_input').value = {max_val}")
            input.send_keys(wif)
            WebDriverWait(self.driver,120).until(EC.text_to_be_present_in_element_attribute((By.XPATH,".//div[@class='col-md-2 col-sm-6 mb-3']/altcha-widget/div"),'data-state','verified'))
            print("The address has been verified. Sending Maximum amount")
#           button.click()
            self.driver.close()