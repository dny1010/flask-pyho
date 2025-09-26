import os
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, g, flash, current_app
from werkzeug.utils import secure_filename

from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.models import Question, Answer, User
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')  # question이 별칭

@bp.route('/list/')  # question으로 간 다음 하위인 list로 감
def _list():  # list는 예약어여서 앞에 _붙여줌
    page = request.args.get('page', default=1, type=int)  # 페이지 / request => url(question/list/) 가져와서 뒤에 페이지 파라미터 추가
    kw = request.args.get('kw', default='', type=str)  # 검색 키워드
    question_list = Question.query.order_by(Question.create_date.desc())
    if kw:
        search = f'%%{kw}%%'
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list.join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()
    question_list = question_list.paginate(page=page, per_page=10)  # 한 페이지에 보여야 할 게시글 수
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw)

@bp.route('/detail/<int:question_id>/') # <url parameter> -> question 아이디만 받아서 원하는 부분만 보여줌 / 문자열로 고정하면 수정이 어려움
def detail(question_id):
    form = AnswerForm() # 질문 상세 템플릿에 답변 폼 추가
    question = Question.query.get_or_404(question_id)  # get 말고 get_or_404 쓰면 값이 없을 때 404 page를 보여줌 / ctrl누르고 클릭하면 함수 정의 보여줌
    return render_template('question/question_detail.html', question=question, form=form)

@bp.route('/create/', methods=['GET', 'POST']) # POST 방식 = 사용자에게 입력받은 값을 DB에 넣어줌
@login_required
def create():
    form = QuestionForm() # 사용자가 입력한 내용이 튜플로 들어감
    if request.method =='POST' and form.validate_on_submit():
        # 폼에서 받은 이미지 파일 처리
        image_file = form.image.data
        image_path = None
        if image_file:
            # 저장 경로 설정 : 오늘 날짜 폴더생성
            today = datetime.now().strftime('%Y%m%d')
            upload_folder = os.path.join(current_app.root_path, 'static/photo', today) # current ~ path 까지가 pybo
            os.makedirs(upload_folder, exist_ok=True)
            # 파일 저장
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)

            # DB에는 파일 저장 경로만 넣어줌(static 기준으로 상대경로)
            image_path = f'photo/{today}/{filename}'

        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(),
                            user_id=g.user.id, image_path=image_path) # Models.py
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form) # 괄호 안에 form은 form 모듈

@bp.route('/modify/<int:question_id>', methods=['GET', 'POST']) # 수정으로 이동할 때 get, 수정한 내용을 저장할 때 post
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id) # 질문 조회
    if g.user != question.user:
        flash('수정권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':  # POST 요청할 때
        form =QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question) # 폼 모듈에서 수정된 내용을 알아서 보내주는 함수 populate_obj
            question.modify_date = datetime.now() # 여기서 업데이트 동작을 해서 session.add는 안해도 됨
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:  # GET 요청할 때
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)

@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=question_id))
    else:
        db.session.delete(question)
        db.session.commit()
    return redirect(url_for('question._list'))
