import json
import requests
from bs4 import BeautifulSoup

def fetch_data(url:str)->dict:
    """
    Takes in a url, scrapes relevant info off of the url into a python dict for later json conversion
    """
    response = requests.get(url)
    response.raise_for_status()  #no try-except an error for any webpage that fails to load would be convenient
    soup = BeautifulSoup(response.content, 'html.parser')

    inclusion = {
        "Age From": 18,
        "Age To": 99,
        "Gender": "Both",
        "Details": None,
    }   

    data = {
        "CTRI Number": None,
        "Public Title": None,
        "Inclusion Criteria": inclusion,
        "Exclusion Criteria": None,
        "URL": url,
    }   #only relevant info to reduce tokens when feeding to LLM

    td_all = soup.find_all("td")

    for i in range(1, len(td_all) - 2):
        
        key = td_all[i].get_text(strip=True)
        value = td_all[i + 1].get_text(strip=True)

        if "CTRI Number" in key:
            data['CTRI Number'] = value.split("[")[0]

        elif "Public Title" in key:
            data["Public Title"] = value

        elif "Inclusion Criteria" in key:
            table = td_all[i + 1].find("table")
            nested_td = table.find_all("td")

            for i in range(0, len(nested_td) - 1):
                key_2 = nested_td[i].get_text(strip=True)
                value_2 = nested_td[i + 1].get_text(strip=True)

                if "Age From" in key_2 and value_2:
                    inclusion["Age From"] = value_2

                elif "Age To" in key_2 and value_2:
                    inclusion["Age To"] = value_2

                elif "Gender" in key_2 and value_2:
                    inclusion["Gender"] = value_2

                elif "Details" in key_2 and value_2:
                    
                    inclusion["Details"] = value_2

        elif "ExclusionCriteria" in key:
            value = td_all[i + 3].get_text(strip=True)
            data['Exclusion Criteria'] = value

    return data

def fetch_but_many(url: list):
    """
    fetch, but... many
    """
    all_json=[]
    i=1
    for x in url:
        json_ind=fetch_data(x)
        print(i)
        i+=1
        all_json.append(json_ind)
    #Added functionality if you want to pump n dump in a json file in local direc
    json_dump(all_json)

#End of parsing

def json_dump(data):
    """
    dump all the data into a local file
    """
    filepath=r"YOUR FILE PATH"
    
    with open (filepath,"w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def pump_n_dump(url):
    """
    useless but funny
    """
    data=fetch_data(url)
    json_dump(data)
    print("Successfully pulled out :)")



if __name__=="__main__":
    #trial url-set:
    ctri_urls = [
    "https://ctri.nic.in/Clinicaltrials/pmaindet2.php?EncHid=MTAxMTMy&Enc=&userName=",
    "https://ctri.nic.in/Clinicaltrials/pmaindet2.php?EncHid=NDg4OQ==&Enc=&userName=",
    "https://ctri.nic.in/Clinicaltrials/pmaindet2.php?EncHid=MjMxODY=&Enc=&userName="
    ]


    fetch_but_many(ctri_urls)

