from flask import Blueprint, render_template, redirect, url_for

from pybo.forms import QuestionForm
from pybo.models import Question

# 블루 프린트 : 라우팅 함수를 관리하는 역할
bp = Blueprint('main', __name__, url_prefix='/')
# main = bp의 별칭 # 지금 주소는 https:// ~ /detail 인데 주소를 /question/list 이런식으로 소주제로 묶어서 views 파일을 만들어 분리

@bp.route('/')
def index():
    # question_list=Question.query.order_by(Question.create_date.desc())
    # return render_template('question/question_list.html', question_list=question_list)
    # 블로그 python > 17_파이썬 타입 어노테이션 / @는 데코레이터

    return redirect(url_for('question._list')) # 'question'은 question_views에 bp 별칭 / 빨간 글씨는 flask에 잇는 걸로 클릭

