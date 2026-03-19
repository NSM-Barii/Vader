# THIS MODULE WILL RUN MODULER CODE FROM HERE


# ETC IMPORTS
import argparse, sys


# NSM IMPORTS
from nsm_vars import (
    console,
    CRITICAL_INFRASTRUCTURE_PORTS,
    DATABASE_PORTS,
    CAMERA_PORTS,
    ROUTER_PORTS,
    NAS_PORTS,
    REMOTE_PORTS,
    IOT_PORTS,
    PATHS_CAMERA,
    PATHS_ROUTER,
    PATHS_NAS,
)
from nsm_scanner import Mass_IP_Scanner
from nsm_database import Database
from nsm_filesaver import File_Saver


# UI IMPORTS
from rich.panel import Panel


class Main:
    """This wil launch program wide logic"""

    data = (
        "\n [bold cyan]Mass IP Scanning Framework[/bold cyan]"
        "\n\n   [bold yellow]Find Vulnerable Devices[/bold yellow]"
        "\n\n    [bold magenta]Made by NSM-Barii[/bold magenta]\n"
    )

    panel = Panel(renderable=data, expand=False, style="bold red")

    parser = argparse.ArgumentParser(
        description="Mass IP Scanning framework meant to find vulnerable devices left uncheck open to the internet"
    )

    parser.add_argument("-p", help="Port to scan.")
    parser.add_argument("-t", help="Maximum number of threads to spawn.")

    parser.add_argument(
        "--save", action="store_true", help="Save all active IPs to database/ips.txt."
    )
    parser.add_argument("--x", help="Use this to set a custom file name")

    parser.add_argument("--country", help="Only create IP Blocks within x Country")
    parser.add_argument(
        "--asn",
        help="Pass asn value(s) Example: 215892, 214735, 214145, 213727, 212056",
    )
    parser.add_argument(
        "--bloom-size",
        help="BloomFilter capacity for global scans (default: 100000000). Warning: Higher values use more memory.",
    )

    parser.add_argument(
        "--geo", choices=["local", "ipinfo"], help="Enable IP geolocation lookup."
    )
    parser.add_argument(
        "--ipinfo", help="Optional ipinfo.io API key. Defaults to none."
    )

    parser.add_argument(
        "--iot", action="store_true", help="Scan for IoT devices (MQTT, CoAP, mDNS)."
    )
    parser.add_argument(
        "--nas",
        action="store_true",
        help="Scan for NAS devices (SMB, Synology, web panels).",
    )
    parser.add_argument(
        "--camera",
        action="store_true",
        help="Scan for IP cameras (RTSP, ONVIF, web interfaces).",
    )
    parser.add_argument(
        "--router",
        action="store_true",
        help="Scan for routers and network infrastructure (admin panels, SSH, Telnet, TR-069).",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Scan for remote access services (RDP, VNC, SSH, FTP).",
    )
    parser.add_argument(
        "--database",
        action="store_true",
        help="Scan for open databases (3306, 5432, 27017, 6379, 9200).",
    )

    parser.add_argument(
        "--paths",
        help="Manually set path for directory bruteforcing (nas, router, camera).",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        console.print(panel)
        parser.print_help()
        exit()

    # REQUIRED VARS
    port = args.p or False
    max_threads = args.t or 250

    # ADDITIONS
    country = args.country or False
    asn = args.asn or False
    bloom_size = int(args.bloom_size) if args.bloom_size else 100000000
    lookup = args.geo or False
    api_key_ipinfo = args.ipinfo or False
    save = args.save or False
    save_name = args.x or False

    # WARNING
    if not country:
        console.print(
            "\n[bold red][!] WARNING:[/bold red] [bold yellow]Scanning without --country will use a 100M BloomFilter limit."
        )
        console.print(
            "[bold yellow]    After 100M IPs, duplicates may be scanned. Use --country for memory-efficient scanning."
        )
        console.print(
            "[bold yellow]    Or increase with --bloom-size (e.g., --bloom-size 500000000) but this uses more RAM.\n"
        )

    # PRESET OPTIONS
    iot = args.iot or False
    nas = args.nas or False
    router = args.router or False
    remote = args.remote or False
    camera = args.camera or False
    database = args.database or False

    # FOR PRESETS
    paths = args.paths or False

    # IRANIAN CRITICAL INFRASTRUCTURE ASN SHORTCUTS (must come before port assignment)
    # TIER 1: CRITICAL INFRASTRUCTURE (Energy, Power Grid, Major Telecom, Transport)
    if asn == "1":
        asn = "5542,6736,21170,31303,34837,35285,39200,42143,42750,42867,42907,43358,44244,44436,47603,48159,49666,50722,50992,51119,51168,51554,51732,52196,57218,57577,58169,59654,59961,60605,62039,197207,199633,200376,201442,202788,203026,205490,205899,206929,208072,209079,214419,214737"
        save = True
        save_name = "iran_ips_critical_infrastructure.txt"

    # TIER 2: INTELLIGENCE & DEFENSE RESEARCH (Universities with Strategic Programs)
    elif asn == "2":
        asn = "12660,29068,29577,41620,47981,48898,49792,57563,59794,61239"
        save = True
        save_name = "iran_ips_defense_research.txt"

    # TIER 3: INFORMATION & PROPAGANDA (State Media, Broadcasting)
    elif asn == "3":
        asn = "42586,44609,47188,204999"
        save = True
        save_name = "iran_ips_state_media.txt"

    # TIER 4: FINANCIAL (Major Banks, Payment Systems)
    elif asn == "4":
        asn = "16018,31182,34871,35615,41061,42990,47817,49433,50855,51460,51618,51785,52070,57241,57574,59754,60407,60516,61250,62238,203162,208493,208651,209941,210470,213682,213872,213916,215700"
        save = True
        save_name = "iran_ips_financial.txt"

    # SET CONSTANTS
    Mass_IP_Scanner.country = country
    Mass_IP_Scanner.asn = asn
    Mass_IP_Scanner.save = save
    Mass_IP_Scanner.save_name = save_name
    Mass_IP_Scanner.bloom_size = bloom_size

    # SET FILE_SAVER COUNTRY
    File_Saver.country = country

    # ASSIGN PRESETS
    if iot:
        port = IOT_PORTS
    elif nas:
        port = NAS_PORTS
        Database.paths = PATHS_NAS
    elif router:
        port = ROUTER_PORTS
        Database.paths = PATHS_ROUTER
    elif remote:
        port = REMOTE_PORTS
    elif camera:
        port = CAMERA_PORTS
        Database.paths = PATHS_CAMERA
    elif database:
        port = DATABASE_PORTS

    if port == "1":
        port = CRITICAL_INFRASTRUCTURE_PORTS

    if paths:
        if paths == "nas":
            Database.paths = PATHS_NAS
        elif paths == "router":
            Database.paths = PATHS_ROUTER
        elif paths == "camera":
            Database.paths = PATHS_CAMERA

    Database.lookup = lookup
    Database.api_key_ipinfo = api_key_ipinfo

    c1 = "red"
    c4 = "bold yellow"

    stats = (
        f"[{c1}][+] Port(s):[{c4}] {port}"
        f"\n[{c1}] [+] Max Workers:[{c4}] {max_threads}"
        f"\n[{c1}] [+] File Saving:[{c4}] {save}"
        f"\n[{c1}] [+] GEO Lookup:[{c4}] {lookup}"
        f"\n[{c1}] [+] API Key:[{c4}] {api_key_ipinfo}"
    )

    console.print(
        f"[{c1}]=========   CONSTANTS   =========\n",
        stats,
        f"\n[{c1}]=================================",
    )

    Mass_IP_Scanner._main(port=port, threads=max_threads)
