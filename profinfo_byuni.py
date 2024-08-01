import urllib.request
import re
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
work_dirs = '/Users/wjs/Library/CloudStorage/OneDrive-Personal/Coding, ML & DL/work_dirs'

def get_unique_df(df:pd.DataFrame,key:str)->pd.DataFrame:
    # Find unique elements
    unique_name_idx_dict = {}
    for idx in range(df.shape[0]):
        name = df[key][idx]
        unique_name_idx_dict[name] = idx
    df = df.iloc[list(unique_name_idx_dict.values())]
    return df

def get_website(url:str):
    response = urllib.request.urlopen(url) # 网站的地址
    html = response.read().decode("utf-8")
    website = BeautifulSoup(html,'html.parser')  # 用于解析获取到的源码
    return website

class nus_profs():
    def __init__(self) -> None:
        self.univ = 'NUS'
        self.univurl = 'https://www.comp.nus.edu.sg'
        self.facultyurl = f"""https://www.comp.nus.edu.sg/cs/research/#ra"""
        self.allurls_byra = self.get_url_allareas()
        self.basicinfo = None
        self.detailedinfo = None

    def get_prof_basicinfo(self):
        prof_df = []
        for area in self.allurls_byra:
            url = self.allurls_byra[area]
            print(f'{area}:{url}')
            raw_jscode = self.get_jscode_byarea(area,self.allurls_byra)
            prof_df_byarea = self.get_profdata_byjscode(raw_jscode)
            prof_df.append(prof_df_byarea)
            # display(prof_df_byarea[["Name","ResearchArea","Bio"]].head())
        prof_df = pd.concat(prof_df)
        prof_df.reset_index(inplace=True,drop=True)
        prof_df = get_unique_df(prof_df,key='Name')
        print(prof_df)
        self.basicinfo = prof_df
    
    def get_prof_detailedinfo(self):
        prof_df = self.basicinfo
        names = prof_df['Name'].tolist()
        urls = prof_df['Bio'].tolist()
        prof_infos = []
        numberofnames = len(names)
        for idx, url in enumerate(urls):
            name = names[idx]
            print(f'Get Data for {name}, {idx}/{numberofnames}')
            prof_info = self.get_detailedinfo_forprof(url)
            prof_info['Name'] = name
            prof_infos.append(prof_info)
        prof_infos = pd.concat(prof_infos)
        prof_infos.reset_index(drop=True,inplace=True)
        self.detailedinfo = prof_infos

    def get_url_allareas(self) -> dict:
        url = self.facultyurl
        bs = get_website(url)
        all_researchareas = [h.find_all('a') for h in bs.find_all("h6",{"class":"elementor-heading-title elementor-size-default"})][:8]
        all_researchareas = [ra[0] for ra in all_researchareas]
        all_researchareas = {ra.text:ra['href'] for ra in all_researchareas}
        return all_researchareas

    def get_jscode_byarea(self, area: str, urls: dict):
        url = f"""{urls[area]}people"""
        print('Get data from: ', url)
        bs = get_website(url)
        jscript = bs.find_all('script')
        js_code = jscript[11]
        return js_code

    def get_profdata_byjscode(self, raw_jscode):
        # Input string containing the data
        data_string = str(raw_jscode)

        # Define a regex pattern to extract key-value pairs
        pattern = r'name:\s*"([^"]*)".*?title:\s*"([^"]*)".*?email:\s*"<img src=\\"([^\\"]+)\\".*?officetel:\s*"([^"]*)".*?tel:\s*"([^"]*)".*?image:\s*"([^"]*)".*?image2:\s*"([^"]*)".*?socid:\s*"([^"]*)".*?Dept:\s*"([^"]*)".*?Area:\s*"([^"]*)".*?Bio:\s*"([^"]*)".*?ApptAdm:\s*"([^"]*)".*?researcharea:\s*"<a [^>]*>(.*?)</a>".*?biolinkstat:\s*"([^"]*)".*?photoSrc:\s*"([^"]*)".*?'
        data_string = data_string.split('scope.allStaffs =')[1]
        matches = re.findall(pattern, data_string, re.DOTALL)

        # Store in a dataframe
        prof_df = []
        for match in matches:
            (name, title, email, officetel, tel, image, image2, socid, Dept, Area, Bio, ApptAdm, researcharea, biolinkstat, photoSrc) = match
            new_df = pd.DataFrame([[name, title, email, officetel, tel, image, image2, socid, Dept, Area, Bio, researcharea]])

            new_df.columns = ['Name','Title','Email','OfficeTel','Tel','Image','Image2','Socid','Dept','Area','Bio','ResearchArea']
            # Email: in the form of photo
            prof_df.append(new_df)
        prof_df = pd.concat(prof_df)
        # Bio: add https://www.comp.nus.edu.sg/ as prefix
        prof_df['Bio'] = self.univurl + prof_df['Bio']
        # Research Area: decompose into a nice string
        pattern = r'<span[^>]*>(.*?)</span>'
        prof_df['ResearchArea'] = [re.findall(pattern, researcharea) for researcharea in prof_df['ResearchArea'].to_list()]
        prof_df.reset_index(inplace=True,drop=True)
        return prof_df

    def get_detailedinfo_forprof(self, profurl):
        def get_researchinterest(website):
            # Research interest
            research_interest = website.find_all(attrs={'id':'res_interest'})[0].find_all('p')
            research_interest = [ri.text for ri in research_interest]
            return research_interest
        def get_award(website):
            # Awards
            awards = website.find_all(attrs={'id':'award'})[0].find_all('p')
            awards = [a.text for a in awards]
            return awards
        def get_teaching(website):
            # Modules Taught
            def clean_special(text):
                text = text.split('\n')[1:3]
                text = ' '.join(text)
                return text
            courses = website.find_all(attrs={'id':'teaching'})[0].find_all('div',attrs={"style":"justify-content:flex-start;gap:15px;display:flex;margin-bottom:8px;"})
            courses = [clean_special(course.text) for course in courses]
            return courses
        def get_profile(website):
            # Profile
            profile = website.find_all(attrs={'id':'profile'})[0].find_all('p')[0]
            profile = profile.text
            return profile
        def get_publication(website):
            # Selected Pub
            def clean_selectedpub(pub):
                # Regex pattern to extract the article name
                pattern = r'"(.*?)"'

                # Search for the pattern in the text
                match = re.search(pattern, pub)
                try:
                    return match.group(1)
                except:
                    return pub
            selectedpubs = website.find_all(attrs={'id':'selectedpublication'})[0].find_all(attrs = {'class':'pub1'})
            selectedpubs = [clean_selectedpub(pub.text) for pub in selectedpubs]
            return selectedpubs
        
        website = get_website(profurl)
        prof_info = dict()
        prof_info['researchinterest'] = get_researchinterest(website)
        prof_info['award'] = get_award(website)
        prof_info['course'] = get_teaching(website)
        prof_info['profile'] = get_profile(website)
        prof_info['publication'] = get_publication(website)
        prof_info = {key:[value] for key,value in prof_info.items()}
        prof_info = (pd.DataFrame(prof_info))
        return prof_info

    def get_filename(self, infotype):
        return f'{self.univ}prof_{infotype}'

    def store_prof_info(self, infotype):
        filename = self.get_filename(infotype)
        # Store the csv
        if infotype == 'basic':
            df = self.basicinfo
        else:
            df = self.detailedinfo
        print(f'Save {infotype} info to {work_dirs}/{filename}.csv')
        df.to_csv(f'{work_dirs}/{filename}.csv')

    def read_prof_info(self, infotype):
        filename = self.get_filename(infotype)
        # Read the csv
        converter_dict = {
            'ResearchArea':lambda x: x.strip("[]").replace("'","").split(", "),
            "researchinterest": lambda x: x.strip("[]").replace("'","").split(", "),
            'publication': lambda x: x.strip("[]").replace("'","").split(", "),
        }
        df = pd.read_csv(f'{work_dirs}/{filename}.csv',converters = converter_dict)
        df = df.set_index('Name')
        if infotype == 'basic':
            self.basicinfo = df
        else:
            self.detailedinfo = df

    def read_prof_info(self,infotype='basic'):
        return f'{self.univ}prof_{infotype}'
    
def main(argv):
    nus_professors = nus_profs()
    nus_professors.get_prof_basicinfo()
    nus_professors.store_prof_info('basic')

import sys
if __name__ == "__main__":
    argv = sys.argv
    main(argv)