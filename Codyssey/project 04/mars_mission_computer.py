# import sys  # 런타임 설정이나 모듈 경로 관리 등에 사용
# import os  # 파일 경로를 다룸
import time # 시간 관련 기능 사용
import json # 딕셔너리를 JSON 문자열로 변환
import threading #동시에 두작업 수행 (센서 반복 실행, 사용자 입력대기)
from datetime import datetime # 현재 날짜/시간 가져오기-> 로그에 시간 기록
from mission_computer import DummySensor #센서 역할을 하는 클래스 가져오기 -> 환경 데이터 생성


class MissionComputer: #미션 컴퓨터 역할을 하는 객체 정의
    def __init__(self): #객체 생성 시 자동 실행
        self.ds = DummySensor() #DummySensor 객체 생성 -> 센서 역할 수행
        self.env_values = {} #현재 환경 데이터 저장할 딕셔너리
        self.stop_flag = False #반복 종료 조건 -> false 계속 실행
        self.all_logs = []  # 모든 로그 데이터를 저장할 리스트 -> 나중에 JSON 파일로 저장

    def get_sensor_data(self): #센서 데이터를 계속 가져오는 함수
        try: #실행 중 오류 발생시 프로그램 죽지 않도록 보호 하기위해 try 사용
            env_history = [] #최근 5분 데이터 저장 -> 평균 계산용
            start_time = time.time() # 5분 시작 시간 기록

            while not self.stop_flag: #종료 신호가 올 때까지 계속 반복
                self.ds.set_env() #센서 값 새로 생성
                self.env_values = self.ds.get_env() #생성된 값 가져오기

                # 시간 포함 데이터
                log_data = {
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    **self.env_values
                } # 딕셔너리 합치기( datetime -> 현재 시간 추가 , **self.~ -> 기존 센서 값 합침

                env_history.append(self.env_values.copy()) # 평균 계산용 저장 copy-> 원본 값 변경 방지, 과거 데이터 유지

                print(json.dumps(log_data, indent=2)) #JSON 형태로 보기 좋게 출력

                self.all_logs.append(log_data)  #전체 로그 리스트에 저장 -> 나중에 파일로 저장

                if time.time() - start_time >= 300: #현재시간 - 시작시간 >= 300초(5분)
                    print("\n5분 평균 환경값")

                    average = {} #평균값 저장용 딕셔너리
                    for key in self.env_values: # 모든 센서 항목 반복
                        values = [entry[key] for entry in env_history] # 특정 항목 값들만 출력
                        average[key] = round(sum(values) / len(values), 2) # sum()합계 /len-> 개수, 소수점 2자리

                    avg_data = { # 평균값도 JSON 구조로 저장
                        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "5min_average": average
                    }

                    print(json.dumps(avg_data, indent=2))

                    self.all_logs.append(avg_data) # 평균도 파일에 포함

                    env_history = []
                    start_time = time.time() # 다음 5분 계산 준비

                time.sleep(5) # 5초마다 반복 실행

        except Exception as e:
            print("에러 발생:", e) # 오류 발생시 메시지 출력 -> 예외처리


# 실행 코드
RunComputer = MissionComputer() # 객체 생성

t = threading.Thread(target=RunComputer.get_sensor_data) # 센서 데이터 수집을 백그라운드에서 실행
t.start()

input("종료하려면 아무 키나 누르세요\n") # 엔터 누르면 종료
RunComputer.stop_flag = True # 반복 종료 신호 전달

t.join() # 센서 작업 끝날 때까지 기다림

with open("env_log.json", "w", encoding="utf-8") as f:
    json.dump(RunComputer.all_logs, f, indent=2) # 리스트 전체를 JSON 파일로 저장

print("Sytem stoped...") # 프로그램 종료 표시