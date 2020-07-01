# -*- coding: utf-8 -*-
# @Author  : Leo
# @File    : crack_bilibili.py


import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying

PHONE = '17621853477'
PASSWORD = 'Zxy19950921'
# 超级鹰用户名、密码、软件 ID、验证码类型
CHAOJIYING_USERNAME = 'FkashPoint'
CHAOJIYING_PASSWORD = 'Zxy19950921'
CHAOJIYING_SOFT_ID = '906105'
CHAOJIYING_KIND = '9004'


class CrackTouClick():

    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, 20)
        self.phone = PHONE
        self.password = PASSWORD
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def __del__(self):
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名和密码
        :return: None
        """
        self.browser.get(self.url)
        self.browser.fullscreen_window()
        phone = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        phone.send_keys(self.phone)
        time.sleep(2)
        password.send_keys(self.password)
        time.sleep(2)

    def get_touclick_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_no_logo.geetest_panelshowclick')))
        return element

    def get_size(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        element = self.get_touclick_element()
        time.sleep(2)
        size = element.size
        width = int(size['width'])
        height = int(size['height'])
        return (width, height)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        im = self.get_touclick_element()
        im.screenshot('screenshot.png')
        screenshot = Image.open('screenshot.png')
        return screenshot

    def get_touclick_image(self, name='captcha_resize.png'):
        """
        获取验证码图片
        :return: 图片对象
        """

        screenshot = self.get_screenshot()
        time.sleep(5)
        width, height = self.get_size()
        print('验证码大小', width, height)
        time.sleep(2)
        captcha = screenshot
        # 改变截图的大小 和原图一致
        captcha = captcha.resize((width, height))
        captcha.save(name)
        return captcha

    def get_points(self, captcha_result):
        """
        解析识别结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(), location[0],
                                                                   location[1]).click().perform()
            time.sleep(1)

    def touch_click_verify(self):
        """
        点击验证按钮
        :return: None
        """
        button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_no_logo.geetest_panelshowclick > div.geetest_panel_next > div > div > div.geetest_panel > a')))
        button.click()
        time.sleep(10)
        print('已验证')

    def login(self):
        """
        登录
        :return: None
        """
        login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-login')))
        login.click()
        time.sleep(5)
        print('请验证')

    def crack(self):
        """
        破解入口
        :return: None
        """
        self.open()
        # 点击登录
        self.login()
        # 获取验证码图片
        image = self.get_touclick_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format('PNG'))
        # 识别验证码
        result = self.chaojiying.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
        print(result)
        locations = self.get_points(result)
        self.touch_click_words(locations)
        self.touch_click_verify()
        time.sleep(5)
        # 判定是否成功
        current_url = self.browser.current_url
        if current_url != self.url:
            success = True

        # 失败后重试
        if not success:
            self.crack()
        else:
            print('验证成功')


if __name__ == '__main__':
    crack = CrackTouClick()
    crack.crack()
