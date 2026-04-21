import re
import os

# Mock environment
TIDB_URL = "mysql --comments -u '2zSvroz3eJhSWyZ.root' -h gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com -P 4000 -D 'test' --ssl-mode=VERIFY_IDENTITY --ssl-ca=<CA_PATH> -p'jnOymssFprrBCdr5'"
TIDB_HOST = None
TIDB_PORT = 4000
TIDB_USER = None
TIDB_PASSWORD = None
TIDB_DB_NAME = "autods"
TIDB_CA_PATH = None

def get_match(regex, s):
    m = re.search(regex, s)
    return m.group(1) or m.group(2) if m else None

def test_parsing():
    config = {}
    if TIDB_URL:
        if TIDB_URL.startswith("mysql://"):
            pattern = r"mysql://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<dbname>[^?]+)(\?ssl_ca=(?P<ssl_ca>.+))?"
            match = re.match(pattern, TIDB_URL)
            if match:
                config = {
                    "host": match.group("host"),
                    "port": match.group("port"),
                    "user": match.group("user"),
                    "password": match.group("password"),
                    "database": match.group("dbname"),
                    "ssl_ca": match.group("ssl_ca") or TIDB_CA_PATH
                }
        elif TIDB_URL.startswith("mysql "):
            config = {
                "user": get_match(r"-u\s+'([^']+)'|-u\s+([^\s]+)", TIDB_URL),
                "host": get_match(r"-h\s+([^\s]+)", TIDB_URL),
                "port": get_match(r"-P\s+(\d+)", TIDB_URL),
                "database": get_match(r"-D\s+'([^']+)'|-D\s+([^\s]+)", TIDB_URL),
                "password": get_match(r"-p'([^']+)'|-p([^\s]+)", TIDB_URL),
            }
            
            ssl_ca = get_match(r"--ssl-ca=([^\s]+)", TIDB_URL)
            if ssl_ca and ssl_ca != "<CA_PATH>":
                config["ssl_ca"] = ssl_ca
            elif TIDB_CA_PATH:
                config["ssl_ca"] = TIDB_CA_PATH
    
    if not config or not config.get("host"):
        config = {
            "host": TIDB_HOST,
            "port": TIDB_PORT or 4000,
            "user": TIDB_USER,
            "password": TIDB_PASSWORD,
            "database": TIDB_DB_NAME or "autods",
            "ssl_ca": TIDB_CA_PATH
        }
    
    print(f"Parsed Config: {config}")
    
    # Assertions for the specific TIDB_URL
    assert config['user'] == '2zSvroz3eJhSWyZ.root'
    assert config['host'] == 'gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com'
    assert config['port'] == '4000'
    assert config['database'] == 'test'
    assert config['password'] == 'jnOymssFprrBCdr5'
    assert 'ssl_ca' not in config or config['ssl_ca'] is None
    print("Test passed!")

if __name__ == "__main__":
    test_parsing()
