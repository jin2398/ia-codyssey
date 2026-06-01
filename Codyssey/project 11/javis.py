import csv
import speech_recognition as sr
import datetime #날짜와 시간 다루기
import os #운영체제
import wave #음성파일저장
import sounddevice as sd #마이크녹음기능(외부라이브러리)


class VoiceRecorder: # 녹음이 객체를 만드는 설계(클래스 이름 대문자)
    def __init__(self): #객체 생성시 자동 실행되는 함수
        self.records_dir = 'records' #저장폴더 이름 지정
        self.sample_rate = 44100 # 녹음 품질 설정(44100=일반적인 음질)
        self.channels = 1 #채널 수 1이면 모노, 2면 스테레오

        self.create_records_directory() #객체 생성하자마자 records 폴더 자동 생성

    def create_records_directory(self): #함수 정의
        if not os.path.exists(self.records_dir): # records 폴더가 존재하지 않으면
            os.makedirs(self.records_dir) #records 폴더 새성

    def generate_file_name(self): # 녹음 파일 이름 만드는 함수
        current_time = datetime.datetime.now() #현재 시간 가져오기

        return current_time.strftime('%Y%m%d-%H%M%S.wav') #시간 형식 변환

    def record_voice(self, duration): #duration=녹음 시간(초)
        file_name = self.generate_file_name() #파일 이름 생성

        file_path = os.path.join(self.records_dir, file_name) # 경로 합치기 ex: records/20260525-211530.wav

        print('녹음을 시작합니다.') #화면 출력

        recording = sd.rec( #실제 녹음 시작
            int(duration * self.sample_rate), # 총 녹음 데이터 개수 계산  ex: 5초 * 44100
            samplerate=self.sample_rate, #녹음 품질 설정
            channels=self.channels, # 모노/스테레오 설정
            dtype='int16' #소리 데이터 저장 형식
        )

        sd.wait() # 녹음 끝날 때 까지 기다림 -> 없으면 녹음 도중 프로그램 끝날 수 있음

        print('녹음이 완료되었습니다.') #화면 출력

        self.save_wave_file(file_path, recording) # 녹음 데이터를 wav 파일로 저장

        print(f'저장 위치: {file_path}') #화면 출력

    def save_wave_file(self, file_path, recording): #음성 파일 저장 함수
        with wave.open(file_path, 'wb') as wave_file: # wav 파일 열기
            wave_file.setnchannels(self.channels) #채널 설정
            wave_file.setsampwidth(2) #음성 데이터 크기 설정 2바이트 = int16
            wave_file.setframerate(self.sample_rate) #녹음 품질 설정
            wave_file.writeframes(recording.tobytes()) # 실제 음성 데이터 저장

    def show_files_by_date(self, start_date, end_date): #특정 날짜 범위 조회 함수
        file_list = os.listdir(self.records_dir) # records 폴더 안 파일 목록 가져오기

        matched_files = [] #조건 맞는 파일 저장할 리스트

        start = datetime.datetime.strptime(start_date, '%Y%m%d') # 문자열 날짜를 날짜 객체로 변환
        end = datetime.datetime.strptime(end_date, '%Y%m%d') # 문자열 날짜를 날짜 객체로 변환

        for file_name in file_list: #파일 하나씩 검사
            if file_name.endswith('.wav'): #wav 파일인지 확인
                file_date = file_name.split('-')[0] # 파일명 날짜 부분만 추출

                current_date = datetime.datetime.strptime(
                    file_date,
                    '%Y%m%d'
                )

                if start <= current_date <= end: #날짜 범위 안에 있는지 검사
                    matched_files.append(file_name) #조건 맞으면 리스트 추가

        matched_files.sort() #날짜순 정렬

        print('\n조회 결과')

        if len(matched_files) == 0:
            print('해당 날짜 범위의 녹음 파일이 없습니다.')

            return

        for file_name in matched_files:
            print(file_name)

    def speech_to_text(self, file_name):
        file_path = os.path.join(self.records_dir, file_name) # records 폴더 안의 wav 파일 전체 경로 새엇ㅇ

        recognizer = sr.Recognizer() # 음성 인식 객체 생성
        result_list = [] # 결과를 저장할 리스트 생성

        with sr.AudioFile(file_path) as source: # wav 파일 열기
            audio = recognizer.record(source) # 파일 전체를 읽어서 audio 변수에 저장

            try: # 구글 STT를 사용해서 음성을 텍스트로 변환
                text = recognizer.recognize_google(audio, language='ko-KR') #language='ko-KR'은 한국어 인식 설정
            except sr.UnknownValueError: # 음성을 알아들을 수 없는 경우
                text = '인식 실패'
            except sr.RequestError: # 인터넷 연결 또는 STT 서버 오류
                text = 'STT 서비스 요청 실패'

        result_list.append([0, text]) # [시간, 변환결과] 형태로 리스트에 저장

        return result_list #결과 반환

    def save_text_csv(self, file_name, result_list):
        csv_file_name = file_name.replace('.wav', '.csv') #wav 확장자를 csv로 변경
        csv_file_path = os.path.join(self.records_dir, csv_file_name) #csv 저장 경로 생성

        with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as file: #csv 파일 생성
            writer = csv.writer(file) #csv 작성 객체 생성
            writer.writerow(['time', 'text']) #첫번째 줄(헤더) 작성

            for result in result_list: #변환 결과를 한 줄씩 저장
                writer.writerow(result)

        print(f'CSV 저장 완료: {csv_file_path}') #저장 완료 메시지 출력

    def convert_voice_to_text(self):
        file_list = os.listdir(self.records_dir) #records 폴더 안 파일 목록 가져오기

        wav_files = [] #wav 파일만 저장할 리스트

        for file_name in file_list: #파일 하나씩 검사
            if file_name.endswith('.wav'): #wav 파일인지 확인
                wav_files.append(file_name) #wav 파일이면 리스트에 추가

        if len(wav_files) == 0: #wav 파일이 없는 경우
            print('녹음 파일이 없습니다.')
            return

        for file_name in wav_files: #wav 파일 하나씩 처리
            print(f'\n변환 중: {file_name}')

            result_list = self.speech_to_text(file_name) # 음성을 텍스트로 변환
            self.save_text_csv(file_name, result_list) #csv 파일로 저장

    def search_keyword(self, keyword):
        file_list = os.listdir(self.records_dir) # records 폴더 안 파일 목록 가져오기
        found = False #검색 결과 존재 여부 확인용 변수

        for file_name in file_list: #파일 하나씩 검사
            if file_name.endswith('.csv'): #csv 파일만 검사
                file_path = os.path.join(self.records_dir, file_name) # csv 파일 경로 생성

                with open(file_path, 'r', encoding='utf-8-sig') as file: #csv 파일 열기
                    reader = csv.reader(file) #csv 읽기 객체 생성
                    next(reader) # 첫번째 줄(time, text) 건너뛰기

                    for row in reader: #한줄씩 읽기
                        time = row[0] #시간 데이터
                        text = row[1] #텍스트 데이터

                        if keyword in text: #사용자가 입력한 키워드 포함 여부 확인
                            print(f'\n파일명: {file_name}')
                            print(f'시간: {time}초')
                            print(f'내용: {text}')
                            found = True

        if not found: #검색 결과가 없는 경우
            print('검색 결과가 없습니다.')
def main(): # 프로그램 시작 함수
    recorder = VoiceRecorder() #녹음기 객체 생성

    while True: #계속 메뉴 반복
        print('\n===== JAVIS =====')
        print('1. 음성 녹음')
        print('2. 날짜 범위 파일 조회')
        print('3. 음성을 문자로 변환')
        print("4. 키워드 검색")
        print('5. 종료')

        menu = input('메뉴 선택: ') #사용자 입력 받기

        if menu == '1': #1번 선택시 녹음
            try:
                duration = int(input('녹음 시간(초): ')) #숫자 입력 받기

                recorder.record_voice(duration)

            except ValueError: # 숫자 아닌 값 입력시 예외 처리
                print('숫자를 입력해주세요.')

        elif menu == '2': #날짜 조회 메뉴
            start_date = input('시작 날짜 입력 (예: 20260524): ')
            end_date = input('종료 날짜 입력 (예: 20260530): ')

            try:
                recorder.show_files_by_date(
                    start_date,
                    end_date
                )

            except ValueError:
                print('날짜 형식이 올바르지 않습니다.')


        elif menu == '3': #wav 파일을 csv 파일로 변환

            recorder.convert_voice_to_text()


        elif menu == '4': #검색할 단어 입력

            keyword = input('검색할 키워드 입력: ')

            recorder.search_keyword(keyword) # 키워드 검색 실행


        elif menu == '5': # 프로그램 종료

            print('프로그램 종료')

            break

        else:
            print('올바른 메뉴를 입력해주세요.')


if __name__ == '__main__':
    main()