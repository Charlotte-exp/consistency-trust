from os import environ


SESSION_CONFIGS = [
    dict(
        name='trust',
        display_name="otree5 Trust game",
        app_sequence=['trust', 'payment_info'],
        num_demo_participants=4,
    ),
    dict(
        name='dictator',
        display_name="otree5 dictator game",
        app_sequence=['introduction', 'dictator', 'payment_info'],
        num_demo_participants=12,
        use_browser_bots=False,
    ),
    dict(
        name='survey', app_sequence=['survey', 'payment_info'], num_demo_participants=1
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=2.00, doc=""
)

SESSION_FIELDS = ['past_groups', ]
PARTICIPANT_FIELDS = ['title', 'conversion', 'new_conversion']


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'tokens'

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'charlotte'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '5784437076353'

INSTALLED_APPS = ['otree']
