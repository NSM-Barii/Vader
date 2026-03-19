# THIS WILL BE A TEST SCRIPT FOR NETBRUTER2.0



# UI IMPORTS
from rich.console import Console
from rich.panel import Panel
from rich.live import Live


# NETWORK IMPORTS
import ipaddress, socket


# ETC IMPORTS
import time, random, threading, sys; from pybloom_live import BloomFilter
from concurrent.futures import ThreadPoolExecutor


# NSM IMPORTS
from nsm_database import File_Saver, Database

console = Console()
LOCK = threading.Lock()




class Mass_IP_Scanner():
    """This class will be responsible for finding active ips on user choosen port"""


    # ARGS
    country = False
    asn     = False
    lookup  = False

    all     = False
    save    = False
    save_name = False   
    bloom_size = 100000000


    # MODES
    iot = False
    nas = False
    router = False
    remote = False
    camera = False
    database = False


    # IPS  // THESE ARE USED BY cls._track_ip_blocks() and cls._generate_random_ip()
    _block_iter      = None
    _block_remaining = 0
    current_block    = False
    bf_all = None
    total_ips        = 0
    total_blocks     = []
    leave            = False




    @classmethod
    def _track_ip_blocks(cls):
        """Return a random IP from the current block"""

        try:


            if cls._block_remaining <= 0:


                if not cls.blocks:

                    time_total = time.time() - cls.time_start
                    
                    if cls.scan:

                        if cls.save and cls.current_ips: 
                            with LOCK: File_Saver.push_ips_found(data=cls.current_ips, CONSOLE=console, verbose=True)
                 

                        c1 = "red"; c2 = "bold green"; c3 = "bold blue"; c4 = "bold yellow"

                        stats = (
                            f"[{c3}] [+] Total online IPv4s:[{c4}] {cls.online_ips}"
                            f"\n[{c3}] [+] Total Blocks scanned:[{c4}] {len(cls.total_blocks)}"
                            f"\n[{c3}] [+] Total IPv4s scanned:[{c4}] {cls.total_ips}"
                            f"\n[{c3}] [+] Elapsed Time:[{c4}] {time_total}"
                        )

                        
                        console.print(
                            f"[{c1}]=========   Results   =========\n",
                            stats,
                            f"\n[{c1}]=================================",
                        )


                    cls.scan = False; cls.leave = True; return False


                cls.current_block = cls.blocks.pop(0)
                network = ipaddress.IPv4Network(cls.current_block); cls.total_ips += network.num_addresses
                cls._block_iter = iter(network)
                cls._block_remaining = network.num_addresses

                console.print(f"\n[bold green][*] Current IPv4 Block:[yellow] {cls.current_block}  -  IPv4 Addresses: {network.num_addresses}")
                time.sleep(1)


            random_ip = next(cls._block_iter)
            cls._block_remaining -= 1

            cls.scanned_ips += 1; cls.last_scan += 1

            return str(random_ip)

        except Exception as e:
            console.print(f"[bold red]IP Exception:[/bold red] {e}")
            return False


    @classmethod
    def _generate_random_ip(cls, verbose=False):
        """This will generate a random ip and return it"""
        

        try:


            if cls.country:

                
                with LOCK:
                    return Mass_IP_Scanner._track_ip_blocks()

            else:
                
                with LOCK:
                    if cls.bf_all is None:
                        cls.bf_all = BloomFilter(capacity=cls.bloom_size, error_rate=0.001)

                    random_ip = (f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}")

                    if random_ip in cls.bf_all: return False
                    cls.bf_all.add(random_ip); cls.scanned_ips += 1

                    if verbose: console.print(f"[bold green]Generated IP:[bold yellow] {random_ip}")

                    return str(random_ip)



        except Exception as e: console.print(f"[bold red]Exception Error:[bold yellow] {e}"); return False
 
  
    @classmethod
    def _random_ip_validator(cls, ports, timeout=3, verbose=False):
        """This will validate random ip"""



        # COLORS
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"

        
        if not cls.scan: return False
        ip = Mass_IP_Scanner._generate_random_ip(verbose=False)
        if not ip: return


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            
            try:
                

                for port in ports:
                    s.settimeout(timeout)
                    result = s.connect_ex((ip, int(port)))

                    if result == 0:

                        with LOCK:
                            if cls.save:
                                cls.current_ips.append(ip)
                            cls.online_ips += 1

                        Database.main(ip=ip, port=port, CONSOLE=console)


            except Exception as e: 
                Database.errors += 1
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")
    
   
    @classmethod
    def _ip_threader(cls, ports, panel, max_workers=250, timeout=1):
        """This will start a multi-proccess thread"""

        # COLORS
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"
        c5 = "white"


        futures = []
        last_save = time.time()


        try: max_workers = int(max_workers)
        except Exception: max_workers = 250

        try: portz  = [int(port) for port in ports.split(',')]
        except Exception: portz = list(ports)
        

    
        with ThreadPoolExecutor(max_workers=max_workers) as executor:

            try:

                while cls.scan:

                    
                    while len(futures) < max_workers and cls.scan:
                        futures.append(executor.submit(Mass_IP_Scanner._random_ip_validator, portz, timeout))


                    futures = [f for f in futures if not f.done()]  


                    if Database.country:  panel.renderable = (f"[{c1}]Filter: [{c2}]{Database.country}  -  [{c1}]Active IPs: [{c2}]{cls.online_ips} / {cls.scanned_ips}  -  [{c1}]Port(s): [{c2}]{portz}  -  [{c1}]Max Workers:[{c2}] {max_workers}  -  [{c1}]Errors:[{c2}] {Database.errors}  -  Developed by NSM Barii")
                    else: panel.renderable = (f"[{c1}]Active IPs: [{c2}]{cls.online_ips} / {cls.scanned_ips}  -  [{c1}]Port(s): [{c2}]{portz}  -  [{c1}]Max Workers:[{c2}] {max_workers}  -  [{c1}]Errors:[{c2}] {Database.errors}  -  Developed by NSM Barii")


                    if time.time() - last_save > 5 and cls.save and cls.current_ips:
                        with LOCK:
                            File_Saver.push_ips_found(data=cls.current_ips, CONSOLE=console, verbose=False)
                            last_save = time.time()
                            cls.current_ips = []

                    if cls.scanned_ips > 0 and cls.last_scan > 250000:
                        console.print(f"\n[bold red][!] Reinitializing ThreadPool!")
                        cls.scan = False
                        return False

            except KeyboardInterrupt as e:
                console.print("[bold red][-] Killing ALL Threads...."); cls.scan=False
                executor.shutdown(wait=False, cancel_futures=True)

            except Exception as e: console.print(f"[bold red]Exception Error:[bold yellow] {e}"); cls.scan=False; exit()

            
            finally:

                if cls.save and cls.current_ips: 
                    with LOCK: File_Saver.push_ips_found(data=cls.current_ips, CONSOLE=console, verbose=True)
                


    @classmethod
    def _main(cls, port, threads):
        """This will run class wide code"""

        
        cls.scan = True
        cls.scanned_ips = 0 
        cls.online_ips  = 0
        cls.current_ips = []

        
        print("\n")
        if cls.country: cls.blocks = Database.get_ip_block(country=cls.country, CONSOLE=console); cls.total_blocks = cls.blocks.copy()
        if cls.save:    File_Saver.push_ips_found(data=False, CONSOLE=console, save_name=cls.save_name  )
        if cls.asn:     data, cls.blocks = Database.get_asn(country=cls.country, asns=cls.asn)

        if cls.country: Database.get_total_ips(blocks=cls.blocks)

        if not port:
            port = console.input("\n[bold yellow]Enter port to mass scan for!: ") or 80
            threads = console.input("[bold yellow]Enter Thread count!: ") or 250; print('\n')
        
        cls.time_start = time.time()
        panel = Panel(renderable="[bold red]Mass IP Scanner", border_style="bold purple", expand=False)
        with Live(panel, console=console, refresh_per_second=4):
            while not cls.leave:
                cls.scan = True; cls.last_scan   = 0; time.sleep(5)
                Mass_IP_Scanner._ip_threader(ports=port, max_workers=threads or 250, panel=panel)

  

if __name__ =="__main__":
    Mass_IP_Scanner._main()