import dpkt
import socket
import geoip2.database

# Initialize the GeoIP database
reader = geoip2.database.Reader('GeoLite2-City.mmdb')


def main():
    # Open a PCAP file for reading
    filename = 'wire.pcap' #Change to file name
    with open(filename, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        kml_content, visited_cities = plot_ips(pcap)
        save_to_kml(kml_content)
        print_unique_cities(visited_cities)


def plot_ips(pcap):
    kml_pts = ''
    visited_cities = set()

    for (ts, buf) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
            kml, dst_city = ret_kml(dst, src, visited_cities)
            if kml:
                kml_pts += kml
        except Exception as e:
            # Handle specific exceptions if needed
            #print(f"Exception in plot_ips: {e}")
            pass
    return kml_pts, visited_cities


def ret_kml(dst_ip, src_ip, visited_cities):
    try:
        dst_response = reader.city(dst_ip)
        src_response = reader.city('143.170.82.70')  # Replace with an actual IP address

        dst_city = dst_response.city.name or dst_response.country.name
        src_city = src_response.city.name

        print(f"Destination IP: {dst_ip}, City: {dst_city}")
        print(f"Source IP: 143.170.82.70, City: {src_city}")

        # Return KML content for the placemark if it's a new city
        if dst_city and dst_city not in visited_cities:
            visited_cities.add(dst_city)
            return f"<Placemark><name>{dst_city}</name><Point><coordinates>{dst_response.location.longitude},{dst_response.location.latitude},0</coordinates></Point></Placemark>", dst_city
        else:
            return '', ''

    except geoip2.errors.AddressNotFoundError:
        # Handle the case where the GeoIP data is not available
        return '', ''
    except Exception as e:
        # Handle other exceptions
        #print(f"Exception in ret_kml: {e}")
        return '', ''


def save_to_kml(kml_content):
    kml_header = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                  '<kml xmlns="http://www.opengis.net/kml/2.2">\n' \
                  '<Document>\n'
    kml_footer = '</Document>\n</kml>'
    with open('visited_cities.kml', 'w') as kml_file:
        kml_file.write(kml_header + kml_content + kml_footer)
    print("KML file saved as 'visited_cities.kml'")


def print_unique_cities(visited_cities):
    print("\nUnique Cities Visited:")
    for city in sorted(visited_cities):
        print(city)
    print(f"\nTotal number of unique cities visited: {len(visited_cities)}")


if __name__ == "__main__":
    main()