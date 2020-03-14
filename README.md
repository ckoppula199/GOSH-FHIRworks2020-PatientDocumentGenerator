# Patient Document Generator

This system is intended to help doctors create documents quickly to hand to a patient in order to obtain feedback on services provided or to check if patient details are up to date. It is also capable of generating a word document that has graphs on the patient's health such as their body weight, height, blood pressure, etc over the past few years.

The frontend is a simple GUI made in python using Tkinter. Clicking on one of the generate buttons will make a request to my API. My API then makes a request to the GOSH FHIR API and gets the details for a specific patient. My API will then extract the required information and create a word document which it then stores on Azure.

To retrieve the Document you simply press the corresponding get button in the GUI and it will automatically retrieve the document from azure onto your local machine ready to use.

The folder PatientDocumentAPI contains the code for the API I created to retrieve patient data and create word documents on Azure.
The folder PatientDocumentGenerator contains the code for the demonstrator which is the frontend I made. This makes use of my API to create documents on Azure and retrieves them to the local machine.