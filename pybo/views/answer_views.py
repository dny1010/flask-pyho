from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, g, flash

from pybo import db
from pybo.forms import AnswerForm
from pybo.models import Question, Answer
from pybo.views.auth_views import login_required

bp = Blueprint('answer', __name__, url_prefix='/answer')

@bp.route('/create/<int:question_id>', methods=['POST']) # methods=('POST') 이렇게 써도 상관 X
@login_required
def create(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    if form.validate_on_submit():
        content = request.form['content'] # 폼태그에서 내용 받아온 것

        # 1번 방식
        # answer = Answer(content=content, create_date=datetime.now()) # create 함수
        # question.answer_set.append(answer) # 역으로 append해서 답변 등록

        # 2번 방식
        answer = Answer(question=question, content=content, create_date=datetime.now(), user_id=g.user.id)
        db.session.add(answer)

        db.session.commit()
        return redirect(url_for('question.detail', question_id=question_id))
    return render_template('question/question_detail.html', question=question, form=form) # AnswerForm

@bp.route('/modify/<int:answer_id>', methods=['GET', 'POST']) # 수정페이지로 넘어가야하니까 get post 둘 다 사용
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if g.user != answer.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=answer.question_id))
    if request.method == 'POST':
        form = AnswerForm()
        if form.validate_on_submit():
            form.populate_obj(answer)
            answer.modify_date = datetime.now()
            db.session.commit()
            return redirect(url_for('question.detail', question_id=answer.question_id))
    else: # GET 요청
            form = AnswerForm(obj=answer)
    return render_template('answer/answer_form.html', form=form)

@bp.route('/delete/<int:answer_id>')
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if g.user != answer.user:
        flash('삭제권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=answer.question.id))
    else:
        db.session.delete(answer)
        db.session.commit()
    return redirect(url_for('question._list'))