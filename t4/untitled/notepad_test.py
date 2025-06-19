import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy # 用于新的元素定位方法
from selenium.webdriver.common.by import By # 如果使用By.ID等，也需要导入
import time
import random
import string # 用于生成随机字符串


# 您提供的 desired_caps 和其他变量定义
# 请根据您的实际设备/模拟器信息确认和修改以下值
# 注意：如果您之前在Appium Inspector中遇到W3C Capabilities错误，
# 并且服务器设置没有自动添加前缀，您可能需要在这些capability名称前手动加上 'appium:'
# 例如 'appium:platformVersion': '9'
desired_caps = {
    'platformName': 'Android',         # 平台名称
    'platformVersion': '9', # Android 版本号，例如 '10' 或 '12' - **请根据您的实际设备/模拟器版本修改**
    'deviceName': 'emulator-5554',    # 可以是adb devices查看到的设备ID或模拟器名称 - **请根据您的实际设备/模拟器名称/ID修改**
    'appPackage': 'com.lht.mali.corporation.notepad', # App 的包名 - 已根据adb命令查到填充
    'appActivity': 'com.example.richtext.ui.activity.NoteActivity',   # App 的启动 Activity - 已根据adb命令查到填充
    'noReset': True,                  # 设置为 True，测试方法之间不会重置应用状态，保留创建的数据
    'unicodeKeyboard': True,          # 使用Unicode输入法，支持中文输入
    'resetKeyboard': True,            # 测试完成后重置输入法
    # 移除 'app' capability，重装逻辑将在 setUpClass 中手动处理
    'automationName': 'Uiautomator2' # 通常需要指定自动化后端，特别是新版本Appium
}

appium_server_url = 'http://localhost:4723' # Appium 服务地址
app_apk_path = 'D:/com.lht.mali.corporation.notepad.apk' # App APK 文件的完整路径 - **请根据您的实际APK文件路径修改**


# 在全流程测试中要创建的便签数量，旨在产生滚动条
NUM_NOTES_FOR_SCROLL_TEST = 20 # 设定创建的便签数量


# --- 常用元素定位器 (根据之前XML分析) ---
ADD_BUTTON_ID = 'com.lht.mali.corporation.notepad:id/addbutton' # 主界面 '+' 按钮ID
CREATE_TITLE_FIELD_ID = 'com.lht.mali.corporation.notepad:id/editor_title' # 创建页面 标题输入框ID
CREATE_CONTENT_FIELD_LOCATOR = "//android.widget.EditText[@hint='请输入内容']" # 创建页面 内容输入框XPath (根据hint定位)
SAVE_BUTTON_ID = 'com.lht.mali.corporation.notepad:id/button_save' # 创建/编辑页面 保存按钮ID
DETAIL_EDIT_BUTTON_ID = 'com.lht.mali.corporation.notepad:id/button_edit' # 详情页面 '编辑' 按钮ID
EDIT_CONTENT_FIELD_LOCATOR = "//android.widget.LinearLayout[@resource-id='com.lht.mali.corporation.notepad:id/note_content']//android.widget.EditText" # 编辑页面 内容输入框XPath

# 主列表页的ListView ID
LIST_VIEW_ID = 'com.lht.mali.corporation.notepad:id/note_list'
# 主列表页便签列表项的XPath片段（用于查找可长按的列表项）
# .//android.widget.TextView[@resource-id='com.lht.mali.corporation.notepad:id/note_title' and contains(@text, '{note_identifying_text}')]
# 结合起来查找包含特定标题的可长按列表项：
LIST_ITEM_BY_TITLE_XPATH = lambda title_text: f"//android.widget.ListView[@resource-id='{LIST_VIEW_ID}']//android.widget.LinearLayout[@long-clickable='true' and .//android.widget.TextView[@resource-id='com.lht.mali.corporation.notepad:id/note_title' and contains(@text, '{title_text}')]]"


class NotepadTest(unittest.TestCase):

    # setUpClass 方法在整个测试类开始前只运行一次
    @classmethod
    def setUpClass(cls):
        print("\n--- setUpClass 开始 (整个测试类运行前执行一次) ---")
        cls.driver = None # 初始化类变量 driver
        try:
            # 连接 Appium 服务器，创建 driver 实例
            # 注意：这里连接时不再依赖 desired_caps 中的 'app' 路径进行安装
            cls.driver = webdriver.Remote(appium_server_url, desired_caps)
            print("成功连接到 Appium Server，类会话已创建。")
            cls.driver.implicitly_wait(10) # 设置隐式等待

            app_package = desired_caps['appPackage']

            # 在 setUpClass 中处理重装应用的逻辑
            try:
                print(f"检查应用 {app_package} 是否已安装...")
                if cls.driver.is_app_installed(app_package):
                    print(f"应用 {app_package} 已安装，开始卸载...")
                    cls.driver.remove_app(app_package)
                    print(f"应用 {app_package} 卸载完成。")
                    time.sleep(5) # 等待卸载完成
                else:
                    print(f"应用 {app_package} 未安装。")

                print(f"开始安装应用 {app_package} 从路径: {app_apk_path}")
                cls.driver.install_app(app_apk_path)
                print(f"应用 {app_package} 安装成功。")
                time.sleep(5) # 等待安装完成

            except Exception as e:
                print(f"应用卸载或安装过程中出现错误: {e}")
                # 如果安装失败，后续测试无法进行，标记 setUpClass 失败
                cls.driver = None # 确保 driver 为 None
                raise unittest.SkipTest(f"SetUpClass 失败: 应用卸载或安装失败: {e}")

            # *** 添加：安装后立即尝试激活应用，以触发权限请求或其他初始化 ***
            try:
                print(f"尝试激活应用以触发权限请求或其他初始化: {app_package}")
                cls.driver.activate_app(app_package)
                print(f"成功激活应用: {app_package}")
                time.sleep(3) # 等待应用启动和潜在的权限弹窗出现
            except Exception as e:
                print(f"安装后立即激活应用 {app_package} 失败: {e}")
                # 注意：即使激活失败，我们仍然继续，因为手动授权步骤会提供机会
                # 但失败可能会导致后续手动授权界面不出现，如果频繁发生，需要排查原因


            # 恢复手动授权的提示和等待时间
            # 在应用安装后可能会出现权限请求
            print(f"\n--- 请在设备/模拟器上为应用 {app_package} 手动授予所有需要的权限！ ---")
            MANUAL_PERMISSION_WAIT_TIME = 20 # 秒
            print(f"将暂停 {MANUAL_PERMISSION_WAIT_TIME} 秒以便您操作。")
            time.sleep(MANUAL_PERMISSION_WAIT_TIME)
            print("--- 手动权限处理等待结束 ---")


            # 再次激活应用（在手动授权后，确保应用回到前台并处于启动 Activity）
            # 第一次激活可能只是触发了权限，这里确保应用真正进入主界面并稳定
            try:
                print(f"手动授权后，再次尝试激活应用: {app_package}")
                cls.driver.activate_app(app_package)
                print(f"手动授权后，成功激活应用: {app_package}")
                time.sleep(5) # 等待应用启动和页面加载 (如您所要求的 5 秒等待)
            except Exception as e:
                print(f"手动授权后激活应用 {app_package} 失败: {e}")
                # 如果激活失败，可能影响后续所有测试，标记为类级别失败
                cls.driver = None # 确保 driver 为 None
                raise unittest.SkipTest(f"SetUpClass 失败: 手动授权后无法激活应用: {e}") # 跳过整个类测试


        except Exception as e:
            print(f"\n连接到 Appium Server 或 setUpClass 过程中出现错误: {e}")
            cls.driver = None # 标记 driver 为 None，以便 tearDownClass 中检查
            # 使用 SkipTest 跳过整个类的测试
            raise unittest.SkipTest(f"SetUpClass 失败: 无法连接 Appium Server 或初始化会话: {e}")

        print("--- setUpClass 结束 ---")


    # tearDownClass 方法在整个测试类结束后只运行一次
    @classmethod
    def tearDownClass(cls):
        print("\n--- tearDownClass 开始 (整个测试类结束后执行一次) ---")
        try:
            # 检查 driver 是否还存活并且会话处于活动状态
            if cls.driver and cls.driver.session_id:
                print("关闭 Appium 类会话...")
                cls.driver.quit() # 关闭会话并退出driver
                print("Appium 类会话已关闭。")
            elif cls.driver:
                print("类 Driver 实例存在但会话已不存在或未成功创建。")
            else:
                print("类 Driver 实例未成功创建。")
        except Exception as e:
            print(f"关闭 Appium 类会话失败: {e}")

        print("--- tearDownClass 结束 ---")


    # setUp 方法在每个测试方法运行前执行
    # 由于 setUpClass 已经处理了安装和初始启动，并且 noReset 为 True
    # setUp 的主要作用是确保应用在前台并处于启动 Activity
    def setUp(self):
        print("\n--- setUp 开始 (每个测试方法运行前执行) ---")
        # 确保 driver 实例在 setUpClass 中成功创建
        if self.driver is None or not self.driver.session_id:
            print("Driver 会话未成功建立，跳过当前测试方法。")
            raise unittest.SkipTest("Driver 会话未成功建立") # 跳过当前测试方法

        # 在每个测试方法开始前，确保应用在前台并处于启动 Activity
        # tearDown 中可能终止了应用，所以这里需要再次激活
        try:
            app_package = desired_caps['appPackage']
            print(f"在测试方法开始前尝试激活应用: {app_package}")
            self.driver.activate_app(app_package)
            print(f"在测试方法开始前成功激活应用: {app_package}")
            time.sleep(2) # 等待页面稳定
        except Exception as e:
            print(f"在测试方法开始前激活应用失败: {e}")
            self.fail(f"SetUp 失败: 无法在测试方法开始前激活应用: {e}") # 标记当前测试失败


        print("--- setUp 结束 ---")


    # tearDown 方法在每个测试方法运行后执行
    # 在 noReset: True 的情况下，通常不需要在 tearDown 中终止应用
    # 但如果您的测试方法可能导致应用退出，或者为了确保下一个测试方法从干净状态开始
    # 可以选择在这里终止应用
    def tearDown(self):
        print("\n--- tearDown 开始 (每个测试方法运行后执行) ---")
        # 在每个测试方法结束后，将应用置于后台或终止
        try:
            # 检查 driver 是否还存活
            if self.driver and self.driver.session_id:
                app_package = desired_caps['appPackage']
                # 将应用置于后台
                # self.driver.background_app(5) # 将应用置于后台5秒
                # 或者终止应用
                self.driver.terminate_app(app_package)
                print(f"成功通过Appium终止应用 {app_package}")
            else:
                print("Driver 会话已不存在，跳过应用终止操作。")
        except Exception as e:
            print(f"在测试方法结束后终止应用失败: {e}")


        print("--- tearDown 结束 ---")


    # 全流程测试场景
    def test_full_scenario(self):
        """
        全流程测试：
        启动App，等待页面加载5秒；
        创建多个便签至列表出现滚动条（20条）；
        滑动列表至最底，点击最后一条；
        进入编辑模式，清除正文并保存；
        关闭App。
        """
        print("\n--- 执行全流程测试场景 ---")
        # driver 会话和应用激活在 setUp 中已处理

        # 确保当前在主列表页面
        try:
            # Appium 启动时指定了 appActivity，通常会直接进入该 Activity
            # 但为了稳健，可以加一个等待列表视图出现的检查
            list_view = self.driver.find_element(AppiumBy.ID, LIST_VIEW_ID)
            self.driver.implicitly_wait(10) # 确保隐式等待已设置
            list_view.is_displayed()
            print("已在主列表页面。")
            # 这里不再需要额外的 5 秒等待，因为 setUpClass 中已经包含了启动后等待
            # time.sleep(5) # 启动App，等待页面加载5秒

        except Exception as e:
            print(f"未能定位主列表视图: {e}")
            self.fail("未能定位主列表视图，无法执行全流程测试")
            return


        # --- 步骤: 创建多个便签至列表出现滚动条 ---
        print(f"\n开始创建 {NUM_NOTES_FOR_SCROLL_TEST} 个便签以填充列表...")
        last_created_note_title = None # 用于存储最后创建的便签标题，以便后续查找

        for i in range(1, NUM_NOTES_FOR_SCROLL_TEST + 1):
            print(f"开始创建第 {i} 个便签...")
            try:
                # 点击主界面“+”按钮，进入新建便签页面
                add_button = self.driver.find_element(AppiumBy.ID, ADD_BUTTON_ID)
                add_button.click()
                print(f"成功点击 '+' 按钮 (ID: {ADD_BUTTON_ID})")
                self.driver.implicitly_wait(5) # 等待页面跳转
                time.sleep(1) # 额外等待确保页面稳定

                # 定位标题文本框并输入内容
                # 使用便签序号和时间戳，确保标题唯一
                note_title = f"全流程测试便签_{i}_{time.strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"
                title_field = self.driver.find_element(AppiumBy.ID, CREATE_TITLE_FIELD_ID)
                title_field.send_keys(note_title)
                # print(f"成功输入标题: '{note_title}'")

                # 定位内容文本框并输入内容
                content_field = self.driver.find_element(AppiumBy.XPATH, CREATE_CONTENT_FIELD_LOCATOR)
                note_content = f"这是全流程测试创建的第 {i} 个便签内容。\n随机: {string.ascii_lowercase[i%26]}{random.randint(1000, 9999)}"
                content_field.send_keys(note_content)
                # print(f"成功输入内容。")

                time.sleep(1) # 输入后等待一下

                # 点击保存按钮
                save_button = self.driver.find_element(AppiumBy.ID, SAVE_BUTTON_ID)
                save_button.click()
                print(f"成功点击保存按钮 (ID: {SAVE_BUTTON_ID})")
                self.driver.implicitly_wait(10) # 等待保存响应，回到列表页
                time.sleep(2) # 额外等待页面稳定

                last_created_note_title = note_title # 记录最后创建的便签标题

                print(f"第 {i} 个便签创建完成。")

            except Exception as e:
                print(f"创建第 {i} 个便签失败: {e}")
                # 如果创建失败，尝试回到列表页并继续创建下一个
                try:
                    self.driver.back()
                    time.sleep(1)
                    self.driver.find_element(AppiumBy.ID, LIST_VIEW_ID).is_displayed() # 检查是否回到列表页
                    print("尝试返回并继续创建。")
                except Exception:
                    print("未能返回列表页，中止便签创建循环。")
                    break # 如果无法回到列表页，中止循环


        print(f"\n创建 {i-1} 个便签完成。尝试滑动列表...") # i-1 是实际成功创建的数量


        # --- 步骤: 滑动列表至最底（滑动两次），点击最后一条 ---

        print("开始滑动列表至底部（滑动两次）...")
        # 直接执行两次滑动操作
        for i in range(2):
            try:
                # 查找可滚动的元素（通常是 ListView）
                list_view_element = self.driver.find_element(AppiumBy.ID, LIST_VIEW_ID)
                scroll_params = {
                    'elementId': list_view_element.id,
                    'direction': 'down', # 向下滚动 (内容向上移动)
                    'percent': 1.0 # 滚动一页
                }
                self.driver.execute_script('mobile: scrollGesture', scroll_params)
                time.sleep(1.5) # 滑动后等待页面加载
                print(f"向下滑动 {i+1} 次完成。")

            except Exception as e:
                print(f"滑动过程中出现错误: {e}")
                # 如果滑动失败，记录错误并继续或中止，这里选择记录
                pass # 滑动失败不中断整个流程，但可能影响后续步骤

        print("滑动到底部附近完成。")
        time.sleep(2) # 等待列表稳定

        # 查找当前屏幕上所有可见的列表项，并点击最后一个
        try:
            print("查找当前屏幕上最后一个可见的便签...")
            # 查找当前可见的所有可长按的列表项
            visible_list_items = self.driver.find_elements(AppiumBy.XPATH, f"//android.widget.ListView[@resource-id='{LIST_VIEW_ID}']//android.widget.LinearLayout[@long-clickable='true']")
            if not visible_list_items:
                print("未能找到当前屏幕上任何可见的列表项。")
                self.fail("未能找到最后一个可见的便签进行点击")
                return

            last_visible_item_element = visible_list_items[-1] # 获取列表中的最后一个元素
            print("成功找到最后一个可见的便签元素，尝试点击...")
            last_visible_item_element.click()
            print("成功点击最后一个可见的便签，进入详情/查看页面...")
            self.driver.implicitly_wait(10) # 等待进入详情/查看页面加载完成
            time.sleep(2) # 额外等待页面稳定

        except Exception as e:
            print(f"查找或点击最后一个可见便签失败: {e}")
            self.fail(f"未能点击最后一个可见的便签: {e}")


        # --- 步骤: 进入编辑模式，清除正文并多次点击保存 ---

        # 在详情/查看页面，点击“编辑”按钮，进入编辑页面
        try:
            print("尝试点击详情/查看页面上的 '编辑' 按钮...")
            edit_button = self.driver.find_element(AppiumBy.ID, DETAIL_EDIT_BUTTON_ID)
            edit_button.click()
            print(f"成功点击详情/查看页面上的 '编辑' 按钮 (ID: {DETAIL_EDIT_BUTTON_ID})，进入编辑页面...")
            self.driver.implicitly_wait(10) # 等待进入编辑页面加载完成
            time.sleep(2) # 额外等待页面稳定

        except Exception as e:
            print(f"点击详情/查看页面上的 '编辑' 按钮失败 (ID: {DETAIL_EDIT_BUTTON_ID}): {e}")
            self.fail(f"无法点击详情/查看页面上的 '编辑' 按钮: {e}")


        # 定位内容文本框并清除内容
        try:
            print("进入编辑页面，尝试清除内容...")
            content_field = self.driver.find_element(AppiumBy.XPATH, EDIT_CONTENT_FIELD_LOCATOR)
            content_field.clear() # 清除文本框中的所有内容
            print(f"成功清除正文内容 (XPath: {EDIT_CONTENT_FIELD_LOCATOR})")
            time.sleep(1)

        except Exception as e:
            print(f"删除正文内容失败 (XPath: {EDIT_CONTENT_FIELD_LOCATOR}): {e}")
            self.fail(f"无法删除正文内容: {e}")

        # 多次点击保存按钮，每次点击后等待 1 秒
        num_save_clicks = 5 # 您希望点击保存按钮的次数
        print(f"\n尝试多次点击保存按钮（共 {num_save_clicks} 次，间隔 1 秒）...")
        try:
            save_button = self.driver.find_element(AppiumBy.ID, SAVE_BUTTON_ID)
            for i in range(num_save_clicks):
                save_button.click()
                print(f"第 {i+1} 次点击保存按钮 (ID: {SAVE_BUTTON_ID})")
                time.sleep(1) # 每次点击后等待 1 秒
            print(f"多次点击保存按钮完成。")
            self.driver.implicitly_wait(10) # 多次点击后，回到正常的隐式等待
            time.sleep(2) # 额外等待页面稳定

        except Exception as e:
            print(f"多次点击保存按钮失败 (ID: {SAVE_BUTTON_ID}): {e}")
            # 这里不直接 fail，因为多次点击中即使有失败，也可能达到触发提示的目的
            # 但是如果第一次点击就失败，那可能需要 fail
            # self.fail(f"多次点击保存按钮失败: {e}") # 如果需要严格要求每次点击都成功

        # TODO: 添加保存成功（或失败提示）后的验证（可选）
        print("\n保存编辑内容步骤执行完成。")

        # --- 在清空并保存后，等待 10 秒方便截图 ---
        print("\n等待 10 秒，方便截图...")
        time.sleep(10)
        print("等待结束。")

        # --- 步骤: 关闭 App ---
        # App 在 tearDown 中自动终止

        print("\n--- 全流程测试场景执行完成 ---")


# 如果直接运行此脚本文件，则运行所有的测试方法
if __name__ == '__main__':
    # 运行测试
    # 可以使用 unittest.main(verbosity=2) 来显示更详细的测试结果
    # 或者通过命令行指定要运行的测试方法：python -m unittest your_module.NotepadTest.test_full_scenario
    unittest.main()