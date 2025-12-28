from web3 import Web3
#web3.py库中，Web3类是核心入口点
from dotenv import load_dotenv
#将.env文件中的键值对加载到系统的环境变量中
from vyper import compile_code
#核心函数，将vyper源代码编译为EVM能理解的形式
import os
from encrypt_key import KEYSTORE_PATH
from eth_account import Account
import getpass
#隐藏输入，更安全

load_dotenv()
#执行加载动作，搜索项目中的.env文

RPC_URL = os.getenv("RPC_URL")


def main():

    print("Let's read in the Vyper code and deploy it to the blockchain!")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    #需要制定一个Provider来实例化Web3类

    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()
        #读取vyper合约
        compliation_details = compile_code(
            favorites_code, output_formats=["bytecode", "abi"]
        )
        #output_fromats接受一个列表，自定义编译产物
        #bytecode和abi是必须选项

    chain_id = 31337  
    # Make sure this matches your virtual or anvil network!

    print("Getting environment variables...")
    my_address = os.getenv("MY_ADDRESS")

    # private_key = os.getenv("PRIVATE_KEY")
    private_key = decrypt_key()

    # Create the contract in Python
    favorites_contract = w3.eth.contract(
        abi=compliation_details["abi"], bytecode=compliation_details["bytecode"]
    )

    # Submit the transaction that deploys the contract
    nonce = w3.eth.get_transaction_count(my_address)

    # We could do this next line as a shortcut :)
    # tx_hash = favorites_contract.constructor().transact()

    print("Building the transaction...")
    transaction = favorites_contract.constructor().build_transaction(
        #constructor()模拟调用合约的构造函数
        #如__init__   如果有参数需要从此传递
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": my_address,
            "nonce": nonce,
            #chainId必须准确，其他可以自定义
        }
    )

    print("Signing transaction...")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("We signed it, check it out:")
    print(signed_txn)
    #产生签名后的交易，此时哈希值已经确定，但未发送

    print("Deploying Contract!")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print("Waiting for transaction to finish...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Done! Contract deployed to {tx_receipt.contractAddress}")
    #发送交易是异步的，发送后拿到一个交易哈希值
    #但并不代表交易成功了，可能还在排队


def decrypt_key() -> str:
    with open(KEYSTORE_PATH, "r") as fp:
        encrypted_account = fp.read()
        password = getpass.getpass("Enter your password for your keystore.json:\n")
        key = Account.decrypt(encrypted_account, password)
        #使用Web3 Keystore JSON专属加密机制
        print("Decrypted key!")
        return key


if __name__ == "__main__":
    main()
