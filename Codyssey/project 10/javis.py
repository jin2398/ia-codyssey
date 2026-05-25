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


def main(): # 프로그램 시작 함수
    recorder = VoiceRecorder() #녹음기 객체 생성

    while True: #계속 메뉴 반복
        print('\n===== JAVIS =====')
        print('1. 음성 녹음')
        print('2. 날짜 범위 파일 조회')
        print('3. 종료')

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

        elif menu == '3': # 종료 메뉴
            print('프로그램 종료')

            break

        else:
            print('올바른 메뉴를 입력해주세요.')


if __name__ == '__main__':
    main()