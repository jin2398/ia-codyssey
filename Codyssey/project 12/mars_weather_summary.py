# CSV 파일을 읽기 위한 기본 모듈
import csv

# PNG 파일을 직접 만들 때 필요한 기본 모듈
import struct

# PNG 이미지 데이터를 압축할 때 사용하는 기본 모듈
import zlib

# MySQL과 Python을 연결하기 위한 외부 라이브러리
import mysql.connector


# MySQL 접속 정보
DB_CONFIG = {
    'host': 'localhost',      # 내 컴퓨터에 설치된 MySQL 서버
    'user': 'root',           # MySQL 사용자 이름
    'password': '!',  # MySQL 비밀번호
    'database': 'mars_db',    # 사용할 데이터베이스 이름
}

# 읽어올 CSV 파일 이름
CSV_FILE = 'mars_weathers_data.csv'

# 저장할 PNG 파일 이름
PNG_FILE = 'mars_weather_result.png'


# MySQL 연결과 쿼리 실행을 쉽게 하기 위한 클래스
class MySQLHelper:

    # MySQLHelper 객체가 만들어질 때 자동으로 실행되는 함수
    def __init__(self):
        # DB_CONFIG 정보를 이용해서 MySQL에 연결한다.
        self.connection = mysql.connector.connect(**DB_CONFIG)

        # SQL 문장을 실행하기 위한 cursor를 만든다.
        self.cursor = self.connection.cursor()

    # INSERT, CREATE 같은 SQL을 실행하는 함수
    def execute(self, query, values=None):
        # SQL 문장을 실행한다.
        self.cursor.execute(query, values or ())

        # 실행한 내용을 데이터베이스에 저장한다.
        self.connection.commit()

    # SELECT 결과를 가져오는 함수
    def fetch_all(self, query):
        # SELECT 쿼리를 실행한다.
        self.cursor.execute(query)

        # 조회된 모든 결과를 반환한다.
        return self.cursor.fetchall()

    # MySQL 연결을 종료하는 함수
    def close(self):
        # cursor를 닫는다.
        self.cursor.close()

        # MySQL 연결을 닫는다.
        self.connection.close()


# mars_weather 테이블을 생성하는 함수
def create_table(db):
    # 테이블이 없을 경우에만 새로 생성한다.
    query = '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT AUTO_INCREMENT PRIMARY KEY,
            mars_date DATETIME NOT NULL,
            temp FLOAT,
            storm INT
        )
    '''

    # 위 SQL 문장을 실행한다.
    db.execute(query)


# CSV 파일을 읽어서 MySQL 테이블에 저장하는 함수
def insert_csv_data(db):
    # CSV 파일을 읽기 모드로 연다.
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        # CSV 파일을 딕셔너리 형태로 읽는다.
        reader = csv.DictReader(file)

        # CSV 파일의 각 줄을 하나씩 반복한다.
        for row in reader:
            # mars_weather 테이블에 데이터를 넣는 INSERT SQL
            query = '''
                INSERT INTO mars_weather (mars_date, temp, storm)
                VALUES (%s, %s, %s)
            '''

            # CSV에서 읽은 값을 INSERT에 넣을 값으로 준비한다.
            values = (
                row['mars_date'],      # 화성 날짜
                float(row['temp']),    # 온도 값은 소수일 수 있어서 float로 변환
                int(row['stom'])       # CSV 컬럼명이 stom이라서 stom 사용
            )

            # INSERT 쿼리를 실행해서 DB에 저장한다.
            db.execute(query, values)


# MySQL에 저장된 전체 날씨 데이터를 조회하는 함수
def get_weather_data(db):
    # mars_weather 테이블의 데이터를 날짜순으로 조회한다.
    query = '''
        SELECT mars_date, temp, storm
        FROM mars_weather
        ORDER BY mars_date
    '''

    # 조회 결과를 반환한다.
    return db.fetch_all(query)


# 결과 PNG 파일을 생성하는 함수
def save_png(weather_data):
    # PNG 이미지의 가로 크기
    width = 900

    # PNG 이미지의 세로 크기
    height = 300

    # 흰색 배경을 만든다.
    background = bytes([255, 255, 255]) * width

    # PNG 이미지 데이터가 저장될 변수
    raw_data = b''

    # 이미지 높이만큼 반복하면서 흰색 배경 데이터를 쌓는다.
    for _ in range(height):
        raw_data += b'\x00' + background

    # PNG 파일 안에 들어가는 chunk를 만드는 내부 함수
    def png_chunk(chunk_type, data):
        # chunk 종류와 데이터를 합친다.
        chunk = chunk_type + data

        # PNG 형식에 맞게 길이, 데이터, CRC 값을 묶어서 반환한다.
        return (
            struct.pack('>I', len(data))
            + chunk
            + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        )

    # PNG 파일의 시작을 알리는 고정 값
    png = b'\x89PNG\r\n\x1a\n'

    # PNG 이미지의 기본 정보 chunk를 추가한다.
    png += png_chunk(
        b'IHDR',
        struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    )

    # 이미지 데이터를 압축해서 PNG에 추가한다.
    png += png_chunk(b'IDAT', zlib.compress(raw_data))

    # PNG 파일의 끝을 알리는 chunk를 추가한다.
    png += png_chunk(b'IEND', b'')

    # PNG 파일을 바이너리 쓰기 모드로 생성한다.
    with open(PNG_FILE, 'wb') as file:
        # 완성된 PNG 데이터를 파일에 저장한다.
        file.write(png)

    # PNG 저장 완료 메시지를 출력한다.
    print(f'결과 PNG 파일 저장 완료: {PNG_FILE}')


# 프로그램의 전체 실행 흐름을 담당하는 함수
def main():
    # MySQL에 연결한다.
    db = MySQLHelper()

    # mars_weather 테이블을 생성한다.
    create_table(db)

    # CSV 데이터를 읽어서 MySQL에 저장한다.
    insert_csv_data(db)

    # MySQL에 저장된 전체 날씨 데이터를 조회한다.
    weather_data = get_weather_data(db)

    # 결과 제목을 출력한다.
    print('화성 날씨 데이터')

    # 조회된 날씨 데이터를 한 줄씩 출력한다.
    for mars_date, temp, storm in weather_data:
        print(f'{mars_date} / 온도: {temp} / 모래폭풍: {storm}')

    # 결과 PNG 파일을 생성한다.
    save_png(weather_data)

    # MySQL 연결을 종료한다.
    db.close()


# 이 파일을 직접 실행했을 때만 main 함수를 실행한다.
if __name__ == '__main__':
    main()