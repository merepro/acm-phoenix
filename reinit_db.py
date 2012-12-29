from acm_phoenix import db, create_app
app = create_app('config.DevelopmentConfig')
db.drop_all(app=app)
db.create_all(app=app)
exit()
