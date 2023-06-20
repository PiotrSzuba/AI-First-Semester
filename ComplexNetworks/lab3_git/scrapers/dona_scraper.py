import io
import os
import time
import shutil
import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from typing import Tuple, List
from pyppeteer import launch, element_handle, page, browser


class DonaScraper:
    author_search_box_id = "#RadDock_formularze_C_RadSearchBox1_Input"
    author_info_id = "#RadDock1_info_autora_T_RadLabel_dock_info_autora"
    page_size_option_id = "li.rddlItem"
    page_size_select_id = "#RadGrid_glowny_ctl00_ctl02_ctl00_PageSizeDropDownList"
    page_size_select_dropdown_id = (
        "#RadGrid_glowny_ctl00_ctl02_ctl00_PageSizeDropDownList_DropDown"
    )
    loading_overlay_id = "#RadAjaxLoadingPanel1RadGrid_glowny"

    def __init__(self):
        self.browser: browser.Browser = None
        self.page: page.Page = None
        self.download_request = None

    async def start(self, url: str) -> Tuple[browser.Browser, page.Page]:
        self.browser = await launch()
        self.page = await self.browser.newPage()
        await self.page.goto(url)

    async def login(self, email: str, password: str):
        await self.change_page("https://dona.pwr.edu.pl/szukaj/")
        await self.click_element("#RadButton_login")
        await self.enter_text("#RadTextBox_uzytkownik", email)
        await self.enter_text("#RadTextBox_haslo", password)
        await self.click_element("#RadButton_zaloguj")
        await self.wait_for_element_to_hide("#RadTextBox_uzytkownik")
        await self.wait_for_element_to_hide(self.loading_overlay_id)

    async def is_logged_in(self):
        element = await self.get_element("#RadButton_login")
        rbText_span = await element.querySelector("span.rbText")
        text = await (await rbText_span.getProperty("textContent")).jsonValue()

        return text == "Wyloguj" or text == "Log out"

    async def change_page(self, url: str):
        await self.page.goto(url)

    async def end(self):
        await self.browser.close()

    async def get_element(self, selector: str) -> element_handle.ElementHandle:
        await self.page.waitForSelector(selector)

        return await self.page.querySelector(selector)

    async def get_elements_list(
        self, selector: str
    ) -> List[element_handle.ElementHandle]:
        await self.page.waitForSelector(selector)

        return await self.page.querySelectorAll(selector)

    async def enter_text(self, selector: str, text: str):
        element = await self.get_element(selector)
        await element.type(text)

    async def click_element(self, selector: str):
        element = await self.get_element(selector)
        await element.click()

    async def wait_for_css_change(
        self, selector: str, css_prop_name: str, wanted_state: str
    ):
        js_function = f"() => {{ return window.getComputedStyle(document.querySelector('{selector}')).{css_prop_name} === '{wanted_state}'; }}"
        await self.page.waitForFunction(js_function)
        time.sleep(1)

    async def select_option_from_list(self, li_selector: str, option: str):
        elements = await self.get_elements_list(li_selector)

        for li_element in elements:
            text = await self.page.evaluate("el => el.textContent", li_element)

            if text != option:
                continue

            if not await li_element.isIntersectingViewport():
                await self.page.evaluate("el => el.scrollIntoView()", li_element)

            await li_element.click()
            break

    async def wait_for_element_to_hide(self, selector: str):
        await self.page.waitForSelector(selector, hidden=True)

    async def get_soup(self) -> BeautifulSoup:
        html_content = await self.page.content()

        return BeautifulSoup(html_content, "html.parser")

    async def download_file(self, button_selector: str, file_path: str):
        self.page.on("request", self._handle_request)

        await self.click_element(button_selector)

        timeout = 60
        try:
            await asyncio.wait_for(self._wait_for_download_request(), timeout)
        except asyncio.TimeoutError:
            print(f"Timeout reached after {timeout} seconds")
            return None

        buffer = await self._fetch_file()

        df = pd.read_excel(io.BytesIO(buffer))
        df.to_csv(file_path, index=False)

    def _handle_request(self, request):
        if (
            "Handler1.ashx" in request.url
            and "plik_nazwa" in request.url
            and "respo=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in request.url
        ):
            self.download_request = request

    async def _fetch_file(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.download_request.url) as response:
                buffer = await response.read()
                self.download_request = None
                return buffer

    async def _wait_for_download_request(self):
        while self.download_request is None:
            await asyncio.sleep(1)

    async def download_publications(self, url: str, output_path: str):
        await self.page.goto(url)
        await self.page.waitForSelector(self.author_info_id, {'timeout': 60000})
        await self.select_option_from_list("li.rtsLI", "Wydruki")

        await self.page.waitForSelector("#RadButton_pobierz_wydruk_wykaz")
        time.sleep(3)

        await self.click_element("#RadDropDownList1")

        await self.select_option_from_list("li.rddlItem", "format Excel (xlsx)")

        await self.download_file("#RadButton_pobierz_wydruk_wykaz", output_path)


async def main(force: bool = False):
    dona_scraper = DonaScraper()
    await dona_scraper.start("https://dona.pwr.edu.pl/szukaj/")
    await dona_scraper.login("252807@student.pwr.edu.pl", "123qazxS#")

    if not await dona_scraper.is_logged_in():
        print("Could not login !")
        return
    
    faculties = ["W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12", "W13"]
    
    for faculty_name in faculties:
        input_path = f"raw_data_cache/{faculty_name}_workers.csv"
        directory = input_path.replace(".csv", "")

        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(input_path):
            print(input_path, "=> doesnt exist")
            continue
    
        df = pd.read_csv(input_path)

        for _, row in df.iterrows():
            worker = (row["dona_url"], row["name"])

            path = f"{directory}/{worker[1].replace(' ', '_')}.csv"

            if os.path.exists(path) and not force:
                print(f"{path} => already scrapped".ljust(shutil.get_terminal_size().columns), end="\r")
                continue

            print(f" {faculty_name} Started scraping: {worker[1]}".ljust(shutil.get_terminal_size().columns), end="\r")

            try:
                await dona_scraper.download_publications(worker[0], path)
            except:
                print(f"{faculty_name} scraping: {worker[1]} FAILED")

    await dona_scraper.end()



asyncio.get_event_loop().run_until_complete(main())

# await dona_scraper.page.screenshot({"path": "00Screshot.png"})
