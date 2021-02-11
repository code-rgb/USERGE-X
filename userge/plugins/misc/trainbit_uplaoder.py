import asyncio
import os
from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from userge import Config, Message, userge
from pudb import set_trace

login_url = "https://trainbit.com/Membership/login.aspx"


def login_trainbit(driver):
    username = os.getenv('TBUSER')
    password = os.getenv('TBPASSWORD')
    if not username:
        return False
    form = driver.find_element_by_id('login-form')
    await asyncio.sleep(1)
    form.find_element_by_id('ctl00_ContentPlaceHolder1_t_email').send_keys(username)
    form.find_element_by_id('ctl00_ContentPlaceHolder1_t_password').send_keys(password)
    btn = form.find_element_by_id('ctl00_ContentPlaceHolder1_b_login').click()


@userge.on_cmd(
    "tb",
    about={
        "header": "آپلود فایل به ترین بیت",
        "flags": {
        },
        "usage": "{tr}bt [flags] [text | reply to msg]",
        "examples": [
        ],
    },
    del_pre=True,
)
async def up_to_trainbit(message: Message):
    r = message.reply_to_message
    if Config.GOOGLE_CHROME_BIN is None:
            await message.err("You need to install google chrome")
            return
    else:
        try:
            input_str = message.filtered_input_str
            if r and (
                r.document or r.audio or r.video or r.animation or r.voice or r.photo):
                message_id = r.message_id
                await message.edit("`Downloading The File...`")
                path_ = await message.client.download_media(
                    r, file_name=Config.DOWN_PATH
                )
            else:
                await message.err("need reply on a media!")
                return
            await message.edit("`Upload To Trainbit...`")
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = Config.GOOGLE_CHROME_BIN
            chrome_options.add_argument("--headless")
            # chrome_options.add_argument("--window-size=1920x1080")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            prefs = {"download.default_directory": Config.DOWN_PATH}
            chrome_options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(login_url)
            login_trainbit(driver)
            await asyncio.sleep(1)
            driver.find_element_by_id('f_upload').send_keys(path_)
            get_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="manual-upload-queue"]/li/div/p[2]/a')))
            get_link.click()
            await asyncio.sleep(1)
            await message.edit("`Uploaded Successfully`")
            text_area = get_link.find_element_by_xpath('//*[@id="t_sharelinks"]')
            dl_link = text_area.get_attribute('value')
            await message.edit(f"Download link: {dl_link}")
            os.remove(path_)
            return driver.quit()
        except Exception as e:
            await message.err(e)
