import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime

def is_valid_ipv4(ip):
    """Validate the format of an IPv4 address."""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not (0 <= int(part) <= 255):
            return False
    return True

def get_latest_exit_list_url(base_url):
    # Fetch the content of the index page
    response = requests.get(base_url)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the latest exit list link by using regex
    latest_file_link = soup.find('a', href=re.compile(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}'))
    if latest_file_link and latest_file_link['href']:
        return "https://collector.torproject.org/recent/exit-lists/" + latest_file_link['href']
    else:
        raise Exception("Could not find the latest exit list file.")

def download_exit_list(file_url):
    # Download the latest exit list file
    response = requests.get(file_url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text, file_url.split('/')[-1]  # Return content and the filename

def extract_ipv4_addresses_from_tor(file_content):
    # Find all lines that contain 'ExitAddress' and extract the IPs
    ipv4_addresses = set()  # Use a set to avoid duplicates
    lines = file_content.splitlines()
    for line in lines:
        if line.startswith('ExitAddress'):
            parts = line.split()
            if len(parts) >= 2:
                ipv4 = parts[1]
                if is_valid_ipv4(ipv4):
                    ipv4_addresses.add(ipv4)  # Add the valid IP address to the set
    return list(ipv4_addresses)  # Convert the set back to a list

def fetch_all_tor_nodes():
    # Fetch Tor node details from the Onionoo API
    response = requests.get("https://onionoo.torproject.org/details?search=type:relay%20running:true")
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()  # Return the response as JSON

def extract_ipv4_addresses_from_onionoo(data):
    ipv4_addresses = set()  # Use a set to avoid duplicates

    for node in data['relays']:
        if 'or_addresses' in node and node['or_addresses']:
            for ip_port in node['or_addresses']:
                if ':' in ip_port:
                    ip = ip_port.split(':')[0]  # Get the IP address part
                    if is_valid_ipv4(ip):
                        ipv4_addresses.add(ip)

    return list(ipv4_addresses)  # Convert the set back to a list

def save_combined_ip_addresses(ipv4_addresses, output_filename):
    # Save the combined list of IP addresses to a file
    with open(output_filename, 'w') as file:
        for ipv4 in sorted(ipv4_addresses):  # Sort for better readability
            file.write(f"{ipv4}\n")

def main():
    # Set base URL for Tor exit list
    base_url = 'https://collector.torproject.org/recent/exit-lists/?C=M;O=D'
    
    try:
        # Get the latest exit list URL from the Tor Project
        latest_file_url = get_latest_exit_list_url(base_url)
        print(f'Fetching Tor exit nodes from collector.torproject.org ...')
        
        # Download the exit list file
        file_content, current_filename = download_exit_list(latest_file_url)

        # Extract IPv4 addresses from the Tor exit list file
        tor_exit_ips = extract_ipv4_addresses_from_tor(file_content)

        # Fetch all Tor nodes and extract their IP addresses
        print('Fetching Tor exit nodes from onionoo.torproject.org ...')
        node_data = fetch_all_tor_nodes()
        onionoo_ips = extract_ipv4_addresses_from_onionoo(node_data)

        # Combine all unique IP addresses
        combined_ips = set(tor_exit_ips) | set(onionoo_ips)  # Union of both sets

        # Create output filename with the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M_")
        output_filename = f"{current_datetime}_tor_exit_ips.txt"
        
        # Save all found IPs to a single output file
        save_combined_ip_addresses(combined_ips, output_filename)
        print(f'Saved {len(combined_ips)} unique Tor exit node IPv4 addresses to {output_filename}')

    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    main()
