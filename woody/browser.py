import socket
import ssl

class ConnectionManager:
  """소켓 연결을 관리하고 재사용하는 클래스"""
  def __init__(self):
    self.connections = {}  # (host, port) -> socket 매핑

  def get_connection(self, host, port, scheme):
    """기존 연결을 반환하거나 새 연결을 생성"""
    key = (host, port)
    
    if key in self.connections:
      return self.connections[key]
    
    # 새 연결 생성
    s = socket.socket(
      family=socket.AF_INET,
      type=socket.SOCK_STREAM,
      proto=socket.IPPROTO_TCP
    )
    s.connect((host, port))
    
    if scheme == "https":
      ctx = ssl.create_default_context()
      s = ctx.wrap_socket(s, server_hostname=host)
    
    self.connections[key] = s
    return s

  def close_connection(self, host, port):
    """특정 연결을 닫고 캐시에서 제거"""
    key = (host, port)
    if key in self.connections:
      self.connections[key].close()
      del self.connections[key]

  def close_all(self):
    """모든 연결을 닫음"""
    for s in self.connections.values():
      s.close()
    self.connections.clear()

# 전역 연결 관리자
connection_manager = ConnectionManager()

# =======================================================

def decode_html_entities(text):
# HTML 엔티티를 실제 문자로 변환
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
      
def load(url):
  body = url.request()
  if url.scheme == "view-source":
    # view-source: HTML 소스 코드를 그대로 출력 (렌더링하지 않음)
    print(body)
  else:
    # 일반적인 렌더링 (HTML 태그 제거)
    show(body)

class URL:
  # 파이썬의 메서드에는 항상 self 매개변수가 있어야 함
  def __init__(self, url):
    if url.startswith("data:"):
      self._parse_data_url(url)
    elif url.startswith("view-source:"):
      self._parse_view_source_url(url)
    else:
      self._parse_standard_url(url)

  def _parse_data_url(self, url):
    """data: URL 파싱"""
    self.scheme = "data"
    url = url[5:]  # "data:" 제거
    if "," in url:
      self.mime_type, self.data = url.split(",", 1)
      if not self.mime_type:
        self.mime_type = "text/plain"
    else:
      self.mime_type = "text/plain"
      self.data = url
    self.host = None
    self.path = None
    self.port = None

  def _parse_view_source_url(self, url):
    """view-source: URL 파싱"""
    self.scheme = "view-source"
    self.target_url = url[12:]  # "view-source:" 제거
    # 내부적으로 실제 URL 객체 생성
    self.inner_url = URL(self.target_url)
    self.host = self.inner_url.host
    self.path = self.inner_url.path
    self.port = self.inner_url.port

  def _parse_standard_url(self, url):
    """HTTP/HTTPS/FILE URL 파싱"""
    self.scheme, url = url.split("://", 1)
    assert self.scheme in ["http", "https", "file"]

    if '/' not in url:
      url  = url + '/'
    self.host, url = url.split("/", 1)
    self.path = "/" + url

    if self.scheme == "https":
      self.port = 443
    elif self.scheme == "http":
      self.port = 80
    elif self.scheme == "file":
      self.port = None
    # 사용자 지정 포트 번호 처리
    if ":" in self.host:
      self.host, port = self.host.split(":", 1)
      self.port = int(port)

  def request(self):
    """URL 스킴에 따른 요청 처리"""
    if self.scheme == "data":
      return self._request_data()
    elif self.scheme == "view-source":
      return self._request_view_source()
    elif self.scheme == "file":
      return self._request_file()
    else:
      return self._request_http()

  def _request_data(self):
    """data: URL에서 직접 데이터 반환"""
    return self.data

  def _request_view_source(self):
    """view-source: 실제 URL의 소스 코드 반환"""
    return self.inner_url.request()

  def _request_file(self):
    """로컬 파일 읽기"""
    try:
      with open(self.path, "r", encoding="utf8") as f:
        return f.read()
    except FileNotFoundError:
      return "File not found: " + self.path
    except Exception as e:
      return "Error reading file: " + str(e)

  def _request_http(self):
    """HTTP/HTTPS 요청 처리 (연결 재사용)"""
    # 연결 관리자에서 소켓 가져오기 (재사용 또는 새로 생성)
    s = connection_manager.get_connection(self.host, self.port, self.scheme)

    # 서버에 요청 보내기 (Connection: close 제거)
    request = "GET {} HTTP/1.1\r\n".format(self.path)
    request += "Host: {}\r\n".format(self.host)
    request += "User-Agent: Woody-Browser/1.0\r\n"
    request += "\r\n"
    s.send(request.encode("utf8"))

    # 데이터가 도착할 떄마다 수집하는 루프
    response = s.makefile("r", encoding="utf8", newline="\r\n")  # socket.read 대신 파이썬에서는 소켓상태를 확인하는 루프 헬퍼 함수(makefile)를 사용
    statusLine = response.readline()
    version, status, explanation = statusLine.split(" ", 2)

    # 헤더 처리(헤더는 대소문자 구분하지 않기 때문에 소문자로 통일)
    response_headers = {}
    while True:
      line = response.readline()
      if line == "\r\n": break
      header, value = line.split(":", 1)
      response_headers[header.casefold()] = value.strip()

    # 처리하지 못하는 헤더는 무시
    assert "transfer-encoding" not in response_headers
    assert "content-encoding" not in response_headers

    if "content-length" in response_headers:
      content_length = int(response_headers["content-length"])
      body = response.read(content_length)
    else:
      # Content-Length가 없으면 연결을 닫고 모든 데이터 읽기
      body = response.read()
      connection_manager.close_connection(self.host, self.port)

    return body


# http://example.org/index.html
if __name__ == "__main__":
  import sys
  try:
    if len(sys.argv) > 1:
      load(URL(sys.argv[1]))
    else:
      # URL이 없으면 기본 로컬 파일 로드
      load(URL("file:///Users/heominjeong/project/Woody/browser-deep-dive/index.html"))
  finally:
    # 프로그램 종료 시 모든 연결 정리
    connection_manager.close_all()
