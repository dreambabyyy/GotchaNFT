import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_status(message, status=None):
    if status == "success":
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    elif status == "error":
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    elif status == "info":
        print(f"{Fore.YELLOW}→ {message}{Style.RESET_ALL}")
    elif status == "header":
        print(f"\n{Fore.BLUE+Style.BRIGHT}{'='*50}")
        print(f"{Fore.CYAN}✦ {message}")
        print(f"{Fore.BLUE+Style.BRIGHT}{'='*50}{Style.RESET_ALL}")

# Base configuration
base_url = "https://gotch.blast0x.xyz/api"

def get_one_referral(address):
    try:
        response = requests.get(f"{base_url}/referral/getOne?address={address}")
        if response.status_code != 200:
            if response.status_code == 500:
                print_status(f"Internal Server Error (Down)", "error")
                return False, None
            else:
                print_status(f"Server Error: {response.status_code} - {response.text}", "error")
                return False, None
        return response.json().get('success', False), response.json().get('data', None)
    except json.JSONDecodeError:
        print_status("Error decoding JSON response in get_one_referral", "error")
        print_status(f"Response content: {response.text}", "error")
        return False, None
    except Exception as e:
        print_status(f"Server error in get_one_referral: {str(e)}", "error")
        return False, None

def get_all_referrals():
    response = requests.get(f"{base_url}/referral/getAll")
    return response.status_code == 200

def check_account(address):
    try:
        response = requests.post(
            f"{base_url}/account/check",
            json={"address": address}
        )
        if response.status_code != 200:
            if response.status_code == 500:
                print_status(f"Internal Server Error (Down)", "error")
                return False
            else:
                print_status(f"Server Error: {response.status_code} - {response.text}", "error")
                return False
        return response.json().get('success', False)
    except json.JSONDecodeError:
        print_status("Error decoding JSON response in check_account", "error")
        print_status(f"Response content: {response.text}", "error")
        return False
    except Exception as e:
        print_status(f"Unhandled error in check_account: {str(e)}", "error")
        return False

def get_balance(address):
    try:
        response = requests.post(
            "https://api.testnet.abs.xyz/",
            json={
                "jsonrpc": "2.0",
                "id": 0,
                "method": "eth_getBalance",
                "params": [address, "latest"]
            }
        )
        if response.status_code != 200:
            if response.status_code == 500:
                print_status(f"Internal Server Error (Down)", "error")
                return 0
            else:
                print_status(f"Server Error: {response.status_code} - {response.text}", "error")
                return 0
        return int(response.json().get('result', '0x0'), 16)
    except json.JSONDecodeError:
        print_status("Error decoding JSON response in get_balance", "error")
        print_status(f"Response content: {response.text}", "error")
        return 0
    except Exception as e:
        print_status(f"Server error in get_balance: {str(e)}", "error")
        return 0


def check_referral(address):
    try:
        response = requests.post(
            f"{base_url}/referral/check",
            json={"address": address}
        )
        if response.status_code != 200:
            if response.status_code == 500:
                print_status(f"Internal Server Error (Down)", "error")
                return False
            else:
                print_status(f"Server Error: {response.status_code} - {response.text}", "error")
                return False
        return response.json().get('exist', False)
    except json.JSONDecodeError:
        print_status("Error decoding JSON response in check_referral", "error")
        print_status(f"Response content: {response.text}", "error")
        return False
    except Exception as e:
        print_status(f"Server error in check_referral: {str(e)}", "error")
        return False
def use_referral_address(address, referral_code):
    try:
        response = requests.post(
            f"{base_url}/referral/usageReferralAddress",
            json={"address": address, "referencedCode": referral_code}
        )
        if response.status_code != 200:
            if response.status_code == 500:
                print_status(f"Internal Server Error (Down)", "error")
                return False, "Internal Server Error"
            else:
                print_status(f"Server Error: {response.status_code} - {response.text}", "error")
                return False, response.text
 
        return response.json().get('success', False), response.json().get('message', '')
    except json.JSONDecodeError:
        print_status("Error decoding JSON response in use_referral_address", "error")
        print_status(f"Response content: {response.text}", "error")
        return False, "JSON decoding error"
    except Exception as e:
        print_status(f"Server error in use_referral_address: {str(e)}", "error")
        return False, str(e)

def load_referral_code(file_path):
    try:
        with open(file_path, 'r') as file:
            referral_code = file.readline().strip()
            if referral_code:
                return referral_code
            else:
                raise ValueError("Referral code is empty.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found.")

def process_wallet_addresses(wallet_addresses, referral_code):
    total = len(wallet_addresses)
    success_count = 0
    
    for index, address in enumerate(wallet_addresses, 1):
        print_status(f"Wallet {index}/{total}", "header")
        
        try:
            # Check initial referral status
            success, data = get_one_referral(address)
            if not data:
                print_status("No existing referral found", "info")
            else:
                print_status("Existing referral found", "info")
            time.sleep(1)
            
            # Check account
            if check_account(address):
                print_status("Account verified", "success")
            else:
                print_status("Account check failed", "error")
            time.sleep(1)
            
            # Check balance
            balance = get_balance(address)
            print_status(f"Balance: {balance} wei", "info")
            time.sleep(1)
            
            # Check referral existence
            has_referral = check_referral(address)
            if not has_referral:
                print_status("No active referral, attempting to use referral code", "info")
                success, message = use_referral_address(address, referral_code)
                if success:
                    print_status("Referral code applied successfully", "success")
                    success_count += 1
                else:
                    print_status(f"Failed to apply referral code: {message}", "error")
            else:
                print_status("Referral already exists", "info")
            
            time.sleep(2)
            
        except Exception as e:
            print_status(f"Error processing wallet: {str(e)}", "error")
        
        print_status("Waiting before next wallet...", "info")
        time.sleep(2)
    
    # Print summary
    print_status(f"Processing complete! Summary", "header")
    print(f"{Fore.YELLOW}Total wallets processed: {total}")
    print(f"{Fore.GREEN}Successful referrals: {success_count}")
    print(f"{Fore.RED}Failed referrals: {total - success_count}{Style.RESET_ALL}")

def main():
    print(Fore.WHITE + r"""
      █▀▀ █░█ ▄▀█ █░░ █ █▄▄ █ █▀▀
      █▄█ █▀█ █▀█ █▄▄ █ █▄█ █ ██▄
    """ + Fore.RESET)
    print(Fore.GREEN + Style.BRIGHT + "Gotcha NFT Auto Reff" + Fore.RESET)
    print(Fore.CYAN + Style.BRIGHT + "Join @ghalibie_sharing | @sirkel_testnet \n\n" + Fore.RESET)
    try:
        # Load referral code
        referral_code = load_referral_code('reff.txt')
        print_status(f"Loaded referral code: {referral_code}", "info")
        
        # Read wallet addresses
        with open('eth_wallets.txt', 'r') as file:
            wallet_addresses = [line.strip() for line in file.readlines() if line.strip()]
        
        if not wallet_addresses:
            print_status("No wallet addresses found in private_keys.txt", "error")
            return
        
        print_status(f"Found {len(wallet_addresses)} wallet addresses", "info")
        process_wallet_addresses(wallet_addresses, referral_code)
        
    except FileNotFoundError as e:
        print_status(str(e), "error")
    except Exception as e:
        print_status(f"An error occurred: {str(e)}", "error")

if __name__ == "__main__":
    main()
