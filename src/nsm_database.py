# THIS WILL HOUSE UTILITIES AND OR FILES

# UI IMPORTS
from rich.console import Console


# ETC IMPORTS
from pathlib import Path
import json, requests, mmh3, re, threading, geoip2.database, os, sys, ipaddress
from datetime import datetime


LOCK = threading.Lock()
console = Console()




class Database:
    """This will hold database values"""


    # HOLD ALL ERRORS
    errors = 0
    

    # SET FROM main.py
    paths = False


    # VARS
    lookup         = False
    country        = False # FOR File_Saving
    api_key_ipinfo = False   
    reader_asn     = False
    reader_city    = False

    

    # PRESETS
    CRITICAL_INFRASTRUCTURE_PORTS = [
        # Web Services & Admin Panels
        80,      # HTTP
        443,     # HTTPS
        8080,    # HTTP Alternate
        8443,    # HTTPS Alternate
        8000,    # Common web panel
        8888,    # Alternate web panel

        # Remote Access
        22,      # SSH
        23,      # Telnet
        21,      # FTP
        3389,    # RDP
        5900,    # VNC

        # ICS/SCADA Protocols
        502,     # Modbus TCP (energy grid, industrial)
        20000,   # DNP3 (electric utility SCADA)
        102,     # Siemens S7 (industrial control)
        44818,   # EtherNet/IP (industrial automation)
        1911,    # Niagara Fox (building automation)
        47808,   # BACnet (building/facility automation)
        789,     # RedLion Crimson3
        4840,    # OPC UA (industrial data exchange)
        2404,    # IEC 60870-5-104 (power system control)

        # Databases
        3306,    # MySQL
        5432,    # PostgreSQL
        27017,   # MongoDB
        6379,    # Redis
        9200,    # Elasticsearch
        1433,    # MS SQL Server
        5984,    # CouchDB

        # Management & Monitoring
        161,     # SNMP
        623,     # IPMI
        8291,    # MikroTik Winbox
        7547,    # TR-069 (ISP remote mgmt)
        9000,    # Various management panels

        # VoIP/Telecom
        5060,    # SIP
        5061,    # SIP TLS
        1720,    # H.323

        # File Sharing
        445,     # SMB
        139,     # NetBIOS
        2049,    # NFS

        # Email
        25,      # SMTP
        110,     # POP3
        143,     # IMAP
        465,     # SMTPS
        993,     # IMAPS
        995,     # POP3S

        # Other Critical Services
        53,      # DNS
        123,     # NTP
        514,     # Syslog
        1883,    # MQTT
        5672,    # AMQP
        9092,    # Kafka
    ]

    DATABASE_PORTS = [
        3306,   # MySQL
        5432,   # PostgreSQL
        27017,  # MongoDB
        6379,   # Redis
        9200    # Elasticsearch
    ]

    CAMERA_PORTS = [
        80,      # HTTP web interface (most common camera login page)
        443,     # HTTPS web interface (secure camera panel)
        554,     # RTSP video stream (very high signal for cameras)
        8000,    # Hikvision / OEM camera management port
        8080,    # Alternate HTTP web interface
        37777,   # Dahua proprietary service port
        34567,   # Common on generic / cheap OEM IP cameras
        3702,    # ONVIF discovery (usually LAN, not internet)
        8443     # Alternate HTTPS web interface
    ]

    ROUTER_PORTS = [
        80,     # HTTP admin panel
        443,    # HTTPS admin panel
        8080,   # Alternate web admin
        8443,   # Alternate secure admin
        23,     # Telnet (legacy routers)
        22,     # SSH management
        7547,   # TR-069 (ISP remote management)
        8291    # MikroTik Winbox
    ]

    NAS_PORTS = [
        5000,   # Synology HTTP
        5001,   # Synology HTTPS
        9000,   # Various NAS web panels
        445,    # SMB file sharing
        139     # NetBIOS session service
    ]

    REMOTE_PORTS = [
        3389,   # RDP
        5900,   # VNC
        22,     # SSH
        21      # FTP
    ]

    IOT_PORTS = [
        1883,   # MQTT
        8883,   # Secure MQTT
        5683,   # CoAP
        5353    # mDNS (mostly LAN discovery)
    ]   


   
    paths_camera = [
         "/onvif/device_service",
        "/snapshot.jpg",
        "/video.cgi",
        "/ISAPI/System/status",
        "/cgi-bin/magicBox.cgi",
        "/doc/page/login.asp",
        "/web/cgi-bin/"
    ]

    paths_router = [
        "/",                 # title / server header
        "/login",            # common
        "/admin",            # common
        "/cgi-bin/",         # embedded web UIs
        "/HNAP1/",           # some consumer routers
        "/setup.cgi",        # older firmwares
        "/rom-0",            # legacy Zyxel-style misconfig (rare, but high signal)
        "/api/",             # modern web panels
    ]

    paths_nas = [
        "/",                       # landing page/title
        "/webman/index.cgi",       # Synology DSM (often redirects)
        "/auth.cgi",               # Synology auth endpoint (presence signal)
        "/cgi-bin/",               # QNAP/Synology patterns
        "/admin/",                 # generic NAS panels
    ]







    zone_to_country = {
        "af.zone": "Afghanistan",
        "ax.zone": "Aland Islands",
        "al.zone": "Albania",
        "dz.zone": "Algeria",
        "as.zone": "American Samoa",
        "ad.zone": "Andorra",
        "ao.zone": "Angola",
        "ai.zone": "Anguilla",
        "aq.zone": "Antarctica",
        "ag.zone": "Antigua and Barbuda",
        "ar.zone": "Argentina",
        "am.zone": "Armenia",
        "aw.zone": "Aruba",
        "au.zone": "Australia",
        "at.zone": "Austria",
        "az.zone": "Azerbaijan",
        "bs.zone": "Bahamas",
        "bh.zone": "Bahrain",
        "bd.zone": "Bangladesh",
        "bb.zone": "Barbados",
        "by.zone": "Belarus",
        "be.zone": "Belgium",
        "bz.zone": "Belize",
        "bj.zone": "Benin",
        "bm.zone": "Bermuda",
        "bt.zone": "Bhutan",
        "bo.zone": "Bolivia",
        "ba.zone": "Bosnia and Herzegovina",
        "bw.zone": "Botswana",
        "br.zone": "Brazil",
        "io.zone": "British Indian Ocean Territory",
        "bn.zone": "Brunei",
        "bg.zone": "Bulgaria",
        "bf.zone": "Burkina Faso",
        "bi.zone": "Burundi",
        "kh.zone": "Cambodia",
        "cm.zone": "Cameroon",
        "ca.zone": "Canada",
        "cv.zone": "Cape Verde",
        "ky.zone": "Cayman Islands",
        "cf.zone": "Central African Republic",
        "td.zone": "Chad",
        "cl.zone": "Chile",
        "cn.zone": "China",
        "cc.zone": "Cocos Islands",
        "co.zone": "Colombia",
        "km.zone": "Comoros",
        "cg.zone": "Congo",
        "cd.zone": "Democratic Republic of the Congo",
        "ck.zone": "Cook Islands",
        "cr.zone": "Costa Rica",
        "ci.zone": "Cote d'Ivoire",
        "hr.zone": "Croatia",
        "cu.zone": "Cuba",
        "cy.zone": "Cyprus",
        "cz.zone": "Czech Republic",
        "dk.zone": "Denmark",
        "dj.zone": "Djibouti",
        "dm.zone": "Dominica",
        "do.zone": "Dominican Republic",
        "ec.zone": "Ecuador",
        "eg.zone": "Egypt",
        "sv.zone": "El Salvador",
        "gq.zone": "Equatorial Guinea",
        "er.zone": "Eritrea",
        "ee.zone": "Estonia",
        "et.zone": "Ethiopia",
        "fk.zone": "Falkland Islands",
        "fo.zone": "Faroe Islands",
        "fj.zone": "Fiji",
        "fi.zone": "Finland",
        "fr.zone": "France",
        "gf.zone": "French Guiana",
        "pf.zone": "French Polynesia",
        "ga.zone": "Gabon",
        "gm.zone": "Gambia",
        "ge.zone": "Georgia",
        "de.zone": "Germany",
        "gh.zone": "Ghana",
        "gi.zone": "Gibraltar",
        "gr.zone": "Greece",
        "gl.zone": "Greenland",
        "gd.zone": "Grenada",
        "gp.zone": "Guadeloupe",
        "gu.zone": "Guam",
        "gt.zone": "Guatemala",
        "gn.zone": "Guinea",
        "gw.zone": "Guinea-Bissau",
        "gy.zone": "Guyana",
        "ht.zone": "Haiti",
        "va.zone": "Vatican City",
        "hn.zone": "Honduras",
        "hk.zone": "Hong Kong",
        "hu.zone": "Hungary",
        "is.zone": "Iceland",
        "in.zone": "India",
        "id.zone": "Indonesia",
        "ir.zone": "Iran",
        "iq.zone": "Iraq",
        "ie.zone": "Ireland",
        "im.zone": "Isle of Man",
        "il.zone": "Israel",
        "it.zone": "Italy",
        "jm.zone": "Jamaica",
        "jp.zone": "Japan",
        "je.zone": "Jersey",
        "jo.zone": "Jordan",
        "kz.zone": "Kazakhstan",
        "ke.zone": "Kenya",
        "ki.zone": "Kiribati",
        "kp.zone": "North Korea",
        "kr.zone": "South Korea",
        "kw.zone": "Kuwait",
        "kg.zone": "Kyrgyzstan",
        "la.zone": "Laos",
        "lv.zone": "Latvia",
        "lb.zone": "Lebanon",
        "ls.zone": "Lesotho",
        "lr.zone": "Liberia",
        "ly.zone": "Libya",
        "li.zone": "Liechtenstein",
        "lt.zone": "Lithuania",
        "lu.zone": "Luxembourg",
        "mo.zone": "Macao",
        "mk.zone": "North Macedonia",
        "mg.zone": "Madagascar",
        "mw.zone": "Malawi",
        "my.zone": "Malaysia",
        "mv.zone": "Maldives",
        "ml.zone": "Mali",
        "mt.zone": "Malta",
        "mh.zone": "Marshall Islands",
        "mq.zone": "Martinique",
        "mr.zone": "Mauritania",
        "mu.zone": "Mauritius",
        "yt.zone": "Mayotte",
        "mx.zone": "Mexico",
        "fm.zone": "Micronesia",
        "md.zone": "Moldova",
        "mc.zone": "Monaco",
        "mn.zone": "Mongolia",
        "me.zone": "Montenegro",
        "ms.zone": "Montserrat",
        "ma.zone": "Morocco",
        "mz.zone": "Mozambique",
        "mm.zone": "Myanmar",
        "na.zone": "Namibia",
        "nr.zone": "Nauru",
        "np.zone": "Nepal",
        "nl.zone": "Netherlands",
        "nc.zone": "New Caledonia",
        "nz.zone": "New Zealand",
        "ni.zone": "Nicaragua",
        "ne.zone": "Niger",
        "ng.zone": "Nigeria",
        "nu.zone": "Niue",
        "nf.zone": "Norfolk Island",
        "mp.zone": "Northern Mariana Islands",
        "no.zone": "Norway",
        "om.zone": "Oman",
        "pk.zone": "Pakistan",
        "pw.zone": "Palau",
        "ps.zone": "Palestine",
        "pa.zone": "Panama",
        "pg.zone": "Papua New Guinea",
        "py.zone": "Paraguay",
        "pe.zone": "Peru",
        "ph.zone": "Philippines",
        "pl.zone": "Poland",
        "pt.zone": "Portugal",
        "pr.zone": "Puerto Rico",
        "qa.zone": "Qatar",
        "re.zone": "Reunion",
        "ro.zone": "Romania",
        "ru.zone": "Russia",
        "rw.zone": "Rwanda",
        "kn.zone": "Saint Kitts and Nevis",
        "lc.zone": "Saint Lucia",
        "pm.zone": "Saint Pierre and Miquelon",
        "vc.zone": "Saint Vincent and the Grenadines",
        "ws.zone": "Samoa",
        "sm.zone": "San Marino",
        "st.zone": "Sao Tome and Principe",
        "sa.zone": "Saudi Arabia",
        "sn.zone": "Senegal",
        "rs.zone": "Serbia",
        "sc.zone": "Seychelles",
        "sl.zone": "Sierra Leone",
        "sg.zone": "Singapore",
        "sk.zone": "Slovakia",
        "si.zone": "Slovenia",
        "sb.zone": "Solomon Islands",
        "so.zone": "Somalia",
        "za.zone": "South Africa",
        "es.zone": "Spain",
        "lk.zone": "Sri Lanka",
        "sd.zone": "Sudan",
        "sr.zone": "Suriname",
        "sz.zone": "Eswatini",
        "se.zone": "Sweden",
        "ch.zone": "Switzerland",
        "sy.zone": "Syria",
        "tw.zone": "Taiwan",
        "tj.zone": "Tajikistan",
        "tz.zone": "Tanzania",
        "th.zone": "Thailand",
        "tl.zone": "Timor-Leste",
        "tg.zone": "Togo",
        "tk.zone": "Tokelau",
        "to.zone": "Tonga",
        "tt.zone": "Trinidad and Tobago",
        "tn.zone": "Tunisia",
        "tr.zone": "Turkey",
        "tm.zone": "Turkmenistan",
        "tc.zone": "Turks and Caicos Islands",
        "tv.zone": "Tuvalu",
        "ug.zone": "Uganda",
        "ua.zone": "Ukraine",
        "ae.zone": "United Arab Emirates",
        "gb.zone": "United Kingdom",
        "us.zone": "United States",
        "um.zone": "US Minor Outlying Islands",
        "uy.zone": "Uruguay",
        "uz.zone": "Uzbekistan",
        "vu.zone": "Vanuatu",
        "ve.zone": "Venezuela",
        "vn.zone": "Vietnam",
        "vg.zone": "British Virgin Islands",
        "vi.zone": "US Virgin Islands",
        "wf.zone": "Wallis and Futuna",
        "ye.zone": "Yemen",
        "zm.zone": "Zambia",
        "zw.zone": "Zimbabwe",
    }
            




   
    @classmethod
    def _check_paths(cls, ip, port, CONSOLE=console, timeout=1, errors=False):
        """This will check path signatures"""

        if not cls.paths: return
        space = "    "
        c1 = "bold red"
        c2 = "bold yellow"
        c4 = "bold green"

        
        for path in cls.paths:

            try:

                url = f"http://{ip}{path}"

                response = requests.get(url=url, timeout=timeout)
                headers = response.headers

                if response.status_code in [200,204]:

                     


                    favicon = mmh3.hash(response.content)
                    title = False
                    match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE | re.DOTALL)
                    if match: title = match.group(1).strip()
                    status = response.status_code
                    redirect = response.url if response.url != url else False
                    content_length = len(response.text) or False
                    server = headers.get("Server", False)
                    x_powered_by = headers.get("X-Powered-By", False)

                    with LOCK:
                        CONSOLE.print(f"\n[{c4}][+] Active IP:[/{c4}] [{c2}]{ip}[/{c2}]:{port}")
                        CONSOLE.print(
                            f"{space}[{c4}][+] Directory:[{c2}] {url}",
                            f"\n{space}[{c4 if status else c1}][+] Status:[{c2}] {status}",
                            f"\n{space}[{c4 if title else c1}][+] Title:[{c2}] {title}",
                            f"\n{space}[{c4 if server else c1}][+] Server:[{c2}] {server}",
                            f"\n{space}[{c4 if redirect else c1}][+] Redirect:[{c2}] {redirect}",
                            f"\n{space}[{c4 if content_length else c1}][+] Content-Length:[{c2}] {content_length}",
                            f"\n{space}[{c4 if x_powered_by else c1}][+] Powered-by:[{c2}] {x_powered_by}",
                            f"\n{space}[{c4 if favicon else c1}][+] Favicon:[{c2}] {favicon}"
                        )
            
            except Exception as e: 
                Database.errors += 1
                if errors: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")


    @classmethod
    def _get_geo_info_local(cls, ip, CONSOLE=console):
        """This method will be used to get our own in house geo ip info"""

        # COLORS
        c4 = "bold green"
        c5 = "white"
        space = "    "

        try:
            if not cls.reader_asn:
                p1 = "geo_lookup"
                path_asn  = str(Path(__file__).parent.parent / "database" /  p1 / "L-ASN" / "L-ASN.mmdb" )
                path_city = str(Path(__file__).parent.parent / "database" /  p1 / "L-City" / "L-City.mmdb" )
                cls.reader_asn  = geoip2.database.Reader(path_asn)
                cls.reader_city = geoip2.database.Reader(path_city)
            


            asn_response  = cls.reader_asn.asn(ip)
            city_response = cls.reader_city.city(ip)

            country  = city_response.country.name or False
            region   = city_response.subdivisions.most_specific.name or False
            city     = city_response.city.name or False
            postal   = city_response.postal.code or False
            timezone = city_response.location.time_zone or False

            org = asn_response.autonomous_system_organization or False
                    

            
        
            CONSOLE.print(
                f" [{c4}]{space}[+] Country:[{c5}] {country}"
                f"\n [{c4}]{space}[+] region:[{c5}] {region}"
                f"\n [{c4}]{space}[+] city:[{c5}] {city}"
                f"\n [{c4}]{space}[+] org:[{c5}] {org}"
                f"\n [{c4}]{space}[+] postal:[{c5}] {postal}"
                f"\n [{c4}]{space}[+] timezone:[{c5}] {timezone}"
            )

 
        except Exception as e: 
            Database.errors += 1
            CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

    
    @classmethod
    def _get_geo_info_ipinfo(cls, ip, CONSOLE=console, timeout=3, verbose=False):
        """This method will be responsible for grabbing the geo info on said ip"""

        # COLORS
        c1 = "bold red"
        c4 = "bold green"
        c5 = "white"
        space = "    "

        if cls.api_key_ipinfo:

            api_key =  cls.api_key_ipinfo   
            url     = f"https://ipinfo.io/{ip}/json/?token={api_key}"
        
        else: url   =  f"https://ipinfo.io/{ip}/json"



        try:

            response = requests.get(url=url, timeout=timeout)
            data = response.json()
            text = response.text


            if response.status_code in [200,204]:

                if verbose: CONSOLE.print(data)

                country   = data.get("country",  False)  
                region    = data.get("region",   False)
                city      = data.get("city",     False)
                org       = data.get("org",      False)
                postal    = data.get("postal",   False)
                timezone  = data.get("timezone", False)


                CONSOLE.print(
                    f" [{c4}]{space}[+] Country:[{c5}] {country}"
                    f"\n [{c4}]{space}[+] region:[{c5}] {region}"
                    f"\n [{c4}]{space}[+] city:[{c5}] {city}"
                    f"\n [{c4}]{space}[+] org:[{c5}] {org}"
                    f"\n [{c4}]{space}[+] postal:[{c5}] {postal}"
                    f"\n [{c4}]{space}[+] timezone:[{c5}] {timezone}"
                )
            

            else:

                CONSOLE.print(f" [{c1}]{space}[-] IPInfo Lookup Failed :[{c5}] {text}")
        

        except Exception:
            cls.errors += 1


    @classmethod
    def validate_country(cls, country, CONSOLE=console, verbose=True):
        """This will be used to validate user inputted country"""


        path_ip_blocks = Path(__file__).parent.parent / "database" / "ip_blocks"
        path_country   = path_ip_blocks / f"{country}.txt"

        if not path_ip_blocks.exists():
            CONSOLE.print("\n[bold red][-] Seems like your missing the ip_blocks directory, please check Documentation for fix")
            sys.exit()

        if path_country.exists():
            if verbose: CONSOLE.print(f"[bold green][+] Found country.txt:[/bold green] {path_country}")
            cls.country = country
            return path_country

        CONSOLE.print("\n[bold red][-] Invalid country given, please check documentation if your having trouble finding your country")
        sys.exit()
  

    @classmethod
    def validate_asn(cls, country, asns, CONSOLE=console):
        """This will be used to validate user inputted country"""


        path_asn = Path(__file__).parent.parent / "database" / "asns" / f"{country}.json"
        valid_asn  = []

        if path_asn.exists():

            CONSOLE.print(f"[bold green][+] Found asn.json:[/bold green] {path_asn}\n")

            with open(path_asn) as file: data = json.load(file)

            presets = [int(key) for key in data]

            for asn in asns:
                
                if asn in presets: CONSOLE.print(f"[bold green][+] Validated ASN:[yellow] {asn}"); valid_asn.append(asn)
                else: CONSOLE.print(f"[bold red][-] Failed to Validated ASN:[yellow] {asn}")
            
            return path_asn, valid_asn
        
        
        CONSOLE.print("\n[bold red][-] Seems like your missing the asns directory, please check Documentation for fix")
        sys.exit()



    @classmethod
    def get_ip_block(cls, country, CONSOLE=console, verbose=False):
        """This method will be resposnible for getting the block for country"""




        path = str(Database.validate_country(country=country, CONSOLE=CONSOLE))
        blocks = []

        try:

            with open(path) as file: 

                for block in file:
                    t = block.strip().split("\t"); t = ''.join(t)
                    blocks.append(t)
            
            if verbose: CONSOLE.print(blocks)
            return blocks
        

        except Exception as e: 
            Database.errors += 1
            CONSOLE.print(f"[bold red]Exception Error:[bold yellow] {e}")

    
     
    @classmethod
    def get_asn(cls, country, asns, CONSOLE=console, verbose=True):
        """This is going to be cool // pass the country and then filter through said country for asns"""


        # COLORS
        c1 = "bold red"
        c4 = "bold green"
        c5 = "white"
        c6 = "yellow"
        total_blocks = []


        try: asns  = [int(asn) for asn in asns.split(',')]
        except Exception: asns = list(asns)      


        Database.validate_country(country=country, CONSOLE=console, verbose=False)
        path_asn, asns = Database.validate_asn(country=country, asns=asns, CONSOLE=console)


        base     = {}



        CONSOLE.print(f"\n[yellow][*] Target asns:[/yellow] {asns}")
        


        try:


            with open(path_asn) as file: data = json.load(file)
            CONSOLE.print("[yellow][+] Pulling blocks <-- asn(s), Please standby\n") 
                


            for key, value in data.items():
                

                asn = int(key)
                country_code = value["country_code"]
                description  = value["description"]
                handle       = value["handle"]

                
                if asn in asns:


                    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"

                    response = requests.get(url=url)
                    data     = response.json()
                    block    = []
                    
                    if response.status_code in [200, 204]:
                        
                        prefixes = data["data"]["prefixes"]

                        for cidr in prefixes:

                            prefix = cidr['prefix']
                            

                            try:
                                if ipaddress.IPv4Network(prefix):

                                    block.append(prefix);  total_blocks.append(prefix)
                            
                            except Exception as e: CONSOLE.print(f"IPV6: {e}")
                                
                        base[asn] = {
                            "asn": asn,
                            "country_code": country_code,
                            "description": description,
                            "handle": handle,
                            "block": block
                        }

                        CONSOLE.print(
                            f"[{c1}]{"=" * 25}"
                            f"\n[{c4}][+] asn:[{c6}] {asn}"
                            f"\n[{c4}][+] country_code:[{c6}] {country_code}"
                            f"\n[{c4}][+] description:[{c6}] {description}"
                            f"\n[{c4}][+] handle:[{c6}] {handle}"
                            f"\n[{c4}][+] prefix(s):[{c5}] {'\n   '.join(block)}"
                            f"\n[{c1}]{"=" * 25}"
                        )
            

            return base, total_blocks
    
        
        except Exception as e: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")




    # WARNING
    @classmethod
    def _download_ip_blocks_for_each_country(cls):
        """This will be a one time use method to automate downloading blocks for each country from ipdeny.com"""



        # WARNING: This is not to be used more than once.
        # If you git cloned this program these files should already be within the database/ip_blocks directory.

        try:

            # 233 COUNTRYS

            ip_block_dir = str(Path(__file__).parent.parent / "database" / "ip_blocks")
            os.chdir(ip_block_dir)
            console.print(f"[bold green][+] Successfully changed DIR to: {ip_block_dir}")
            
            for zone in cls.zone_to_country:

                url = f"https://www.ipdeny.com/ipblocks/data/countries/{zone}"
                country  = cls.zone_to_country.get(zone, False)
                if not country: continue
                safe_country = country.replace(" ", "_")
                
                response = requests.get(url=url)
                
                if response.status_code in [200, 204]:
                    with open(f"{safe_country}.txt", "w") as file: file.write(str(response.text))
                    console.print(f"[bold green][+] Successfully downloaded:[bold yellow] {country}/{zone} <-> {url}")
                
        except Exception as e: console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")


    @classmethod
    def _download_asns_within_each_country(cls):
        """This will be used to download asns for each domain within a country"""

        import csv

        try:

   
            asn_file = str(Path(__file__).parent.parent / "database" / "asns" / "info.txt")

            console.print(f"[bold green][+] Reading ASN database from: {asn_file}")
            


            for code in cls.zone_to_country:


                asns = {}
                country = cls.zone_to_country.get(code, False)
                if not country: continue
                country = country.replace(" ", "_")
                code = code.split('.')[0]

                with open(asn_file) as file:
                    reader = csv.DictReader(file)




                    for row in reader:
                        if row['country-code'].lower() == code:
                            

                            # DATA
                            country_code = row["country-code"]
                            asn          = row["asn"]
                            description  = row["description"]
                            handle       = row["handle"]

                            data = {
                                "country_code": country_code,
                                "asn": asn,
                                "description": description,
                                "handle": handle
                            }

                            asns[row["asn"]] = data
                
                save_file = str(Path(__file__).parent.parent / "database" / "asns" / f"{country}.json")
                with open(save_file, "w") as file:
                    json.dump(asns, file, indent=4)
                    console.print(f"[bold green][+] Successfully saved asns: {save_file}")
                    
                
      
                console.print(f"[bold green][+] Found {len(asns)} ASNs for country code: {code}")





        

        except Exception as e: console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")
    

    @staticmethod
    def _download_ip_blocks_for_asn():
        """This will download all ip blocks for asn given"""



        try:

            asns = [
                "AS5661"
            ]
            

            package = {}

            ip_block_dir = str(Path(__file__).parent.parent / "database" / "asns" / "US")
            os.chdir(ip_block_dir)
            console.print(f"[bold green][+] Successfully changed DIR to: {ip_block_dir}")

            for asn in asns:

                url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"

                response = requests.get(url=url)
                data = response.json()

                if response.status_code in [200, 204]:

                    prefixes = data["data"]["prefixes"]
                    saved    = []

                    for cidr in prefixes:
                        prefix = cidr['prefix']
                        console.print(f"[bold green] Found Block:[/bold green] {prefix}")
                        saved.append(prefix)

                    package[asn] = saved

                    with open(f"{asn}.json", "w") as file:
                        json.dump(package, file, indent=4)
                    console.print(f"[bold green][+] Successfully downloaded:[bold yellow] {asn}  <-> {url}")
            

        
        except Exception as e: console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")



    @classmethod
    def get_total_ips(cls, blocks):
        """This will be for getting total ip in ip block(s)"""


        total = 0


        for block in blocks:
            network = ipaddress.IPv4Network(block)
            total += network.num_addresses
        

        
        console.print(f"[bold red][*] Total IPv4 Blocks:[/bold red] {len(blocks)}")
        console.print(f"[bold red][*] Total IPv4 Addresses:[/bold red] {total}")





    @classmethod
    def main(cls, ip, port, CONSOLE=console):
        """This will be the main method for spawning co-methods for Database"""


        # COLORS
        c2 = "bold yellow"
        c4 = "bold green"

        with LOCK:
            CONSOLE.print(f"\n[{c4}][+] Active IP:[/{c4}] [{c2}]{ip}[/{c2}]:{port}")
            if   cls.lookup == "local":  Database._get_geo_info_local(ip=ip, CONSOLE=CONSOLE)
            elif cls.lookup == "ipinfo": Database._get_geo_info_ipinfo(ip=ip, CONSOLE=CONSOLE)
        
            if Database.paths: Database._check_paths(ip=ip, port=port, CONSOLE=CONSOLE)






class File_Saver:
    """This class will save files"""


    path = False
    ips_saved = set()



    @classmethod
    def push_ips_found(cls, data, CONSOLE, save_name=False, verbose=False):
        """This will push current set of ips"""



        if not cls.path: 

            
            try:
                path = Path(__file__).parent.parent / "database" / "saved_ips"

                if path.exists():


                    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                    
                    if save_name:          cls.path = path / str(save_name)
                    elif Database.country: cls.path = path / f"{Database.country}_{timestamp}.txt"
                    else:                  cls.path = path / f"{timestamp}.txt"

                    CONSOLE.print(f"[bold green][+] File Path successfully made:[/bold green] {cls.path}")


            except Exception as e: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")
            
            return
                

    
        try:
            with LOCK:
                ips = []
                for ip in data:
                    if ip not in cls.ips_saved: ips.append(ip); cls.ips_saved.add(ip)

                if not ips: return
                clean = "\n".join(ips) + "\n"


            with open(str(cls.path), "a") as file: file.write(clean)
            if verbose: CONSOLE.print("[bold green][+] Successfully pushed new info")

        
        except FileNotFoundError as e:
            CONSOLE.print(f"[bold red][-] FileNotFoundError:[bold yellow] {e}")
            with open(str(cls.path), "w") as file:
                file.write("\n".join(data) + "\n")
        
        except Exception as e: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

