# Import necessary libraries
import dpkt
import socket
import geoip2.database
import escape

# Initialize the GeoIP database
reader = geoip2.database.Reader('GeoLite2-City.mmdb')
# Define the main function
def main():

    # Open a PCAP file for reading
    filename='wire.pcap'
    f = open(filename, 'rb')
    pcap = dpkt.pcap.Reader(f)
    plotIPs(pcap)
    # Define KML header with a style for the KML file
    kmlheader = '<?xml version="1.0" encoding="UTF-8"?> \n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n' \
                '<Style id="transBluePoly">' \
                '<LineStyle>' \
                '<width>1.5</width>' \
                '<color>501400E6</color>' \
                '</LineStyle>' \
                '</Style>'

    # Define KML footer
    kmlfooter = '</Document>\n</kml>\n'
    # Create KML document by combining header, IP plotting, and footer
    kmldoc = kmlheader + plotIPs(pcap) + kmlfooter

    # Print the KML document
    print(kmldoc)

# Define a function to plot IP addresses in KML format
def plotIPs(pcap):
    kmlPts = ''
    for (ts, buf) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
            KML = retKML(dst, src)
            kmlPts = kmlPts + KML
        except:
            pass
    return kmlPts

# Define a function to generate KML for a given source and destination IP
def retKML(dstip, srcip):
    try:
        dst_response = reader.city(dstip)
        src_response = reader.city('143.170.82.70')  # Replace with an actual IP address

        dst_city = dst_response.city.name
        if(dst_city == 'None'):
            dst_city = dst_response.country.name
        src_city = src_response.city.name

       #dst_longitude = dst_response.location.longitude
        #dst_latitude = dst_response.location.latitude
        #src_longitude = src_response.location.longitude
        #src_latitude = src_response.location.latitude

        print(f"Destination IP: {dstip}, City: {dst_city}")
        print(f"Source IP: 143.170.82.70, City: {src_city}")

        #kml = (
        #    '<Placemark>\n'
        #    '<name>%s</name>\n'
        #    '<extrude>1</extrude>\n'
        #    '<tessellate>1</tessellate>\n'
        #    '<styleUrl>#transBluePoly</styleUrl>\n'
       #     '<LineString>\n'
       #     '<coordinates>%f,%f\n%f,%f</coordinates>\n'
        #    '</LineString>\n'
        #    '</Placemark>\n'
       # ) % (escape(dstip), dst_longitude, dst_latitude, src_longitude, src_latitude)

        #return kml

    except geoip2.errors.AddressNotFoundError:
        # Handle the case where the GeoIP data is not available
        return ''
    except Exception as e:
        # Handle other exceptions
        print(f"Exception in retKML: {e}")
        return ''

if __name__ == "__main__":
    main()