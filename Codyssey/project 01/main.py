# Mission Computer Log Analysis
# Description: mission_computer_main.log 파일을 분석하여 문제 로그를 찾고 보고서를 생성하는 프로그램

print('Hello Mars')

log_file = 'mission_computer_main.log'  # 분석할 로그 파일
report_file = 'log_analysis.md'  # 생성할 보고서 파일

try:  # 실행 중 오류가 발생하면 프로그램이 멈추지 않도록 처리

    # 로그 파일 열기
    with open(log_file, 'r', encoding='utf-8') as file:
        log_data = file.readlines()

    print(f"'{log_file}' 파일 내용 출력:")

    # 로그를 시간 역순으로 출력 (최신 로그 먼저)
    for line in reversed(log_data):
        print(line.strip())

    # 문제 로그 탐지
    keywords = ['unstable', 'explosion']  # 문제 판단 키워드

    problem_logs = [ # 로그에서 문제되는 코드 골라내 problems_logs에 저장
        line.strip()
        for line in log_data #리스트에 있는 모든 로그를 하나씩 검사
        if any(keyword in line for keyword in keywords) #unstable, explosion이 있는 줄 골라내기
    ]

    print('\n문제 로그:')
    for log in problem_logs:
        print(log)

    # 문제 로그 별도 파일 저장 (보너스 과제)
    problem_file = 'problem_logs.txt'
    # w 모드
    with open(problem_file, 'w', encoding='utf-8') as f:
        for log in problem_logs:
            f.write(log + '\n')

    # Markdown 보고서 생성 w 모드
    with open(report_file, 'w', encoding='utf-8') as report:

        # 보고서 제목
        report.write('# Mission Computer Log Analysis\n\n')

        # 1. 분석 대상
        report.write('## 1. 분석 대상\n')
        report.write(f'- 로그 파일: {log_file}\n\n')

        # 2. 로그 분석 과정
        report.write('## 2. 로그 분석 과정\n')
        report.write('- Python을 사용하여 로그 파일을 읽고 분석하였다.\n')
        report.write('- 로그를 시간 역순으로 확인하여 최근 이벤트를 먼저 분석하였다.\n')
        report.write('- 특정 키워드를 기반으로 문제 로그를 탐지하였다.\n\n')

        # 3. 문제 발생 로그
        report.write('## 3. 문제 발생 로그\n')

        if problem_logs:
            for log in problem_logs:
                report.write(f'- {log}\n')
        else:
            report.write('- 문제 로그 없음\n')

        # 4. 사고 원인 분석
        report.write('\n## 4. 사고 원인 분석\n')
        report.write(
            '로그 분석 결과 11:35에 "Oxygen tank unstable"(산소 탱크 불안정) 메시지가 기록되었으며 \n '
            '이후 11:40에 "Oxygen tank explosion"(산소 탱크 폭발) 메시지가 발생하였다. \n '
            '따라서 산소 탱크의 불안정 상태가 폭발로 이어진 것으로 판단된다.\n\n'
        )

        # 5. 결론
        report.write('## 5. 결론\n')
        report.write(
            '산소 탱크의 불안정 상태가 폭발 사고의 주요 원인으로 분석된다.\n '
            '향후 유사 사고를 방지하기 위해 산소 탱크 상태 모니터링과 '
            '시스템 안전 점검이 필요하다.\n'
        )

    print('\n분석 결과 저장 완료')

except FileNotFoundError:
    print(f"파일 '{log_file}'을 찾을 수 없습니다")

except Exception as e:
    print(f'오류 발생: {e}')
