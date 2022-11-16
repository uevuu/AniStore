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


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.route('/')
def hello_world():
    return redirect(url_for('main_page'))


@app.route('/ani_store')
def main_page():
    curr_request = request.args.to_dict(flat=False)
    universe_filter = list(map(int, curr_request['universe'])) if 'universe' in curr_request else []
    search_filter = request.args.get('search_by_name')
    if search_filter is not None:
        products = db.get_products_by_title(search_filter)
    else:
        products = db.get_all_products(universe_filter)
    context = {
        'title': 'Ani store',
        'products': products,
        'universes': db.get_universes(),
        'universe_filter': universe_filter
    }
    return render_template('main_page.html', **context)


@app.route('/ani_store/<string:category_name>')
def category_page(category_name):
    curr_request = request.args.to_dict(flat=False)
    universe_filter = list(map(int, curr_request['universe'])) if 'universe' in curr_request else []
    search_filter = request.args.get('search_by_name')
    if search_filter is not None:
        products = db.get_products_by_title_category(search_filter, category_name)
    else:
        products = db.get_all_products_by_category(category_name, universe_filter)
    context = {
        'title': category_name,
        'products': products,
        'universes': db.get_universe_in_category(category_name),
        'universe_filter': universe_filter
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
        'is_admin': False
    }
    if current_user.is_authenticated:
        context['is_admin'] = db.get_user_by_id(current_user.get_id())[5]

    return render_template('product_page.html', **context)


def reg_login_func():
    curr_form = request.form
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    if 'register_form' in curr_form:
        db.register_user(first_name, last_name, email, generate_password_hash(password))
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


@app.route('/ani_store/wishlist', methods=['GET', 'POST'])
def wishlist_page():
    if request.method == 'POST':
        reg_login_func()
    context = {
        'title': "Wishlist",
        'is_auth': current_user.is_authenticated,
    }
    if current_user.is_authenticated:
        products = db.get_user_wl_products(current_user.get_id())
        context['products'] = products

    return render_template('wishlist_page.html', **context)


@app.route('/ani_store/cart', methods=['GET', 'POST'])
def cart_page():
    if request.method == 'POST':
        if current_user.is_authenticated:
            if 'accept_order_form' in request.form:
                address = request.form.get('address')
                total_price = request.form.get('total_price')
                user_id = current_user.get_id()
                db.create_order(user_id, address, total_price)
                db.clear_cart(user_id)
                return redirect(url_for('cart_page'))
        reg_login_func()

    context = {
        'title': "Cart",
        'is_auth': current_user.is_authenticated
    }
    if current_user.is_authenticated:
        products = db.get_user_products(current_user.get_id())
        context['products'] = products
        context['total_price'] = sum([product['count'] * product['cost'] for product in products])

    return render_template('cart_page.html', **context)


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
        user_id = current_user.get_id()
        user = db.get_user_by_id(user_id)
        universes = db.get_universes()
        orders = db.get_all_orders(user_id)
        print(orders)
        context = {
            'title': "Profile",
            'is_auth': current_user.is_authenticated,
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'is_admin': user[5],
            'universes': universes,
            'orders': orders
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


@app.route('/add_to_cart/', methods=['GET', 'POST'])
@login_required
def add_to_cart():
    if request.method == "POST":
        product_id = request.form.get('product_id')
        user_id = current_user.get_id()
        if not db.user_have_product(user_id, product_id):
            db.add_product_to_cart(user_id, product_id)
    return render_template('main_page.html')


@app.route('/add_to_fav/', methods=['GET', 'POST'])
@login_required
def add_to_fav():
    if request.method == "POST":
        product_id = request.form.get('product_id')
        user_id = current_user.get_id()
        if not db.user_have_product_in_fav(user_id, product_id):
            db.add_product_to_fav(user_id, product_id)
    return render_template('main_page.html')


@app.route('/reduce_count/<int:product_id>')
@login_required
def reduce_count(product_id):
    user_id = current_user.get_id()
    if db.count_of_product_in_car(user_id, product_id) == 1:
        db.delete_product_from_cart(user_id, product_id)
    else:
        db.reduce_count_of_product(user_id, product_id)
    return redirect(url_for('cart_page'))


@app.route('/increase_count/<int:product_id>')
@login_required
def increase_count(product_id):
    user_id = current_user.get_id()
    db.increase_count_of_product(user_id, product_id)
    return redirect(url_for('cart_page'))


@app.route('/remove_product_from_cart/<int:product_id>')
@login_required
def remove_product_from_cart(product_id):
    user_id = current_user.get_id()
    db.delete_product_from_cart(user_id, product_id)
    return redirect(url_for('cart_page'))


@app.route('/remove_product_from_wl/<int:product_id>')
@login_required
def remove_product_from_wl(product_id):
    user_id = current_user.get_id()
    db.remove_product_from_wl(user_id, product_id)
    return redirect(url_for('wishlist_page'))


# @app.route('/increase_count/', methods=['GET', 'POST'])
# @login_required
# def increase_count():
#     if request.method == "POST":
#         product_id = request.form.get('product_id')
#         count = 10
#         print('update_count')
#         return {'product_id': product_id, 'count': count}
#     print('not return')
#     return render_template('cart_page.html')
#
#
# @app.route('/reduce_count/', methods=['GET', 'POST'])
# @login_required
# def reduce_count():
#     if request.method == "POST":
#         product_id = request.form.get('product_id')
#     return render_template('cart_page.html')


if __name__ == '__main__':
    app.run()
