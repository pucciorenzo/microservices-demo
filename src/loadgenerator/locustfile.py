import random
import datetime
from locust import FastHttpUser, TaskSet, between, LoadTestShape
from faker import Faker
import math
import os

fake = Faker()

products = [
    '0PUK6V6EV0', '1YMWWN1N4O', '2ZYFJ3GM2N', '66VCHSJNUP',
    '6E92ZMYYFZ', '9SIQT8TOJO', 'L9ECAV7KIM', 'LS4PSXUNUM', 'OLJCESPC7Z'
]

# Task functions
def index(l):
    l.client.get("/")

def setCurrency(l):
    currencies = ['EUR', 'USD', 'JPY', 'CAD', 'GBP', 'TRY']
    l.client.post("/setCurrency", {'currency_code': random.choice(currencies)})

def browseProduct(l):
    l.client.get("/product/" + random.choice(products))

def viewCart(l):
    l.client.get("/cart")

def addToCart(l):
    product = random.choice(products)
    l.client.get("/product/" + product)
    l.client.post("/cart", {
        'product_id': product,
        'quantity': random.randint(1, 10)
    })

def empty_cart(l):
    l.client.post('/cart/empty')

def checkout(l):
    addToCart(l)
    current_year = datetime.datetime.now().year + 1
    l.client.post("/cart/checkout", {
        'email': fake.email(),
        'street_address': fake.street_address(),
        'zip_code': fake.zipcode(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'country': fake.country(),
        'credit_card_number': fake.credit_card_number(card_type="visa"),
        'credit_card_expiration_month': random.randint(1, 12),
        'credit_card_expiration_year': random.randint(current_year, current_year + 70),
        'credit_card_cvv': f"{random.randint(100, 999)}",
    })

def logout(l):
    l.client.get('/logout')


class UserBehavior(TaskSet):
    def on_start(self):
        index(self)

    tasks = {
        index: 1,
        setCurrency: 2,
        browseProduct: 10,
        addToCart: 2,
        viewCart: 3,
        checkout: 1
    }

class WebsiteUser(FastHttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)


# Custom sinusoidal load pattern
class SinusoidalShape(LoadTestShape):
    """
    Sinusoidal user load shape:
    users(t) = min_users + amplitude * (1 + sin(2π * t / period)) / 2
    """

    # get min_users, max_users, and period from environment variables or set defaults
    min_users = int(os.getenv("MIN_USERS", 10))
    max_users = int(os.getenv("MAX_USERS", 100))
    period = int(os.getenv("PERIOD", 120))  # full cycle every 2 minutes

    min_users = 10
    max_users = 100
    period = 120  # full cycle every 2 minutes

    def tick(self):
        run_time = self.get_run_time()
        amplitude = self.max_users - self.min_users
        users = self.min_users + amplitude * (1 + math.sin(2 * math.pi * run_time / self.period)) / 2
        spawn_rate = users / 10  # adjust spawn rate as needed
        return round(users), spawn_rate
