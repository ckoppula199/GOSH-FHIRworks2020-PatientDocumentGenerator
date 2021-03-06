from azure.common import AzureMissingResourceHttpError
from flask import Flask, abort, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from fhir_parser.fhir import FHIR
from GenerateDocuments import FeedbackForm, PatientHealthForm, PatientDataForm
from AzureBlobStorage import *
import os
import json

app = Flask(__name__)
api = Api(app)


def get_address(patient):
    """
    Creates and returns a dictionary containing details of a patients address
    """
    address = {"address_lines": patient.addresses[0].lines, "city": patient.addresses[0].city,
               "state": patient.addresses[0].state, "postcode": patient.addresses[0].postal_code,
               "country": patient.addresses[0].country}
    return address


def get_name(patient):
    """
    Creates and returns a dictionary containing details of a patients address
    """
    name = {"prefix": patient.name.prefix, "first_name": patient.name.given,
            "last_name": patient.name.family}
    return name


def generate_feedback_data(patient):
    """
    Creates a dictionary that stores all the data used to create a document asking for patient feedback including
    name, address and questions to be asked.
    """
    address = get_address(patient)

    name = get_name(patient)

    questions_and_messages = {"intro": "We welcome all feedback on the services we provide to tell us what we are "
                                       "doing right and where we can improve.",
                              "recommendation": "Based on your recent experience of our services, how likely are "
                                                "you to recommend us to friends or family if they needed similar "
                                                "care or treatment?",
                              "comment": "With regards to your response to the previous question, what is the "
                                         "main reason you feel this way?",
                              "hospital": "What is the name of the hospital where you received treatment?",
                              "clinic": "What is the name of the clinic/department where you were treated?",
                              }

    return {"name": name, "address": address, "questions_and_messages": questions_and_messages}


def get_patient_data(observations, vital_sign):
    """
    Creates a list of dates and values for observations made on Weight, BMI, Heart rate and Respiratory rate as well
    as noting the unit used to measure them.
    """
    date = []
    value = []
    unit = ""
    for observation in observations:
        if observation.type != "vital-signs":
            continue
        for component in observation.components:
            if component.display == vital_sign:
                date.append(observation.issued_datetime)
                value.append(component.value)
                unit = component.unit

    return date, value, unit


class GenerateFeedbackReport(Resource):
    """
    Class used to create a word document on an azure account asking for a specific patient for feedback.
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str)
        super(GenerateFeedbackReport, self).__init__()

    def get(self):
        """
        The GET request for this endpoint not only returns the data about the patient and the questions used to
        create a patient feedback form in JSON, but also creates a word document and stores it on an Azure account.
        """
        args = self.reqparse.parse_args()
        if args['id'] is None:
            abort(400)

        fhir_parser = FHIR('https://localhost:5001/api/', verify_ssl=False)
        try:
            patient = fhir_parser.get_patient(args['id'])
        except ConnectionError:
            return make_response(jsonify({'message': 'Patient Does Not Exist'}), 404)

        feedback_data = generate_feedback_data(patient)

        feedback_form = FeedbackForm(args['id'], feedback_data)
        feedback_form.generate_feedback_form()

        write_data_to_azure(args['id'] + " feedback request.docx", storage_account_name, storage_account_key, feedback_container_name)
        os.remove(args['id'] + " feedback request.docx")

        return make_response(generate_feedback_data(patient), 200)


class GenerateFeedbackReportData(Resource):
    """
    Class used to generate required data and questions needed to create a feedback form for a specific patient
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str)
        super(GenerateFeedbackReportData, self).__init__()

    def get(self):
        """
        The GET request for this endpoint is JSON on data about the patient and the questions used to create
        a patient feedback form without creating the document on an Azure account.
        """
        args = self.reqparse.parse_args()
        if args['id'] is None:
            abort(400)

        fhir_parser = FHIR('https://localhost:5001/api/', verify_ssl=False)
        try:
            patient = fhir_parser.get_patient(args['id'])
        except ConnectionError:
            return make_response(jsonify({'message': 'Patient Does Not Exist'}), 404)

        return make_response(generate_feedback_data(patient), 200)


class GeneratePatientReport(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str)
        super(GeneratePatientReport, self).__init__()

    def get(self):
        """
        The GET response for this endpoint not only returns JSON containing information on the readings and dates of
        those readings for patient health data regarding weight, heart rate, BMI , diastolic blood pressure,
        systolic blood pressure and respiratory rate, but also creates a word document containing visualisations of
        the data and saves it to an Azure storage account.
        """
        args = self.reqparse.parse_args()
        if args['id'] is None:
            abort(400)

        patient_data = {}

        fhir_parser = FHIR('https://localhost:5001/api/', verify_ssl=False)
        try:
            patient = fhir_parser.get_patient(args['id'])
        except ConnectionError:
            return make_response(jsonify({'message': 'Patient Does Not Exist'}), 404)
        observations = fhir_parser.get_patient_observations(args['id'])
        vital_signs = ['Body Weight', 'Heart rate', 'Respiratory rate', 'Body Mass Index', 'Diastolic Blood Pressure',
                       'Systolic Blood Pressure']

        for vital_sign in vital_signs:
            value_dates, values, unit = get_patient_data(observations, vital_sign)
            dates = [str(date) for date in value_dates]
            patient_data[vital_sign] = {"Dates": dates, "Values": values, 'Unit': unit}

        patient_data_document = PatientHealthForm(args['id'], patient.full_name(), patient_data)
        patient_data_document.generate_patient_data_form()

        write_data_to_azure(args['id'] + " health data.docx", storage_account_name, storage_account_key, health_data_container_name)
        os.remove(args['id'] + " health data.docx")

        return make_response(patient_data, 200)


class GeneratePatientReportData(Resource):
    """
    Class used to collect all the dates and values for patient health data in regards to Weight, BMI, Heart rate,
    Respiratory rate.
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str)
        super(GeneratePatientReportData, self).__init__()

    def get(self):
        """
        The GET response for the endpoint is JSON containing information on the readings and dates of those readings
        for patient health data regarding weight, heart rate, BMI , diastolic blood pressure, systolic blood pressure
        and respiratory rate.
        """
        args = self.reqparse.parse_args()
        if args['id'] is None:
            abort(400)

        fhir_parser = FHIR('https://localhost:5001/api/', verify_ssl=False)
        try:
            observations = fhir_parser.get_patient_observations(args['id'])
        except ConnectionError:
            return make_response(jsonify({'message': 'Patient Does Not Exist'}), 404)

        vital_signs = ['Body Weight', 'Heart rate', 'Respiratory rate', 'Body Mass Index', 'Diastolic Blood Pressure',
                       'Systolic Blood Pressure']
        patient_data = {}

        for vital_sign in vital_signs:
            dates, values, unit = get_patient_data(observations, vital_sign)
            dates = [str(date) for date in dates]
            patient_data[vital_sign] = {"Dates": dates, "Values": values, 'Unit': unit}

        return make_response(patient_data, 200)


class GeneratePatientInformation(Resource):
    """
    Class used to create a word document asking patient to check and update all personal details held on them.
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str)
        super(GeneratePatientInformation, self).__init__()

    def get(self):
        """
        The GET response for the endpoint is JSON containing a message as to whether or not the document was
        successfully created and stored on Azure
        """
        args = self.reqparse.parse_args()
        if args['id'] is None:
            abort(400)

        fhir_parser = FHIR('https://localhost:5001/api/', verify_ssl=False)
        try:
            patient = fhir_parser.get_patient(args['id'])
        except ConnectionError:
            return make_response(jsonify({'message': 'Patient Does Not Exist'}), 404)

        patient_data_form = PatientDataForm(patient)
        patient_data_form.generate_patient_info_form()

        write_data_to_azure(args['id'] + " details.docx", storage_account_name, storage_account_key,
                            patient_info_container_name)
        os.remove(args['id'] + " details.docx")

        return make_response(jsonify({'message': 'Document created successfully'}, 200))


# declares the routing for each endpoint
api.add_resource(GenerateFeedbackReport, '/FormFiller/feedback', endpoint='feedback')
api.add_resource(GenerateFeedbackReportData, '/FormFiller/feedbackDocumentData', endpoint='feedbackDocumentData')
api.add_resource(GeneratePatientReport, '/report/patientReport', endpoint='report')
api.add_resource(GeneratePatientReportData, '/report/rawData', endpoint='reportData')
api.add_resource(GeneratePatientInformation, '/info/infoDocument', endpoint='patientInfo')

# loads the details for the azure storage account from the config file.
with open('config.json') as config_file:
    data = json.load(config_file)
    storage_account_name = data["account_name"]
    storage_account_key = data["account_key"]
    feedback_container_name = data["feedback_container_name"]
    health_data_container_name = data["health_data_container_name"]
    patient_info_container_name = data['patient_info_container_name']

if __name__ == '__main__':
    app.run(debug=True, port=5010)
