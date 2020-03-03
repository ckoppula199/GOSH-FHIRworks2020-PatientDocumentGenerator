def get_patient_name_data(patient_data):
    prefix = patient_data["name"]["prefix"]
    first_name = patient_data["name"]["first_name"]
    last_name = patient_data["name"]["last_name"]
    return prefix, first_name, last_name


def get_patient_address_data(patient_data):
    address_lines = patient_data["address"]["address_lines"]
    city = patient_data["address"]["city"]
    state = patient_data["address"]["state"]
    postcode = patient_data["address"]["postcode"]
    country = patient_data["address"]["country"]
    return address_lines, city, state, postcode, country


def get_feedback_text(patient_data):
    intro = patient_data["questions_and_messages"]["intro"]
    recommendation = patient_data["questions_and_messages"]["recommendation"]
    comment = patient_data["questions_and_messages"]["comment"]
    hospital = patient_data["questions_and_messages"]["hospital"]
    clinic = patient_data["questions_and_messages"]["clinic"]
    return intro, recommendation, comment, hospital, clinic
