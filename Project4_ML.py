#%%

import os
import pandas as pd
import sqlite3
import numpy as np
import psycopg2

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from category_encoders import OrdinalEncoder
from imblearn.over_sampling import SMOTE
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier


#DATABASE_PATH = os.path.join(os.getcwd(), 'wadiz_data.db')

#conn = sqlite3.connect(DATABASE_PATH)

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="1q2w3e4r")

df = pd.read_sql('SELECT * FROM wadiz', conn, index_col=None)

conn.close()



df = df[df['percentage'] != 0]
df['goal_amount'] = round(100 / df['percentage'] * df['amount'], -1)

df_drop = df.drop(columns=['id', 'name', 'percentage', 'amount'])
df_drop = df_drop.dropna()


target = 'goal'
features = df_drop.drop(columns=target).columns.to_list()

train, val = train_test_split(
    df_drop, train_size=0.80, test_size=0.20, stratify=df_drop[target], random_state=2
)

X_train = train[features]
y_train = train[target]
X_val = val[features]
y_val = val[target]

oe = OrdinalEncoder()
X_train_encoded = oe.fit_transform(X_train)
X_val_encoded = oe.transform(X_val)
X_train_sampled, y_train_sampled = SMOTE(random_state=2).fit_resample(X_train_encoded, y_train)

RFC = RandomForestClassifier(random_state=2)

RFC.fit(X_train_sampled, y_train_sampled)

y_pred_proba = RFC.predict_proba(X_val_encoded)[:,1]
print(roc_auc_score(y_val, y_pred_proba))


print(X_train_encoded['category'].unique())
print(X_train['category'].unique())
# 모델 피클링, 포스트맨, 대시보드 완성, 프로젝트 완성 가능하면 데이터베이스 옮기기

# 이 아래는 평소엔 주석처리 하고 모델 저장 때만 사용

#import joblib

#joblib.dump(RFC, './rfc_model.pkl')
#print("Saved model to disk")