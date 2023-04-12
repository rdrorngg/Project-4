import joblib
import os
import numpy as np


from flask import Flask, render_template, request

app = Flask(__name__)
model = joblib.load('./rfc_model.pkl')

@app.route('/', methods=['GET', '[POST]'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    category = request.args.get('category')
    type = request.args.get('type')
    goal = request.args.get('goal_amount')
    arr = np.array([[category, type, goal]])
    pred = model.predict(arr)
    return render_template('index.html', pred=pred)

# FLASK_APP=project4_flask flask run

# 카테고리, 타입(REWARD(1), PREORDER(2)), goal_amount
# 카테고리 [ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17] 데이터 부족으로 모임 카테고리를 학습시키지 못함
#['푸드' '홈·리빙' '출판' '베이비·키즈' '스포츠·모빌리티' '패션·잡화' '뷰티' '컬쳐·아티스트' '테크·가전'
# '캐릭터·굿즈' '기부∙캠페인' '레저·아웃도어' '반려동물' '클래스·컨설팅' '후원' '게임·취미' '여행·숙박']