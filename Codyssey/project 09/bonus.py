def caesar_cipher_decode(target_text, shift):
    decoded_text = ''

    for char in target_text:
        if 'a' <= char <= 'z':
            decoded_char = chr(
                (ord(char) - ord('a') - shift) % 26 + ord('a')
            )
            decoded_text += decoded_char

        elif 'A' <= char <= 'Z':
            decoded_char = chr(
                (ord(char) - ord('A') - shift) % 26 + ord('A')
            )
            decoded_text += decoded_char

        else:
            decoded_text += char

    return decoded_text


def save_result(text):
    try:
        with open('result.txt', 'w', encoding='utf-8') as file:
            file.write(text)

        print('result.txt 저장 완료')

    except OSError:
        print('파일 저장 중 오류가 발생했습니다.')


def main():
    # 사전 단어 목록
    dictionary_words = [
        'hello',
        'password',
        'admin',
        'mars',
        'secret',
        'key'
    ]

    try:
        with open('password2.txt', 'r', encoding='utf-8') as file:
            password_text = file.read().strip()

    except FileNotFoundError:
        print('password2.txt 파일이 없습니다.')
        return

    except OSError:
        print('파일 읽기 오류')
        return

    print('암호 해독 시작\n')

    for shift in range(1, 26):
        decoded = caesar_cipher_decode(password_text, shift)

        print(f'[{shift}칸 이동]')
        print(decoded)
        print()

        # 사전 단어 포함 여부 검사
        for word in dictionary_words:
            if word in decoded.lower():
                print('의미 있는 단어 발견!')
                print(f'발견 단어: {word}')
                print(f'자리수: {shift}')

                save_result(decoded)
                return

    print('사전에 등록된 단어를 찾지 못했습니다.')


if __name__ == '__main__':
    main()