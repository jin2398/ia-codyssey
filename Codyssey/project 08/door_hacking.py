import zipfile # 압축 파일(zip)을 다루기 위한 모듈 불러오기
import itertools # 모든 경우의 수 조합을 만들기 위한 모듈 불러오기
import string # 알파벳, 숫자 등 문자 집합을 쉽게 쓰기 위한 모듈 불러오기
import multiprocessing
import time
from datetime import datetime

ZIP_FILE = "emergency_storage_key.zip" # 암호를 풀 zip 파일 이름 (같은 폴더에 있어야 함)
OUTPUT_FILE = "password.txt" # 암호를 찾으면 저장할 파일 이름

CHARSET = string.ascii_lowercase + string.digits # 암호에 사용될 문자 집합: 소문자 알파벳(a~z) + 숫자(0~9) = 총 36글자
PASSWORD_LENGTH = 6 # 암호의 자릿수 (6자리)
PROCESS_COUNT = multiprocessing.cpu_count() # 현재 컴퓨터의 CPU 코어 수를 자동으로 가져옴 (예: 8코어면 8)

# 보너스 과제: 로컬 카운터 배치 처리로 lock 경쟁 최소화
# 기존 방식: 매 시도마다 공유 lock 획득 → 약 21억 번 lock 발생
# 개선 방식: 로컬 카운터로 집계 후 1000번마다 1번만 공유 카운터 업데이트
#            → lock 횟수를 1/1000로 줄여 병렬 처리 성능 대폭 향상
BATCH_SIZE = 1000


def try_passwords(start_chars, counter, found_flag, start_time, target_file):
    """
    하나의 프로세스가 주어진 시작 문자 목록으로 가능한 6자리 암호를 생성하여 압축 해제를 시도한다.
    - zf.read()로 메모리에서만 검증하여 디스크 I/O를 제거, 속도를 대폭 향상시킨다.
    - 로컬 카운터 배치 처리로 공유 lock 경쟁을 최소화한다.
    """
    try:
        with zipfile.ZipFile(ZIP_FILE) as zf: # zip 파일을 열어서 zf라는 이름으로 사용 (with 블록을 벗어나면 자동으로 닫힘)
            for start_char in start_chars: # 이 프로세스가 맡은 시작 문자들을 하나씩 순서대로 처리
                if found_flag.value: # 다른 프로세스가 이미 암호를 찾았으면 바로 종료
                    return

                local_count = 0 # 로컬(이 프로세스만의) 시도 횟수 카운터, lock 없이 빠르게 셈

                for pwd_tuple in itertools.product(CHARSET, repeat=PASSWORD_LENGTH - 1): # 나머지 5자리의 모든 조합을 생성 (36^5 = 약 6천만 가지)
                    if found_flag.value: # 다른 프로세스가 암호를 찾았으면 즉시 종료
                        return

                    password = start_char + ''.join(pwd_tuple) # 시작 문자 + 나머지 5글자 조합으로 6자리 암호 완성
                    local_count += 1 # 로컬 카운터 1 증가

                    # BATCH_SIZE마다 공유 카운터에 반영 (lock 경쟁 최소화)
                    if local_count % BATCH_SIZE == 0: # 1000번 시도할 때마다 공유 카운터에 반영하고 진행 상황 출력
                        with counter.get_lock(): # lock을 걸어 다른 프로세스와 동시에 접근하지 못하게 함
                            counter.value += BATCH_SIZE # 공유 카운터에 1000 더하기
                            count = counter.value # 현재 총 시도 횟수 저장
                        elapsed = time.time() - start_time # 현재까지 경과한 시간 계산
                        print(f"[{start_char}] {count}회 시도 중... 경과 시간: {elapsed:.2f}초") # 진행 상황 출력

                    try:
                        # extractall() 대신 read()로 메모리에서만 검증 (디스크 I/O 없음)
                        zf.read(target_file, pwd=password.encode()) # zip 파일에서 첫 번째 파일을 메모리로만 읽어서 암호 검증

                        # 여기까지 오면 암호가 맞은 것! (예외 없이 통과했으므로)

                        # 남은 로컬 카운트 반영
                        with counter.get_lock():  # 남은 로컬 카운트(1000 미만의 나머지)를 공유 카운터에 반영
                            counter.value += local_count % BATCH_SIZE
                            count = counter.value

                        found_flag.value = 1 # 암호를 찾았다고 다른 프로세스에게 알림 (1로 설정)
                        duration = time.time() - start_time  # 총 소요 시간 계산

                        # 결과 출력
                        print(f"\n[+] 암호 해제 성공!")
                        print(f"[+] 암호: {password}")
                        print(f"[+] 시작 시간: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"[+] 시도 횟수: {count}")
                        print(f"[+] 소요 시간: {duration:.2f}초")

                        with open(OUTPUT_FILE, 'w') as f: # 찾은 암호를 password.txt 파일에 저장
                            f.write(password)

                        return # 이 프로세스 종료

                    except Exception: # 암호가 틀렸으면 예외가 발생하므로 그냥 넘어가고 다음 암호 시도
                        pass

    except Exception as e: # zip 파일을 열지 못하는 등 예상치 못한 오류 발생 시 출력
        print(f"[!] 오류 발생: {e}")


def unlock_zip():
    """
    멀티코어로 암호를 병렬로 해제하는 메인 함수.
    - CHARSET 전체를 CPU 코어 수만큼 균등 분배하여 탐색 범위 누락 방지
    - 보너스: 로컬 카운터 배치 처리 알고리즘으로 lock 경쟁을 최소화하여 속도 향상
    """
    start_time = time.time() # 프로그램 시작 시간 기록
    counter = multiprocessing.Value('i', 0) # 모든 프로세스가 공유하는 시도 횟수 카운터 (정수형, 초기값 0)
    found_flag = multiprocessing.Value('i', 0) # 암호를 찾았는지 여부를 공유하는 변수 (0: 못찾음, 1: 찾음)

    # 시작 정보 출력
    print(f"[*] 멀티코어 해킹 시작 (사용 코어 수: {PROCESS_COUNT})")
    print(f"[*] 시작 시간: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] 알고리즘: 로컬 카운터 배치 처리 (배치 크기: {BATCH_SIZE})")

    # zip 파일 내 첫 번째 파일명 추출 (메모리 검증용)
    with zipfile.ZipFile(ZIP_FILE) as zf:
        target_file = zf.namelist()[0]
    print(f"[*] 검증 대상 파일: {target_file}") # 검증에 사용할 파일 이름 출력

    # CHARSET 전체(36글자)를 코어 수만큼 균등 분배 (round-robin)
    # 예: 8코어면 [0::8], [1::8], ..., [7::8] 로 나눠서 각 프로세스에 배분
    chunks = [CHARSET[i::PROCESS_COUNT] for i in range(PROCESS_COUNT)]

    processes = [] # 각 코어에 프로세스를 하나씩 만들어서 실행
    for chunk in chunks: # 프로세스 생성: 실행할 함수와 전달할 인자 지정
        p = multiprocessing.Process(
            target=try_passwords,
            args=(chunk, counter, found_flag, start_time, target_file)
        )
        p.start()  # 프로세스 시작
        processes.append(p) # 나중에 기다릴 수 있도록 목록에 추가

    for p in processes: # 모든 프로세스가 끝날 때까지 기다림
        p.join()

    if not found_flag.value: # 모든 프로세스가 끝났는데도 암호를 못 찾은 경우 출력
        print("[!] 암호를 찾지 못했습니다.")

# 이 파일을 직접 실행할 때만 unlock_zip() 함수 호출
# (다른 파일에서 import할 때는 자동으로 실행되지 않도록 하는 파이썬 관용구)
if __name__ == "__main__":
    unlock_zip()
