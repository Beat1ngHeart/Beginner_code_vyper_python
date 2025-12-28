import getpass
from eth_account import Account
from pathlib import Path
import json

KEYSTORE_PATH = Path(".keystore.json")

def main():
    private_key = getpass.getpass("Enter your private key")
    my_account = Account.from_key(private_key)

    password = getpass.getpass("Enter a pass word\n")
    encrypted_account = my_account.encrypt(password)

    print(f"Saving to{KEYSTORE_PATH}")
    with KEYSTORE_PATH.open("w") as fp:
        json.dump(encrypted_account,fp)
        #写入文件中
        
if __name__ == "__main__":
    main()
