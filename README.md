# Upbit Altcoin index
## Requirements
`pip install pyjwt requests`

## File descriptions
- `get_data.py`: 데이터 확인용 실행하면 n개의 티커, 24시간 거래대금, 현재가를 보여줌
- `check_settings.py`: 세팅 및 1회 주문 단가 확인용
- `buy_all.py`: input_krw을 n종목에 배분하여 매수
- `clear_all.py`: 매수 대기 중인 모든 주문 취소 후 전부 매도
- `alt_list.txt`: 매수한 알트 목록

## Usage
- `settings.json`에 매매에 사용할 총 시드 input_krw와 몇 종목 매수할 것인지 num_of_alts 설정
- `python3 buy_all.py` 실행하여 씨뿌리기
- `python3 clear_all.py` 뿌린 모든 씨앗 회수

## ETC
- `settings.json`의 `num_of_alts`가 10이라면, "거래 대금" 기준 상위 10개 알트만 매매한다.
- 제외 알트 목록은 `get_data.py`에 명시되어 있음
    - ['KRW-BTC', 'KRW-ETH', 'KRW-SOL', 'KRW-USDT', 'KRW-USDC', 'KRW-CVC']
- `buy_all.py` 실행 후 매수한 알트는 `alt_list.txt`에 기재되며 매도할 때도 이 파일을 참조하여 매도 실행