import os
import cv2
import pathlib
import requests
from datetime import datetime


class ChangeDetection:
    result_prev = []  # 이전 결과를 저장할 리스트

    HOST = 'https://kwangju.pythonanywhere.com'  # 서버 주소
    username = 'admin'  # 사용자명
    password = 'admin'  # 비밀번호
    token = ''  # 인증 토큰
    title = ''  # 알림 제목
    text = ''  # 알림 텍스트

    def __init__(self, names):
        """
        초기화 함수. 'names'에 따라 result_prev 초기화하고
        서버에서 인증 토큰을 가져옵니다.
        """
        # names의 길이에 맞게 result_prev 초기화
        self.result_prev = [0 for i in range(len(names))]

        # 서버에서 인증 토큰 받기
        res = requests.post(self.HOST + '/api-token-auth/', {
            'username': self.username,
            'password': self.password,
        })

        # 요청 실패 시 예외 처리
        res.raise_for_status()

        # 토큰 추출 및 저장
        self.token = res.json()['token']

        # 토큰 출력
        print(self.token)

    def add(self, names, detected_current, save_dir, image):
        """
        객체 상태를 확인하고 변화를 감지하여 알림을 보내는 함수.
        """
        self.title = ''
        self.text = ''
        change_flag = 0  # 변화 감지 플래그
        i = 0

        while i < len(self.result_prev):
            if self.result_prev[i] == 0 and detected_current[i] == 1:
                change_flag = 1
                self.title = names[i]
                self.text += names[i] + ", "
            i += 1

        # 객체 검출 상태 저장
        self.result_prev = detected_current[:]

        # 변화가 감지된 경우 알림 전송
        if change_flag == 1:
            self.send(save_dir, image)

    def send(self, save_dir, image):
        """
        이미지 저장 후 서버로 전송하는 함수.
        """
        now = datetime.now()
        now.isoformat()

        today = datetime.now()

        # 경로 설정 (pathlib를 사용하여 경로 처리)
        save_path = os.getcwd()/save_dir/'detected'/str(today.year)/str(today.month)/str(today.day)
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

        # 파일명 생성
        full_path = save_path/f'{today.hour}-{today.minute}-{today.second}-{today.microsecond}.jpg'

        # 이미지 리사이즈 후 저장
        dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(full_path), dst)

        # 서버로 전송할 데이터 준비
        headers = {
            'Authorization': 'JWT ' + self.token,
            'Accept': 'application/json'
        }
        data = {
            'author': 'KJO',
            'title': self.title,
            'text': self.text,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }

        # 이미지 파일 열기
        file = {'image': open(full_path, 'rb')}
        res = requests.post(self.HOST + '/api_root/Post/', data=data, files=file, headers=headers)
        # 응답 출력
        print(res)