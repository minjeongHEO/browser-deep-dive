#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""
Chapter 2: 브라우저 GUI 구현
Python 3.12 이상 필요 (macOS 26 호환성)
"""

import tkinter
import sys
import os
import socket

# chapter-01의 URL 클래스 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'chapter-01'))
from browser import URL


WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

def lex(body):
  """HTML 본문에서 태그를 제거하고 텍스트만 추출"""
  text = ""
  in_tag = False
  for c in body:
    if c == "<":
      in_tag = True
    elif c == ">":
      in_tag = False
    elif not in_tag:
      text += c
  return text

def layout(text):
  """텍스트를 화면에 표시할 위치와 문자로 변환 (display_list)"""
  display_list = []  # 화면에 그려야 할 요소의 집합
  cursor_x, cursor_y = HSTEP, VSTEP
  
  for c in text:
    display_list.append((cursor_x, cursor_y, c))
    cursor_x += HSTEP
    
    if cursor_x > WIDTH - HSTEP:
      cursor_y += VSTEP
      cursor_x = HSTEP
  
  return display_list

class Browser:
  def __init__(self):
    self.window = tkinter.Tk() # tkinter.Tk() : 데스크톱 환경에 창을 만들도록 요청 후 그 창에 무언가를 그리는데 사용할 객체를 반환
    self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
    self.canvas.pack()
    self.scroll = 0
    self.display_list = []
    
    # 키 바인딩: 화살표 키로 스크롤
    self.window.bind("<Down>", self.scroll_down)
    self.window.bind("<Up>", self.scroll_up)
    # 마우스 휠 스크롤 (macOS와 Windows 호환)
    self.window.bind("<MouseWheel>", self.scroll_wheel)  # Windows
    self.window.bind("<Button-4>", self.scroll_up)  # macOS 위로
    self.window.bind("<Button-5>", self.scroll_down)  # macOS 아래로
    self.canvas.bind("<MouseWheel>", self.scroll_wheel)  # Canvas에서도 마우스 휠
    self.canvas.bind("<Button-4>", self.scroll_up)  # macOS 위로
    self.canvas.bind("<Button-5>", self.scroll_down)  # macOS 아래로
    self.window.focus_set()  # 키 입력을 받기 위해 포커스 설정
    
  def scroll_down(self, event):
    """아래로 스크롤"""
    self.scroll += SCROLL_STEP
    self.draw()
    
  def scroll_up(self, event):
    """위로 스크롤"""
    self.scroll = max(0, self.scroll - SCROLL_STEP)
    self.draw()
    
  def scroll_wheel(self, event):
    """마우스 휠로 스크롤"""
    if event.delta > 0:
      self.scroll_up(event)
    else:
      self.scroll_down(event)
    
  def draw(self):
    """display_list를 화면에 그리기 (스크롤 오프셋 적용) - 16ms 프레임 버짓 최적화"""
    self.canvas.delete("all")
    
    # 화면에 보이는 범위만 빠르게 필터링 (성능 최적화)
    # y 좌표 범위 계산: scroll - VSTEP ~ scroll + HEIGHT + VSTEP
    min_y = self.scroll - VSTEP
    max_y = self.scroll + HEIGHT + VSTEP
    
    # 배치 렌더링을 위한 리스트
    text_items = []
    
    for x, y, c in self.display_list:
      # 빠른 범위 체크 (y 좌표만 확인)
      if y < min_y or y > max_y:
        continue
      
      # 스크롤 오프셋 적용
      display_y = y - self.scroll
      
      # 화면 범위 내에 있는 문자만 추가
      if -VSTEP <= display_y <= HEIGHT:
        text_items.append((x, display_y, c))
    
    # 배치로 한 번에 그리기 (성능 최적화)
    if text_items:
      for x, display_y, c in text_items:
        self.canvas.create_text(x, display_y, text=c)

  def load(self, url):
    """URL을 로드하고 렌더링. 성공하면 True, 실패하면 False 반환"""
    try:
      # 로딩 메시지 표시
      self.canvas.delete("all")
      self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Loading...")
      self.window.update()
      print(f"Requesting URL: {url.host}:{url.port}{url.path}")
      
      try:
        body = url.request()
      except socket.timeout:
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Connection timeout", fill="red")
        print("Connection timeout")
        return False
      except socket.gaierror as e:
        self.canvas.delete("all")
        error_msg = f"DNS resolution failed: {str(e)}"
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text=error_msg, fill="red")
        print(f"DNS error: {e}")
        return False
      except ConnectionRefusedError:
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Connection refused", fill="red")
        print("Connection refused")
        return False
      except Exception as e:
        self.canvas.delete("all")
        error_msg = f"Connection error: {str(e)}"
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text=error_msg, fill="red")
        print(f"Connection error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
      if not body:
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="No content received")
        return False
      
      # HTML에서 텍스트 추출 (최적화)
      print("Extracting text from HTML...")
      self.canvas.delete("all")
      self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Extracting text...")
      self.window.update()
      
      text = lex(body)
      if not text:
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="No text content found")
        return False
      
      print(f"Text extracted: {len(text)} characters")
      
      # 텍스트를 display_list로 변환 (점진적 렌더링)
      print("Layouting text...")
      self.canvas.delete("all")
      self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Layouting text...")
      self.window.update()
      
      self.display_list = layout(text)
      self.scroll = 0  # 스크롤 위치 초기화
      
      print(f"Rendering {len(self.display_list)} display items...")
      self.draw()
      self.window.update()  # 즉시 화면 업데이트
      
      print(f"Successfully rendered {len(text)} characters, {len(self.display_list)} display items")
      return True
      
    except Exception as e:
      # 에러 메시지 표시
      self.canvas.delete("all")
      error_msg = f"Error loading page: {str(e)}"
      self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text=error_msg, fill="red")
      print(f"Error in load: {e}")
      import traceback
      traceback.print_exc()
      return False

if __name__ == "__main__":
  try:
    browser = Browser()
    # 창을 먼저 표시 (URL 요청 전에 창이 보이도록)
    browser.window.update()
    
    if len(sys.argv) > 1:
      url_string = sys.argv[1]
      print(f"Loading URL: {url_string}")
      url = URL(url_string)
    else:
      url_string = "http://example.org/index.html"
      print(f"Loading default URL: {url_string}")
      url = URL(url_string)
    
    print("Requesting page...")
    success = browser.load(url)
    if success:
      print("Page loaded successfully. Starting mainloop...")
      print("Use arrow keys or mouse wheel to scroll")
    else:
      print("Failed to load page. Starting mainloop anyway...")
    tkinter.mainloop()
  except Exception as e:
    print(f"Fatal error: {e}")
    import traceback
    traceback.print_exc()

# http://browser.engineering/examples/xiyouji.html