import json
import os
import xml.etree.ElementTree as Et
from app.db_models import Experiment
import app.experiment.object_code.scripts.data_process as data_process


class TaskRunner:
    def __init__(self, obj_code):
        """ This class will be changed"""
        print(obj_code)


class ExperimentError(Exception):
    pass


class XMLTree:
    def __init__(self, xml):
        if os.path.isfile(xml) is True:
            self.xml_tree = Et.parse(xml)
            self.xml_tree.getroot()
        else:
            self.xml_tree = Et.fromstring(xml)
        self.root = self.xml_tree
        if self.root.tag != "experiment":
            raise ExperimentError()


class DataProcessor:
    def __init__(self, xml):
        self.root = XMLTree(xml).root
        self.processing = self.root.find('data_processing')

    def generate_object_code(self):
        # have to consider about exception
        return data_process.make_code(self.root)

    def run_obj_code(self, obj_code):
        """This function just for test object code"""
        OUTPUT_PATH = '/Users/chan/test/output.py'
        output_file = open(OUTPUT_PATH, "w")
        output_file.write(obj_code)
        output_file.close()


class TFConverter:
    """This code is NOT considered about exception"""
    SCRIPT_MODULE = 'app.experiment.object_code.scripts'

    def __init__(self, xml):
        self.root = XMLTree(xml).root
        self.model_type = self.root.find("model").find("type").text

    def generate_object_code(self):
        # have to consider about exception
        script_module = __import__(self.SCRIPT_MODULE, globals(),
                                   locals(), [self.model_type], 0)
        object_script = getattr(script_module, self.model_type)
        return object_script.make_code(self.root)

    def run_obj_code(self, obj_code):
        """This function just for test object code"""
        OUTPUT_PATH = '/Users/chan/test/output.py'
        output_file = open(OUTPUT_PATH, "w")
        output_file.write(obj_code)
        output_file.close()


class Refiner(json.JSONEncoder):
    def __init__(self, exps):
        super().__init__()
        self.exps = []
        for exp in exps:
            temp = self.exp_to_dict(exp)
            self.exps.append(temp)

    def exp_to_dict(self, exp):
        exp_dict = dict(
            id=exp.id,
            date_modified=str(exp.date_modified),
            date_created=str(exp.date_created),
            user_id=exp.user_id,
            name=exp.name,
            xml=exp.xml.decode(),
            drawing=exp.drawing.decode(),
            input=exp.input
        )
        return exp_dict


class JsonParser:
    @staticmethod
    def parse_post(json):
        try:
            exp_json = json['exp_data']
            exp_data = Experiment(exp_json['name'],
                                  exp_json['user_id'],
                                  exp_json['xml'].encode(),
                                  exp_json['drawing'].encode(),
                                  exp_json['input'])
        except KeyError as e:
            return e
        return exp_data
