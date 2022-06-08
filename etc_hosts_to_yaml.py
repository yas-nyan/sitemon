import yaml
import argparse



if __name__  == "__main__":
    # parse args
    parser = argparse.ArgumentParser("sitemon options")
    parser.add_argument("hostsPath", help="source hosts file")
    parser.add_argument("destPath", help="dest yaml file")
    args = parser.parse_args()

    hosts = []
    with open(args.hostsPath, "r") as f:
        for line in  f.readlines():
            
            # コメントがあったらそれ以降を切る
            if "#" in line:
                commentOutIndex = line.index("#")
                line = line[:commentOutIndex]
            words = line.split()
            if len(words) < 2: 
                continue
            host = {
                "name": words[1].strip(),
                "value": words[0].strip(),
                "type": "icmp"
            }
            hosts.append(host)
    resultDict = {
        "slack": {
            "url": "CHANGEME"
        },
        "targets": hosts
    }
    with open(args.destPath, "w")  as f:
        yaml.dump(resultDict, f)

