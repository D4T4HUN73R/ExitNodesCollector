import requests
from datetime import datetime

def get_proton_vpn_exit_nodes(api_url):
    # Fetch the Proton VPN exit nodes data from the API
    response = requests.get(api_url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()  # Return the response as JSON

def extract_ipv4_addresses_from_proton(data):
    # Extract IPv4 exit addresses from the Proton VPN JSON data
    ipv4_addresses = set()  # Use a set to avoid duplicates
    for server in data['LogicalServers']:
        for server_info in server['Servers']:
            exit_ip = server_info['ExitIP']
            ipv4_addresses.add(exit_ip)  # Add the IP address to the set
    return list(ipv4_addresses)  # Convert the set back to a list

def save_to_file(ipv4_addresses, output_filename):
    # Save the list of IP addresses to a file
    with open(output_filename, 'w') as file:
        for ipv4 in ipv4_addresses:
            file.write(f"{ipv4}\n")

def main():
    api_url = 'https://api.protonmail.ch/vpn/logicals'
    
    try:
        response_data = get_proton_vpn_exit_nodes(api_url)
        
        ipv4_addresses = extract_ipv4_addresses_from_proton(response_data)

        # Get the current date and time formatted as "YYYY-MM-DD-HH-MM_"
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M_")
        
        # Create the output filename with the current date and time included
        output_filename = f'{current_datetime}protonvpn_exit_ips.txt'
        
        save_to_file(ipv4_addresses, output_filename)
        print(f'Saved {len(ipv4_addresses)} unique IP addresses to {output_filename}')
    
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    main()
