from selenium import webdriver
import webdriver_manager.chrome
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from secrets import phone_num
import pytesseract
from PIL import Image
import pyscreenshot as ImageGrab
from pynput.keyboard import Key, Controller
# pip3 install webdriver-manager  <-- Use this if your chromedriver is out of date

# Global variable to control our keyboard
keyboard = Controller()


# Method to screen shot the 6-digit SMS code Tinder sends to verify the user
# Sorry if this function is misplaced I'm not sure where it's supposed to go
def screen_shot():
    # Desktop coordinate of the iMessage you receive from Tinder
    image = ImageGrab.grab(bbox=(1123, 70, 1280, 90))
    image.save('code4.png')
    # Using our OCR, record the 6-digit auth code sent to you
    im = Image.open('code4.png')
    text = pytesseract.image_to_string(im, lang="eng")
    write_file = open("output1.txt", "w")
    write_file.write(text)
    write_file.close()

    # Extracting the code from the screen shot, used later when signing into Tinder via phone
    screen = open("output1.txt", "r")
    output = screen.readline()
    output2 = output.split()
    code = output2[4]
    return code


class TinderBot:
    right = 0

    # Create the browser we will use
    def __init__(self):
        self.driver = webdriver.Chrome(webdriver_manager.chrome.ChromeDriverManager().install())

    def log_on(self):
        # Log onto Tinder
        self.driver.get('https://tinder.com')

        # Wait for the login screen to popup
        sleep(5)

        # Close Cookies popup on web page
        close_stalker = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div/div/div[1]/button')
        close_stalker.click()

        # Tinder changes the welcome page so that the phone log in option is in a different path (1, 2, 3) each time
        # First try to log in by phone in first path:
        try:
            log_in_by_text = self.driver.find_element_by_xpath(
                '//*[@id="modal-manager"]/div/div/div/div/div[3]/span/div[1]/button'
            )
            log_in_by_text.click()
            # If the first path doesn't work, that means the phone log in is either in the second or third path
        except NoSuchElementException:
            # Try the second path, if it works, the number of windows that appear is still 1 (Window to enter phone #)
            log_in_by_text = self.driver.find_element_by_xpath(
                '//*[@id="modal-manager"]/div/div/div/div/div[3]/span/div[2]/button'
            )
            log_in_by_text.click()
            sleep(3)

            # If first path isn't the phone number and the second path isn't the phone number,
            # we know the second path is the Facebook login, which pops up a second window.
            # To deal with this second window, command+w out of it and select the third option
            if len(self.driver.window_handles) >= 2:  # important in order to reload page b/c you get error page after exiting Facebook popup
                # switch the Facebook window
                self.driver.switch_to.window(self.driver.window_handles[1])

                # close the window through command w
                keyboard.press(Key.cmd)
                keyboard.press('w')
                keyboard.release('w')
                keyboard.release(Key.cmd)
                sleep(2)
                # After you close window, you need to refresh page
                # because you are given new UI
                keyboard.press(Key.cmd)
                keyboard.press('r')
                keyboard.release('r')
                keyboard.release(Key.cmd)

                sleep(5)
                # Important: We need to command tab a new window in order to keep the if condition true
                keyboard.press(Key.cmd)
                keyboard.press('t')
                keyboard.release('t')
                keyboard.release(Key.cmd)
                # switch back to tinder (aka command+1)
                self.driver.switch_to.window(self.driver.window_handles[0])

                # Select the third option which should be the phone login screen
                log_in_by_text = self.driver.find_element_by_xpath(
                    '//*[@id="modal-manager"]/div/div/div/div/div[3]/span/div[3]/button'
                )
                log_in_by_text.click()

        sleep(1)
        # Now, we have the phone number screen up and we can enter our phone number
        self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[1]/div[2]/div/input').send_keys(phone_num)
        # Click log in
        login = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[1]/button')
        login.click()
        # My computer takes 6 seconds for the Tinder message notification to pop up in the top right screen
        sleep(6)
        # This line calls the screen_shot() method above, which takes a screen shot of the top right corner of the screen
        # With tesseract-OCR and returns the code that Tinder sends you. It then enters that code into the login popup
        self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[1]/div[3]/input[1]').send_keys(screen_shot())
        sleep(1)
        # Press the continue login button after entering the Tinder 6-digit code
        enter = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[1]/button')
        enter.click()

        """When you log in, a bunch of stuff pops up, such as location enabling, premium member upgrades, etc."""
        sleep(5)
        # Allow location tracking
        allow = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')
        allow.click()

        sleep(3)
        # Not interested in being a premium member
        not_interested = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/button[2]')
        not_interested.click()

    # Method to swipe right on a person, by simply pressing the 'right' arrow key
    def like(self):
        keyboard.press(Key.right)
        keyboard.release(Key.right)

    # Finite State machine to auto-swipe
    def auto_swipe(self):
        while True:
            sleep(0.5)
            # First, we test the end condition, which is when we run out of likes
            try:
                self.out_of_likes()
                break
            # If that doesn't work
            except NoSuchElementException:
                try:
                    # We can try closing any pop-up windows that may appear
                    self.close_popup()
                # If there are no pop-up windows
                except NoSuchElementException:
                    try:
                        # Try closing any match windows
                        self.close_match()
                    # If there aren't any match windows, then we know we are on our default person profile
                    # and can continue swiping right
                    except NoSuchElementException:
                        self.like()

    # If I get a match, Message match a compliment and close popup.
    def close_match(self):
        self.driver.find_element_by_xpath('//*[@id="chat-text-area"]').send_keys(
            "Hi! I'm not really looking for a relationship but I just wanted to let you know that you are gorgeous and amazing! Stay awesome!")
        send_message = self.driver.find_element_by_xpath('//*[@id="modal-manager-canvas"]/div/div/div[1]/div/div[3]/div[3]/form/button')
        send_message.click()

    # Close popup that says "Add Tinder to your home screen"
    def close_popup(self):
        close_pop = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[2]/button[2]')
        close_pop.click()

    # If I am out of likes, a window will pop up. Simply close that window and go to message the matches
    def out_of_likes(self):
        close = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[3]/button[2]')
        close.click()
        self.message()

    # After I run out of swipes (100 total), I can start messaging those matches who replied to the initial compliment
    def message(self):
        # Go to the messages tab
        message_tab = self.driver.find_element_by_xpath('//*[@id="messages-tab"]')
        message_tab.click()
        # The messages are organized in a 'group', in which I can access each element
        matches = self.driver.find_elements_by_class_name('messageListItem')
        # For every message in the group
        for i in range(0, len(matches) - 1):
            # I need to first see if they replied to me, otherwise I am just spamming them
            # The get_attribute function gets the entire innerHTML code of a match. I found out
            # that if the innerHTML does not have "svg" in it, the other person messaged me back
            current = matches[i].get_attribute('innerHTML')
            # If the current match I am on messaged me back
            if not 'svg' in current:
                # Select that person and initiate conversation
                matches[i].click()
                # self.actually_message()
                break

    # def actually_message(self): I will write this later when I decide how to initiate conversation


# Calling the functions to run the bot
bot = TinderBot()
bot.log_on()
bot.auto_swipe()

