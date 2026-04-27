from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import sys


class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        # 인스턴스 속성 미리 선언 (PyCharm 경고 제거 및 초기값 설정)
        self.current_value = '0'      # 현재 화면에 표시되는 값
        self.operand = None           # 연산자 앞에 입력된 첫 번째 숫자
        self.operator = None          # 현재 선택된 연산자 (+, -, ×, ÷)
        self.waiting_for_new = True   # 새 숫자 입력 대기 상태 여부

        self.init_ui()   # UI 초기화
        self.reset()     # 계산기 상태 초기화

    def init_ui(self):
        # 윈도우 기본 설정
        self.setWindowTitle('iPhone Calculator')
        self.setGeometry(100, 100, 320, 600)  # 위치(x, y)와 크기(width, height)
        self.setStyleSheet("background-color: #000000;")  # 전체 배경 검정

        # 숫자 표시 화면(디스플레이) 설정
        self.display = QLineEdit(self)
        self.display.setReadOnly(True)  # 직접 키보드 입력 불가, 버튼으로만 입력
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)  # 텍스트 우측 하단 정렬
        self.display.setFixedHeight(160)  # 디스플레이 높이 고정
        self.display.setStyleSheet("""
            font-size: 72px;
            padding: 20px;
            color: white;
            background-color: #000000;
            border: none;
        """)

        # 그리드 레이아웃 생성 (버튼 배치용)
        grid = QGridLayout()

        # 버튼 목록 정의: (버튼 텍스트, 행, 열) 또는 (텍스트, 행, 열, 행span, 열span)
        # '0' 버튼은 두 칸을 차지하므로 colspan=2 지정
        buttons = [
            ('AC', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3),
        ]

        for btn in buttons:
            # 버튼 정보 언패킹 (span 값이 없으면 기본값 1 사용)
            text = btn[0]
            row = btn[1]
            col = btn[2]
            rowspan = btn[3] if len(btn) > 3 else 1
            colspan = btn[4] if len(btn) > 4 else 1

            button = QPushButton(text)
            button.setFixedSize(80, 80)  # 버튼 크기 고정 (80x80 정사각형)

            # 버튼 종류별 스타일 지정
            if text in ['AC', '±', '%']:
                # 기능 버튼: 회색 배경, 검정 텍스트
                style = """
                    background-color: #A5A5A5;
                    color: black;
                    font-size: 28px;
                    border-radius: 40px;
                """
            elif text in ['÷', '×', '-', '+', '=']:
                # 연산자 버튼: 주황 배경, 흰색 텍스트
                style = """
                    background-color: #FF9500;
                    color: white;
                    font-size: 28px;
                    border-radius: 40px;
                """
            else:
                # 숫자 버튼 및 소수점: 어두운 회색 배경, 흰색 텍스트
                style = """
                    background-color: #333333;
                    color: white;
                    font-size: 28px;
                    border-radius: 40px;
                """

            # '0' 버튼은 두 칸 너비이므로 최소 너비를 2배로 설정
            if text == '0':
                button.setMinimumSize(160, 80)

            button.setStyleSheet(style)
            button.clicked.connect(self.on_click)  # 버튼 클릭 시 on_click() 연결
            grid.addWidget(button, row, col, rowspan, colspan)  # 그리드에 버튼 추가

        # 전체 레이아웃: 디스플레이 위, 버튼 그리드 아래
        layout = QVBoxLayout()
        layout.addWidget(self.display)
        layout.addLayout(grid)

        self.setLayout(layout)

    # ---------------------------
    # 계산 로직
    # ---------------------------

    def reset(self):
        # 계산기를 초기 상태로 되돌림 (AC 버튼 역할)
        self.current_value = '0'
        self.operand = None
        self.operator = None
        self.waiting_for_new = True
        self.update_display()

    def update_display(self):
        # 현재 값을 화면에 표시하고, 숫자 길이에 따라 폰트 크기 자동 조정
        text = self.current_value
        length = len(text)

        if length <= 9:
            font_size = 72    # 짧은 숫자: 큰 폰트
        elif length <= 12:
            font_size = 52    # 중간 길이: 중간 폰트
        else:
            font_size = 36    # 긴 숫자: 작은 폰트

        self.display.setStyleSheet(f"""
            font-size: {font_size}px;
            padding: 20px;
            color: white;
            background-color: #000000;
            border: none;
        """)
        self.display.setText(text)

    def input_number(self, num):
        # 숫자 버튼 입력 처리
        if self.waiting_for_new:
            # 새 숫자 입력 대기 중이면 현재 값을 새 숫자로 교체
            self.current_value = num
            self.waiting_for_new = False
        else:
            if self.current_value == '0':
                # 현재 값이 '0'이면 앞에 0이 붙지 않도록 교체
                self.current_value = num
            else:
                # 기존 값 뒤에 숫자를 이어 붙임
                self.current_value += num
        self.update_display()

    def input_dot(self):
        # 소수점 버튼 입력 처리
        if self.waiting_for_new:
            # 새 입력 대기 중이면 '0.'으로 시작
            self.current_value = '0.'
            self.waiting_for_new = False
        elif '.' not in self.current_value:
            # 소수점이 없을 때만 추가 (중복 방지)
            self.current_value += '.'
        self.update_display()

    def add(self, a, b):
        # 덧셈 연산 메소드
        return a + b

    def subtract(self, a, b):
        # 뺄셈 연산 메소드
        return a - b

    def multiply(self, a, b):
        # 곱셈 연산 메소드
        return a * b

    def divide(self, a, b):
        # 나눗셈 연산 메소드 (0으로 나누면 ZeroDivisionError 발생)
        if b == 0:
            raise ZeroDivisionError
        return a / b

    def negative_positive(self):
        # 양수/음수 전환 (± 버튼 역할)
        if self.current_value.startswith('-'):
            # 음수이면 맨 앞 '-' 제거 → 양수로 전환
            self.current_value = self.current_value[1:]
        else:
            # 양수이고 0이 아닌 경우 '-' 추가 → 음수로 전환
            if self.current_value != '0':
                self.current_value = '-' + self.current_value
        self.update_display()

    def percent(self):
        # 퍼센트 변환 (현재 값을 100으로 나눔)
        value = float(self.current_value) / 100
        self.current_value = str(round(value, 6))  # 소수점 6자리 반올림
        self.update_display()

    def set_operator(self, op):
        # 연산자 버튼(+, -, ×, ÷) 입력 처리
        if self.operator and not self.waiting_for_new:
            # 이전 연산자가 있고 새 숫자가 입력된 상태면 먼저 계산 수행 (연속 연산 지원)
            self.equal()

        self.operand = float(self.current_value)  # 첫 번째 피연산자 저장
        self.operator = op                         # 선택된 연산자 저장
        self.waiting_for_new = True                # 다음 숫자 입력 대기 상태로 전환

    def equal(self):
        # = 버튼 처리: 저장된 연산자와 피연산자로 계산 수행
        try:
            value = float(self.current_value)  # 두 번째 피연산자

            # 연산자에 따라 개별 메소드 호출
            if self.operator == '+':
                result = self.add(self.operand, value)
            elif self.operator == '-':
                result = self.subtract(self.operand, value)
            elif self.operator == '×':
                result = self.multiply(self.operand, value)
            elif self.operator == '÷':
                result = self.divide(self.operand, value)
            else:
                return  # 연산자가 없으면 계산하지 않음

            # 결과 저장 및 상태 초기화
            self.current_value = str(round(result, 6))  # 소수점 6자리 반올림
            self.operator = None
            self.operand = None
            self.waiting_for_new = True
            self.update_display()

        except ZeroDivisionError:
            # 0으로 나누기 오류 처리
            self.display.setText("오류: 0으로 나눌 수 없음")
            self.operator = None
            self.operand = None
            self.waiting_for_new = True

        except OverflowError:
            # 숫자 범위 초과 오류 처리
            self.display.setText("오류: 범위 초과")
            self.operator = None
            self.operand = None
            self.waiting_for_new = True

    def on_click(self):
        # 버튼 클릭 이벤트 핸들러: 클릭된 버튼 텍스트에 따라 동작 분기
        text = self.sender().text()  # 클릭된 버튼의 텍스트 가져오기

        if text.isdigit():
            self.input_number(text)       # 숫자 버튼

        elif text == '.':
            self.input_dot()              # 소수점 버튼

        elif text in ['+', '-', '×', '÷']:
            self.set_operator(text)       # 연산자 버튼

        elif text == '=':
            self.equal()                  # 등호 버튼

        elif text == 'AC':
            self.reset()                  # 초기화 버튼

        elif text == '±':
            self.negative_positive()      # 부호 전환 버튼

        elif text == '%':
            self.percent()               # 퍼센트 버튼


def main():
    # 애플리케이션 실행 진입점
    app = QApplication(sys.argv)   # QApplication 인스턴스 생성
    calc = Calculator()            # 계산기 위젯 생성
    calc.show()                    # 화면에 표시
    sys.exit(app.exec_())          # 이벤트 루프 실행 (종료 시 sys.exit 호출)


if __name__ == '__main__':
    main()
