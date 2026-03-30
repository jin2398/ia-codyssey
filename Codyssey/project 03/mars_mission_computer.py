import random #파이썬에 있는 랜덤 숫자 생성 도구 가져오기
from datetime import datetime

class DummySensor:
    #화성 기지 환경 데이터를 생성하는 더미 센서 클래스
    def __init__(self): #객체 만들때 자동으로 실행됨
        # 환경 값 초기화
        self.env_values = { #환경 데이터를 저장하는 상자(딕셔너리)
            "mars_base_internal_temperature": None,
            "mars_base_external_temperature": None,
            "mars_base_internal_humidity": None,
            "mars_base_external_illuminance": None,
            "mars_base_internal_co2": None,
            "mars_base_internal_oxygen": None,
        }

    def set_env(self): #환경 값을 랜덤으로 채우는 함수
        # 환경 값을 랜덤으로 생성하여 env_values에 저장
        self.env_values["mars_base_internal_temperature"] = round(random.uniform(18, 30), 2) #18에서 30 랜덤 숫자 생성
        self.env_values["mars_base_external_temperature"] = round(random.uniform(0, 21), 2) #round(...,2) 소수점 2자리로 자르기
        self.env_values["mars_base_internal_humidity"] = round(random.uniform(50, 60), 2)
        self.env_values["mars_base_external_illuminance"] = round(random.uniform(500, 715), 2)
        self.env_values["mars_base_internal_co2"] = round(random.uniform(0.02, 0.1), 4) # 소수점 4자리로.. 2자리면 너무 부정확, 값이 작아서
        self.env_values["mars_base_internal_oxygen"] = round(random.uniform(4.0, 7.0), 2)
        #self.env_values["~"] "~" = 12.43 저장 이렇게 될거임.. 비어있는 값들을 전부 랜덤으로 채움

    def get_env(self): # 값 반환, 파일에 기록
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        """
        현재 환경 값을 반환하고 로그 파일에 저장

        Returns:
             dict: 환경 값 딕셔너리
        """
        #",".join(...) =>리스트를 하나의 문자열로 합침(중요)
        # log_entry = ", ".join(f"{key}:{value}" for key, value in self.env_values.items()) + "\n"
        #log_entry = key + value 같이 꺼냄 f"{key}:{value}" -> 문자열 만들기. ex: mars_base_internal_temperature:23.45
        #join(전부이어붙임) 온도:23, 습도: 42 이런식으로 ..
        log_entry = (
            f"{now}, "
            f"{self.env_values['mars_base_internal_temperature']}, "
            f"{self.env_values['mars_base_external_temperature']}, "
            f"{self.env_values['mars_base_internal_humidity']}, "
            f"{self.env_values['mars_base_external_illuminance']}, "
            f"{self.env_values['mars_base_internal_co2']}, "
            f"{self.env_values['mars_base_internal_oxygen']}\n"
        )

        with open("env_log.txt", "a", encoding="utf-8") as log_file: #파일저장 (append 이어쓰기)
            log_file.write(log_entry)

        return self.env_values #데이터를 밖으로 보내줌


def main():
    #프로그램 실행 테스트
    ds = DummySensor() #객체(인스턴스) 생성-> DummySensor 클래스를 ds라는 이름으로 인스턴스 생성
    ds.set_env() #랜덤 값 채우기
    env_data = ds.get_env() #값 가져오기 + 파일 저장

    print("현재 환경 데이터:") #화면 출력
    for key, value in env_data.items(): #하나씩 꺼내기
        print(f"{key}: {value}") #보기 좋게 출력


if __name__ == "__main__": # 이 파일을 직접 실행했을때만 실행됨, 다른 파일에서 import하면 실행 x
    main()