import os

BASE_DIR=os.path.dirname(__file__) # 프로젝트 경로


SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False # 이벤트 등록

SECRET_KEY = "dev" # CSRF 웹사이트 취약점 공격 방지