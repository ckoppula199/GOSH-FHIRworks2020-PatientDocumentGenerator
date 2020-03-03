from tkinter import *
import threading
import time
import requests

from azure.common import AzureMissingResourceHttpError
from azure.storage.blob import BlockBlobService

storage_account_key = 'storage_account_key'
storage_account_name = 'storage_account_name'
#Example patient ID
#8f789d0b-3145-4cf2-8504-13159edaa747


def get_feedback_document():
    def get_feedback_form():
        file_name = patient_id.get() + " feedback request.docx"
        blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)
        try:
            blob_service.get_blob_to_path("feedbackforms",
                                          file_name,
                                          file_name)
        except AzureMissingResourceHttpError:
            information.set("File does not exist on Azure")
            time.sleep(1)
            information.set("Enter Patient ID")

    t = threading.Thread(target=get_feedback_form)
    t.start()


def make_feedback_document():
    def make_feedback_form():
        response = requests.get("http://localhost:5010/FormFiller/feedback?id=" + patient_id.get())
        if response.status_code == 200:
            information.set("Document created on Azure")
            time.sleep(1)
            information.set("Enter Patient ID")
        else:
            information.set("File could not be created")
            time.sleep(1)
            information.set("Enter Patient ID")

    t = threading.Thread(target=make_feedback_form)
    t.start()


def get_health_document():
    def get_health_form():
        file_name = patient_id.get() + " health data.docx"
        blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)
        try:
            blob_service.get_blob_to_path("patienthealthdata",
                                          file_name,
                                          file_name)
        except AzureMissingResourceHttpError:
            information.set("File does not exist on Azure")
            time.sleep(1)
            information.set("Enter Patient ID")

    t = threading.Thread(target=get_health_form)
    t.start()


def make_health_document():
    def make_health_form():
        response = requests.get("http://localhost:5010/report/patientReport?id=" + patient_id.get())
        if response.status_code == 200:
            information.set("Document created on Azure")
            time.sleep(1)
            information.set("Enter Patient ID")
        else:
            information.set("File could not be created")
            time.sleep(1)
            information.set("Enter Patient ID")

    t = threading.Thread(target=make_health_form)
    t.start()


window = Tk()
window.wm_title("Patient Document Generator")

patient_id = StringVar()
entry = Entry(window, textvariable=patient_id, width=45)
entry.grid(row=1, column=0)

information = StringVar()
information.set("Enter Patient ID")
label = Label(window, textvariable=information, width=25)
label.grid(row=0, column=0)

feedback_form_button = Button(window, text="Get Feedback Form", width=45, command=get_feedback_document, height=2)
feedback_form_button.grid(row=2, column=0)

generate_feedback_button = Button(window, text="Generate Feedback Form", width=45, command=make_feedback_document,
                                  height=2)
generate_feedback_button.grid(row=2, column=1)

health_form_button = Button(window, text="Get Health Data Form", width=45, command=get_health_document, height=2)
health_form_button.grid(row=3, column=0)

generate_health_form_button = Button(window, text="Generate Health Data Form", width=45, command=make_health_document,
                                     height=2)
generate_health_form_button.grid(row=3, column=1)

window.mainloop()
