import appdaemon.plugins.hass.hassapi as hass
from datetime import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Solarman(hass.Hass):

    sensors = {
        "webdata_now_p": {
            'type': 'power',
            'friendly_name': 'Current power',
            'unit_of_measurement': 'W',
            'icon': 'mdi:solar-power',
        },
        "webdata_today_e": {
            'type': 'energy',
            'friendly_name': 'Yield today',
            'unit_of_measurement': 'kWh',
            'icon': 'mdi:lightning-bolt-outline',
        },
        "webdata_total_e": {
            'type': 'energy',
            'friendly_name': 'Yield total',
            'unit_of_measurement': 'kWh',
            'icon': 'mdi:lightning-bolt'
        }
    }
    
    DEFAULT_VALUE = "not-found"
    DEFAULT_UNIT = "??"
    

    def initialize(self):
        self.log("Initializing Solarman App")
        
        self.init_selenium_driver()
        self.make_url()
        self.run_minutely(self.read_inverter_page, time(0,0,1))
    
    def make_url(self):
        auth = f"{self.args['user']}:{self.args['password']}"
        self.url =  f"http://{auth}@{self.args['ip']}/index_cn.html"
    
    def read_inverter_page(self, kwargs):
        if not self.get_page():
            return
        
        try:
            iframe = self.driver.find_element(By.ID, "child_page")
            self.driver.switch_to.frame(iframe)
            
            readouts = self.get_readouts()
            
            self.solarman_state("on")
            
            self.update_sensors(readouts)
            
        except Exception as e:
            self.log("Unable to find elements in DOM ")
            self.log(e)
            return

    def get_page(self):
        """ Loads URL content and handles potential errors
        """
        try:
            self.driver.get(self.url)
        except Exception as e:
            self.log("Unable to reach URL")
            self.log(e)
            self.solarman_state("off")
            return False
        
        return True

    def get_readouts(self):
        """ Loops over all sensors and asks to fetch data
        """
        readouts = {
            entity: self.get_element(entity) for entity in self.sensors
        }
            
            
        log_str = ", ".join(f"{entity}: {value} {unit}" for entity, (value, unit) in readouts.items())
        self.log(f"Readout values: {log_str}")
        
        return readouts
    
    def get_element(self, id):
        """ Fetches data for one sensor
        """
        value = self.DEFAULT_VALUE
        unit = self.DEFAULT_UNIT
        try:
            text = WebDriverWait(self.driver, timeout=2, poll_frequency=.2).until(
                EC.presence_of_element_located((By.ID, id))
            ).text
            
            value, unit = text.split(" ")
        except:
            pass
        
        return value, unit
    
    def update_sensors(self, readouts):
        """ Sets new value - unit for all sensors
        """
        for entity, (value, unit) in readouts.items():
            if value == self.DEFAULT_VALUE:
                continue
            
            self.set_state(
                f"solarman.{entity}",
                state=value,
                attributes={
                    "unit_of_measurement": unit
                }
            )
    
    def solarman_state(self, state):
        """ Set solarman.state to on / off
        """
        self.set_state(
            "solarman.state",
            state=state,
        )
    
    def init_selenium_driver(self):
        """ Initialize selenium driver with all required options
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--user-data-dir=chrome-data")
        chrome_options.add_argument("user-data-dir=chrome-data")
        
        service = Service(executable_path='/usr/bin/chromedriver')
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.log("Initialized Selenium driver")
    
    def terminate(self):
        self.driver.quit()
        self.solarman_state("off")
