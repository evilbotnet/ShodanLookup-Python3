import shodan
import argparse
import sqlite3
import time

# Interprets arguments. Database, API Key, and file containing IPs are required
parser = argparse.ArgumentParser()
parser.add_argument("-d", help="Database output", required=True)
parser.add_argument("-k", help="Shodan API Key", required=True)
parser.add_argument("-i", help="List of IP's 1 per line", required=True)
args = parser.parse_args()

def shodanQuery(iplist):
    for ip in iplist:
        #Attempts to retrieve value from DB. "Primary Key" is the IP address
        cursor.execute('SELECT * FROM shodan WHERE (ip_str=?)', (ip,))
        entry = cursor.fetchone()
        if entry is None:
            #If IP not in database, run shodan queries..
            print("Not found in db... Checking... {}".format(ip))
            try:
                host = api.host(ip)
                country = host['country_code']
                shodan_ip = host['ip_str']
                shodan_org = str(host.get('org', 'n/a'))
                shodan_os = str(host.get('os', 'n/a'))
                hostname = str(host.get('hostnames', 'n/a'))
                for item in host['data']:
                    shodan_ports = "Port: %s <br>Banner: %s <br>" % (item['port'], item['data'])
                print(shodan_ip)
                print(country)
                print(hostname)
                print(shodan_ports)
                cursor.execute('INSERT INTO shodan (ip_str, country_code, hostname, data, date) VALUES (?,?,?,?,?)',
                               (shodan_ip, country, str(hostname), str(shodan_ports),time.strftime("%H:%M:%S %d-%m-%Y")))
                conn.commit()
                print("New entry added")
            except shodan.APIError as e:
                #Shodan doesn't have all the answers.
                print(e)
                print("No information found for {}".format(ip))
            time.sleep(0.7)
        else:
            #Doesn't waste cycles/API usages if IP is already in DB.
            print("Already in DB.. Skipping {}".format(ip))


if __name__ =='__main__':
    api = shodan.Shodan(args.k)
    #Builds the output file if necessary
    conn = sqlite3.connect(args.d)
    conn.execute("CREATE TABLE IF NOT EXISTS shodan (ip_str str, country_code str, hostname str, data str, date text,"
                 "UNIQUE(ip_str))")
    cursor = conn.cursor()
    #Reads IP Addresses line-by-line into a list
    print("Loading content from {}...".format(args.i))
    list = args.i
    with open(list) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    shodanQuery(iplist=content)

