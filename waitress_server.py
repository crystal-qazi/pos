from waitress import serve
# from py_config.all_modules import *
import app

serve(app.app, host= '0.0.0.0', port=4245)