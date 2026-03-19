# THIS WILL HOUSE GEO LOOKUP UTILITIES

import requests
import geoip2.database

from nsm_vars import BASE_DIR, OK_STATUS, console as default_console


def print_geo(country, region, city, org, postal, timezone, CONSOLE=default_console):
    """Print geo info for an IP"""
    c4 = "bold green"
    c5 = "white"
    space = "    "
    CONSOLE.print(
        f" [{c4}]{space}[+] Country:[{c5}] {country}"
        f"\n [{c4}]{space}[+] region:[{c5}] {region}"
        f"\n [{c4}]{space}[+] city:[{c5}] {city}"
        f"\n [{c4}]{space}[+] org:[{c5}] {org}"
        f"\n [{c4}]{space}[+] postal:[{c5}] {postal}"
        f"\n [{c4}]{space}[+] timezone:[{c5}] {timezone}"
    )


def get_geo_info_local(ip, db_state, CONSOLE=default_console):
    """Get geo IP info using local MaxMind databases"""

    try:
        if not db_state.reader_asn:
            path_asn = str(BASE_DIR / "geo_lookup" / "L-ASN" / "L-ASN.mmdb")
            path_city = str(BASE_DIR / "geo_lookup" / "L-City" / "L-City.mmdb")
            db_state.reader_asn = geoip2.database.Reader(path_asn)
            db_state.reader_city = geoip2.database.Reader(path_city)

        asn_response = db_state.reader_asn.asn(ip)
        city_response = db_state.reader_city.city(ip)

        country = city_response.country.name or False
        region = city_response.subdivisions.most_specific.name or False
        city = city_response.city.name or False
        postal = city_response.postal.code or False
        timezone = city_response.location.time_zone or False
        org = asn_response.autonomous_system_organization or False

        print_geo(country, region, city, org, postal, timezone, CONSOLE=CONSOLE)

    except Exception as e:
        db_state.errors += 1
        CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")


def get_geo_info_ipinfo(
    ip, db_state, CONSOLE=default_console, timeout=3, verbose=False
):
    """Get geo IP info using ipinfo.io API"""

    if db_state.api_key_ipinfo:
        url = f"https://ipinfo.io/{ip}/json/?token={db_state.api_key_ipinfo}"
    else:
        url = f"https://ipinfo.io/{ip}/json"

    try:
        response = requests.get(url=url, timeout=timeout)
        data = response.json()

        if response.status_code in OK_STATUS:
            if verbose:
                CONSOLE.print(data)

            country = data.get("country", False)
            region = data.get("region", False)
            city = data.get("city", False)
            org = data.get("org", False)
            postal = data.get("postal", False)
            timezone = data.get("timezone", False)

            print_geo(country, region, city, org, postal, timezone, CONSOLE=CONSOLE)

        else:
            CONSOLE.print(
                f" [bold red]    [-] IPInfo Lookup Failed :[white] {response.text}"
            )

    except Exception:
        db_state.errors += 1
