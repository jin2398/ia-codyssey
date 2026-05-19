# 카이사르 암호를 해독하는 함수
def caesar_cipher_decode(target_text, shift):

    # 해독된 문자열을 저장할 변수
    decoded_text = ''

    # 문자열의 문자 하나씩 반복
    for char in target_text:

        # 소문자인 경우
        if 'a' <= char <= 'z':

            # 아스키코드를 이용해 shift 만큼 뒤로 이동
            decoded_char = chr(
                (ord(char) - ord('a') - shift) % 26 + ord('a')
            )

            # 결과 문자열에 추가
            decoded_text += decoded_char

        # 대문자인 경우
        elif 'A' <= char <= 'Z':

            # 대문자도 동일하게 처리
            decoded_char = chr(
                (ord(char) - ord('A') - shift) % 26 + ord('A')
            )

            # 결과 문자열에 추가
            decoded_text += decoded_char

        # 알파벳이 아닌 경우
        else:

            # 그대로 결과 문자열에 추가
            decoded_text += char

    # 최종 해독 결과 반환
    return decoded_text


# 결과를 파일로 저장하는 함수
def save_result(text):

    try:
        # result.txt 파일을 쓰기 모드로 열기
        with open('result.txt', 'w', encoding='utf-8') as file:

            # 해독 결과 저장
            file.write(text)

        # 저장 완료 메시지 출력
        print('result.txt 저장 완료')

    # 파일을 찾을 수 없는 경우
    except FileNotFoundError:
        print('파일을 찾을 수 없습니다.')

# 메인 함수
def main():

    try:
        # password.txt 파일 읽기
        with open('password.txt', 'r', encoding='utf-8') as file:

            # 파일 내용 읽기
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
    for shift in range(1, 26):

        # 카이사르 암호 해독 수행
        decoded = caesar_cipher_decode(password_text, shift)

        # 현재 shift 결과 출력
        print(f'[{shift}칸 이동 결과]')
        print(decoded)
        print()

    try:
        # 사용자가 정답 shift 입력
        correct_shift = int(
            input('정답이라고 생각하는 자리수를 입력하세요: ')
        )

        # 입력 범위 검사
        if 1 <= correct_shift <= 25:

            # 최종 해독 결과 생성
            final_result = caesar_cipher_decode(
                password_text,
                correct_shift
            )

            # 최종 결과 출력
            print('\n최종 해독 결과:')
            print(final_result)

            # 파일 저장
            save_result(final_result)

        # 잘못된 숫자 입력
        else:
            print('1 ~ 25 사이의 숫자를 입력해야 합니다.')

    # 숫자가 아닌 값 입력 시 처리
    except ValueError:
        print('숫자를 입력해야 합니다.')


# 현재 파일이 직접 실행될 경우 main 함수 실행
if __name__ == '__main__':
    main()