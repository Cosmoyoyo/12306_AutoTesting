import time
import datetime
from itertools import count

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PageOperations:

    def __init__(self, driver):
        """
        初始化PageOperations类，传入一个WebDriver实例
        """
        self.driver = driver

    def single_city_and_date(self, start, end, date, stu, hsr):

        startInput = self.driver.find_element(By.ID, "fromStationText")
        startInput.clear()
        startInput.send_keys(start)
        panel_lists = self.driver.find_elements(By.XPATH, "//div[@id='panel_cities']/*/span[@class='ralign'][1]")
        for panel in panel_lists:
            if panel.text == start:
                panel.click()
                break

        endInput = self.driver.find_element(By.ID, "toStationText")
        endInput.clear()
        endInput.send_keys(end)
        panel_lists = self.driver.find_elements(By.XPATH, "//div[@id='panel_cities']/*/span[@class='ralign'][1]")
        for panel in panel_lists:
            if panel.text == end:
                panel.click()
                break

        dateInput = self.driver.find_element(By.ID, "train_date")
        dateInput.clear()
        dateInput.send_keys(date)

        if stu:
            stu_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "isStudentDan"))
            )
            stu_button.click()
        if hsr:
            hsr_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "isHighDan"))
            )
            hsr_button.click()
        #查询按钮
        query_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "search_one"))
        )
        query_button.click()



    def round_city_and_date(self, start, end, date1, date2, stu, hsr):
        startInput = self.driver.find_element(By.ID, "fromStationFanText")
        startInput.send_keys(start)

        endInput = self.driver.find_element(By.ID, "toStationFanText")
        endInput.send_keys(end)

        date1input = self.driver.find_element(By.ID, "go_date")
        date1input.send_keys(date1)

        date2input = self.driver.find_element(By.ID, "from_date")
        date2input.send_keys(date2)

        if stu:
            self.driver.find_element(By.ID, "isStudent").click()
        if hsr:
            self.driver.find_element(By.ID, "isHigh").click()
        self.driver.find_element(By.ID, "search_two").click()

    def midterm_city_and_date(self, start, end, date, stu):
        startInput = self.driver.find_element(By.ID, "fromStationSerialText")
        startInput.send_keys(start)

        endInput = self.driver.find_element(By.ID, "toStationSerialText")
        endInput.send_keys(end)

        dateInput = self.driver.find_element(By.ID, "serial_date")
        dateInput.send_keys(date)

        if stu:
            self.driver.find_element(By.ID, "isStudentLian").click()

        self.driver.find_element(By.ID, "search_three").click()



