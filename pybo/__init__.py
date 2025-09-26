from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

import config

# SQLite 버그 패치를 위한 사용자 규칙 설정
nameing_convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}

# database 등록
# db = SQLAlchemy()
db = SQLAlchemy(metadata=MetaData(naming_convention=nameing_convention))
migrate = Migrate()

def create_app(): # 애플리케이션 팩토리
    app = Flask(__name__)
    app.config.from_object(config)

    #ORM / SQLite 안 쓸 땐 if X migrate.init_app(app,db)만 쓰면 됨
    db.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    from . import models

    # 블루 프린트 등록
    from .views import main_views, question_views, answer_views, auth_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)

    # 템플릿 필터 등록
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app

# flask db init 으로 초기화 해줘야 db를 관리해주는 파일(migrations)가 생김