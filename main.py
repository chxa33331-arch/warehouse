#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨云自动签到工具
基于 Selenium + ddddocr
"""

import os
import sys
import time
import base64
import requests
import ddddocr
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class RainyunSignin:
    """雨云自动签到类"""
    
    # 雨云相关URL
    BASE_URL = "https://app.rainyun.com"
    LOGIN_URL = f"{BASE_URL}/account/signin"
    SIGNIN_URL = f"{BASE_URL}/account/reward/bindwxtips"
    USER_CENTER_URL = f"{BASE_URL}/account/overview"
    
    def __init__(self, username: str, password: str, headless: bool = True):
        """
        初始化
        :param username: 用户名/邮箱/手机号
        :param password: 密码
        :param headless: 是否无头模式
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        
    def _init_driver(self):
        """初始化Chrome驱动"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
            
        # 常用配置
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # 设置User-Agent
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 使用webdriver_manager自动管理chromedriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 防止被检测
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        self.driver.implicitly_wait(10)
        print("✅ 浏览器驱动初始化成功")
        
    def _recognize_captcha(self, captcha_element) -> str:
        """
        识别验证码
        :param captcha_element: 验证码图片元素
        :return: 识别结果
        """
        try:
            # 方法1: 通过截图获取验证码
            captcha_png = captcha_element.screenshot_as_png
            result = self.ocr.classification(captcha_png)
            print(f"🔍 验证码识别结果: {result}")
            return result
        except Exception as e:
            print(f"❌ 验证码识别失败: {e}")
            return ""
    
    def _recognize_captcha_from_src(self, img_src: str) -> str:
        """
        从图片src识别验证码
        :param img_src: 图片地址或base64
        :return: 识别结果
        """
        try:
            if img_src.startswith("data:image"):
                # Base64编码的图片
                img_data = base64.b64decode(img_src.split(",")[1])
            else:
                # URL图片
                response = requests.get(img_src, timeout=10)
                img_data = response.content
                
            result = self.ocr.classification(img_data)
            print(f"🔍 验证码识别结果: {result}")
            return result
        except Exception as e:
            print(f"❌ 验证码识别失败: {e}")
            return ""
            
    def login(self) -> bool:
        """
        登录雨云
        :return: 是否登录成功
        """
        try:
            print("🚀 开始登录雨云...")
            self.driver.get(self.LOGIN_URL)
            time.sleep(3)
            
            # 等待登录表单加载
            wait = WebDriverWait(self.driver, 15)
            
            # 输入用户名 - 根据实际页面调整选择器
            username_selectors = [
                "//input[@placeholder='邮箱/用户名/手机号']",
                "//input[@name='username']",
                "//input[@type='text']",
                "//input[contains(@class, 'username')]"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if username_input:
                        break
                except:
                    continue
                    
            if not username_input:
                print("❌ 找不到用户名输入框")
                return False
                
            username_input.clear()
            username_input.send_keys(self.username)
            print("✅ 已输入用户名")
            time.sleep(0.5)
            
            # 输入密码
            password_selectors = [
                "//input[@placeholder='密码']",
                "//input[@name='password']",
                "//input[@type='password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.XPATH, selector)
                    if password_input:
                        break
                except:
                    continue
                    
            if not password_input:
                print("❌ 找不到密码输入框")
                return False
                
            password_input.clear()
            password_input.send_keys(self.password)
            print("✅ 已输入密码")
            time.sleep(0.5)
            
            # 处理验证码（如果存在）
            self._handle_captcha()
            
            # 点击登录按钮
            login_btn_selectors = [
                "//button[contains(text(), '登录')]",
                "//button[contains(text(), '登 录')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(@class, 'login')]"
            ]
            
            login_btn = None
            for selector in login_btn_selectors:
                try:
                    login_btn = self.driver.find_element(By.XPATH, selector)
                    if login_btn:
                        break
                except:
                    continue
                    
            if login_btn:
                login_btn.click()
                print("✅ 已点击登录按钮")
            else:
                print("❌ 找不到登录按钮")
                return False
                
            time.sleep(3)
            
            # 验证登录是否成功
            if self._check_login_status():
                print("✅ 登录成功！")
                return True
            else:
                print("❌ 登录失败，请检查账号密码")
                return False
                
        except Exception as e:
            print(f"❌ 登录过程出错: {e}")
            self._save_screenshot("login_error")
            return False
            
    def _handle_captcha(self, max_retry: int = 3):
        """
        处理验证码
        :param max_retry: 最大重试次数
        """
        for i in range(max_retry):
            try:
                # 查找验证码图片
                captcha_selectors = [
                    "//img[contains(@class, 'captcha')]",
                    "//img[contains(@src, 'captcha')]",
                    "//img[contains(@alt, '验证码')]",
                    "//img[contains(@id, 'captcha')]"
                ]
                
                captcha_img = None
                for selector in captcha_selectors:
                    try:
                        captcha_img = self.driver.find_element(By.XPATH, selector)
                        if captcha_img:
                            break
                    except:
                        continue
                        
                if not captcha_img:
                    print("ℹ️ 未发现验证码")
                    return
                    
                # 识别验证码
                captcha_code = self._recognize_captcha(captcha_img)
                
                if not captcha_code:
                    # 点击刷新验证码
                    captcha_img.click()
                    time.sleep(1)
                    continue
                    
                # 输入验证码
                captcha_input_selectors = [
                    "//input[@placeholder='验证码']",
                    "//input[contains(@name, 'captcha')]",
                    "//input[contains(@id, 'captcha')]"
                ]
                
                captcha_input = None
                for selector in captcha_input_selectors:
                    try:
                        captcha_input = self.driver.find_element(By.XPATH, selector)
                        if captcha_input:
                            break
                    except:
                        continue
                        
                if captcha_input:
                    captcha_input.clear()
                    captcha_input.send_keys(captcha_code)
                    print(f"✅ 已输入验证码: {captcha_code}")
                    return
                    
            except Exception as e:
                print(f"⚠️ 处理验证码失败 (尝试 {i+1}/{max_retry}): {e}")
                time.sleep(1)
                
    def _check_login_status(self) -> bool:
        """检查是否登录成功"""
        try:
            # 检查URL是否跳转
            time.sleep(2)
            current_url = self.driver.current_url
            
            # 如果还在登录页，说明登录失败
            if "signin" in current_url or "login" in current_url:
                return False
                
            # 检查是否有用户相关元素
            user_indicators = [
                "//div[contains(@class, 'user')]",
                "//span[contains(@class, 'username')]",
                "//a[contains(@href, 'logout')]",
                "//div[contains(text(), '账户')]"
            ]
            
            for selector in user_indicators:
                try:
                    if self.driver.find_element(By.XPATH, selector):
                        return True
                except:
                    continue
                    
            # 如果URL变化了，通常表示登录成功
            return "signin" not in current_url
            
        except Exception as e:
            print(f"⚠️ 检查登录状态失败: {e}")
            return False
            
    def signin(self) -> bool:
        """
        执行签到
        :return: 是否签到成功
        """
        try:
            print("🚀 开始执行签到...")
            
            # 访问用户中心或签到页面
            self.driver.get(self.USER_CENTER_URL)
            time.sleep(3)
            
            # 查找签到按钮
            signin_btn_selectors = [
                "//button[contains(text(), '签到')]",
                "//a[contains(text(), '签到')]",
                "//div[contains(text(), '签到')]",
                "//span[contains(text(), '签到')]",
                "//button[contains(@class, 'sign')]",
                "//div[contains(@class, 'sign')]"
            ]
            
            signin_btn = None
            for selector in signin_btn_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            text = elem.text
                            if "已签到" in text or "已签" in text:
                                print("ℹ️ 今日已经签到过了")
                                return True
                            signin_btn = elem
                            break
                    if signin_btn:
                        break
                except:
                    continue
                    
            if not signin_btn:
                # 尝试通过API接口签到
                return self._signin_via_api()
                
            # 点击签到按钮
            signin_btn.click()
            print("✅ 已点击签到按钮")
            time.sleep(2)
            
            # 处理签到可能出现的验证码
            self._handle_captcha()
            time.sleep(2)
            
            # 检查签到结果
            if self._check_signin_result():
                print("🎉 签到成功！")
                return True
            else:
                print("⚠️ 签到结果未知")
                return False
                
        except Exception as e:
            print(f"❌ 签到过程出错: {e}")
            self._save_screenshot("signin_error")
            return False
            
    def _signin_via_api(self) -> bool:
        """通过API接口签到"""
        try:
            print("🔄 尝试通过API接口签到...")
            
            # 获取cookies
            cookies = {cookie['name']: cookie['value'] 
                      for cookie in self.driver.get_cookies()}
            
            # 雨云签到API（需要根据实际情况调整）
            api_urls = [
                f"{self.BASE_URL}/api/user/sign",
                f"{self.BASE_URL}/api/user/reward/sign",
                f"{self.BASE_URL}/api/account/sign"
            ]
            
            headers = {
                "User-Agent": self.driver.execute_script("return navigator.userAgent"),
                "Referer": self.USER_CENTER_URL,
                "Content-Type": "application/json"
            }
            
            for api_url in api_urls:
                try:
                    response = requests.post(
                        api_url, 
                        cookies=cookies, 
                        headers=headers,
                        timeout=10
                    )
                    if response.status_code == 200:
                        result = response.json()
                        print(f"📡 API响应: {result}")
                        if result.get("code") == 0 or result.get("success"):
                            print("🎉 API签到成功！")
                            return True
                except Exception as e:
                    continue
                    
            return False
            
        except Exception as e:
            print(f"❌ API签到失败: {e}")
            return False
            
    def _check_signin_result(self) -> bool:
        """检查签到结果"""
        try:
            # 检查页面是否有成功提示
            success_indicators = [
                "//*[contains(text(), '签到成功')]",
                "//*[contains(text(), '获得')]",
                "//*[contains(text(), '积分')]",
                "//*[contains(@class, 'success')]"
            ]
            
            for selector in success_indicators:
                try:
                    if self.driver.find_element(By.XPATH, selector):
                        return True
                except:
                    continue
                    
            # 检查是否显示已签到
            try:
                page_source = self.driver.page_source
                if "已签到" in page_source or "签到成功" in page_source:
                    return True
            except:
                pass
                
            return False
            
        except Exception as e:
            print(f"⚠️ 检查签到结果失败: {e}")
            return False
            
    def _save_screenshot(self, name: str):
        """保存截图用于调试"""
        try:
            filename = f"{name}_{int(time.time())}.png"
            self.driver.save_screenshot(filename)
            print(f"📸 已保存截图: {filename}")
        except Exception as e:
            print(f"⚠️ 保存截图失败: {e}")
            
    def run(self) -> bool:
        """
        运行签到流程
        :return: 是否成功
        """
        try:
            self._init_driver()
            
            if not self.login():
                return False
                
            if not self.signin():
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ 运行出错: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                print("✅ 浏览器已关闭")
                

def main():
    """主函数"""
    # 从环境变量获取账号信息
    username = os.environ.get("RAINYUN_USERNAME", "")
    password = os.environ.get("RAINYUN_PASSWORD", "")
    
    if not username or not password:
        print("❌ 请设置环境变量 RAINYUN_USERNAME 和 RAINYUN_PASSWORD")
        sys.exit(1)
        
    print("=" * 50)
    print("🌧️ 雨云自动签到工具")
    print("=" * 50)
    print(f"📧 账号: {username[:3]}***{username[-3:] if len(username) > 6 else '***'}")
    print(f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    signin = RainyunSignin(username, password, headless=True)
    success = signin.run()
    
    print("=" * 50)
    if success:
        print("✅ 签到任务完成！")
        sys.exit(0)
    else:
        print("❌ 签到任务失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()