import logging
import os
import sys
from time import sleep

import requests
from bs4 import BeautifulSoup

from push_notif import PushBullet


class Bot:
    def __init__(self, parse_url, pushbullet_client, retry_delay_seconds=60) -> None:
        self.url = parse_url
        self.retry_delay = retry_delay_seconds
        logging.basicConfig(
            format="[%(levelname)s] %(asctime)s: %(message)s",
            level=logging.INFO,
            handlers=[
                logging.StreamHandler(sys.stdout),
            ]
        )
        self.pb = pushbullet_client
        self.logger = logging.getLogger(name="burergerbot")
        self.proxy_flag = False

        self.pb.push_note("Burgeramt bot starting...", "good luck!")

    def fetch_page(self) -> requests.Response:
        self.logger.info("Fetching URL")
        if self.proxy_flag:
            # return requests.get(self.url, proxies={'https':'socks5://85.25.201.22:5577'})
            pass

        return requests.get(self.url)

    def toggle_proxy(self) -> None:
        self.logger.info(f"Toggling proxy to {not self.proxy_flag}")
        self.proxy_flag ^= self.proxy_flag

    def start(self) -> None:
        self.logger.info("Starting")
        while True:
            buchbar_list, nichtbuchbar_list = [], []
            page = self.fetch_page()
            if page.status_code == 429:
                print(page.content)
                self.logger.warning("rate limit. sleeping 5 min...")
                # self.toggle_proxy()
                sleep(300)
                continue

            soup = BeautifulSoup(page.content, 'html.parser')
            buchbar_list = soup.find_all('td', class_='buchbar')
            nichtbuchbar_list = soup.find_all('td', class_='nichtbuchbar') 

            if buchbar_list:
                found_msg = f"Found {len(buchbar_list)} days with termin."
                
                try:
                    termin_urls = [slot.a['href'] for slot in buchbar_list]
                except:
                    termin_urls = buchbar_list

                self.logger.info(found_msg)
                self.pb.push_note(found_msg, " ".join(termin_urls))
            else:
                self.logger.info(f"{len(nichtbuchbar_list)} ausgebucht, 0 verfugbar. Retrying in {self.retry_delay}s.")
            
            sleep(self.retry_delay)


if __name__ == "__main__":
    # Required args
    parse_url = "https://service.berlin.de/terminvereinbarung/termin/tag.php?termin=1&dienstleister=327427&anliegen[]=318998&herkunft=1"
    pushbullet_access_token = "o.rkgTIWggAb4hCg775viqOH4CuecBv9fn"

    # PushBullet, Bot init
    buerger_bot = Bot(
        parse_url=parse_url,
        pushbullet_client=PushBullet(pushbullet_access_token)
    )

    # Start Bot
    buerger_bot.start()
