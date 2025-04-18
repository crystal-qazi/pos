# from py_config.all_modules import *
# from main import *
from app import *


def yaml_data():
    with open('config.yaml' , 'r') as f:
        yml_data = yaml.load(f, Loader=yaml.FullLoader)
        return yml_data

if __name__=='__main__':
     with app.app_context():   

        con = yaml_data()['server-intra']    
        app.run(debug=True, host=con['host'],  port=con['port'], threaded=True)