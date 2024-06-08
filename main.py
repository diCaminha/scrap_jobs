import os.path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from bs4 import BeautifulSoup
import pandas as pd

from Job import Job


def get_job_from_card(job_card):
    td = job_card.find("td")
    if td:
        div_tags = [div for div in td.find_all('div', recursive=False)]
    else:
        return None

    title = div_tags[0].find("h2").text
    link = div_tags[0].find("h2").find("a").get("href")
    div_c_l = div_tags[1].find('div')
    company_location_divs = [div for div in div_c_l.find_all('div', recursive=False)]

    company = company_location_divs[0].find("span").text
    location = company_location_divs[1].text

    return Job(title, company, location, link)


if __name__ == '__main__':

    vaga = input("informe a vaga: ")
    vaga = vaga.replace(" ", "+")

    localidade = input("informe a localidade para a vaga: ")
    localidade = localidade.replace(" ", "+")

    file_name = f"{vaga}_{localidade}.csv"

    if not os.path.exists(file_name):
        service = Service('/opt/homebrew/bin/chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

        driver = webdriver.Chrome(service=service, options=options)

        try:
            url = f"https://br.indeed.com/jobs?q={vaga}&l={localidade}"
            print(f"Buscando vagas no site Indeed com link: {url}")

            driver.get(url)

            wait = WebDriverWait(driver, 10)

            job_cards = wait.until(EC.presence_of_element_located((By.ID, 'mosaic-provider-jobcards')))
            time.sleep(random.uniform(1, 5))

            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')

            job_cards = soup.find(id="mosaic-provider-jobcards")

            if job_cards:
                lis = job_cards.find("ul").find_all("li", recursive=False)
                jobs = []
                for li in lis:
                    job = get_job_from_card(li)
                    if job:
                        jobs.append(job)

            jobs_dict = [vars(j) for j in jobs]
            df = pd.DataFrame(jobs_dict)
            df.to_csv(file_name)
            print(df["title"])

        finally:
            driver.quit()

    else:
        df = pd.read_csv(file_name)
        print(df["title"])




