import sqlite3

from flask import Flask, render_template, request, make_response, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_util import Database, UserLogin

# SECRET_KEY = '1111'

app = Flask(__name__)
app.config['SECRET_KEY'] = '2211dfc3f8ade025d4bf1fea4e40c549380da3e7'
login_manager = LoginManager(app)
db = Database()


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, db)


@app.route('/')
def hello_world():
    return redirect(url_for('main_page'))


@app.route('/ani_store')
def main_page():
    products = db.get_all_products()
    context = {
        'title': 'Ani store',
        'products': products
    }
    return render_template('main_page.html', **context)


@app.route('/ani_store/<string:category_name>')
def category_page(category_name):
    products = db.get_all_products_by_category(category_name)
    context = {
        'title': category_name,
        'products': products
    }
    return render_template('main_page.html', **context)


@app.route('/ani_store/<int:product_id>', methods=['GET', 'POST'])
def product_page(product_id):
    if request.method == 'POST':
        curr_form = request.form
        if 'edit_product_form' in curr_form:
            new_title = request.form.get('title')
            new_category = request.form.get('category')
            new_universe = request.form.get('universe')
            new_cost = request.form.get('cost')
            new_img_url = request.form.get('img_url')
            db.edit_product_by_id(product_id, new_title, new_category, new_universe, new_cost, new_img_url)
        if 'delete_product_form' in curr_form:
            db.delete_product(product_id)
            return redirect(url_for('main_page'))
    universes = db.get_universes()
    product = db.get_product_by_id(product_id)
    context = {
        'title': product['title'],
        'product': product,
        'universes': universes,
        'is_admin': current_user.is_authenticated
    }

    return render_template('product_page.html', **context)


@app.route('/ani_store/cart', methods=['GET', 'POST'])
def cart_page():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        if first_name is not None and last_name is not None:
            db.registerUser(first_name, last_name, email, generate_password_hash(password))
            user = db.get_user_by_email(email)
            user_login = UserLogin().create(user)
            login_user(user_login, remember=True)
        else:
            user = db.get_user_by_email(email)
            if user is not None and check_password_hash(user[4], password):
                user_login = UserLogin().create(user)
                login_user(user_login, remember=True)
            else:
                print('nol have account or wrong password')
    context = {
        'title': "Cart",
        'is_auth': current_user.is_authenticated
    }
    return render_template('user_not_auth.html', **context)


@app.route('/ani_store/profile', methods=['GET', 'POST'])
def profile_page():
    if request.method == 'POST':
        curr_form = request.form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        if 'edit_profile_form' in curr_form:
            edit_first_name = request.form.get('edit_first_name')
            edit_last_name = request.form.get('edit_last_name')
            db.edit_user_names(current_user.get_id(), edit_first_name, edit_last_name)
        elif 'register_form' in curr_form:
            db.register_user(first_name, last_name, email, generate_password_hash(password))
            user = db.get_user_by_email(email)
            user_login = UserLogin().create(user)
            login_user(user_login, remember=True)
        elif 'add_universe_form' in curr_form:
            name = request.form.get('universe_name')
            db.add_universe(name)
        elif 'add_product_form' in curr_form:
            title = request.form.get('title')
            category = request.form.get('category')
            universe = request.form.get('universe')
            cost = request.form.get('cost')
            img_url = request.form.get('img_url')
            db.add_product(title, category, universe, cost, img_url)
        else:
            user = db.get_user_by_email(email)
            if user is not None and check_password_hash(user[4], password):
                user_login = UserLogin().create(user)
                login_user(user_login, remember=True)
            else:
                print('nol have account or wrong password')
    if current_user.is_authenticated:
        user = db.get_user_by_id(current_user.get_id())
        universes = db.get_universes()
        context = {
            'title': "Profile",
            'is_auth': current_user.is_authenticated,
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'is_admin': user[5],
            'universes': universes
        }
    else:
        context = {
            'title': "Profile",
            'is_auth': current_user.is_authenticated
        }
    return render_template('profile.html', **context)


@app.route('/test')
@login_required
def test_page():
    return ('hello world')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    app.run()
