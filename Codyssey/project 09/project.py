# 카이사르 암호를 해독하는 함수
def caesar_cipher_decode(target_text, shift):

    # 해독 결과를 저장할 빈 문자열 생성
    decoded_text = ''

    # 암호문 문자열의 문자 하나씩 반복
    for char in target_text:

        # 현재 문자가 소문자인 경우
        if 'a' <= char <= 'z':

            # ord() : 문자를 아스키 코드 숫자로 변환
            # chr() : 숫자를 다시 문자로 변환
            #
            # ord(char) - ord('a')
            # → 알파벳 위치 계산
            #
            # - shift
            # → shift 값만큼 뒤로 이동
            #
            # % 26
            # → z를 넘어가면 다시 a로 순환
            #
            # + ord('a')
            # → 다시 소문자 아스키 범위로 변환
            decoded_char = chr(
                (ord(char) - ord('a') - shift) % 26 + ord('a')
            )

            # 해독된 문자 결과 문자열에 추가
            decoded_text += decoded_char

        # 현재 문자가 대문자인 경우
        elif 'A' <= char <= 'Z':

            # 대문자도 동일한 방식으로 처리
            decoded_char = chr(
                (ord(char) - ord('A') - shift) % 26 + ord('A')
            )

            # 결과 문자열에 추가
            decoded_text += decoded_char

        # 알파벳이 아닌 경우
        else:

            # 공백, 숫자, 특수문자는 그대로 저장
            decoded_text += char

    # 최종 해독 결과 반환
    return decoded_text


# 결과를 파일로 저장하는 함수
def save_result(text):

    try:
        # result.txt 파일을 쓰기 모드(w)로 열기
        # encoding='utf-8' : 한글 깨짐 방지
        with open('result.txt', 'w', encoding='utf-8') as file:

            # 전달받은 문자열 파일에 저장
            file.write(text)

        # 저장 완료 메시지 출력
        print('result.txt 저장 완료')

    # 파일을 찾을 수 없는 경우
    except FileNotFoundError:
        print('파일을 찾을 수 없습니다.')

# 메인 함수
def main():

    # 보너스 과제 부분
    # 정상 단어를 저장한 사전 리스트 생성
    dictionary_words = [
        'hello',
        'password',
        'admin',
        'secret',
        'key',
        'python'
    ]

    try:
        # password.txt 파일 읽기 모드(r)로 열기
        with open('password.txt', 'r', encoding='utf-8') as file:

            # 파일 내용 읽기
            # strip() : 양쪽 공백, 줄바꿈 제거
            password_text = file.read().strip()

    # 파일이 존재하지 않는 경우
    except FileNotFoundError:
        print('password.txt 파일이 존재하지 않습니다.')
        return


    # 원본 암호문 출력
    print('원본 암호문:')
    print(password_text)
    print()

    # 1칸부터 25칸까지 반복
    # 카이사르 암호는 알파벳 26개 사용
    for shift in range(1, 26):

        # 현재 shift 값으로 암호 해독
        decoded = caesar_cipher_decode(password_text, shift)

        # 현재 결과 출력
        print(f'[{shift}칸 이동 결과]')
        print(decoded)
        print()

        # 보너스 과제 부분
        # 사전 단어 리스트 반복
        for word in dictionary_words:

            # lower() : 대소문자 구분 없이 비교하기 위해 사용
            #
            # 해독 결과 안에 사전 단어가 포함되어 있는지 검사
            if word in decoded.lower():

                # 의미 있는 단어 발견 메시지 출력
                print('의미 있는 단어 발견!')
                print(f'발견 단어: {word}')
                print(f'자리수: {shift}')
                print()

                # 결과 파일 저장
                save_result(decoded)

                # 프로그램 종료
                return

    # 사전 단어를 찾지 못한 경우
    print('사전에 등록된 단어를 찾지 못했습니다.')

    try:
        # 사용자가 직접 정답 shift 입력
        correct_shift = int(
            input('정답이라고 생각하는 자리수를 입력하세요: ')
        )

        # 1 ~ 25 범위 검사
        if 1 <= correct_shift <= 25:

            # 사용자가 선택한 shift 값으로 최종 해독
            final_result = caesar_cipher_decode(
                password_text,
                correct_shift
            )

            # 최종 결과 출력
            print('\n최종 해독 결과:')
            print(final_result)

            # 최종 결과 파일 저장
            save_result(final_result)

        # 잘못된 범위 입력 시
        else:
            print('1 ~ 25 사이의 숫자를 입력해야 합니다.')

    # 숫자가 아닌 값을 입력한 경우
    except ValueError:
        print('숫자를 입력해야 합니다.')


# 현재 파일이 직접 실행될 경우에만 main 함수 실행
if __name__ == '__main__':
    main()