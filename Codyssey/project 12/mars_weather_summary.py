import csv #csv 파일을 읽기 위한 모듈
import struct #png 파일을 직접 만들 때 사용하는 모듈
import zlib # png 압축에 사용하는 모듈

import mysql.connector #MySQL 데이터베이스 연결을 위한 라이브러리

#MySQL 접속 정보
DB_CONFIG = {
    'host': 'localhost', #현재 컴퓨터의 MySQL 서버 사용
    'user': 'root', #MySQL 관리자 계정
    'password': '!', #MySQL 비밀번호
    'database': 'mars_db', # 사용할 데이터베이스 이름
}

CSV_FILE = 'mars_weathers_data.csv' # 읽어올 CSV 파일 이름
PNG_FILE = 'mars_weather_result.png' # 저장할 PNG 파일 이름


class MySQLHelper: #MySQL 작업을 쉽게 하기 위한 클래스
    def __init__(self): #객체 생성시 자동 실행
        self.connection = mysql.connector.connect(**DB_CONFIG) #MySQL 서버 연결
        self.cursor = self.connection.cursor() #SQL 실행용 커서 생성

    def execute(self, query, values=None): # INSERT, UPDATE, DELETE 같은 쿼리 실행
        self.cursor.execute(query, values or ())
        self.connection.commit() # 변경사항 저장

    def fetch_all(self, query): #SELECT 결과를 모두 가져오기
        self.cursor.execute(query)
        return self.cursor.fetchall() #조회 결과 반환

    def close(self): # 프로그램 종료 시 연결 해제
        self.cursor.close()
        self.connection.close()


def create_table(db): #mars_weather 테이블 생성 함수
    query = '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT AUTO_INCREMENT PRIMARY KEY, #자동 증가하는 기본 키
            mars_date DATETIME NOT NULL, # 화성날짜(필수입력)
            temp FLOAT, # 온도
            storm INT # 모래폭풍 여부 
        )
    '''
    db.execute(query) # 테이블 생성 실행


def insert_csv_data(db): #csv 파일 데이터를 DB에 저장하는 함수
    with open(CSV_FILE, 'r', encoding='utf-8') as file: #csv 파일 열기
        reader = csv.DictReader(file) #csv를 딕셔너리 형태로 읽기

        for row in reader: #csv 모든 행 반복
            query = ''' #데이터 삽입 SQL 
                INSERT INTO mars_weather (mars_date, temp, storm)
                VALUES (%s, %s, %s)
            '''
            values = ( #CSV 값 가져오기
                row['mars_date'], #날짜
                float(row['temp']), #온도 (실수형 변환)
                int(row['stom']) # 모래폭풍 값(정수형 변환)
            )

            db.execute(query, values) #DB에 저장


def get_clear_weather_data(db): #모래폭풍이 없는(0) 날씨 데이터 조회
    query = '''
        SELECT mars_date, temp, storm
        FROM mars_weather
        WHERE storm = 0 # 모래폭풍이 없는 데이터만 조회 
        ORDER BY mars_date #날짜 순 정렬
    '''
    return db.fetch_all(query)


def save_png(text_lines): #png 파일 생성 함수
    width = 900 #png가로 크기
    height = 300 #세로 크기
    background = bytes([255, 255, 255]) * width #흰색 배경 생성

    raw_data = b'' #png 원본 데이터 저장 변수

    for _ in range(height): #이미지 높이만큼 반복
        raw_data += b'\x00' + background # png 형식에 맞는 데이터 추가

    def png_chunk(chunk_type, data): #png 청크 생성 함수
        chunk = chunk_type + data
        return (
            struct.pack('>I', len(data)) + #데이터 길이 저장
            chunk + # 청크데이터
            struct.pack('>I', zlib.crc32(chunk) & 0xffffffff) #오류 검사용 CRC 저장
        )

    png = b'\x89PNG\r\n\x1a\n' #png 파일 시작 시그니처
    png += png_chunk( # 이미지 정보 저장
        b'IHDR',
        struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    )
    png += png_chunk(b'IDAT', zlib.compress(raw_data)) # 이미지 데이터 압축 저장
    png += png_chunk(b'IEND', b'') #png 종료 정보 저장

    with open(PNG_FILE, 'wb') as file: #png 파일 생성
        file.write(png)

    print(f'결과 PNG 파일 저장 완료: {PNG_FILE}')


def main(): # 프로그램 시작 함수
    db = MySQLHelper() #db 연결

    create_table(db) #테이블 생성
    insert_csv_data(db) #CSV 데이터 저장

    clear_weather_data = get_clear_weather_data(db) # 맑은 날씨 데이터 조회

    print('맑은 날씨 데이터')
    for mars_date, temp, storm in clear_weather_data: # 주말 결과 출력
        print(f'{mars_date} / 온도: {temp} / 모래폭풍: {storm}')

    save_png(clear_weather_data) #png 생성

    db.close() #DB 연결 종류


if __name__ == '__main__': #현재 파일을 직접 실행한 경우 main 함수 실행 
    main()