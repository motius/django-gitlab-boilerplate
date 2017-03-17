import string
import datetime
import random

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from model_mommy.random_gen import gen_email
from model_mommy.recipe import Recipe, seq, foreign_key, related


def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_short_id():
    return generate_id(4)


def generate_id_or_none(*args, **kwargs):
    if random.uniform(0, 1):
        return generate_id(*args, **kwargs)
    else:
        return None


def generate_past_date():
    random_date = datetime.date.today()\
                  - datetime.timedelta(days=6 * 30)\
                  + datetime.timedelta(days=random.uniform(-100, 100))
    return random_date


def generate_future_date():
    random_date = datetime.date.today()\
                  + datetime.timedelta(days=6 * 30)\
                  + datetime.timedelta(days=random.uniform(-100, 100))
    return random_date


def generate_duration():
    return random.randrange(1, 20)


def generate_duration_or_zero():
    if random.uniform(0, 10) > 8:
        return generate_duration()
    else:
        return 0


def generate_bool():
    return random.uniform(0, 1) > 0


def generate_color_hex():
    """
    See http://stackoverflow.com/a/14019260
    """
    def r():
        return random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())


UserRecipe = Recipe(get_user_model(), email=gen_email())
EmailAddressRecipe = Recipe(EmailAddress, user=foreign_key(UserRecipe), verified=True, primary=True)
