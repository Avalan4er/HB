import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union

from PIL import Image

from config import Configuration
from logger import logger


def save_match_result(screenshot: Image) -> Union[None, str]:
    results_storage = 'results'
    if not os.path.exists(results_storage):
        os.makedirs(results_storage)

    file_name = Configuration.HERO_TO_LEVEL + '_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    file_path = os.path.join(results_storage, file_name)

    logger.debug('Сохраняем результаты матча: ' + file_path)
    try:
        screenshot.save(file_path)
    except OSError as error:
        logger.debug('Ошибка сохранения результатов матча: ' + error.__str__())
        return None
    except:
        logger.debug('Неизвестная ошибка сохранения результатов матча')
        return None

    return file_path


def send_match_result(screenshot_path: str):
    sender = Configuration.EMAIL
    recipient = Configuration.EMAIL

    # Create message container.
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Уведомление от бота HOTS'
    msgRoot['From'] = sender
    msgRoot['To'] = recipient

    # Create the body of the message.
    html = """\
        <p>This is an inline image<br/>
            <img src="cid:image1">
        </p>
    """

    # Record the MIME types.
    msgHtml = MIMEText(html, 'html')

    logger.debug('Отправляем Email уведомление с результатами матча')
    try:
        img = open(screenshot_path, 'rb').read()
        msgImg = MIMEImage(img, 'png')
        msgImg.add_header('Content-ID', '<image1>')
        msgImg.add_header('Content-Disposition', 'inline', filename=os.path.basename(screenshot_path))

        msgRoot.attach(msgHtml)
        msgRoot.attach(msgImg)

        # Send the message via local SMTP server.
        s = smtplib.SMTP(Configuration.SMTP_SERVER_ADDRESS, Configuration.SMTP_SERVER_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(Configuration.SMTP_LOGIN, Configuration.SMTP_PASSWORD)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        # s.sendmail(options.sender, options.recipient, msgRoot.as_string())
        s.sendmail(sender, recipient, msgRoot.as_string())
        s.quit()
        logger.debug('Email отправлен')

    except (AttributeError, OSError) as error:
        logger.error('Ошибка отправки Email: ' + error.__str__())
    except:
        logger.error('Неизвестная ошибка отправки Email')
