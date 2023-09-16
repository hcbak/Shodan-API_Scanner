import os
import json
import time
import asyncio
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
        except Exception as e:
            try:
                system_alert("!", i + " Error!! " + str(e))
                system_alert(" ", "retry...")
                time.sleep(3)
                results.append(api.host(i))
            except Exception as e:
                system_alert("!", i + " Error!! pass this IP...")
                results.append("No Results")
        system_alert("+", i)
    return results

def result_to_json(name, data, DirName):
    try:
        os.makedirs("result")
        system_alert("!", "Dir Ready.")
    except:
        system_alert("+", "Dir Ready.")
    os.makedirs("result/" + DirName)
    os.makedirs("result/" + DirName + "/json")
    for i, j in zip(name, data):
        with open("result/" + DirName + "/json/" + i + ".json", "w") as f:
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
                    frame["server"].append(None)
                    frame["isp"].append(j["isp"])
                    frame["city"].append(j["location"]["city"])
                    frame["timestamp"].append(j["timestamp"])
                    
        except Exception as e:
            system_alert("!", i2 + " Error")
            system_alert("!", e)
            frame["ip_str"].append(i2)
            frame["port"].append(None)
            frame["module"].append(None)
            frame["server"].append(None)
            frame["isp"].append(None)
            frame["city"].append(None)
            frame["timestamp"].append(None)
                
            
    df = pd.DataFrame(frame)
    df = df.set_index("ip_str", append = True).swaplevel(1, 0)

    return df

# 
async def async_master(sList, options, exposedDir, Account):
    futures = [search_tool(i, options, exposedDir, Account) for i in sList]
    await asyncio.gather(*futures)
    
async def search_tool(url, options, exposedDir, Account):
    system_alert(" ", "Start " + url + " screen capture...")
    driver = webdriver.Edge(options = options)
    driver.get("https://account.shodan.io/login")
    driver.find_element(By.NAME, 'username').send_keys(Account[0])
    driver.find_element(By.NAME, 'password').send_keys(Account[1])
    driver.find_element(By.XPATH, '/html/body/div[2]/main/div/div/div/div[1]/form/div[3]/input').click()

    driver.get("https://www.shodan.io/host/" + url)
    await asyncio.sleep(3)
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    driver.find_element(By.TAG_NAME, 'body').screenshot(exposedDir + "/"+ url +".png")
    driver.quit()
    system_alert("+", "" + url + " capture is done!")
        
    
    

# main
if __name__ == "__main__":

    DirName = datetime.now().strftime("%Y%m%d_%H%M%S%f")

    print("\n\n\tShodan 노출 검색 자동화 스크립트\n\tv0.0.1β\n\n\t문의: hcbak@sk.com\n\n")
    
    # import module
    while True:
        try:
            import shodan
            import pandas as pd
            import openpyxl
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options
            from selenium.webdriver.common.by import By
            import edgedriver_autoinstaller
            autodriver = edgedriver_autoinstaller.install()
            system_alert("+", "imported all module.")
            break
        except Exception as e:
            system_alert("-", e)
            pip_install("shodan")
            pip_install("pandas")
            pip_install("openpyxl")
            pip_install("selenium")
            pip_install("edgedriver_autoinstaller")

    # get API Key
    try:
        system_alert(" ", "get API Key.")
        with open("API_Key.txt", "r") as f:
            ShodanApiKey = f.readline()
        api = shodan.Shodan(ShodanApiKey)
        system_alert("+", "Connected API.")
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
        system_alert("!", "Search List Error.")

    # get Account
    Account = []
    try:
        system_alert(" ", "get Account.")
        with open("Account.txt", "r") as f:
            for i in f:
                Account.append(i.strip("\n"))
        system_alert("+", "read Account.")
    except Exception as e:
        system_alert("-", e)
        system_alert("!", "Account Error.")

    results = search_shodan(api, SearchList)

    result_to_json(SearchList, results, DirName)

    df = make_table(results, SearchList)
    df.to_excel("result/" + DirName + "/result.xlsx")

    exposedDir = "result/" + DirName + "/exposed"
    os.makedirs(exposedDir)
    
    serverList = df["server"].dropna()
    serverListIP = [i[0] for i in serverList.index]

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--inprivate")
    options.add_argument("--window-size= 1920, 1080")

    asyncio.run(async_master(serverListIP, options, exposedDir, Account))

    system_alert("+", "End Script.")
    os.startfile("result\\" + DirName)

os.system("pause")
