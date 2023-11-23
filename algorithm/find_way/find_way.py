import cv2
import numpy as np
import json
import os
from queue import Queue
from PIL import ImageFont, ImageDraw, Image
def myPutText(src, text, pos, font_size, font_color) :
    img_pil = Image.fromarray(src)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype("C:/Windows/Fonts/batang.ttc", font_size)
    draw.text(pos, text, font=font, fill= font_color)
    return np.array(img_pil)
startPoint,startfloor = 1,1
endPoint,endfloor = 63,5
semipoint = startPoint
ele_up = 0
dx = [1, 0, -1, 0,1,1,-1,-1]
dy = [0, 1, 0, -1,1,-1,1,-1]
# JSON 파일들의 기본 경로
base_path = "algorithm/result/"
# 파일명들을 나타내는 리스트
file_names = [("data_01.json","way.png"), ("data_02.json","way.png"), ("data_03.json","way.png"), ("data_04.json","way.png"), ("data_05.json","way05.png")]

# 파일 경로 생성 및 처리를 위한 for문
for file_name in file_names:
    file_path = os.path.join(base_path, file_name[0])
    mask_path = os.path.join(base_path, file_name[1])
    floor = int(file_name[0][5:7])
    if ele_up:
        if floor != ele_up:
            continue
    # JSON 파일에서 데이터 읽기
    with open(file_path, "r") as file:
        data = json.load(file)

    # 마스크 이미지의 크기 설정
    elevator = []
    board = [[0] * 1025 for _ in range(1025)]
    next = [[[0,0] for _ in range(1025)] for _ in range(1025)]
    # JSON 파일의 데이터를 사용하여 각 픽셀 위치에 점 찍기
    height, width = 1024, 1024  # 실제 이미지 크기에 맞게 조정해야 합니다.
    mask = np.zeros((height, width,3), dtype=np.uint8)
    mask = myPutText(mask, file_name[0][:4]+" 건물 "+str(floor)+" 층입니다", (700, 20), 30, (255,0,0))
    for group in data:
        sum_x, sum_y, div = 0, 0, 0
        id = group["id"]
        caption = group["caption"]
        if caption == "엘리베이터":
            elevator.append(id)
        for pixel in group["pixels"]:
            x, y = pixel["x"], pixel["y"]
            if id != semipoint:
                board[y][x] = id
            if id != -2:
                mask[y, x] = 255
            sum_x += x
            sum_y += y
            div+=1
        if id != -2:
            mask = myPutText(mask, caption, (sum_x//div-7, sum_y//div-5), 11, (0,255,0))
        if id == semipoint:
            st_Averx, st_Avery = sum_x//div, sum_y//div

    print(st_Averx, st_Avery)
    dx = (1, 0, -1, 0,1,1,-1,-1)
    dy = (0, 1, 0, -1,1,-1,1,-1)

    Q = Queue()
    Q.put((st_Averx, st_Avery))
    board[st_Averx][st_Avery]=-1
    escape=True

    while escape:
        cur = Q.get()
        for dir in range(8):
            nx = cur[0] + dx[dir]
            ny = cur[1] + dy[dir]
            # print(nx, ny, board[ny][nx])
            if (floor==endfloor and board[ny][nx]==endPoint) or (floor != endfloor and board[ny][nx] in elevator):
                endX, endY = nx,ny
                escape=False
                next[ny][nx] = (cur[0], cur[1])
                semipoint = board[ny][nx]
                ele_up = endfloor
                break
            elif 0<=nx<=1024 and 0<=ny<=1024 and board[ny][nx] == 0:
                Q.put((nx, ny))
                next[ny][nx] = (cur[0], cur[1])
                board[ny][nx]=-1


    path = []
    st = (endX, endY)
    while st != (st_Averx, st_Avery):
        path.append(st)
        mask[st[1],st[0]] = [0, 0, 255]
        st = next[st[1]][st[0]]
    path.append(st)
    mask[st[1],st[0]] = [0, 0, 255]
    mask_file_path =base_path+"way_"+file_name[0][5:7]+".png"
    cv2.imwrite(mask_file_path, mask)
