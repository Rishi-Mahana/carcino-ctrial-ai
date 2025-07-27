#VERY UNRELIABLE KAAJ PHAAJ KORENA TAO DILAM CUZ I SPENT TOO MUCH TIME DEBUGGING THIS NOT TO 
import requests
import os
from bs4 import BeautifulSoup
from openai import OpenAI
import json

def fetch(url: str)->dict:
    """ This function takes in an URL, parses and pre-processes the data within it, and returns it as a python dict"""
    webdata=requests.get(url).content
    soup = BeautifulSoup(webdata, 'html.parser')
    all_entries=soup.find_all('td') #all td->table data entries
    trial_data={}

    for i in range(2,len(all_entries),2):  #each td occurs in pairs, one for index and one for the content, therefore step size is kept 2, 
        key=all_entries[i].get_text(strip=True) #first pair is alwyays a huge summary so we start at 2
        value=all_entries[i+1].get_text(strip=True)
        trial_data[key]=value

    return trial_data

def cleanup(trial_data:dict)->dict:
    """ This function will take in a python dict with messy but formatted data entries and call an LLM to clean it up and return a JSON dict"""
    prompt = f"""
    You are a data extraction expert.

    Extract and clean clinical trial data from the input JSON. Output a structured, clean, valid JSON object only. Follow these rules:

    Merge logically related fields.

    Format entries whose field names or values may have been mismatched.

    Standardize field names (e.g., "CTRI Number", "Study Title", "Interventions", "Investigators", "Outcomes", etc.).

    If a field lacks data, remove it.



    Strict rules:

    DO NOT REMOVE any field containing meaningful data.

    Ensure the output is valid JSON:

    Starts and ends with curly braces.

    No code blocks, explanations, or extra text.

    No unterminated strings.

    No special or foreign characters.
   

    Include the "CTRI Number" field with its correct value.

    Return only a valid JSON string as the output.
    HTML:
    {trial_data}
    """
    
    #were using Groq API
    client=OpenAI(
    api_key="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",  
    base_url="https://api.groq.com/openai/v1"
    )

    
    response=client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {"role":"system","content":"You are a JSON data extraction expert."},
        {"role":"user","content":prompt}
    ],
    temperature=0
    )

    #extracting what we need from the response into a pure JSON str
    json_str = response.choices[0].message.content
    #loading the data from the str into a python dict
    #json_data=json.loads(json_str)
    filepath=filedir="C:/Users/rishi/OneDrive/Desktop/Python/Carcino/TRIAL_DATA/smesky"
    with open(filepath,'w', encoding='utf-8')as dr:
        json.dump(json_str, dr, indent=4, ensure_ascii=False)
    return {}
    

def save_json(json_data:dict):
    """A function that takes in the fully cleaned JSON data and saves it locally as a JSON file with the trial number as its name"""
    #gets the CTRI No. 
    filename=json_data.get("CTRI Number")
    print(filename)
    safe_filename = filename.replace('/', '_') + ".json"
    filedir="YOUR FILE PATH"
    #making a filepath for the trial data
    filepath=os.path.join(filedir,safe_filename)
    #dumping
    with open(filepath, 'w', encoding='utf-8') as dr:
        json.dump(json_data,dr, indent=4, ensure_ascii=False)
    print(f"Saved at {filepath}")

def extract(url):
    """Just a combination"""
    trial_data=fetch(url)
    json_data=cleanup(trial_data)
    save_json(json_data)

url = 'https://ctri.nic.in/Clinicaltrials/pmaindet2.php?EncHid=MzMxNQ==&Enc=&userName='
trail_data=fetch(url)
jsonda=cleanup(trail_data)
