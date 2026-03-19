# THIS WILL HOUSE FILE SAVING UTILITIES

from datetime import datetime

from nsm_vars import BASE_DIR, LOCK


class File_Saver:
    """This class will save files"""

    path = False
    country = False
    ips_saved = set()

    @classmethod
    def push_ips_found(cls, data, CONSOLE, save_name=False, verbose=False):
        """This will push current set of ips"""

        if not cls.path:
            try:
                path = BASE_DIR / "saved_ips"

                if path.exists():
                    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

                    if save_name:
                        cls.path = path / str(save_name)
                    elif cls.country:
                        cls.path = path / f"{cls.country}_{timestamp}.txt"
                    else:
                        cls.path = path / f"{timestamp}.txt"

                    CONSOLE.print(
                        f"[bold green][+] File Path successfully made:[/bold green] {cls.path}"
                    )

            except Exception as e:
                CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

            return

        try:
            with LOCK:
                ips = []
                for ip in data:
                    if ip not in cls.ips_saved:
                        ips.append(ip)
                        cls.ips_saved.add(ip)

                if not ips:
                    return
                clean = "\n".join(ips) + "\n"

            with open(str(cls.path), "a") as file:
                file.write(clean)
            if verbose:
                CONSOLE.print("[bold green][+] Successfully pushed new info")

        except FileNotFoundError as e:
            CONSOLE.print(f"[bold red][-] FileNotFoundError:[bold yellow] {e}")
            with open(str(cls.path), "w") as file:
                file.write("\n".join(data) + "\n")

        except Exception as e:
            CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")
