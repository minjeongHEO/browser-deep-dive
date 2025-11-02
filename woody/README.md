## 1. 서버의 연결

1. url이 주어지면 브라우저는 웹페이지를 다운로드
2. 브라우저는 운영체제에게 호스트 이름에 해당하는 서버와 연결을 요청함
3. 운영체제는 DNS(DomainNameSystem)서버와 통신하여 example.org와 같은 호스트 이름을 93.184.216.34와 같은 IP주소로 변환함
4. 운영체제는 라우팅 테이블을 이용해 해당 IP주소와 통신하기에 가장 적합한 장치를 결정함
5. 운영체제는 장치 드라이벌르 사용하여 신호를 보냄
6. 라우터는 신호를 감지하고 유저의 메세지를 전달하기 위한 최적의 다음 라우터에 전송함
7. 일련의 라우터를 거니 뒤에 목적지 도착
8. 메세지가 서버에 도착하면 해당 서버와의 연결 성공

## 2. 정보 요청하기

연결 후 브라우저는 `index.html`처럼 호스트 이름 뒤에 오는 URL의 경로에 해당하는 정보를 요청함

## 3. 서버의 응답

[HTTP 버전] [응답 코드] [응답 설명]
HTTP/1.0 200 OK

## 4. 파이썬을 통한 텔넷

1. URL 파싱하여 호스트 이름과 경로를 추출
2. 소켓을 생성
3. 요청을 보내기
4. 응답을 수신

## 5. HTTP 스킴 지원 구현

### 구현된 기능

- **URL 클래스**: HTTP URL을 파싱하여 호스트, 경로, 스킴을 분리
- **HTTP 요청**: 소켓을 사용하여 HTTP/1.0 GET 요청 전송
- **응답 처리**: HTTP 응답 헤더와 본문을 파싱
- **HTML 렌더링**: HTML 태그를 제거하고 텍스트만 출력

### 주요 컴포넌트

#### URL 클래스

```python
class URL:
    def __init__(self, url):  # URL 파싱
    def request(self):        # HTTP 요청 전송
```

#### 핵심 함수

- `load(url)`: URL을 로드하고 렌더링
- `show(body)`: HTML 본문에서 태그 제거 후 텍스트 출력

### 사용법

```bash
python3 browser.py http://example.org/
```

### 지원 기능

- ✅ HTTP 스킴 지원
- ✅ HTTPS 스킴 지원 (SSL/TLS 암호화)
- ✅ 기본적인 HTML 태그 제거
- ✅ Content-Length 헤더 처리
- ✅ 사용자 지정 포트 번호 지원
- ❌ Transfer-Encoding (미지원)
- ❌ Content-Encoding (미지원)

## 6. HTTPS 스킴 지원 추가

### 새로 추가된 기능

- **SSL/TLS 암호화**: `ssl` 모듈을 사용한 HTTPS 연결 지원
- **포트 자동 감지**: HTTP(80), HTTPS(443) 포트 자동 설정
- **사용자 지정 포트**: URL에 포트 번호가 포함된 경우 자동 처리

### 기술적 구현

```python
# SSL/TLS 연결 처리
if self.scheme == "https":
    ctx = ssl.create_default_context()
    s = ctx.wrap_socket(s, server_hostname=self.host)

# 포트 자동 감지
if self.scheme == "https":
    self.port = 443
elif self.scheme == "http":
    self.port = 80
```

### 테스트 예제

```bash
# HTTP 사이트 테스트
python3 browser.py http://example.org/

# HTTPS 사이트 테스트
python3 browser.py https://example.org/

# 사용자 지정 포트 테스트
python3 browser.py http://localhost:8000/
```

## 7. HTTP/1.1 프로토콜 지원 및 표준 헤더 추가

### 새로 추가된 기능

- **HTTP/1.1 프로토콜**: HTTP/1.0에서 HTTP/1.1로 업그레이드
- **표준 HTTP 헤더**: Host, Connection, User-Agent 헤더 추가
- **브라우저 식별**: "Woody-Browser/1.0" User-Agent로 브라우저 식별

### 기술적 구현

```python
# HTTP/1.1 요청 헤더 구성
request = "GET {} HTTP/1.1\r\n".format(self.path)
request += "Host: {}\r\n".format(self.host)
request += "Connection: close\r\n"
request += "User-Agent: Woody-Browser/1.0\r\n"
```

### HTTP 헤더 설명

- **Host 헤더**: 가상 호스팅 지원, 서버가 요청 대상 도메인 식별
- **Connection: close**: 요청 후 연결 즉시 종료 (keep-alive 비활성화)

  Connection 일반 헤더는 현재의 전송이 완료된 후 네트워크 접속을 유지할지 말지를 제어합니다. 만약 전송된 값이 keep-alive면, 연결은 지속되고 끊기지 않으며, 동일한 서버에 대한 후속 요청을 수행할 수 있습니다.

  경고 : Connection 와 Keep-Alive 같은 연결-지정(Connection-specific) 헤더 필드들은 HTTP/2.에서 금지되었습니다.
  크롬과 Firefox는 HTTP/2 응답에서 그들을 무시하지만, Safari는 HTTP/2 규격 요건에 따라 해당 필드가 포함된 응답은 처리하지 않습니다.

- **User-Agent**: 서버가 클라이언트 브라우저를 식별할 수 있도록 함

### 요청 예시

```http
GET / HTTP/1.1
Host: example.org
Connection: close
User-Agent: Woody-Browser/1.0

```

## 8. File 스킴 지원 및 로컬 파일 처리

### 새로 추가된 기능

- **File 스킴 지원**: `file://` URL을 통한 로컬 파일 접근
- **로컬 파일 읽기**: 파일 시스템에서 직접 파일 내용 읽기
- **기본 파일 로드**: URL 없이 실행 시 기본 로컬 파일 자동 로드
- **에러 처리**: 파일이 없거나 읽기 오류 시 적절한 메시지 출력

### 기술적 구현

```python
# File 스킴 처리
if self.scheme == "file":
    try:
        with open(self.path, "r", encoding="utf8") as f:
            return f.read()
    except FileNotFoundError:
        return "File not found: " + self.path
    except Exception as e:
        return "Error reading file: " + str(e)

# 기본 파일 로드
if len(sys.argv) > 1:
    load(URL(sys.argv[1]))
else:
    load(URL("file:///path/to/default/file.html"))
```

### 사용법

```bash
# 로컬 파일 직접 지정
python3 browser.py file:///path/to/file.html

# URL 없이 실행 (기본 파일 로드)
python3 browser.py

# HTTP/HTTPS URL (기존 기능)
python3 browser.py http://example.org/
```

### 지원하는 스킴

- ✅ **http**: HTTP 프로토콜 지원
- ✅ **https**: HTTPS 프로토콜 지원 (SSL/TLS)
- ✅ **file**: 로컬 파일 시스템 접근
- ✅ **data**: 인라인 데이터 URL 지원

## 9. Data 스킴 지원 및 인라인 데이터 처리

### 새로 추가된 기능

- **Data 스킴 지원**: `data:` URL을 통한 인라인 데이터 처리
- **MIME 타입 인식**: `data:text/html,content` 형식 지원
- **직접 데이터 반환**: 네트워크 요청 없이 URL에 포함된 데이터 직접 사용

### 기술적 구현

```python
# Data URL 파싱
if url.startswith("data:"):
    self.scheme = "data"
    url = url[5:]  # "data:" 제거
    if "," in url:
        self.mime_type, self.data = url.split(",", 1)
    else:
        self.mime_type = "text/plain"
        self.data = url

# Data 요청 처리
if self.scheme == "data":
    return self.data
```

### 사용법

```bash
# 텍스트 데이터
python3 browser.py "data:text/plain,Hello World!"

# HTML 데이터
python3 browser.py "data:text/html,<h1>Hello World!</h1>"

# MIME 타입 없이 (기본값: text/plain)
python3 browser.py "data:,Simple text"
```

### Data URL 형식

- `data:[<mediatype>][;base64],<data>`
- 예: `data:text/html,<h1>Hello</h1>`
- 예: `data:text/plain,Hello World!`
- 예: `data:,Simple text` (MIME 타입 생략 시 text/plain)

## 10. HTML 엔티티 처리 기능 추가

### 새로 추가된 기능

- **HTML 엔티티 디코딩**: `&lt;`, `&gt;` 등의 HTML 엔티티를 실제 문자로 변환
- **사전 기반 변환**: 딕셔너리를 사용한 효율적인 엔티티 처리
- **태그 제거 전 처리**: HTML 엔티티를 먼저 변환한 후 태그 제거

### 기술적 구현

```python
def decode_html_entities(text):
    entities = {
        '&lt;': '<',
        '&gt;': '>',
    }

    for entity, char in entities.items():
        text = text.replace(entity, char)
    return text

def show(body):
    # HTML 엔티티를 먼저 디코딩
    body = decode_html_entities(body)

    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")
```

### 지원하는 HTML 엔티티

- `&lt;` → `<` (Less Than)
- `&gt;` → `>` (Greater Than)

### 사용법 및 예시

```bash
# HTML 엔티티가 포함된 데이터 URL
python3 browser.py "data:text/html,&lt;div&gt;Hello World!&lt;/div&gt;"
# 출력: Hello World!

# 실제 HTML과 동일한 결과
python3 browser.py "data:text/html,<div>Hello World!</div>"
# 출력: Hello World!
```

### 처리 순서

1. **HTML 엔티티 디코딩**: `&lt;` → `<`, `&gt;` → `>`
2. **HTML 태그 제거**: `<div>`, `</div>` 등 제거
3. **텍스트 출력**: 순수 텍스트만 출력

## 11. View-Source 스킴 지원 및 HTML 소스 코드 표시

### 새로 추가된 기능

- **View-Source 스킴 지원**: `view-source:` URL을 통한 HTML 소스 코드 직접 표시
- **소스 코드 보기**: 페이지를 렌더링하지 않고 원본 HTML 소스 코드 출력
- **중첩 URL 처리**: view-source 내부의 실제 URL을 처리하는 기능

### 기술적 구현

```python
# View-Source URL 파싱
elif url.startswith("view-source:"):
    self.scheme = "view-source"
    self.target_url = url[12:]  # "view-source:" 제거
    # 내부적으로 실제 URL 객체 생성
    self.inner_url = URL(self.target_url)

# View-Source 요청 처리
if self.scheme == "view-source":
    return self.inner_url.request()

# 렌더링 방식 결정
def load(url):
    body = url.request()
    if url.scheme == "view-source":
        print(body)  # 소스 코드 그대로 출력
    else:
        show(body)   # 일반 렌더링 (태그 제거)
```

### 사용법 및 예시

```bash
# HTML 소스 코드 보기
python3 browser.py "view-source:http://example.org/"
# 출력: <!doctype html><html>...</html>

# 일반 렌더링과 비교
python3 browser.py "http://example.org/"
# 출력: Example Domain (태그 제거된 텍스트)

# Data URL의 소스 코드 보기
python3 browser.py "view-source:data:text/html,<h1>Hello</h1>"
# 출력: <h1>Hello</h1>
```

### 지원하는 스킴 (업데이트)

- ✅ **http**: HTTP 프로토콜 지원
- ✅ **https**: HTTPS 프로토콜 지원 (SSL/TLS)
- ✅ **file**: 로컬 파일 시스템 접근
- ✅ **data**: 인라인 데이터 URL 지원
- ✅ **view-source**: HTML 소스 코드 직접 표시

## 12. 코드 리팩토링 및 구조 개선

### 리팩토링 목표

- **가독성 향상**: 긴 메서드를 작은 단위로 분리
- **유지보수성 개선**: 각 기능별로 독립적인 메서드 구성
- **코드 재사용성**: 공통 로직을 별도 메서드로 분리

### 리팩토링된 구조

#### URL 클래스 메서드 분리

```python
class URL:
    def __init__(self, url):
        # 스킴별 파싱 메서드 호출
        if url.startswith("data:"):
            self._parse_data_url(url)
        elif url.startswith("view-source:"):
            self._parse_view_source_url(url)
        else:
            self._parse_standard_url(url)

    def request(self):
        # 스킴별 요청 처리 메서드 호출
        if self.scheme == "data":
            return self._request_data()
        elif self.scheme == "view-source":
            return self._request_view_source()
        elif self.scheme == "file":
            return self._request_file()
        else:
            return self._request_http()
```

#### 분리된 메서드들

- **파싱 메서드**: `_parse_data_url()`, `_parse_view_source_url()`, `_parse_standard_url()`
- **요청 메서드**: `_request_data()`, `_request_view_source()`, `_request_file()`, `_request_http()`

### 리팩토링 효과

- **가독성**: 각 메서드가 단일 책임을 가짐
- **테스트 용이성**: 개별 메서드 단위 테스트 가능
- **확장성**: 새로운 스킴 추가 시 해당 메서드만 구현하면 됨
- **디버깅**: 문제 발생 시 특정 메서드만 확인하면 됨

## 13. HTTP 연결 재사용 (Keep-Alive) 구현

### 새로 추가된 기능

- **연결 재사용**: 같은 서버에 대한 반복 요청 시 소켓 연결 유지
- **성능 향상**: 연결 설정 오버헤드 제거로 요청 속도 향상
- **연결 관리**: ConnectionManager 클래스로 소켓 연결 생명주기 관리
- **자동 정리**: 프로그램 종료 시 모든 연결 자동 해제

### 기술적 구현

```python
class ConnectionManager:
    def __init__(self):
        self.connections = {}  # (host, port) -> socket 매핑

    def get_connection(self, host, port, scheme):
        # 기존 연결 반환 또는 새 연결 생성
        if key in self.connections:
            return self.connections[key]
        # 새 연결 생성 및 캐시에 저장
        s = socket.socket(...)
        self.connections[key] = s
        return s
```

### HTTP 요청 변경사항

```python
# 이전: Connection: close 헤더 전송
request += "Connection: close\r\n"

# 이후: Connection: close 헤더 제거 (keep-alive 기본값)
# request += "Connection: close\r\n"  # 제거됨
```

### 연결 재사용 동작 방식

1. **첫 번째 요청**: 새 소켓 연결 생성 및 캐시에 저장
2. **후속 요청**: 캐시된 소켓 연결 재사용
3. **Content-Length 처리**: 정확한 바이트 수만 읽고 연결 유지
4. **프로그램 종료**: 모든 연결 자동 정리

### 성능 향상 효과

- **연결 설정 시간 절약**: TCP 핸드셰이크 생략
- **SSL/TLS 재협상 생략**: HTTPS 연결 재사용 시 암호화 설정 유지
- **서버 리소스 절약**: 서버 측에서도 연결 재사용 가능
- **네트워크 효율성**: 연결 오버헤드 최소화

### 사용법 및 테스트

```bash
# 같은 서버에 여러 요청 (연결 재사용)
python3 browser.py "http://example.org/"
python3 browser.py "http://example.org/"  # 연결 재사용
python3 browser.py "http://example.org/"  # 연결 재사용

# 다른 서버 요청 (새 연결 생성)
python3 browser.py "http://httpbin.org/get"
```

### 연결 관리 특징

- **자동 관리**: 개발자가 직접 연결을 관리할 필요 없음
- **메모리 효율**: 사용하지 않는 연결은 자동으로 정리
- **안전성**: 프로그램 종료 시 모든 연결 확실히 해제
- **확장성**: 여러 서버에 대한 동시 연결 지원
