from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit #PyQt 위젯들 import
from PyQt5.QtCore import Qt # PyQt 위젯들 import
import sys # 정렬 등 상수 사용


class Calculator(QWidget): # QWidget을 상속받아 계산기 클래스 정의
    def __init__(self):
        super().__init__() # 부모 클래스 생성자 호출
        self.init_ui() # 부모 클래스 생성자 호출

    def init_ui(self):
        self.setWindowTitle('iPhone Calculator') # 창 제목 설정
        self.setGeometry(100, 100, 320, 600) # 창 위치 및 크기 설정
        self.setStyleSheet("background-color: #000000;") # 배경색을 검정색을 설정

        # 디스플레이 (입력값 표시 영역)
        self.display = QLineEdit(self) # 한줄 입력창 생성
        self.display.setReadOnly(True) # 키보드 입력 비활성화 (버튼으로만 입력)
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom) # 오른쪽 아래 정렬
        self.display.setFixedHeight(160) # 높이 고정
        self.display.setStyleSheet(""" 
            font-size: 32px; 
            padding: 20px; 
            color: white;  
            background-color: #000000; 
            border: none;  
        """) # 글자크기, 내부 여백, 글자색, 배경색, 테두리 제거

        # 버튼 레이아웃 (격자 형태)
        grid = QGridLayout() # Grid 레이아웃 생성

        # 버튼 정보 (텍스트, 행, 열, [선택] 행span, 열span)
        buttons = [
            ('AC', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3), # 첫줄
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3), # 둘째줄
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3), # 셋째줄
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3), # 넷째줄
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3), # 마지막줄(0은 두칸)
        ]
        # 버튼 생성 반복문
        for btn in buttons:
            text = btn[0] # 버튼 텍스트
            row = btn[1] # 행 위치
            col = btn[2] # 열 위치
            rowspan = btn[3] if len(btn) > 3 else 1 # 행 확장(없으면 1)
            colspan = btn[4] if len(btn) > 4 else 1 # 열 확장(없으면 1)

            button = QPushButton(text) # 버튼 생성
            button.setFixedSize(80, 80) # 버튼 크기 고정

            # 버튼 스타일 설정
            if text in ['AC', '±', '%']: # 기능 버튼 (회색)
                style = """
                    background-color: #A5A5A5;
                    color: black;
                    font-size: 28px;
                    border-radius: 40px;
                """
            elif text in ['÷', '×', '-', '+', '=']: # 연산자 버튼 (주황색)
                style = """
                    background-color: #FF9500;
                    color: white;
                    font-size: 28px;
                    border-radius: 40px;
                """
            else: # 숫자 버튼 (어두운 회색)
                style = """
                    background-color: #333333;
                    color: white;
                    font-size: 28px;
                    border-radius: 40px;
                """

            # 0 버튼은 2칸
            if text == '0':
                button.setMinimumSize(160, 80) # 최소 크기를 가로 2칸으로 설정
                style = """
                    background-color: #333333;
                    color: white;
                    font-size: 28px;
                    border-radius: 40px;
                """

            button.setStyleSheet(style) # 스타일 적용

            button.clicked.connect(self.on_click) # 버튼 클릭 시 이벤트 연결
            grid.addWidget(button, row, col, rowspan, colspan) # 레이아웃에 버튼 추가

        #전체 레이아웃 (세로방향)
        layout = QVBoxLayout() # 세로 레이아웃 설정
        layout.addWidget(self.display) # 디스플레이 추가
        layout.addLayout(grid) # 버튼 레이아웃 추가

        self.setLayout(layout) # 최종 레이아웃 적용

    # 버튼 클릭 이벤트 처리 함수
    def on_click(self):
        text = self.sender().text() # 클릭된 버튼의 텍스트 가져오기
        current = self.display.text() # 현재 디스플레이 값 가져오기

        if text == 'AC': #AC 버튼 -> 초기화
            self.display.clear()

        elif text == '±': #± 버튼 -> 부호 변경
            if current:
                if current.startswith('-'):
                    self.display.setText(current[1:]) # '-'  제거
                else:
                    self.display.setText('-' + current) # '-' 추가

        elif text == '=':
            # 보너스 과제: 4칙 연산 기능 구현
            try:
                expression = current.replace('÷', '/').replace('×', '*') # 연산자 변환
                result = eval(expression) # 수식 계산
                self.display.setText(str(result)) # 결과 출력
            except Exception:
                self.display.setText("Error") # 오류 발생 시 Error 출력

        else:
            self.display.setText(current + text) # 입력값 이어붙이기

# 프로그램 실행 함수
def main():
    app = QApplication(sys.argv) # 애플리케이션 생성
    calc = Calculator() # 계산기 객체 생성
    calc.show() # 창 화면에 표시
    sys.exit(app.exec_()) # 이벤트 루프 실행


if __name__ == '__main__':
    main() # main 함수 실행