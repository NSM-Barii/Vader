# THIS WILL HOUSE DATABASE UTILITIES

import json, requests, mmh3, re, ipaddress, os, sys

from nsm_vars import LOCK, console, BASE_DIR, OK_STATUS, ZONE_TO_COUNTRY
from nsm_geo import get_geo_info_local, get_geo_info_ipinfo


class Database:
    """This will hold database values"""

    # HOLD ALL ERRORS
    errors = 0

    # SET FROM main.py
    paths = False

    # VARS
    lookup = False
    country = False
    api_key_ipinfo = False
    reader_asn = False
    reader_city = False

    @staticmethod
    def _probe_path(ip, port, path, CONSOLE=console, timeout=1, errors=False):
        """Probe a single path on an IP and print results if reachable"""

        space = "    "
        c1 = "bold red"
        c2 = "bold yellow"
        c4 = "bold green"

        try:
            url = f"http://{ip}{path}"
            response = requests.get(url=url, timeout=timeout)
            headers = response.headers

            if response.status_code in OK_STATUS:
                favicon = mmh3.hash(response.content)
                title = False
                match = re.search(
                    r"<title>(.*?)</title>",
                    response.text,
                    re.IGNORECASE | re.DOTALL,
                )
                if match: title = match.group(1).strip()
                status = response.status_code
                redirect = response.url if response.url != url else False
                content_length = len(response.text) or False
                server = headers.get("Server", False)
                x_powered_by = headers.get("X-Powered-By", False)

                with LOCK:
                    CONSOLE.print(
                        f"\n[{c4}][+] Active IP:[/{c4}] [{c2}]{ip}[/{c2}]:{port}"
                    )
                    CONSOLE.print(
                        f"{space}[{c4}][+] Directory:[{c2}] {url}",
                        f"\n{space}[{c4 if status else c1}][+] Status:[{c2}] {status}",
                        f"\n{space}[{c4 if title else c1}][+] Title:[{c2}] {title}",
                        f"\n{space}[{c4 if server else c1}][+] Server:[{c2}] {server}",
                        f"\n{space}[{c4 if redirect else c1}][+] Redirect:[{c2}] {redirect}",
                        f"\n{space}[{c4 if content_length else c1}][+] Content-Length:[{c2}] {content_length}",
                        f"\n{space}[{c4 if x_powered_by else c1}][+] Powered-by:[{c2}] {x_powered_by}",
                        f"\n{space}[{c4 if favicon else c1}][+] Favicon:[{c2}] {favicon}",
                    )

        except Exception as e:
            Database.errors += 1
            if errors:
                CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

    @classmethod
    def _check_paths(cls, ip, port, CONSOLE=console, timeout=1, errors=False):
        """This will check path signatures"""

        if not cls.paths: return

        for path in cls.paths:
            cls._probe_path(
                ip, port, path, CONSOLE=CONSOLE, timeout=timeout, errors=errors
            )

    @classmethod
    def validate_country(cls, country, CONSOLE=console, verbose=True):
        """This will be used to validate user inputted country"""

        path_ip_blocks = BASE_DIR / "ip_blocks"
        path_country = path_ip_blocks / f"{country}.txt"

        if not path_ip_blocks.exists(): CONSOLE.print("\n[bold red][-] Seems like your missing the ip_blocks directory, please check Documentation for fix"); sys.exit()

        if path_country.exists():
            if verbose:
                CONSOLE.print(
                    f"[bold green][+] Found country.txt:[/bold green] {path_country}"
                )
            cls.country = country
            return path_country

        CONSOLE.print(
            "\n[bold red][-] Invalid country given, please check documentation if your having trouble finding your country"
        )
        sys.exit()

    @classmethod
    def validate_asn(cls, country, asns, CONSOLE=console):
        """This will be used to validate user inputted ASNs"""

        path_asn = BASE_DIR / "asns" / f"{country}.json"
        valid_asn = []

        if path_asn.exists():
            CONSOLE.print(f"[bold green][+] Found asn.json:[/bold green] {path_asn}\n")

            with open(path_asn) as file:
                data = json.load(file)

            presets = {int(key) for key in data}

            for asn in asns:
                if asn in presets:
                    CONSOLE.print(f"[bold green][+] Validated ASN:[yellow] {asn}")
                    valid_asn.append(asn)
                else:
                    CONSOLE.print(
                        f"[bold red][-] Failed to Validated ASN:[yellow] {asn}"
                    )

            return path_asn, valid_asn

        CONSOLE.print(
            "\n[bold red][-] Seems like your missing the asns directory, please check Documentation for fix"
        )
        sys.exit()

    @classmethod
    def get_ip_block(cls, country, CONSOLE=console, verbose=False):
        """This method will be responsible for getting the block for country"""

        path = str(Database.validate_country(country=country, CONSOLE=CONSOLE))

        try:
            with open(path) as file:
                blocks = [block.strip().replace("\t", "") for block in file]

            if verbose:
                CONSOLE.print(blocks)
            return blocks

        except Exception as e:
            Database.errors += 1
            CONSOLE.print(f"[bold red]Exception Error:[bold yellow] {e}")

    @classmethod
    def get_asn(cls, country, asns, CONSOLE=console):
        """Fetch announced prefixes for given ASNs within a country"""

        # COLORS
        c1 = "bold red"
        c4 = "bold green"
        c5 = "white"
        c6 = "yellow"
        total_blocks = []

        try:
            asns = [int(asn) for asn in asns.split(",")]
        except Exception:
            asns = list(asns)

        Database.validate_country(country=country, CONSOLE=console, verbose=False)
        path_asn, asns = Database.validate_asn(
            country=country, asns=asns, CONSOLE=console
        )

        base = {}

        CONSOLE.print(f"\n[yellow][*] Target asns:[/yellow] {asns}")

        try:
            with open(path_asn) as file:
                asn_data = json.load(file)
            CONSOLE.print("[yellow][+] Pulling blocks <-- asn(s), Please standby\n")

            for asn in asns:
                value = asn_data.get(str(asn))
                if not value: continue

                country_code = value["country_code"]
                description = value["description"]
                handle = value["handle"]

                url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"

                response = requests.get(url=url)
                resp_data = response.json()
                block = []

                if response.status_code in OK_STATUS:
                    prefixes = resp_data["data"]["prefixes"]

                    for cidr in prefixes:
                        prefix = cidr["prefix"]

                        try:
                            if ipaddress.IPv4Network(prefix):
                                block.append(prefix)
                                total_blocks.append(prefix)

                        except Exception as e:
                            CONSOLE.print(f"IPV6: {e}")

                    base[asn] = {
                        "asn": asn,
                        "country_code": country_code,
                        "description": description,
                        "handle": handle,
                        "block": block,
                    }

                    CONSOLE.print(
                        f"[{c1}]{'=' * 25}"
                        f"\n[{c4}][+] asn:[{c6}] {asn}"
                        f"\n[{c4}][+] country_code:[{c6}] {country_code}"
                        f"\n[{c4}][+] description:[{c6}] {description}"
                        f"\n[{c4}][+] handle:[{c6}] {handle}"
                        f"\n[{c4}][+] prefix(s):[{c5}] {'\n   '.join(block)}"
                        f"\n[{c1}]{'=' * 25}"
                    )

            return base, total_blocks

        except Exception as e:
            CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

    @classmethod
    def get_total_ips(cls, blocks):
        """This will be for getting total ip in ip block(s)"""

        total = sum(ipaddress.IPv4Network(block).num_addresses for block in blocks)

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

        if cls.lookup == "local":
            get_geo_info_local(ip=ip, db_state=cls, CONSOLE=CONSOLE)
        elif cls.lookup == "ipinfo":
            get_geo_info_ipinfo(ip=ip, db_state=cls, CONSOLE=CONSOLE)

        if Database.paths:
            Database._check_paths(ip=ip, port=port, CONSOLE=CONSOLE)

    # WARNING
    @classmethod
    def _download_ip_blocks_for_each_country(cls):
        """This will be a one time use method to automate downloading blocks for each country from ipdeny.com"""

        # WARNING: This is not to be used more than once.
        # If you git cloned this program these files should already be within the database/ip_blocks directory.

        try:
            # 233 COUNTRYS

            ip_block_dir = str(BASE_DIR / "ip_blocks")
            os.chdir(ip_block_dir)
            console.print(
                f"[bold green][+] Successfully changed DIR to: {ip_block_dir}"
            )

            for zone, country in ZONE_TO_COUNTRY.items():
                if not country: continue

                url = f"https://www.ipdeny.com/ipblocks/data/countries/{zone}"
                safe_country = country.replace(" ", "_")

                response = requests.get(url=url)

                if response.status_code in OK_STATUS:
                    with open(f"{safe_country}.txt", "w") as file:
                        file.write(str(response.text))
                    console.print(
                        f"[bold green][+] Successfully downloaded:[bold yellow] {country}/{zone} <-> {url}"
                    )

        except Exception as e:
            console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

    @classmethod
    def _download_asns_within_each_country(cls):
        """This will be used to download asns for each domain within a country"""

        import csv

        try:
            asn_file = str(BASE_DIR / "asns" / "info.txt")

            console.print(f"[bold green][+] Reading ASN database from: {asn_file}")

            # Read CSV once, group by country code
            rows_by_code = {}
            with open(asn_file) as file:
                for row in csv.DictReader(file):
                    cc = row["country-code"].lower()
                    rows_by_code.setdefault(cc, []).append(row)

            for zone, country_name in ZONE_TO_COUNTRY.items():
                if not country_name: continue
                safe_country = country_name.replace(" ", "_")
                code = zone.split(".")[0]

                asns = {}
                for row in rows_by_code.get(code, []):
                    asns[row["asn"]] = {
                        "country_code": row["country-code"],
                        "asn": row["asn"],
                        "description": row["description"],
                        "handle": row["handle"],
                    }

                save_file = str(BASE_DIR / "asns" / f"{safe_country}.json")
                with open(save_file, "w") as file:
                    json.dump(asns, file, indent=4)

                console.print(
                    f"[bold green][+] Saved {len(asns)} ASNs for {code}: {save_file}"
                )

        except Exception as e:
            console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

    @staticmethod
    def _download_ip_blocks_for_asn():
        """This will download all ip blocks for asn given"""

        try:
            asns = ["AS5661"]

            package = {}

            ip_block_dir = str(BASE_DIR / "asns" / "US")
            os.chdir(ip_block_dir)
            console.print(
                f"[bold green][+] Successfully changed DIR to: {ip_block_dir}"
            )

            for asn in asns:
                url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"

                response = requests.get(url=url)
                data = response.json()

                if response.status_code in OK_STATUS:
                    prefixes = data["data"]["prefixes"]
                    saved = []

                    for cidr in prefixes:
                        prefix = cidr["prefix"]
                        console.print(
                            f"[bold green] Found Block:[/bold green] {prefix}"
                        )
                        saved.append(prefix)

                    package[asn] = saved

                    with open(f"{asn}.json", "w") as file:
                        json.dump(package, file, indent=4)
                    console.print(
                        f"[bold green][+] Successfully downloaded:[bold yellow] {asn}  <-> {url}"
                    )

        except Exception as e:
            console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")
