from datetime import datetime
from flask import json, render_template, flash, redirect, url_for, request, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, SearchForm, TransactionForm
from app.models import User, Transaction, Holding, Tickers
from app.main import bp
import yfinance as yf

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('main.index', page=transactions.prev_num) \
        if transactions.has_prev else None
    return render_template('index.html', title=('Home'),
                           transactions=transactions.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    form_search = SearchForm(request.form)
    if form_search.validate_on_submit():
        companies = Tickers.query.filter(Tickers.ticker.like('%{}%'.format(form_search.ticker.data)) \
             | Tickers.name.like('%{}%'.format(form_search.ticker.data)))[0:100]
        return render_template('trade.html', title=('Trade'),
                                form=form_search, companies = companies)
    return render_template('trade.html', title=('Trade'),
                            form=form_search)

@bp.route('/ticker/<sticker>', methods=['GET', 'POST'])
@login_required
def ticker(sticker):
    history = yf.Ticker(sticker).history(period='12mo').Close
    maxim = max(history)*1.2
    minim = min(history)*0.8
    x = [x.strftime("%d/%m/%Y") for x in list(history.index)]
    y = list(history)
    zipped = json.dumps([{'x':x, 'y':y} for x,y in zip(x,y)])
    print(minim)
    return render_template('stock.html', title=sticker, x_min=x[0],x_max=x[-1], y_max=maxim, y_min=minim, data=zipped)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    holdings = user.holdings.order_by(Holding.value.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=holdings.next_num) if holdings.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=holdings.prev_num) if holdings.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, holdings=holdings.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=('Edit Profile'),
                           form=form)


"""
form = TransactionForm()
if form.validate_on_submit():
    print(form.buy_or_sell.data)
    transaction = Transaction(ticker=form.ticker.data, price = float(form.price.data), amount = form.amount.data,\
        company = form.company.data, buy_or_sell = form.buy_or_sell.data, client=current_user)
    db.session.add(transaction)
    db.session.commit()
    flash(('Your Transaction has been processed'))
    return redirect(url_for('main.index'))
"""