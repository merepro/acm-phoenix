# Base configuration to be used on running server

"""
Note: Unless you are working on the server itself, you will not be able to run 
it with a Config object. You must use a DevelopmentConfig or TestConfig.
"""
import os
_basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    Testing = False

    ADMINS = frozenset(['acm.at.ucr+webmaster@gmail.com'])

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'acm_phoenix.db')
    DATABASE_CONNECT_OPTIONS = {}

    THREADS_PER_PAGE = 8

    CSRF_ENABLED = True
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_OPTIONS = {'theme': 'white'}

    # Giving server defined configuration default values.
    SECRET_KEY = None
    CSRF_SESSION_KEY = None
    RECAPTCHA_PUBLIC_KEY = None
    RECAPTCHA_PRIVATE_KEY = None
    GOOGLE_CLIENT_ID = None
    GOOGLE_CLIENT_SECRET = None
    HOST_URL = None
    WEPAY_ACCT_ID = None
    WEPAY_ACC_TOK = None
    WEPAY_IN_PROD = None

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'MIIEpAIBAAKCAQEAwTs9CBbomFmsYmYzChcAT6FYm6szVtW2wlYaPRajiV7XvFaoZfBpDKDy2xsTaWkWdspR2juyyoVStJSuzLt7pIP7SX6ibDkbKtSthZJA5JAqhtvVF2BtR+yApLoM9hWEF4XQZDswMAGgYOBi+/C5FSqW/jPKoSaO+6dVgf+VKS9Nmp9G'

    CSRF_SESSION_KEY="TNSDOSJBjVSszvLMelsRafiw/z/flEnxh2LeZYMXuiSXxCAm32h9d6hkZpJRbE7Lpbk46sJmNLqRzCVInBOezAwOzR3Dv0FHx2s9kwIDAQABAoIBACB3Fnr8dlnafycNKrggQzId1qhY7EhDofAmzUPEQPe8kpyXJrXx3YR8qjD77JgCSv7sYTI8Y365RbsHXBMT0ONENX0UpK9wLMtWbk0J1JNSUYLU/olt7w5tgvOqOrFBzi6xkeC1PR"
    RECAPTCHA_PUBLIC_KEY = '6LfDW9YSAAAAAAjSp9n2mS7G1bMwrYH7EESVOLQe'
    RECAPTCHA_PRIVATE_KEY = '6LfDW9YSAAAAAIJTT53vTrOzG5NdPhetB6Z8JLao'

    GOOGLE_CLIENT_ID = '401399822645-a1015kkb76m6evpn3mhk3hr4voqejt2f.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = 'TS6HarpynHCdSTesaRMlbaU_'

    HOST_URL = 'http://localhost:5000'

    WEPAY_ACCT_ID = 319493
    WEPAY_ACC_TOK = '6dd6802f8ebef4992308a0e4f7698c275781ac36854f9451127115d995d8cda7'
    WEPAY_IN_PROD = False

class TestingConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'tests/test.db')
