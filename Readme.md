# 의료 예약 시스템
## 

## 데이터 입력
- 데이터 추출(한글 깨짐 방지)
```commandline
python -Xutf8 ./manage.py dumpdata > data.json
```
- 데이터 입력
- 필요한 경우 간단히 만들어 둔 몇가지 데이터를 DB에 넣을 수 있습니다.
```commandline
python manage.py loaddata data.json
```
- swagger 활용
- 로컬에서 서버 실행 시 http://127.0.0.1:8000/swagger/ 주소에서 API를 실행시켜 볼 수 있습니다.
- 환자, 진료과, 비급여진료항목, 의사 및 영업스케줄 입력 api가 준비되어있습니다.
- 의사 생성 api 같은 경우 영업시간일정까지 포함해서 한번에 입력할 수 있도록 만들어져 있고, 만약 영업시간을 뺴먹었다면 스케줄 생성 api로 따로 추가할 수도 있습니다.
