import os

from selenium import webdriver
import time
import platform
import getpass
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By


def find_path(autore_to_find):
    path = ""
    so = platform.system()
    print("Il sistema operativo è: " + so)

    username = getpass.getuser()
    print("L'utente è: " + username)

    if so == "Windows":
        path = "C:\\Users\\" + username + "\\Desktop\\FilePDF\\" + autore_to_find + ""
        if not os.path.exists(path):
            os.makedirs(path)
        print(path)
    elif so == "Mac OS X":
        path = "/Users/" + username + "/Desktop"
        print(path)
    elif so == "Linux":
        path = "/home/" + username + "/Desktop"

    return path


def reload(this_driver, page_to_reload):
    this_driver.implicitly_wait(5)
    this_driver.get(page_to_reload)
    time.sleep(1)
    this_driver.find_element(By.ID, "gsc_bpf_more").click()
    time.sleep(1)
    this_driver.find_element(By.ID, "gsc_bpf_more").click()
    time.sleep(1)


def find_path(autore_to_find):
    path = ""
    so = platform.system()
    print("Il sistema operativo è: " + so)

    username = getpass.getuser()
    print("L'utente è: " + username)

    if so == "Windows":
        path = "C:\\Users\\" + username + "\\Desktop\\FilePDF\\" + autore_to_find + ""
        if not os.path.exists(path):
            os.makedirs(path)
        print(path)
    elif so == "Mac OS X":
        path = "/Users/" + username + "/Desktop"
        print(path)
    elif so == "Linux":
        path = "/home/" + username + "/Desktop"

    return path


def setup_driver(autore_to_find):

    path = find_path(autore_to_find)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--start-maximized")
    options.add_experimental_option('prefs', {
        "download.default_directory": path,
        # Change default directory for downloads
        "download.prompt_for_download": False,  # To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
    })
    # Optional argument, if not specified will search path.
    service = ChromeService(executable_path="C:\\Program Files (x86)\\chromedriver.exe")
    our_driver = webdriver.Chrome(service=service, options=options)

    return our_driver


if __name__ == '__main__':  # MAIN! PREPARAZIONE AL PRELIEVO DEI FILE PDF

    autori = ["Zhenchang Xing", "Bram Adams", "Kelly Blincoe", "Xin Xia", "Gordon Fraser", "Romain Robbes", "Sven Apel"]

    for autore in autori:

        driver = setup_driver(autore)
        driver.get("https://scholar.google.com//")
        form_textfield = driver.find_element(By.NAME, 'q')
        form_textfield.send_keys(autore + Keys.ENTER)
        driver.find_element(By.PARTIAL_LINK_TEXT, autore).click()
        driver.find_element(By.PARTIAL_LINK_TEXT, autore).click()
        driver.find_element(By.PARTIAL_LINK_TEXT, "ANNO").click()
        time.sleep(2)
        driver.find_element(By.ID, "gsc_bpf_more").click()
        time.sleep(2)
        driver.find_element(By.ID, "gsc_bpf_more").click()
        time.sleep(2)

        # si prendono tutte le righe della tabella e per ognuna di esse si va a prelevare il titolo e l'anno di pubblicazione
        # che verranno inseriti nelle apposite liste

        table_id = driver.find_element(By.ID, 'gsc_a_t')
        rows = table_id.find_elements(By.CLASS_NAME, "gsc_a_tr")  # get all of the rows in the table
        list_years = []
        list_titles = []
        for row in rows:

            # Get the columns (all the column 2)
            year = row.find_elements(By.CLASS_NAME, "gsc_a_y")  # note: index start from 0, 1 is col 2
            if year[0].text >= "2019":
                list_years.append(year[0].text)
                title = row.find_elements(By.CLASS_NAME, "gsc_a_at")
                list_titles.append(title[0].text)

        # prelievo dell'URL della pagina corrente
        principal_page = driver.current_url

        # prelievo dei file PDF da ogni singolo articolo
        for (year_row, title_row) in zip(list_years, list_titles):
            if int(year_row) >= 2019:
                try:
                    driver.implicitly_wait(10)
                    driver.find_element(By.LINK_TEXT, title_row).click()
                    driver.implicitly_wait(10)
                    time.sleep(2)
                    driver.find_element(By.PARTIAL_LINK_TEXT, "PDF").click()
                    time.sleep(2)
                    driver.implicitly_wait(10)
                    time.sleep(2)
                    reload(driver, principal_page)

                except:

                    print("Eccezione sul titolo " + title_row)
                    driver.implicitly_wait(10)
                    reload(driver, principal_page)
            time.sleep(2)