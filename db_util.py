import psycopg2


class Database:
    def __init__(self):
        with psycopg2.connect(dbname="anistore", user="postgres", password="#ur_psw", host="localhost", port=5432) as conn:
            conn.autocommit = True
            self.cur = conn.cursor()

    def register_user(self, first_name, last_name, email, password):
        try:
            self.cur.execute("""INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)""",
                             (str(first_name), str(last_name), str(email), str(password)))
            return True
        except Exception as exc:
            print("Error with insert data in DB: " + str(exc))
            return False

    def get_user_by_email(self, email):
        try:
            self.cur.execute("""SELECT * FROM users WHERE email=%s """, (str(email),))
            rez = self.cur.fetchone()
            if not rez:
                return None
            return rez
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))
            return None

    def get_password_by_email(self, email):
        try:
            self.cur.execute("""SELECT password FROM users WHERE email=%s """, (str(email),))
            return self.cur.fetchone()
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))
            return None

    def get_user_by_id(self, user_id):
        try:
            self.cur.execute("""SELECT * FROM users WHERE id=%s """, (str(user_id),))
            res = self.cur.fetchone()
            if not res:
                print("User not find")
                return False
            return res
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))
            return False

    def edit_user_names(self, user_id, new_first_name, new_last_name):
        try:
            self.cur.execute("""UPDATE users SET first_name=%s, last_name=%s WHERE id=%s""",
                             (str(new_first_name), str(new_last_name), int(user_id)))
        except Exception as exc:
            print("Error with update data in DB: " + str(exc))

    def add_universe(self, universe_name):
        try:
            self.cur.execute("""INSERT INTO universes (name) VALUES (%s)""",
                             (str(universe_name),))
        except Exception as exc:
            print("Error with insert data in DB: " + str(exc))

    def get_universes(self):
        try:
            self.cur.execute("""SELECT * FROM universes""")
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))

    def get_universe_in_category(self, category):
        try:
            self.cur.execute(
                """SELECT u.id, u.name FROM products p JOIN universes u ON p.universe = u.id WHERE p.category=%s GROUP BY u.id, u.name""",
                (str(category),))
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))

    def add_product(self, title, category, universe, cost, img_url):
        try:
            self.cur.execute(
                """INSERT INTO products (title, category, universe, cost, img_url) values (%s,%s, %s,%s,%s) """,
                (str(title), str(category), int(universe), int(cost), str(img_url)))
        except Exception as exc:
            print("Error with insert data in DB: " + str(exc))

    def get_all_products(self, universe_filter):
        try:
            if universe_filter:
                self.cur.execute("""SELECT id, title, cost, img_url FROM products WHERE universe=ANY(%s)""",
                                 (universe_filter,))
            else:
                self.cur.execute("""SELECT id, title, cost, img_url FROM products""")
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with selects data from DB: " + str(exc))

    def get_all_products_by_category(self, category_name, universe_filter):
        try:
            if universe_filter:
                self.cur.execute(
                    """SELECT id, title, cost, img_url FROM products WHERE category=%s AND universe=ANY(%s)""",
                    (str(category_name), universe_filter))
            else:
                self.cur.execute("""SELECT id, title, cost, img_url FROM products WHERE category=%s""",
                                 (str(category_name),))
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with selects data from DB: " + str(exc))

    def get_product_by_id(self, product_id):
        try:
            self.cur.execute("""SELECT p.id, name universe_name, category, title, cost, img_url
                                FROM products p
                                JOIN universes u ON u.id = p.universe WHERE p.id=%s """, (int(product_id),))
            return self.prepare_data(self.cur.fetchall())[0]
        except Exception as exc:
            print("Error with selects data from DB: " + str(exc))

    def get_products_by_title(self, title_name):
        try:
            self.cur.execute("""SELECT * FROM products WHERE position(LOWER(%s) in LOWER(title)) > 0""",
                             (str(title_name),))
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with selects data from DB: " + str(exc))

    def get_products_by_title_category(self, title_name, category_name):
        try:
            self.cur.execute("""SELECT * FROM products WHERE position(LOWER(%s) in LOWER(title)) > 0 and category=%s""",
                             (str(title_name), str(category_name)))
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with selects data from DB: " + str(exc))

    def prepare_data(self, data):
        rez = []
        if len(data):
            column_names = [desc[0] for desc in self.cur.description]
            for row in data:
                rez += [{c_name: row[key] for key, c_name in enumerate(column_names)}]

        return rez

    def edit_product_by_id(self, product_id, title, category, universe, cost, img_url):
        try:
            self.cur.execute(
                """UPDATE products SET title=%s, category=%s, universe=%s, cost=%s, img_url=%s WHERE id=%s""",
                (str(title), str(category), int(universe), int(cost), str(img_url), int(product_id)))
        except Exception as exc:
            print("Error with update data in DB: " + str(exc))

    def delete_product(self, product_id):
        try:
            self.cur.execute("""DELETE FROM products WHERE id=%s""", (int(product_id),))
        except Exception as exc:
            print("Error with delete data in DB: " + str(exc))

    def get_user_products(self, user_id):
        try:
            self.cur.execute(
                """SELECT c.id, title, cost, count, product_id, user_id, img_url 
                    FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id=%s""",
                (int(user_id),))
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with select data in DB: " + str(exc))

    def add_product_to_cart(self, user_id, product_id):
        try:
            self.cur.execute("""INSERT INTO cart (user_id, product_id) values (%s,%s) """,
                             (int(user_id), int(product_id)))
        except Exception as exc:
            print("Error with update/insert data in DB: " + str(exc))

    def user_have_product(self, user_id, product_id):
        try:
            self.cur.execute("""SELECT EXISTS (SELECT * FROM cart WHERE user_id=%s and product_id=%s)""",
                             (int(user_id), int(product_id)))
            return self.cur.fetchone()[0]
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))

    def add_product_to_fav(self, user_id, product_id):
        try:
            self.cur.execute("""INSERT INTO wishlist (user_id, product_id) values (%s,%s) """,
                             (int(user_id), int(product_id)))
        except Exception as exc:
            print("Error with update/insert data in DB: " + str(exc))

    def user_have_product_in_fav(self, user_id, product_id):
        try:
            self.cur.execute("""SELECT EXISTS (SELECT * FROM wishlist WHERE user_id=%s and product_id=%s)""",
                             (int(user_id), int(product_id)))
            return self.cur.fetchone()[0]
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))

    def count_of_product_in_car(self, user_id, product_id):
        try:
            self.cur.execute("""SELECT count FROM cart WHERE user_id=%s and product_id=%s""",
                             (int(user_id), int(product_id)))
            return self.cur.fetchone()[0]
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))

    def delete_product_from_cart(self, user_id, product_id):
        try:
            self.cur.execute("""DELETE FROM cart WHERE user_id=%s and product_id=%s""", (int(user_id), int(product_id)))
        except Exception as exc:
            print("Error with delete data in DB: " + str(exc))

    def reduce_count_of_product(self, user_id, product_id):
        try:
            self.cur.execute("""UPDATE cart SET count = count - 1 WHERE user_id=%s and product_id=%s""",
                             (int(user_id), int(product_id)))
        except Exception as exc:
            print("Error with update data from DB: " + str(exc))

    def increase_count_of_product(self, user_id, product_id):
        try:
            self.cur.execute("""UPDATE cart SET count = count + 1 WHERE user_id=%s and product_id=%s""",
                             (int(user_id), int(product_id)))
        except Exception as exc:
            print("Error with update data from DB: " + str(exc))

    def get_user_wl_products(self, user_id):
        try:
            self.cur.execute(
                """SELECT w.id, title, cost, product_id, user_id, img_url 
                    FROM wishlist w JOIN products p ON w.product_id = p.id WHERE w.user_id=%s""",
                (int(user_id),))
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with select data in DB: " + str(exc))

    def remove_product_from_wl(self, user_id, product_id):
        try:
            self.cur.execute("""DELETE FROM wishlist WHERE user_id=%s and product_id=%s""",
                             (int(user_id), int(product_id)))
        except Exception as exc:
            print("Error with delete data in DB: " + str(exc))

    def create_order(self, user_id, address, total_price):
        try:
            self.cur.execute("""INSERT INTO orders (user_id, address, total_price) values (%s,%s,%s)""",
                             (int(user_id), address, int(total_price)))
        except Exception as exc:
            print("Error with insert data in DB: " + str(exc))

    def clear_cart(self, user_id):
        try:
            self.cur.execute("""DELETE FROM cart WHERE user_id=%s""", (int(user_id),))
        except Exception as exc:
            print("Error with delete data from DB: " + str(exc))

    def get_all_orders(self, user_id):
        try:
            self.cur.execute("""SELECT * FROM orders WHERE user_id=%s""", (int(user_id),))
            return self.prepare_data(self.cur.fetchall())
        except Exception as exc:
            print("Error with select data from DB: " + str(exc))


class UserLogin:
    def fromDB(self, user_id, db):
        self.__user = db.get_user_by_id(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user[0])
