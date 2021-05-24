# 웹페이지 html 데이터 가져올때 사용하는 함수
import requests
from typing import Dict, Tuple


def request(url: str) -> Tuple[str, bool, Dict]:

    # Error 로그를 생성하는 dict형태의 변수
    # 기본적으로 정상 메시지를 담고 있음
    error_log: dict = {
        'case': 'OK',
        'msg': 'Sucess',
        'httpStatusCode': '200'
    }

    # request를 수행하는 과정에서 에러가 발생하는 지 확인함
    # dict타입의 error_log변수와 False를 Tuple형식으로 리턴
    try:
        response = requests.get(url)
        status_code: str = response.status_code
        html_text: str = response.text

    # HTTP에러가 발생 했을 경우에 error로그를 생성
    # dict타입의 error_log변수와 False를 Tuple형식으로 리턴
    except requests.exceptions.HTTPError as e:
        error_log['case'] = 'HTTPError'
        error_log['msg'] = e
        error_log['httpStatusCode'] = status_code
        return "", error_log, False

    # 커넥션 관련 에러가 발생했을 경우에 error로그를 생성
    # dict타입의 error_log변수와 False를 Tuple형식으로 리턴
    except requests.exceptions.ConnectionError as e:
        error_log['case'] = 'ConnectionError'
        error_log['msg'] = e
        error_log['httpStatusCode'] = None
        return "", error_log, False

    # 그밖의 에러가 requests 관련 오류가 발생했을 경우
    # dict타입의 error_log변수와 False를 Tuple형식으로 리턴
    except requests.exceptions.RequestException as e:
        error_log['case'] = 'OtherError'
        error_log['msg'] = e
        error_log['httpStatusCode'] = None
        return "", error_log, False

    # 문제 없는 경우 str타입의 html_text변수와 True를 Tuple형식으로 리턴
    return html_text, True, error_log
