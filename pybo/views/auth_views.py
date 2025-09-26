# 인증 / 인증 인가
import functools

from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm
from pybo.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 회원가입
@bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() # where절, filter_by 똑같음
        if not user:
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password1.data),
                        # 암호화해서 해시코드로 저장 => 비밀번호 찾기 누르면 재설정이 나오는 이유. 찾아줄 수 없기 때문(관리자도 암호를 모름)
                        email=form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자입니다.')
    return render_template('auth/signup.html', form=form)

# 로그인
@bp.route('/login/', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        errormsg = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            errormsg = '존재하지 않는 사용자입니다.'
        elif not check_password_hash(user.password, form.password.data):
            errormsg = '비밀번호가 올바르지 않습니다.'
        if errormsg is None:
            session.clear()
            session['user_id'] = user.id
            _next = request.args.get('next', '') # request.args = 요청 url에 파라미터
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.index'))
        else:
            flash(errormsg)
    return render_template('auth/login.html', form=form)

# 라우팅 함수보다 먼저 실행하는 함수 (요청처리 들어오기 전에 실행)
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None # 플라스크에서 사용하는 객체 g => 컨텍스트 변수, 요청 -> 응답 과정에서 유효함, 사용자의 정보를 기억
    else:
        g.user= User.query.get(int(user_id)) # user의 정보(id, pw, em ...)을 다 가져와서 g에 저장

# 로그아웃
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index')) # 메인페이지로 돌아가기

# login_required 데코레이터 함수 (로그인을 요구하는 함수)
def login_required(view): # 원래 함수(현재 실행하고 있는 함수)가 view에 들어감
    @functools.wraps(view)
    def wrapped_view(*arg, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else '' # get 방식일 때 에러 나기 전 마지막 위치로 이동
            return redirect(url_for('auth.login', next=_next))
        return view(*arg, **kwargs) # 원래 함수
    return wrapped_view