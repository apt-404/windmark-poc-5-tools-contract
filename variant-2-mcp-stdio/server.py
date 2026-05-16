from fastmcp import FastMCP

from tools.nmap_scan import nmap_scan as _nmap_scan
from tools.gobuster_dir import gobuster_dir as _gobuster_dir

mcp = FastMCP("windmark-poc5-v2")


@mcp.tool()
def nmap_scan(target: str, ports: str = "1-1000", flags: list[str] = None) -> dict:
    return _nmap_scan(target=target, ports=ports, flags=flags)


@mcp.tool()
def gobuster_dir(target: str, wordlist: str, extensions: list[str] = None) -> dict:
    return _gobuster_dir(target=target, wordlist=wordlist, extensions=extensions)


if __name__ == "__main__":
    mcp.run(transport="stdio")
