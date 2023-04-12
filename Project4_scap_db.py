import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


# 임시 함수 모음
#def get_href(element): # 셀레니움으로 상품의 주소를 획득
#    return element.get_attribute('href')

def get_per(element):
    per = re.sub(r"[^0-9]", "", element.text)
    return int(per)

def get_amount(element):
    amount = re.sub(r"[^0-9]", "", element.text)
    return int(amount)

def get_SN_data(element):
    product_id = element.get_attribute('data-ec-id')
    product_name = element.get_attribute('data-ec-name')
    product_category = element.get_attribute('data-ec-category')
    product_type = element.get_attribute('data-ec-contenttype') # 프리 오더는 이미 유통된 상품도 포함 될 수 있다.
    return product_id, product_name, product_category, product_type


# 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless') # 화면 출력 없이 작업
options.add_argument("no-sandbox")
options.add_argument('--ignore-certificate-errors') # 인증서 관련 에러 무시
options.add_argument("--ignore-ssl-errors")
options.add_argument('window-size=1920x1080') # 브라우저 윈도우 사이즈
options.add_argument("disable-gpu") # 가속 사용 x

# 로드
driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options) # 드라이버 위치 경로

driver.get('https://www.wadiz.kr/web/wreward/main?endYn=Y&order=recent')

for c in range(150): # 정해진 횟수 만큼 Page down을 누른다.
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    time.sleep(0.3)

production_elements = driver.find_elements(By.CLASS_NAME, 'PreorderMainCard_item__2FrO0')
funding_percentage = driver.find_elements(By.CLASS_NAME, 'PreorderMainCard_participants__JDp58') # 펀딩 퍼센트
funding_amount = driver.find_elements(By.CLASS_NAME, 'PreorderMainCard_amount__3UOXm') # 펀딩 금액


#href = list(map(get_href, production_elements)) # href 들을 리스트에 저장
percentage = list(map(get_per, funding_percentage))
amount = list(map(get_amount, funding_amount))
sn_data = list(map(get_SN_data, production_elements))


driver.quit() # driver 종료



import os
import sqlite3
import psycopg2



#DATABASE_PATH = os.path.join(os.getcwd(), 'wadiz_data.db')

#conn = sqlite3.connect(DATABASE_PATH)

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="1q2w3e4r")


def init_db(conn):
    create_table = """CREATE TABLE wadiz (
                        id INTEGER,
                        name TEXT,
                        category VARCHAR(128),
                        type VARCHAR(128),
                        percentage INTEGER,
                        amount INTEGER,
                        goal VARCHAR(32),
                        PRIMARY KEY (id)
                        );"""

    drop_table_if_exists = "DROP TABLE IF EXISTS wadiz;"

    cur = conn.cursor()

    cur.execute(drop_table_if_exists)
    cur.execute(create_table)
    cur.close()

def store_by_page_num(conn):
    init_db(conn)

    cur = conn.cursor()
    
    for i in range(len(percentage)):
        goal = '성공' if percentage[i] >= 100 else '실패'
        cur.execute("INSERT INTO wadiz VALUES (%s,%s,%s,%s,%s,%s,%s)",(sn_data[i][0], sn_data[i][1], sn_data[i][2], sn_data[i][3], percentage[i], amount[i], goal))
        #postgresql인 경우 ?이 아닌 %s로 입력
    cur.close()
    
store_by_page_num(conn)

conn.commit()

conn.close()

#docker metabase 호스트 host.docker.internal

