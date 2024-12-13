# Upbit Altcoin index
## Requirements
`pip install pyjwt requests`

## Usage
- `settings.json`에 매매에 사용할 총 시드 input_krw와 몇 종목 매수할 것인지 num_of_alts 설정
-  **[Deprecated]** `python3 buy_all.py` 실행하여 씨뿌리기 
- `python3 buy_all_concurrent.py`: 실행하여 씨뿌리기 (n개 주문 동시에 넣기)
- `python3 unlock_all_and_buy.py` 체결 안 된 주문 취소 후 재매수
- **[Deprecated]** `python3 clear_all.py` 뿌린 모든 씨앗 회수
    - 여러번 실행하여 체결 안 되어 회수 안 된 씨앗 계속 회수
- `python3 clear_all_concurrent.py` 뿌린 모든 씨앗 회수
    - 여러번 실행하여 체결 안 되어 회수 안 된 씨앗 계속 회수
- `python3 get_current_status.py {pnl}`
    - 보유 알트 pnl 확인, 토탈 pnl 확인
    - 보유 알트 목록 확인
    - 매수/매도 대기 주문 확인 (open orders)

## File descriptions
- `get_data.py`: 데이터 확인용. 실행하면 n개의 티커, 24시간 거래대금, 현재가를 보여줌
- `check_settings.py`: 세팅 및 1회 주문 단가 확인용
- **[Deprecated]** `buy_all.py`: input_krw을 n종목에 배분하여 매수 
- `buy_all_concurrent.py`: input_krw을 n종목에 배분하여 매수 (n개 요청 동시에)
- `unlock_all_and_buy.py`: (매수) 대기 중인 모든 주문 취소 후 재매수
- `get_current_status.py`
    - 보유 알트 목록, 개수 확인
    - 현재 open 매수/매도 주문들 확인
- **[Deprecated]** `clear_all.py`: (매도) 대기 중인 모든 주문 취소 후 전부 매도
- `clear_all_concurrent.py`: (매도) 대기 중인 모든 주문 취소 후 전부 매도 (n개 요청 동시에)
- `alt_list.txt`: 매수한 알트 목록

## etc
- `settings.json`의 `num_of_alts`가 10이라면, "거래 대금" 기준 상위 10개 알트만 매매한다.
- 제외 알트 목록은 `settings.json`에 명시되어 있음.
    - ['KRW-BTC', 'KRW-ETH', 'KRW-SOL', 'KRW-USDT', 'KRW-USDC', 'KRW-CVC', 'KRW-XRP', 'KRW-MOVE', 'KRW-ME', 'KRW-BTG', 'KRW-ETC', 'KRW-BCH'] 등
    - 각자 입맛대로 조절
- `buy_all.py` 실행 후 성공적으로 매수 주문 넣은 알트는 `alt_list.txt`에 기재되며 매도할 때도 이 파일을 참조하여 매도 실행