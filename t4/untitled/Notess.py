from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time
import random
import string

# Appium Server 地址和 Desired Capabilities
# 请根据您的实际设备/模拟器信息确认和修改以下值
# 注意：如果您之前在Appium Inspector中遇到W3C Capabilities错误，
# 并且服务器设置没有自动添加前缀，您可能需要在这些capability名称前手动加上 'appium:'
# 例如 'appium:platformVersion': '9'
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9', # **请根据您的实际设备/模拟器版本修改**
    'deviceName': 'emulator-5554',    # **请根据您的实际设备/模拟器名称/ID修改**
    'appPackage': 'com.lht.mali.corporation.notepad',
    'appActivity': 'com.example.richtext.ui.activity.NoteActivity',
    'noReset': True,                  # 设置为 True 可以保留之前创建的便签
    'unicodeKeyboard': True,
    'resetKeyboard': True,
    'automationName': 'Uiautomator2'
}

appium_server_url = 'http://localhost:4723' # Appium 服务地址
num_notes_to_create = 30 # 要创建的便签数量

# --- 元素定位器 ---
# 根据之前您提供的XML查找到的实际元素信息
ADD_BUTTON_ID = 'com.lht.mali.corporation.notepad:id/addbutton' # 主界面 '+' 按钮ID
TITLE_FIELD_ID = 'com.lht.mali.corporation.notepad:id/editor_title' # 创建/编辑页面 标题输入框ID
CONTENT_FIELD_LOCATOR = "//android.widget.EditText[@hint='请输入内容']" # 创建页面 内容输入框XPath (根据hint定位)
SAVE_BUTTON_ID = 'com.lht.mali.corporation.notepad:id/button_save' # 创建/编辑页面 保存按钮ID

def generate_random_string(length):
    """生成随机字符串"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

if __name__ == '__main__':
    driver = None
    try:
        print(f"--- 开始创建 {num_notes_to_create} 个便签 ---")
        # 连接 Appium 服务器
        driver = webdriver.Remote(appium_server_url, desired_caps)
        driver.implicitly_wait(10) # 设置隐式等待

        app_package = desired_caps['appPackage']

        # 激活应用，确保应用在前台运行并处于启动Activity
        try:
            driver.activate_app(app_package)
            print(f"成功激活应用: {app_package}")
            time.sleep(3) # 等待应用启动和页面加载
        except Exception as e:
            print(f"激活应用 {app_package} 失败: {e}")
            # 如果应用激活失败，整个创建过程可能无法进行
            exit() # 退出脚本

        for i in range(1, num_notes_to_create + 1):
            print(f"\n开始创建第 {i} 个便签...")
            try:
                # 1. 点击主界面“+”按钮，进入新建便签页面
                add_button = driver.find_element(AppiumBy.ID, ADD_BUTTON_ID)
                add_button.click()
                print(f"成功点击 '+' 按钮 (ID: {ADD_BUTTON_ID})")
                time.sleep(2) # 等待页面跳转

                # 2. 定位标题文本框并输入内容
                note_title = f"自动化便签 - {i}"
                title_field = driver.find_element(AppiumBy.ID, TITLE_FIELD_ID)
                title_field.send_keys(note_title)
                print(f"成功输入标题: '{note_title}' (ID: {TITLE_FIELD_ID})")

                # 3. 定位内容文本框并输入内容
                # 内容可以更随意，例如包含时间戳和随机字符串
                note_content = f"这是第 {i} 个自动化便签的内容。\n创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n随机内容: {generate_random_string(50)}"
                content_field = driver.find_element(AppiumBy.XPATH, CONTENT_FIELD_LOCATOR)
                content_field.send_keys(note_content)
                print(f"成功输入内容 (XPath: {CONTENT_FIELD_LOCATOR})")

                time.sleep(1) # 输入后等待一下

                # 4. 点击保存按钮
                save_button = driver.find_element(AppiumBy.ID, SAVE_BUTTON_ID)
                save_button.click()
                print(f"成功点击保存按钮 (ID: {SAVE_BUTTON_ID})")
                time.sleep(2) # 等待保存响应，回到列表页

                print(f"第 {i} 个便签创建完成。")
                # 在创建每个便签后可以短暂等待，让应用回到列表页稳定

            except Exception as e:
                print(f"创建第 {i} 个便签失败: {e}")
                # 发生错误时，可以根据需要捕获异常并继续，或者中断
                # 这里选择打印错误并继续尝试创建下一个便签

        print(f"\n--- 完成创建 {num_notes_to_create} 个便签 ---")

    except Exception as e:
        print(f"\n脚本运行过程中发生错误: {e}")

    finally:
        # 最后关闭 Appium 会话
        if driver:
            try:
                print("关闭 Appium 会话...")
                driver.quit()
                print("Appium 会话已关闭。")
            except Exception as e:
                print(f"关闭 Appium 会话失败: {e}")