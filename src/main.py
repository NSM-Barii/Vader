import argparse
import sys

from rich.console import Console
from rich.panel import Panel

from nsm_scanner import Mass_IP_Scanner
from nsm_database import Database

console = Console()

IRAN_PRESETS = {
    "1": {
        "name": "iran_ips_critical_infrastructure.txt",
        "asn": "5542,6736,21170,31303,34837,35285,39200,42143,42750,42867,42907,43358,44244,44436,47603,48159,49666,50722,50992,51119,51168,51554,51732,52196,57218,57577,58169,59654,59961,60605,62039,197207,199633,200376,201442,202788,203026,205490,205899,206929,208072,209079,214419,214737",
    },
    "2": {
        "name": "iran_ips_defense_research.txt",
        "asn": "12660,29068,29577,41620,47981,48898,49792,57563,59794,61239",
    },
    "3": {
        "name": "iran_ips_state_media.txt",
        "asn": "42586,44609,47188,204999",
    },
    "4": {
        "name": "iran_ips_financial.txt",
        "asn": "16018,31182,34871,35615,41061,42990,47817,49433,50855,51460,51618,51785,52070,57241,57574,59754,60407,60516,61250,62238,203162,208493,208651,209941,210470,213682,213872,213916,215700",
    },
}

PORT_PRESETS = {
    "1": lambda: Database.CRITICAL_INFRASTRUCTURE_PORTS,
}

DEVICE_PRESETS = {
    "iot":      lambda: (Database.IOT_PORTS, None),
    "nas":      lambda: (Database.paths_nas, Database.paths_nas),
    "router":   lambda: (Database.ROUTER_PORTS, Database.paths_router),
    "remote":   lambda: (Database.REMOTE_PORTS, None),
    "camera":   lambda: (Database.CAMERA_PORTS, Database.paths_camera),
    "database": lambda: (Database.DATABASE_PORTS, None),
}

PATH_MAP = {
    "nas": lambda: Database.paths_nas,
    "router": lambda: Database.paths_router,
    "camera": lambda: Database.paths_camera,
}

BANNER = Panel(
    renderable=(
        "\n [bold cyan]Mass IP Scanning Framework[/bold cyan]"
        "\n\n   [bold yellow]Find Vulnerable Devices[/bold yellow]"
        "\n\n    [bold magenta]Made by NSM-Barii[/bold magenta]\n"
    ),
    expand=False,
    style="bold red",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Mass IP Scanning framework meant to find vulnerable devices left uncheck open to the internet"
    )

    parser.add_argument("-p", help="Port to scan.")
    parser.add_argument("-t", type=int, default=250, help="Maximum number of threads to spawn.")
    parser.add_argument("--save", action="store_true", help="Save all active IPs to database/ips.txt.")
    parser.add_argument("--x", help="Use this to set a custom file name")
    parser.add_argument("--country", help="Only create IP Blocks within x Country")
    parser.add_argument("--asn", help="Pass asn value(s) Example: 215892, 214735, 214145, 213727, 212056")
    parser.add_argument("--bloom-size", type=int, default=100_000_000, help="BloomFilter capacity for global scans (default: 100000000).")
    parser.add_argument("--geo", choices=["local", "ipinfo"], help="Enable IP geolocation lookup.")
    parser.add_argument("--ipinfo", help="Optional ipinfo.io API key.")
    parser.add_argument("--iot", action="store_true", help="Scan for IoT devices (MQTT, CoAP, mDNS).")
    parser.add_argument("--nas", action="store_true", help="Scan for NAS devices (SMB, Synology, web panels).")
    parser.add_argument("--camera", action="store_true", help="Scan for IP cameras (RTSP, ONVIF, web interfaces).")
    parser.add_argument("--router", action="store_true", help="Scan for routers and network infrastructure.")
    parser.add_argument("--remote", action="store_true", help="Scan for remote access services (RDP, VNC, SSH, FTP).")
    parser.add_argument("--database", action="store_true", help="Scan for open databases (3306, 5432, 27017, 6379, 9200).")
    parser.add_argument("--show-all", action="store_true", help="Show all active IPS")
    parser.add_argument("--paths", choices=["nas", "router", "camera"], help="Set path for directory bruteforcing.")

    if len(sys.argv) == 1:
        console.print(BANNER)
        parser.print_help()
        sys.exit()

    return parser.parse_args()


def resolve_asn(args):
    if args.asn in IRAN_PRESETS:
        preset = IRAN_PRESETS[args.asn]
        return preset["asn"], True, preset["name"]
    return args.asn, args.save, args.x


def resolve_port(args):
    if args.p in PORT_PRESETS:
        return PORT_PRESETS[args.p]()

    for flag, resolver in DEVICE_PRESETS.items():
        if getattr(args, flag):
            port, paths = resolver()
            if paths:
                Database.paths = paths
            return port

    return args.p


def main():
    args = parse_args()

    if not args.country:
        console.print(
            "\n[bold red][!] WARNING:[/bold red] [bold yellow]Scanning without --country will use a 100M BloomFilter limit."
            "\n    After 100M IPs, duplicates may be scanned. Use --country for memory-efficient scanning."
            "\n    Or increase with --bloom-size (e.g., --bloom-size 500000000) but this uses more RAM.\n"
        )

    asn, save, save_name = resolve_asn(args)
    port = resolve_port(args)

    if args.paths and args.paths in PATH_MAP:
        Database.paths = PATH_MAP[args.paths]()

    Mass_IP_Scanner.country = args.country
    Mass_IP_Scanner.asn = asn
    Mass_IP_Scanner.all = args.show_all
    Mass_IP_Scanner.save = save
    Mass_IP_Scanner.save_name = save_name
    Mass_IP_Scanner.bloom_size = args.bloom_size

    Database.ports = port
    Database.lookup = args.geo
    Database.api_key_ipinfo = args.ipinfo

    console.print(
        "[red]=========   CONSTANTS   =========\n",
        f"[red][+] Port(s):[bold yellow] {port}"
        f"\n[red] [+] Max Workers:[bold yellow] {args.t}"
        f"\n[red] [+] File Saving:[bold yellow] {save}"
        f"\n[red] [+] GEO Lookup:[bold yellow] {args.geo}"
        f"\n[red] [+] API Key:[bold yellow] {args.ipinfo}",
        "\n[red]=================================",
    )

    Mass_IP_Scanner._main(port=port, threads=args.t)


main()
