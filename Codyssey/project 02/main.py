file = 'Mars_Base_Inventory_List.csv' # 읽어올 csv 파일 이름

inventory_list = [] #inventory_list 데이터를 저장하는 리스트(비어있음)

try: #파일 오류, 데이터 오류 대비를 위해 try 사용
    # 1. CSV 파일 읽기 → 리스트 변환
    with open(file, 'r', encoding='utf-8') as f: #csv 파일 읽기
        header = f.readline().strip().split(',') #첫줄읽기.줄바꿈제거.콤마기준분리

        for line in f: #데이터 한줄씩 처리
            values = line.strip().split(',') # 한줄 데이터(문자열) 리스트로 변환
            item = dict(zip(header, values)) # header, values 묶어 딕셔너리 생성(데이터를 쉽게 다루기 위해)
            inventory_list.append(item) # 모든 데이터를 리스트로 저장

    print('# 전체 데이터') #전체데이터 출력
    for item in inventory_list: #데이터 세로 출력
        print(item)

    # 2. 배열 내용을 적제 화물 목록을 인화성이 높은 순으로 정렬
    sorted_inventory = sorted(
        inventory_list,
        key=lambda x: float(x['Flammability']), #Flammability 값을 기준으로 정렬 (문자열 -> float 변환)
        reverse=True #높은 값부터 정렬
    )
    

    # 3. 인화성 0.7 이상 목록을 뽑아 별도 출력
    danger_list = [
        item for item in sorted_inventory
        if float(item['Flammability']) >= 0.7 #인화성이 0.7이상인것만 추출
    ]

    print('\n# 인화성 0.7 이상 위험 물질') #출력
    for item in danger_list: # 데이터 세로 출력
        print(item)

    # 4. CSV 파일 저장
    with open('Mars_Base_Inventory_danger.csv', 'w', encoding='utf-8') as f: #새로운 파일 생성
        f.write(','.join(header) + '\n') # csv 파일 첫 줄(컬럼명) 저장

        for item in danger_list:
            row = [item[h] for h in header] #header 순서 유지, csv 형식 유지
            f.write(','.join(row) + '\n') # 데이터 한 줄씩 저장

    print('\n# 위험 물질 CSV 저장 완료') #저장 완료 출력

    # 보너스 과제
    # 5. 이진 파일 저장
    with open('Mars_Base_Inventory_List.bin', 'wb') as f: #바이너리 쓰기 모드
        for item in sorted_inventory:
            line = ','.join([item[h] for h in header]) + '\n' #딕셔너리 값을 header 순서대로 꺼내서 콤마로 이어붙이고 줄바꿈을 추가한 문자열 만들기
            f.write(line.encode('utf-8')) #문자열 encode() -> 바이트변환(이진파일은 바이트만) , 파일에 저장

    print('# 이진 파일 저장 완료') # 파일 저장 완료 출력

    # 6. 이진 파일 다시 읽기
    print('\n# 이진 파일 내용 출력')
    with open('Mars_Base_Inventory_List.bin', 'rb') as f: # 바이너리 읽기 모드
        for line in f:
            print(line.decode('utf-8').strip()) #decode 바이트 -> 문자열 , 줄바꿈 제거

except FileNotFoundError: #예외처리 파일이 없을때
    print('파일을 찾을 수 없습니다.')
except ValueError: # 예외처리 숫자 변환 오류
    print('데이터 형식이 올바르지 않습니다.')
except Exception as e: # 모든 예외 처리
    print(f'오류 발생: {e}')