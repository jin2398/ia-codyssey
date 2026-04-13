import time  # 시간 관련 기능을 사용하기 위한 모듈 (sleep, time 등)
import json  # 딕셔너리를 JSON 형식 문자열로 변환하거나 파일로 저장할 때 사용
import threading  # 여러 작업을 동시에 실행할 수 있게 해주는 모듈 (멀티스레드)
from datetime import datetime  # 현재 날짜와 시간을 가져오기 위해 datetime 클래스만 불러옴
from mission_computer import DummySensor  # 센서 역할을 하는 DummySensor 클래스를 mission_computer 파일에서 불러옴


class MissionComputer:  # MissionComputer라는 이름의 클래스(설계도)를 정의함
    """
    미션 컴퓨터 클래스
    - 센서 데이터 수집
    - 시스템 정보 출력
    - 시스템 부하 출력
    - 설정 파일 기반 출력 제어
    """  # 클래스 전체에 대한 설명 (독스트링, 실행되지 않고 설명용으로만 사용됨)

    def __init__(self):  # 객체가 처음 만들어질 때 자동으로 실행되는 초기화 함수
        self.ds = DummySensor()  # DummySensor 객체를 만들어서 self.ds에 저장 → 센서 역할을 담당함
        self.env_values = {}  # 현재 센서에서 받아온 환경 데이터를 저장할 빈 딕셔너리
        self.stop_flag = False  # 반복 실행을 멈출지 여부를 저장하는 변수 → False = 계속 실행
        self.all_logs = []  # 수집한 모든 로그 데이터를 저장할 빈 리스트 → 나중에 파일로 저장
        self.settings = {}  # setting.txt에서 읽어온 출력 설정을 저장할 빈 딕셔너리

        self.load_settings()  # 객체 생성 시 바로 설정 파일을 읽어오는 함수 실행

    # ----------------------------------------
    # 보너스: setting.txt 파일 읽기
    # ----------------------------------------
    def load_settings(self):  # 설정 파일(setting.txt)을 읽어서 설정값을 저장하는 함수
        """
        setting.txt 파일을 읽어서
        어떤 데이터를 출력할지 설정하는 함수
        """  # 함수 설명용 독스트링
        try:  # 아래 코드를 실행하다가 오류가 생기면 except로 넘어감 (프로그램이 죽지 않도록 보호)
            with open("setting.txt", "r") as f:  # setting.txt 파일을 읽기 모드("r")로 열고, f라는 이름으로 사용
                for line in f:  # 파일의 각 줄을 하나씩 꺼내서 반복
                    key, value = line.strip().split("=")  # 줄 양쪽 공백 제거 후 "="를 기준으로 key와 value로 나눔
                    self.settings[key] = int(value)  # key는 항목 이름, value는 숫자(0 또는 1)로 변환해서 저장
        except Exception as e:  # 파일이 없거나 형식이 잘못됐을 때 오류를 잡아서 e에 저장
            print("설정 파일 오류:", e)  # 어떤 오류인지 화면에 출력
            print("기본값으로 전체 출력 진행")  # 설정 없이 전체 데이터를 출력하겠다고 알려줌

    # ----------------------------------------
    # 7번: 센서 데이터 수집
    # ----------------------------------------
    def get_sensor_data(self):  # 센서 데이터를 5초마다 수집하고 5분마다 평균을 계산하는 함수
        """
        센서 데이터를 5초마다 수집하고
        5분마다 평균을 계산하는 함수
        """
        try:  # 실행 중 오류가 생겨도 프로그램이 멈추지 않도록 보호
            env_history = []  # 5분 동안의 센서 데이터를 모아두는 리스트 → 평균 계산에 사용
            start_time = time.time()  # 현재 시각을 저장 → 5분이 지났는지 계산하는 기준점

            while not self.stop_flag:  # stop_flag가 False인 동안 계속 반복 → True가 되면 반복 종료
                self.ds.set_env()  # DummySensor에게 새로운 센서 값을 생성하라고 지시
                self.env_values = self.ds.get_env()  # 생성된 센서 값(딕셔너리)을 가져와서 저장

                filtered_env = {  # 설정(setting.txt)에 따라 출력할 항목만 골라내는 딕셔너리
                    key: value  # 필터링된 항목의 키와 값을 그대로 저장
                    for key, value in self.env_values.items()  # 센서 데이터의 모든 항목을 하나씩 꺼냄
                    if self.settings.get(key, 1) == 1  # settings에서 해당 key의 값이 1이면 포함 (없으면 기본값 1 → 포함)
                }

                log_data = {  # 화면에 출력하고 파일에 저장할 로그 데이터 딕셔너리 생성
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 현재 시간을 "연-월-일 시:분:초" 형식 문자열로 저장
                    **filtered_env  # 필터링된 센서 데이터를 딕셔너리에 풀어서 합침 (**는 딕셔너리 펼치기)
                }

                env_history.append(self.env_values.copy())  # 전체 센서 값을 복사해서 히스토리에 추가 (copy()로 원본 변경 방지)

                print(json.dumps(log_data, indent=2))  # log_data를 보기 좋은 JSON 형식으로 화면에 출력 (indent=2는 들여쓰기 2칸)

                self.all_logs.append(log_data)  # 전체 로그 리스트에 현재 데이터를 추가 → 나중에 파일 저장에 사용

                if time.time() - start_time >= 300:  # 현재 시각 - 시작 시각이 300초(5분) 이상이면 평균 계산
                    print("\n[5분 평균 환경값]")  # 평균값 출력 시작을 알리는 구분 문구 출력

                    average = {}  # 각 항목의 평균값을 저장할 빈 딕셔너리
                    for key in filtered_env:  # 출력 대상 항목(filtered_env)의 키를 하나씩 꺼냄
                        values = [entry[key] for entry in env_history]  # 히스토리에서 해당 항목 값만 꺼내 리스트로 만듦
                        average[key] = round(sum(values) / len(values), 2)  # 합계 ÷ 개수로 평균 계산, 소수점 2자리로 반올림

                    avg_data = {  # 평균값 데이터를 JSON 구조로 만들기
                        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 평균 계산 시점의 현재 시간
                        "5min_average": average  # 계산한 평균값 딕셔너리를 "5min_average" 키로 저장
                    }

                    print(json.dumps(avg_data, indent=2))  # 평균 데이터를 JSON 형식으로 화면에 출력
                    self.all_logs.append(avg_data)  # 평균 데이터도 전체 로그에 추가

                    env_history = []  # 히스토리 초기화 → 다음 5분 동안 새로 쌓기 시작
                    start_time = time.time()  # 시작 시간 초기화 → 다음 5분 카운트 시작

                time.sleep(5)  # 5초 동안 대기 → 5초마다 한 번씩 센서 데이터 수집

        except Exception as e:  # 반복 실행 중 예상치 못한 오류가 발생하면 잡아서 e에 저장
            print("센서 데이터 에러:", e)  # 어떤 오류인지 화면에 출력

    # ----------------------------------------
    # 8번: 시스템 정보 출력
    # ----------------------------------------
    def get_mission_computer_info(self):  # 운영체제, CPU, 메모리 등 시스템 정보를 출력하는 함수
        """
        운영체제, CPU, 메모리 정보 출력
        (외부 라이브러리 사용 시 예외 처리 포함)
        """
        try:  # 오류 발생 시 프로그램이 멈추지 않도록 보호
            import platform  # 운영체제, CPU 정보를 가져오는 표준 라이브러리 (파이썬 기본 제공)

            info = {  # 시스템 정보를 담을 딕셔너리 생성
                "os": platform.system(),  # 운영체제 이름 가져옴 (예: "Windows", "Linux", "Darwin")
                "os_version": platform.version(),  # 운영체제의 세부 버전 정보 가져옴
                "cpu_type": platform.processor(),  # CPU 종류/이름 가져옴 (예: "Intel64 Family 6...")
                "cpu_cores": None,  # CPU 코어 수 → 아직 모름, psutil로 채울 예정이라 None으로 초기화
                "memory_size_gb": None  # 메모리 크기(GB) → 아직 모름, psutil로 채울 예정이라 None으로 초기화
            }

            try:  # psutil 설치 여부를 확인하는 내부 try → 없어도 위 정보는 출력되도록 분리
                import psutil  # CPU 코어 수, 메모리 크기 등 상세 정보를 제공하는 외부 라이브러리
                info["cpu_cores"] = psutil.cpu_count(logical=True)  # 논리 CPU 코어 수를 가져와서 저장 (하이퍼스레딩 포함)
                info["memory_size_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # 전체 메모리(bytes)를 GB로 변환 후 소수점 2자리로 저장
            except ImportError:  # psutil이 설치되어 있지 않으면 ImportError 발생 → 여기서 처리
                print("psutil 없음 → 일부 정보 제한됨")  # 설치 안 됨을 알리고 계속 진행

            print("\n[시스템 정보]")  # 시스템 정보 출력 시작을 알리는 구분 문구
            print(json.dumps(info, indent=2))  # 수집한 시스템 정보를 JSON 형식으로 보기 좋게 출력

            return info  # 수집한 정보를 딕셔너리로 반환 (다른 곳에서 활용 가능하도록)

        except Exception as e:  # 예상치 못한 오류 발생 시 잡아서 처리
            print("시스템 정보 에러:", e)  # 어떤 오류인지 화면에 출력

    # ----------------------------------------
    # 8번: 시스템 부하 출력
    # ----------------------------------------
    def get_mission_computer_load(self):  # 현재 CPU와 메모리 사용량을 출력하는 함수
        """
        CPU 및 메모리 사용량 출력
        """  # 함수 설명용 독스트링
        try:  # 오류 발생 시 프로그램이 멈추지 않도록 보호
            import psutil  # CPU/메모리 사용량 측정을 위한 외부 라이브러리

            load = {  # 시스템 부하 데이터를 저장할 딕셔너리
                "cpu_usage_percent": psutil.cpu_percent(interval=1),  # 1초 동안 측정한 CPU 사용률(%) 가져옴
                "memory_usage_percent": psutil.virtual_memory().percent  # 현재 메모리 사용률(%) 가져옴
            }

            print("\n[시스템 부하]")  # 시스템 부하 출력 시작을 알리는 구분 문구
            print(json.dumps(load, indent=2))  # 수집한 부하 데이터를 JSON 형식으로 출력

            return load  # 수집한 데이터를 딕셔너리로 반환

        except ImportError:  # psutil이 설치되지 않았을 때 발생하는 오류 처리
            print("psutil 설치 필요")  # 설치가 필요하다고 안내
        except Exception as e:  # 그 외 예상치 못한 오류 처리
            print("부하 정보 에러:", e)  # 어떤 오류인지 화면에 출력


# ----------------------------------------
# 실행 코드
# ----------------------------------------
if __name__ == "__main__":  # 이 파일을 직접 실행할 때만 아래 코드가 실행됨 (다른 파일에서 import하면 실행 안 됨)
    runComputer = MissionComputer()  # MissionComputer 객체를 만들어서 runComputer 변수에 저장

    runComputer.get_mission_computer_info()  # 시스템 정보(OS, CPU, 메모리)를 출력하는 함수 실행
    runComputer.get_mission_computer_load()  # 현재 CPU/메모리 사용량을 출력하는 함수 실행

    t = threading.Thread(target=runComputer.get_sensor_data)  # get_sensor_data 함수를 백그라운드에서 실행할 스레드 생성
    t.start()  # 스레드 시작 → get_sensor_data가 백그라운드에서 5초마다 실행됨

    input("\n종료하려면 Enter 입력\n")  # 사용자가 Enter를 누를 때까지 대기 → 그 동안 백그라운드에서 센서 수집 계속됨
    runComputer.stop_flag = True  # stop_flag를 True로 바꿔서 while 반복문이 종료되도록 신호 전달

    t.join()  # 백그라운드 스레드(센서 수집)가 완전히 끝날 때까지 기다림

    with open("env_log.json", "w", encoding="utf-8") as f:  # env_log.json 파일을 쓰기 모드로 열고, 한글 깨짐 방지를 위해 utf-8 인코딩 지정
        json.dump(runComputer.all_logs, f, indent=2)  # all_logs 리스트 전체를 JSON 형식으로 파일에 저장 (indent=2로 보기 좋게)

    print("Sytem stoped...")  # 프로그램이 정상적으로 종료됐음을 알리는 마지막 메시지
