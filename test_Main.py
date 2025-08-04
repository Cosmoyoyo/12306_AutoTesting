import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait as WDW
from methods import PageOperations
import time
from datetime import datetime, timedelta
import datetime as dt
import os

SCREENSHOT_DIR = "./ScreenshotResult"
if not os.path.exists(SCREENSHOT_DIR):
    os.mkdir(SCREENSHOT_DIR)

@pytest.fixture(scope="module")
def browser_setup():
    print("\n--- 正在启动浏览器 ---")
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()
    print("\n--- 已保存图片至本地并关闭浏览器 ---")


@pytest.mark.parametrize("start,end,date,stu,hsr", [
    ("北京", "上海", "2025-08-05", True, True),  # 合法查询
    ("北京", "上海", "2025-08-05", False, False),
    ("北京", "上海", "2025-08-05", True, False),
    ("北京", "上海", "2025-08-05", False, True),
    ("北京", "北京", "2025-08-05", False, False),  # 无效输入：同城
    ("北京", "上海", "2024-01-01", False, False),  # 无效输入：过去日期
    ("北京", "上海", "2025-08-20", False, False),  # 无效输入：日期相差超过14天 (假设今天是2025-08-04)
], ids=[
    "12306_R001_001",
    "12306_R001_002",
    "12306_R001_003",
    "12306_R001_004",
    "12306_R002_001",
    "12306_R002_002",
    "12306_R002_003",
])
def test_single_12306(browser_setup, start, end, date, stu, hsr, request):
    driver = browser_setup
    test_case_id = request.node.callspec.id  # 获取当前测试用例的 ID (即 ids 中定义的值)
    print(f"\n--- 执行测试用例: {test_case_id} ---")
    driver.get("https://www.12306.cn/index/")
    dr = PageOperations(driver)
    dr.single_city_and_date(start, end, date, stu, hsr)

    today = dt.datetime.now().strftime('%Y-%m-%d')
    #换到搜索结果页面
    driver.switch_to.window(driver.window_handles[1])
    '''
    判断输入值
    1. 出发地和目的地相同
    2. 出发日期小于当前日期
    3. 出发日期大于当前日期14天以上
    '''
    # 加载完后才进行判断
    WDW(driver, 5).until(ec.presence_of_element_located((By.ID, "queryLeftTable")))
    if start == end or checkDifference(date, today):
        if driver.find_element(By.ID,"queryLeftTable").text == '':
            timestamp = dt.datetime.now().strftime("%Y-%m-%d")
            screenshot_filename = os.path.join(SCREENSHOT_DIR,f"{timestamp}_{test_case_id}.png")
            driver.save_screenshot(screenshot_filename)
        else:
            timestamp = dt.datetime.now().strftime('%Y-%m-%d')
            screenshot_filename = os.path.join(SCREENSHOT_DIR,f"{timestamp}_{test_case_id}_FAILURE.png")
            driver.save_screenshot(screenshot_filename)
            pytest.fail(f"测试用例 {test_case_id} 失败: 日期或地址错误")  # 使用 pytest.fail 标记测试用例失败
    else:
        timestamp = dt.datetime.now().strftime("%Y-%m-%d")
        screenshot_filename = os.path.join(SCREENSHOT_DIR,f"{timestamp}_{test_case_id}.png")
        driver.save_screenshot(screenshot_filename)

    #关闭页面
    driver.close()
    #回到首页
    driver.switch_to.window(driver.window_handles[0])


def checkDifference(target, today):
    """
    检查两个日期字符串之间的天数差是否严格大于14天。
    接受 'YYYY-MM-DD' 格式的日期字符串。
    target: 出发日期
    today:  今天
    """
    target = datetime.strptime(target, "%Y-%m-%d")
    today = datetime.strptime(today, "%Y-%m-%d")
    if (target - today).days > 14 or (target - today).days < 0:
        return True
    else:
        return False

