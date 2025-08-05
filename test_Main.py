import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait as WDW
from methods import PageOperations
import datetime as dt
import os
import allure
import shutil

# 定义截图保存目录
SCREENSHOT_DIR = "TestScreenshots"

# 确保截图目录存在，如果不存在则创建
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)
    print(f"已创建截图目录: {SCREENSHOT_DIR}")
# #每次执行都删除旧记录
# if os.path.exists(SCREENSHOT_DIR):
#     shutil.rmtree(SCREENSHOT_DIR)
#     print(f"已删除旧截图目录: {SCREENSHOT_DIR}")

# checkDifference 函数保持不变
def checkDifference(date_str1: str, date_str2: str):
    """
    检查两个日期字符串之间的天数差是否严格大于14天。
    接受 'YYYY-MM-DD' 格式的日期字符串。
    """
    d1 = dt.datetime.strptime(date_str1, "%Y-%m-%d").date()
    d2 = dt.datetime.strptime(date_str2, "%Y-%m-%d").date()

    days_diff = d1 - d2
    if days_diff.days > 14:
        return 'Over14'
    elif days_diff.days < 0:
        return 'Less0'
    else:
        return 'Normal'


@pytest.fixture(scope="module")
def browser_setup():
    print("\n--- 正在启动浏览器 ---")
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.12306.cn/index/")
    driver.implicitly_wait(10)  # 隐式等待，用于一般的元素查找
    yield driver
    driver.quit()
    print("\n--- 已关闭浏览器 ---")


@allure.epic("12306 车票查询系统")
@allure.feature("单程车票查询")
@pytest.mark.parametrize(
    "start,end,date,stu,hsr,test_case_id",
    [
        ("北京", "上海", "2025-08-05", True, True, "12306_R001_001"),
        ("北京", "上海", "2025-08-05", False, False, "12306_R001_002"),
        ("北京", "上海", "2025-08-05", True, False, "12306_R001_003"),
        ("北京", "上海", "2025-08-05", False, True, "12306_R001_004"),
        ("北京", "北京", "2025-08-05", False, False, "12306_R002_001"),
        ("北京", "上海", "2024-01-01", False, False, "12306_R002_002"),
        ("北京", "上海", "2025-08-20", False, False, "12306_R002_003"),
    ]
)
def test_single_12306(browser_setup, start, end, date, stu, hsr, test_case_id):
    allure.dynamic.title(f"测试用例: {test_case_id} - {start} 至 {end} ({date})")

    base_description = (
        f"**测试用例编号:** {test_case_id}<br>\n"
        f"**测试目的:** 验证从 {start} 到 {end}，日期为 {date} 的单程车票查询功能。<br>\n"
        f"**输入参数:** 学生票: {stu}, 高铁/动车: {hsr}。<br>\n"
    )
    driver = browser_setup
    with allure.step("1. 打开12306官网并等待页面加载"):
        # 等待出发地输入框可见并可交互，确认页面加载完成
        WDW(driver, 15).until(
            ec.visibility_of_element_located((By.ID, "fromStationText"))
        )
        screenshot_name = f"{test_case_id}_InitialPage"
        allure_attach_screenshot(driver, screenshot_name)

    dr = PageOperations(driver)

    try:
        with allure.step(f"2. 输入查询信息并点击查询按钮: 出发地:{start}, 目的地:{end}, 日期:{date}, 学生票:{stu}, 高铁/动车:{hsr}"):
            dr.single_city_and_date(start, end, date, stu, hsr)
            driver.switch_to.window(driver.window_handles[1])
            screenshot_name = f"{test_case_id}_AfterSearchAndSwitch"
            allure_attach_screenshot(driver, screenshot_name)  # 在切换到新窗口后截图

        # 获取当前日期字符串，用于条件判断
        today = dt.datetime.now().strftime('%Y-%m-%d')
        is_invalid_input_scenario = False

        if start == end:
            is_invalid_input_scenario = True
            expected_result_message = "预期显示 '很抱歉，按您的查询条件，当前未找到' 消息 (出发地和目的地相同)。"
        elif checkDifference(date,today) == 'Over14':
            is_invalid_input_scenario = True
            expected_result_message = "预期显示 '很抱歉，按您的查询条件，当前未找到' 消息 (出发日期超出14天)。"
        elif checkDifference(date, today) == 'Less0':
            is_invalid_input_scenario = True
            expected_result_message = "预期显示 '很抱歉，按您的查询条件，当前未找到' 消息 (出发日期早于今天)。"
        else:
            expected_result_message = "预期显示符合条件的车次列表。"

        allure.dynamic.description(base_description + f"<br><b>预期结果:</b> {expected_result_message}")

        if is_invalid_input_scenario:
            with allure.step("3. 验证无效输入场景的预期结果"):
                try:
                    # 等待“没有查询到车次”的提示信息可见
                    no_results_element1 = WDW(driver, 30).until(  # 增加等待时间
                        ec.presence_of_element_located((By.ID, "no_filter_ticket_2"))
                    )
                    no_results_element2 = WDW(driver, 30).until(  # 增加等待时间
                        ec.presence_of_element_located((By.ID, "no_filter_ticket_6"))
                    )
                    # 检查其文本内容是否符合预期
                    if "很抱歉，按您的查询条件，当前未找到从" in no_results_element1.text or "查询超时，请稍后再试！" in no_results_element2.text:
                        allure.attach(
                            driver.get_screenshot_as_png(),
                            name=f"{test_case_id}_Success_InvalidInput_Displayed",
                            attachment_type=allure.attachment_type.PNG
                        )
                        pytest.assume(True, f"测试用例 {test_case_id} 成功: 预期无效输入结果匹配。")
                    else:
                        allure.attach(
                            driver.get_screenshot_as_png(),
                            name=f"{test_case_id}_Failure_InvalidInput_ContentMismatch",
                            attachment_type=allure.attachment_type.PNG
                        )
                        pytest.fail(f"测试用例 {test_case_id} 失败: 预期无效输入结果不符。")
                except Exception as e:
                    # 如果元素在30秒内都未变得可见，则捕获异常
                    allure.attach(
                        driver.get_screenshot_as_png(),
                        name=f"{test_case_id}_Failure_InvalidInput_NoElementOrNotVisible",
                        attachment_type=allure.attachment_type.PNG
                    )
                    pytest.fail(f"测试用例 {test_case_id} 失败: 预期无效输入但页面未显示预期结果。")

        else:  # 处理有效输入场景
            with allure.step("3. 验证有效输入场景的预期结果"):
                try:
                    # 等待车次列表表格可见
                    results_table = WDW(driver, 30).until(  # 增加等待时间
                        ec.presence_of_element_located((By.ID, "queryLeftTable"))
                    )

                    # 确保表格中没有“没有查询到车次”的提示，并且包含“车次”关键字（表示有列数据）
                    if results_table.text != '':
                        allure.attach(
                            driver.get_screenshot_as_png(),
                            name=f"{test_case_id}_Success_ValidInput_Displayed",
                            attachment_type=allure.attachment_type.PNG
                        )
                        pytest.assume(True, f"测试用例 {test_case_id} 成功: 有效输入结果匹配。")
                    else:
                        allure.attach(
                            driver.get_screenshot_as_png(),
                            name=f"{test_case_id}_Failure_ValidInput_ContentMismatch",
                            attachment_type=allure.attachment_type.PNG
                        )
                        pytest.fail(f"测试用例 {test_case_id} 失败: 预期有效输入结果不符。")
                except Exception as e:
                    allure.attach(
                        driver.get_screenshot_as_png(),
                        name=f"{test_case_id}_Failure_ValidInput_NoElementOrNotVisible",
                        attachment_type=allure.attachment_type.PNG
                    )
                    pytest.fail(f"测试用例 {test_case_id} 失败: 页面未加载车次列表或未按预期显示。")

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"{test_case_id}_CriticalFailure",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"测试用例 {test_case_id} 严重失败: {e}")
    finally:  # 确保在测试结束时进行清理，无论测试结果如何
        driver.close()
        driver.switch_to.window(driver.window_handles[0])


# 辅助函数：将截图附加到 Allure 报告中
def allure_attach_screenshot(driver, name):
    """保存屏幕截图并将其附加到 Allure 报告中"""
    timestamp = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{name}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(filepath)
    with open(filepath, "rb") as image_file:
        allure.attach(image_file.read(), name=name, attachment_type=allure.attachment_type.PNG)
    print(f"截图已保存并附加到报告: {filepath}")