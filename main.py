import os
import json
from datetime import datetime

def system_alert(icon = " ", word = ""):
    print("[" + str(icon) + "]", word)

def pip_install(module):
    system_alert(" ", "pip install " + module)
    try:
        os.system("pip install " + module)
        system_alert("+", module + " Installation Complate.")
    except Exception as e:
        system_alert("-", e)
        system_alert("!", "Installation Fail.")

def search_shodan(api, S_list):
    results = []
    
    for i in S_list:
        try:
            results.append(api.host(i))
        except:
            results.append("No Results")
        system_alert("+", i)
    return results

def result_to_json(name, data):
    try:
        os.makedirs("result")
        system_alert("!", "Dir Ready.")
    except:
        system_alert("+", "Dir Ready.")
    DirName = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    os.makedirs("result/" + DirName)
    for i, j in zip(name, data):
        with open("result/" + DirName + "/" + i + ".json", "w") as f:
            json.dump(j, f, indent = 4)
    system_alert("+", "Result File Saved.")

def make_table(data, index):
    frame = {
        "ip_str" : [],
        "port" : [],
        "module" : [],
        "server" : [],
        "isp" : [],
        "city" : [],
        "timestamp" : []
    }
    
    for i, i2 in zip(data, index):
        try:
            for j in i["data"]:
                try:
                    ip_str = j["ip_str"]
                    port = j["port"]
                    module = j["_shodan"]["module"]
                    server = j["http"]["server"]
                    isp = j["isp"]
                    city = j["location"]["city"]
                    timestamp = j["timestamp"]
                    
                    frame["ip_str"].append(ip_str)
                    frame["port"].append(port)
                    frame["module"].append(module)
                    frame["server"].append(server)
                    frame["isp"].append(isp)
                    frame["city"].append(city)
                    frame["timestamp"].append(timestamp)
                except Exception as e:
                    system_alert("!", i["ip_str"] + " Error")
                    system_alert("!", e)
                    frame["ip_str"].append(j["ip_str"])
                    frame["port"].append(j["port"])
                    frame["module"].append(j["_shodan"]["module"])
                    frame["server"].append("")
                    frame["isp"].append(j["isp"])
                    frame["city"].append(j["location"]["city"])
                    frame["timestamp"].append(j["timestamp"])
                    
        except Exception as e:
            system_alert("!", i2 + " Error")
            system_alert("!", e)
            frame["ip_str"].append(i2)
            frame["port"].append("")
            frame["module"].append("")
            frame["server"].append("")
            frame["isp"].append("")
            frame["city"].append("")
            frame["timestamp"].append("")
                
    print(frame)
    df = pd.DataFrame(frame)
    df = df.set_index("ip_str", append = True).swaplevel(1, 0)

    return df

# main
if __name__ == "__main__":
    # import module
    while True:
        try:
            import shodan
            import pandas as pd
            import openpyxl
            system_alert("+", "imported all module.")
            break
        except Exception as e:
            system_alert("-", e)
            pip_install("shodan")
            pip_install("pandas")
            pip_install("openpyxl")

    # get API Key
    try:
        system_alert(" ", "get API Key.")
        with open("API_Key.txt", "r") as f:
            ShodanApiKey = f.readline()
        api = shodan.Shodan(ShodanApiKey)
        system_alert("+", "Connect API.")
    except Exception as e:
        system_alert("-", e)
        system_alert("!", "API Key Error.")

    # get Search List
    SearchList = []
    try:
        system_alert(" ", "get Search List.")
        with open("Search_List.txt", "r") as f:
            for i in f:
                SearchList.append(i.strip("\n"))

    except Exception as e:
        system_alert("-", e)

    results = search_shodan(api, SearchList)

    result_to_json(SearchList, results)

    df = make_table(results, SearchList)
    df.to_excel("test.xlsx")
    



os.system("pause")
