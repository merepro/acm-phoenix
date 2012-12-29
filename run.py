from acm_phoenix import create_app
app = create_app('config.DevelopmentConfig')
app.run(debug=True)
