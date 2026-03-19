# THIS WILL HOUSE PROGRAM WIDE VARIABLES

import threading
from pathlib import Path

from rich.console import Console

LOCK = threading.RLock()
console = Console()
BASE_DIR = Path(__file__).parent.parent / "database"
OK_STATUS = (200, 204)


# PRESET PORT LISTS

# Optimized critical infrastructure port list (15 high-value ports)
CRITICAL_INFRASTRUCTURE_PORTS = [
    # Web/Admin (most common)
    80,  # HTTP
    443,  # HTTPS
    8080,  # HTTP Alternate
    # Remote Access (high-value targets)
    22,  # SSH
    23,  # Telnet
    # ICS/SCADA (critical for power/energy)
    502,  # Modbus TCP (energy grid, industrial)
    20000,  # DNP3 (electric utility SCADA)
    102,  # Siemens S7 (industrial control)
    47808,  # BACnet (building/facility automation)
    1911,  # Niagara Fox (building automation)
    # Management (network infrastructure)
    161,  # SNMP
    8291,  # MikroTik Winbox
    # Databases (exposed data)
    3306,  # MySQL
    5432,  # PostgreSQL
    27017,  # MongoDB
]

DATABASE_PORTS = [
    3306,  # MySQL
    5432,  # PostgreSQL
    27017,  # MongoDB
    6379,  # Redis
    9200,  # Elasticsearch
]

CAMERA_PORTS = [
    80,  # HTTP web interface (most common camera login page)
    443,  # HTTPS web interface (secure camera panel)
    554,  # RTSP video stream (very high signal for cameras)
    8000,  # Hikvision / OEM camera management port
    8080,  # Alternate HTTP web interface
    37777,  # Dahua proprietary service port
    34567,  # Common on generic / cheap OEM IP cameras
    3702,  # ONVIF discovery (usually LAN, not internet)
    8443,  # Alternate HTTPS web interface
]

ROUTER_PORTS = [
    80,  # HTTP admin panel
    443,  # HTTPS admin panel
    8080,  # Alternate web admin
    8443,  # Alternate secure admin
    23,  # Telnet (legacy routers)
    22,  # SSH management
    7547,  # TR-069 (ISP remote management)
    8291,  # MikroTik Winbox
]

NAS_PORTS = [
    5000,  # Synology HTTP
    5001,  # Synology HTTPS
    9000,  # Various NAS web panels
    445,  # SMB file sharing
    139,  # NetBIOS session service
]

REMOTE_PORTS = [
    3389,  # RDP
    5900,  # VNC
    22,  # SSH
    21,  # FTP
]

IOT_PORTS = [
    1883,  # MQTT
    8883,  # Secure MQTT
    5683,  # CoAP
    5353,  # mDNS (mostly LAN discovery)
]


# PRESET PATH LISTS

PATHS_CAMERA = [
    "/onvif/device_service",
    "/snapshot.jpg",
    "/video.cgi",
    "/ISAPI/System/status",
    "/cgi-bin/magicBox.cgi",
    "/doc/page/login.asp",
    "/web/cgi-bin/",
]

PATHS_ROUTER = [
    "/",  # title / server header
    "/login",  # common
    "/admin",  # common
    "/cgi-bin/",  # embedded web UIs
    "/HNAP1/",  # some consumer routers
    "/setup.cgi",  # older firmwares
    "/rom-0",  # legacy Zyxel-style misconfig (rare, but high signal)
    "/api/",  # modern web panels
]

PATHS_NAS = [
    "/",  # landing page/title
    "/webman/index.cgi",  # Synology DSM (often redirects)
    "/auth.cgi",  # Synology auth endpoint (presence signal)
    "/cgi-bin/",  # QNAP/Synology patterns
    "/admin/",  # generic NAS panels
]


# ZONE TO COUNTRY MAPPING

ZONE_TO_COUNTRY = {
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
