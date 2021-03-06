import requests
import time
import re
from datetime import date
from datetime import datetime
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from discord_webhook import DiscordEmbed, DiscordWebhook
from patient_info import Patient, Questions
from general_info import Colors, Discord_Webhook
from errors import Errors

s = requests.Session()


def utc2est():
    current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return str(current) + ' EST'


def error_handle(error):
    return str(Errors.error_dict[error])


site_print = Colors.CYAN + "[VACCINE SEARCH]" + Colors.END

today = date.today()

api_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'referer': 'https://www.cvs.com/',
    'origin': 'https://www.cvs.com',
    'x-api-key': 'rFd64We9AwyvAFzIXsoSp8bYuewNohOZ'

}

monitor_url = 'https://www.cvs.com/Services/ICEAGPV1/immunization/1.0.0/getIMZStores'
monitor_headers = {
    'accept': 'application/json',
    'referer': 'https://www.cvs.com/vaccine/intake/store/cvd-store-select/first-dose-select',
    'origin': 'https://www.cvs.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="89"',
    'sec-ch-ua-mobile': '?0',
    'accept-type': 'application/json'
}
first_dose_soft_url = 'https://www.cvs.com/services/ICEAGPV1/inventory/1.0.0/softAllocation'
first_dose_soft_headers = {
    'accept': 'application/json',
    'referer': 'https://www.cvs.com/vaccine/intake/store/cvd-store-select/dose-select',
    'origin': 'https://www.cvs.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="89"',
    'sec-ch-ua-mobile': '?0',
    'accept-type': 'application/json'
}
time_url = 'https://api.cvshealth.com/scheduler/v3/clinics/availabletimeslots'
reserve_url = 'https://api.cvshealth.com/scheduler/v3/clinics/reservation'
sd_monitor_headers = {
    'accept': 'application/json',
    'referer': 'https://www.cvs.com/vaccine/intake/store/cvd-store-select/second-dose-select',
    'origin': 'https://www.cvs.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="89"',
    'sec-ch-ua-mobile': '?0',
    'accept-type': 'application/json'
}
submit_registration_url = 'https://www.cvs.com/Services/ICEAGPV1/immunization/1.0.0/submitImzRegistration'
submit_registration_headers = {
    'accept': 'application/json',
    'referer': 'https://www.cvs.com/vaccine/intake/store/consent',
    'origin': 'https://www.cvs.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="89"',
    'sec-ch-ua-mobile': '?0',
    'accept-type': 'application/json',
    'x-distil-ajax': 'xebztatfusvxtdxdzzerd'
}

vaccine_codes = {
    'PFIZER1': "59267100002",
    'PFIZER': "59267100003",
}

# VALUE CONTROLS
# -------------------

vaccine_controls = ["PFIZER1", "PFIZER"]

home = input("Please enter your location: ")
radius = input("Monitor radius: ")
monitor_delay = int(input("Monitor delay (Ex. 7=7s): "))


# patient questions values --> 1: Yes, 2: No, 3: I don't know
# (experimental) currently only works for "America/New_York" time zone
# ethnicity value --> U: Unknown, N: Not Hispanic..., Y: Is Hispanic...


def question_values(question_id):
    if question_id == "No":
        return 2
    if question_id == "Yes":
        return 1
    if question_id == "I don't know":
        return 3


if Patient.non_medicare:
    insurance_data = {
        "typeId": 6,
        "typeText": "Insurance",
        "insuranceData": [
            {
                "cardHolderFirstName": Patient.first_name,
                "cardHolderLastName": Patient.last_name,
                "groupId": None,
                "insuranceType": "secondary",
                "isPatientPrimaryCardholder": "Y",
                "memberId": Patient.insurance_id,
                "provider": Patient.non_medicare_provider,
                "relationshipWithCardHolder": "1",
                "payerId": None
            }
        ]
    }

if not Patient.non_medicare:
    insurance_data = {
        "typeId": 5,
        "typeText": "Medicare",
        "medicareData": {
            "memberId": Patient.insurance_id
        },
        "insuranceData": [

        ]
    }

# PROCESS
# -------------------


vaccine_code_list = []
for vaccine in vaccine_controls:
    vaccine_code_list.append(vaccine_codes[vaccine])
if not vaccine_controls:
    print(utc2est(), site_print, Colors.FAIL + "Please enter in a vaccine(s).", Colors.END)
    exit(1)


def monitor_loop_status(loop):
    if loop == 1:
        print(utc2est(), site_print,
              Colors.BOLD + "No appointments available at the location you selected. Monitoring for appointments..." + Colors.END)
    elif loop == 360:
        print(utc2est(), site_print, Colors.BOLD + "Still searching for appointments..." + Colors.END)
    elif loop == 540:
        print(utc2est(), site_print, Colors.BOLD + "Still searching for appointments..." + Colors.END)
    elif loop == 720:
        print(utc2est(), site_print, Colors.BOLD + "Still searching for appointments..." + Colors.END)
    elif loop == 900:
        print(utc2est(), site_print, Colors.BOLD + "Still searching for appointments..." + Colors.END)


def covid_monitor():
    print(utc2est(), site_print, Colors.CYAN + "Monitor for CVS in", Colors.WARNING + home,
          Colors.CYAN + "has begun..." + Colors.END)
    print(utc2est(), site_print, Colors.CYAN + "Looking for:", str(vaccine_controls) + Colors.END)
    try:
        for monitor_loop in range(9999):

            # [First Dose] Monitor

            time.sleep(monitor_delay)

            monitor_form_data = {
                "requestMetaData": {
                    "appName": "CVS_WEB",
                    "lineOfBusiness": "RETAIL",
                    "channelName": "WEB",
                    "deviceType": "DESKTOP",
                    "deviceToken": "7777",
                    "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                    "source": "ICE_WEB",
                    "securityType": "apiKey",
                    "responseFormat": "JSON",
                    "type": "cn-dep"
                },
                "requestPayloadData": {
                    "selectedImmunization": [
                        "CVD"
                    ],
                    "distanceInMiles": radius,
                    "imzData": [
                        {
                            "imzType": "CVD",
                            "ndc": vaccine_code_list,
                            "allocationType": "1"
                        }
                    ],
                    "searchCriteria": {
                        "addressLine": home
                    }
                }
            }

            geo_code_get = s.post(monitor_url, json=monitor_form_data, headers=monitor_headers)

            if geo_code_get.status_code != 200:
                print(utc2est(), site_print,
                      Colors.FAIL + Colors.BOLD + "Request UNSUCCESSFULLY Received by the API. STATUS CODE:",
                      str(geo_code_get.status_code) + Colors.END)
                exit(1)
            if monitor_loop == 0:
                if geo_code_get.status_code == 200:
                    print(utc2est(), site_print,
                          Colors.CYAN + Colors.BOLD + "Request Successfully Received by CVS API." + Colors.END)

            geo_code_status_desc = geo_code_get.json()["responseMetaData"]["statusDesc"]
            geo_code_status_code = geo_code_get.json()["responseMetaData"]["statusCode"]

            unknown_error = re.findall('Inventory unavailable', geo_code_status_desc)
            if unknown_error:
                print(error_handle("unknown"))

            if geo_code_status_desc == 'Failed calling getStoreDetails -Locations Not Found':
                print(error_handle("location_not_found"))
                exit(1)

            if geo_code_status_desc == "No stores with immunizations found":
                monitor_loop_status(monitor_loop)
                continue

            if geo_code_status_desc == "Did you mean" or geo_code_status_desc == "Success":
                # Coordinates

                latitude = geo_code_get.json()["responsePayloadData"]["locations"][0]["geographicLatitudePoint"]
                longitude = geo_code_get.json()["responsePayloadData"]["locations"][0]["geographicLongitudePoint"]

                geo_form_data = {
                    "requestMetaData": {
                        "appName": "CVS_WEB",
                        "lineOfBusiness": "RETAIL",
                        "channelName": "WEB",
                        "deviceType": "DESKTOP",
                        "deviceToken": "7777",
                        "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                        "source": "ICE_WEB",
                        "securityType": "apiKey",
                        "responseFormat": "JSON",
                        "type": "cn-dep"
                    },
                    "requestPayloadData": {
                        "selectedImmunization": [
                            "CVD"
                        ],
                        "distanceInMiles": 35,
                        "imzData": [
                            {
                                "imzType": "CVD",
                                "ndc": vaccine_code_list,
                                "allocationType": "1"
                            }
                        ],
                        "locations": {
                            "geographicLatitudePoint": latitude,
                            "geographicLongitudePoint": longitude
                        }
                    }
                }

                for IMZRetry in range(999):
                    time.sleep(monitor_delay)

                    # [First Dose] Geo Code Submitting

                    getIMZStores = s.post(monitor_url, json=geo_form_data, headers=monitor_headers)

                    if getIMZStores.json()["responseMetaData"]["statusDesc"] == "No stores with immunizations found":
                        monitor_loop_status(IMZRetry)
                        continue

                    if getIMZStores.json()["responseMetaData"]["statusDesc"] == "Success":
                        print(utc2est(), site_print, Colors.CYAN + "GEO LOCATION CODES FOUND:",
                              Colors.WARNING + longitude + ",", latitude + Colors.END)

                        # General Variables
                        location_json = getIMZStores.json()["responsePayloadData"]["locations"][0]
                        available_dates = location_json["imzAdditionalData"][0]["availableDates"]

                        # Address Variables
                        address_line = location_json["addressLine"]
                        city = location_json["addressCityDescriptionText"]
                        state = location_json["addressState"]
                        zip_code = location_json["addressZipCode"]
                        store_id = location_json["StoreNumber"]

                        store_address = address_line + " " + city + ", " + state + " " + zip_code

                        print(utc2est(), site_print, Colors.GREEN + "Appointment Time Slots have been found in",
                              Colors.WARNING + home + Colors.END)

                        print(utc2est(), site_print, Colors.CYAN + "Available vaccination dates:",
                              Colors.WARNING + str(available_dates) + Colors.END)

                        print(utc2est(), site_print,
                              Colors.CYAN + 'CVS Address: ' + Colors.WARNING + store_address + Colors.END)

                        # Beginning Reservation Process
                        print('---------------------- Reservation Process Beginning ----------------------')
                        for NoADDates in range(len(available_dates)):
                            vaccine_select = None

                            # [First Dose] Soft Allocation

                            first_dose_soft_form_data = {
                                "requestMetaData": {
                                    "appName": "CVS_WEB",
                                    "lineOfBusiness": "RETAIL",
                                    "channelName": "WEB",
                                    "deviceType": "DESKTOP",
                                    "deviceToken": "7777",
                                    "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                                    "source": "ICE_WEB",
                                    "securityType": "apiKey",
                                    "responseFormat": "JSON",
                                    "type": "cn-micro-imzinventoryapp"
                                },
                                "requestPayloadData": {
                                    "allocationDate": available_dates[NoADDates],
                                    "ndc": vaccine_code_list,
                                    "storeId": store_id,
                                    "allocationType": "1"
                                }
                            }

                            first_dose_SA = s.post(first_dose_soft_url, json=first_dose_soft_form_data,
                                                   headers=first_dose_soft_headers, )

                            # General Variables
                            first_dose_status_desc = first_dose_SA.json()["responseMetaData"]["statusDesc"]
                            first_dose_status_code = first_dose_SA.json()["responseMetaData"]["statusCode"]

                            # Code Variables
                            first_dose_ndc = first_dose_SA.json()["responsePayloadData"]["data"]["ndc"]
                            first_dose_allocation_date = first_dose_SA.json()["responsePayloadData"]["data"][
                                "allocationDate"]
                            first_dose_allocation_code = first_dose_SA.json()["responsePayloadData"]["data"][
                                "allocationCode"]

                            # PFIZER NDC Code Adaptation
                            if first_dose_ndc == "59267100002" or first_dose_ndc == "59267100003":
                                print(utc2est(), site_print,
                                      Colors.CYAN + "Reserving a PFIZER appointment..." + Colors.END)
                                ndc = ["59267100002", "59267100003"]
                                vaccine_select = 'PFIZER'

                            elif first_dose_ndc == "59676058015":
                                print(utc2est(), site_print,
                                      Colors.CYAN + "Reserving a JOHNSON & JOHNSON appointment..." + Colors.END)

                            elif first_dose_ndc == "80777027399":
                                print(utc2est(), site_print,
                                      Colors.CYAN + "Reserving a MODERNA appointment..." + Colors.END)

                            # [First Dose] Available Time Slots

                            fd_time_form_params = {
                                'visitStartDate': first_dose_allocation_date,
                                'clinicId': "CVS_" + store_id
                            }

                            first_dose_AT = s.get(time_url, params=fd_time_form_params, headers=api_headers)

                            if first_dose_AT.json()["header"][
                                "statusDescription"] == "No Available Timeslots Found for Reservation":
                                print(utc2est(), site_print, Colors.WARNING + 'No Available Time Slots for',
                                      first_dose_allocation_date + ". Trying another day..." + Colors.END)
                                print(first_dose_AT.json())
                                continue

                            if first_dose_AT.json()["header"][
                                "statusDescription"] != "No Available Timeslots Found for Reservation":

                                first_dose_times_time_slots = first_dose_AT.json()["details"][0]["timeSlots"][0]

                                # [First Dose] Reserve

                                fd_reserve_form_data = {
                                    "reservation": {
                                        "clinicId": "CVS_" + store_id,
                                        "clinicType": "IMZ_STORE",
                                        "visitDateTime": first_dose_times_time_slots
                                    }
                                }

                                first_dose_R = s.post(reserve_url, json=fd_reserve_form_data, headers=api_headers,
                                                      )

                                first_dose_reserve_reservation_code = first_dose_R.json()["details"]["reservationCode"]
                                first_dose_reserve_status_desc = first_dose_R.json()["header"]["statusDescription"]
                                first_dose_reserve_visit_date_time = first_dose_R.json()["details"]["visitDateTime"]

                                # [First Dose] Reservation Frontend

                                if first_dose_reserve_status_desc == "Success":
                                    print(utc2est(),
                                          site_print,
                                          Colors.GREEN + '[First Dose] Reserved Session Successfully ----------------' + Colors.END)
                                    print(utc2est(), site_print, Colors.CYAN + "Allocation Date:",
                                          Colors.WARNING + first_dose_allocation_date + Colors.END)
                                    print(utc2est(), site_print, Colors.CYAN + "Allocation Time:",
                                          Colors.WARNING + first_dose_times_time_slots + Colors.END)
                                    print(utc2est(), site_print, Colors.CYAN + "Visit Date and Time:",
                                          Colors.WARNING + first_dose_reserve_visit_date_time + Colors.END)
                                    print('-----------------------------------------')

                                # SECOND DOSE
                                # ----------------------------------------------------------------------------------

                                # [Second Dose] Monitor

                                time.sleep(3)

                                sd_monitor_form_data = {
                                    "requestMetaData": {
                                        "appName": "CVS_WEB",
                                        "lineOfBusiness": "RETAIL",
                                        "channelName": "WEB",
                                        "deviceType": "DESKTOP",
                                        "deviceToken": "7777",
                                        "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                                        "source": "ICE_WEB",
                                        "securityType": "apiKey",
                                        "responseFormat": "JSON",
                                        "type": "cn-dep"
                                    },
                                    "requestPayloadData": {
                                        "selectedImmunization": [
                                            "CVD"
                                        ],
                                        "distanceInMiles": 35,
                                        "imzData": [
                                            {
                                                "imzType": "CVD",
                                                "ndc": first_dose_ndc,
                                                "firstDoseDate": first_dose_allocation_date,
                                                "allocationType": "2"
                                            }
                                        ],
                                        "destination": {
                                            "storeNumber": [
                                                store_id
                                            ]
                                        }
                                    }
                                }

                                second_dose_GIS = s.post(monitor_url, json=sd_monitor_form_data,
                                                         headers=sd_monitor_headers,
                                                         )

                                if geo_code_get.status_code != 200:
                                    print(utc2est(), site_print,
                                          Colors.FAIL + Colors.BOLD + "Request UNSUCCESSFULLY Received by the API. STATUS CODE:",
                                          str(geo_code_get.status_code) + Colors.END)
                                    exit(1)

                                second_dose_monitor_status_desc = second_dose_GIS.json()["responseMetaData"][
                                    "statusDesc"]
                                second_dose_monitor_status_code = second_dose_GIS.json()["responseMetaData"][
                                    "statusCode"]

                                SD_unknown_error = re.findall('Inventory unavailable', second_dose_monitor_status_desc)
                                if SD_unknown_error:
                                    print(error_handle("unknown"))

                                if second_dose_monitor_status_desc == "No stores with immunizations found":
                                    print(utc2est(), site_print,
                                          Colors.WARNING + "There are no Second Dose Availabilities at the location you selected." + Colors.END)

                                if second_dose_monitor_status_desc == "Success":

                                    sd_avail_dates_available_dates = \
                                        second_dose_GIS.json()["responsePayloadData"]["locations"][0][
                                            "imzAdditionalData"][
                                            0][
                                            "availableDates"]

                                    # [Second Dose] Soft Allocation

                                    sd_allocation_form_data = {
                                        "requestMetaData": {
                                            "appName": "CVS_WEB",
                                            "lineOfBusiness": "RETAIL",
                                            "channelName": "WEB",
                                            "deviceType": "DESKTOP",
                                            "deviceToken": "7777",
                                            "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                                            "source": "ICE_WEB",
                                            "securityType": "apiKey",
                                            "responseFormat": "JSON",
                                            "type": "cn-micro-imzinventoryapp"
                                        },
                                        "requestPayloadData": {
                                            "allocationDate": sd_avail_dates_available_dates[0],
                                            "ndc": first_dose_ndc,
                                            "storeId": store_id,
                                            "allocationType": "2",
                                            "firstDoseDate": first_dose_allocation_date
                                        }
                                    }

                                    second_dose_SA = s.post(first_dose_soft_url, json=sd_allocation_form_data,
                                                            headers=first_dose_soft_headers,
                                                            )

                                    second_dose_soft_allocation_date = \
                                        second_dose_SA.json()["responsePayloadData"]["data"][
                                            "allocationDate"]
                                    second_dose_soft_allocation_code = \
                                        second_dose_SA.json()["responsePayloadData"]["data"][
                                            "allocationCode"]

                                    # [Second Dose] Available Time Slots

                                    sd_time_form_params = {
                                        'visitStartDate': second_dose_soft_allocation_date,
                                        'clinicId': "CVS_" + store_id
                                    }

                                    second_dose_AT = s.get(time_url, params=sd_time_form_params, headers=api_headers,
                                                           )

                                    second_dose_times_time_slots = second_dose_AT.json()["details"][0]["timeSlots"][0]

                                    # [Second Dose] Reserve

                                    sd_reserve_form_data = {
                                        "reservation": {
                                            "clinicId": "CVS_" + store_id,
                                            "clinicType": "IMZ_STORE",
                                            "visitDateTime": second_dose_times_time_slots
                                        }
                                    }

                                    second_dose_R = s.post(reserve_url, json=sd_reserve_form_data, headers=api_headers,
                                                           )

                                    second_dose_reserve_status_desc = second_dose_R.json()["header"][
                                        "statusDescription"]
                                    second_dose_reserve_reservation_code = second_dose_R.json()["details"][
                                        "reservationCode"]
                                    second_dose_reserve_visit_date_time = second_dose_R.json()["details"][
                                        "visitDateTime"]

                                    # [Second Dose] Reservation Frontend

                                    if second_dose_reserve_status_desc == "Success":
                                        print(utc2est(),
                                              site_print,
                                              Colors.GREEN + '[Second Dose] Reserved Session Successfully ----------------' + Colors.END)
                                        print(utc2est(), site_print, Colors.CYAN + "Available Dates:",
                                              Colors.WARNING + str(sd_avail_dates_available_dates) + Colors.END)
                                        print(utc2est(), site_print, Colors.CYAN + "Allocation Date:",
                                              Colors.WARNING + second_dose_soft_allocation_date + Colors.END)
                                        print(utc2est(), site_print, Colors.CYAN + "Allocation Time:",
                                              Colors.WARNING + second_dose_times_time_slots + Colors.END)
                                        print(utc2est(), site_print, Colors.CYAN + "Visit Date and Time:",
                                              Colors.WARNING + second_dose_reserve_visit_date_time + Colors.END)

                                        # Submit Registration #

                                        print('---------------------- Submission Process Beginning ----------------------')
                                        print(utc2est(), site_print,
                                              Colors.CYAN + Colors.BOLD + "Beginning Submission Stage..." + Colors.END)

                                        submit_registration_PFIZER_form_data = {
                                            "requestMetaData": {
                                                "appName": "CVS_WEB",
                                                "lineOfBusiness": "RETAIL",
                                                "channelName": "WEB",
                                                "deviceType": "DESKTOP",
                                                "deviceToken": "7777",
                                                "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                                                "source": "ICE_WEB",
                                                "securityType": "apiKey",
                                                "responseFormat": "JSON",
                                                "type": "cn-dep"
                                            },
                                            "requestPayloadData": {
                                                "data": {
                                                    "patientId": "",
                                                    "encryptionType": "",
                                                    "patientData": {
                                                        "firstName": Patient.first_name,
                                                        "lastName": Patient.last_name,
                                                        "DOB": Patient.dob,
                                                        "gender": Patient.gender,
                                                        "emailId": Patient.email,
                                                        "phoneNumber": Patient.phone,
                                                        "address": {
                                                            "addressLine1": Patient.address_1,
                                                            "addressLine2": Patient.address_2,
                                                            "city": Patient.city,
                                                            "state": Patient.state,
                                                            "zip": Patient.zip_code
                                                        }
                                                    },
                                                    "immunizationAnswers": [
                                                        {
                                                            "questionId": "2",
                                                            "questionText": "Have you ever had a severe allergic reaction (e.g., anaphylaxis) to something? For example, a reaction for which you were treated with epinephrine, or EpiPen, or for which you had to go to the hospital? If yes, what are you allergic to?",
                                                            "answerValue": question_values(Questions.question_id_2),
                                                            "answerText": Questions.question_id_2,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55404"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "3",
                                                            "questionText": "Had you ever had a severe allergic reaction after receiving a COVID-19 vaccine?",
                                                            "answerValue": question_values(Questions.question_id_3),
                                                            "answerText": Questions.question_id_3,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55406"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "4",
                                                            "questionText": "Have you ever had a severe allergic reaction after receiving another vaccine or injectable medication?",
                                                            "answerValue": question_values(Questions.question_id_4),
                                                            "answerText": Questions.question_id_4,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55408"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "5",
                                                            "questionText": "Have you ever had a severe allergic reaction after receiving Polyethylene Glycol?",
                                                            "answerValue": question_values(Questions.question_id_5),
                                                            "answerText": Questions.question_id_5,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55410"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "6",
                                                            "questionText": "Have you ever had a severe allergic reaction related to receiving Polysorbate or products containing Polysorbate?",
                                                            "answerValue": question_values(Questions.question_id_6),
                                                            "answerText": Questions.question_id_6,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55412"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "7",
                                                            "questionText": "For women, are you currently pregnant or breastfeeding?",
                                                            "answerValue": question_values(Questions.question_id_7),
                                                            "answerText": Questions.question_id_7,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55414"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "11",
                                                            "questionText": "Do you have a bleeding disorder or are you taking a blood thinner?",
                                                            "answerValue": question_values(Questions.question_id_11),
                                                            "answerText": Questions.question_id_11,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55422"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "12",
                                                            "questionText": "Have you received any vaccines in the past 14 days?",
                                                            "answerValue": question_values(Questions.question_id_12),
                                                            "answerText": Questions.question_id_12,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55424"
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "questionId": "13",
                                                            "questionText": "Have you received monoclonal antibodies or convalescent plasma as part of a COVID-19 treatment in the past 90 days?",
                                                            "answerValue": question_values(Questions.question_id_13),
                                                            "answerText": Questions.question_id_13,
                                                            "answerFreeText": "",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "55426"
                                                                }
                                                            ]
                                                        }
                                                    ],
                                                    "additionalSubmitData": {
                                                        "optionalQuestion": [
                                                            {
                                                                "questionId": "1",
                                                                "questionText": "Are you sick today?",
                                                                "errorMessage": "Please enter your health today",
                                                                "imzTypeCode": [
                                                                    {
                                                                        "code": "CVD",
                                                                        "refId": "55402"
                                                                    }
                                                                ],
                                                                "answerText": Questions.question_id_1,
                                                                "answerValue": question_values(
                                                                    Questions.question_id_1)
                                                            },
                                                            {
                                                                "questionId": "8",
                                                                "questionText": "In the past 14 days, have you teste positive for COVID-19?",
                                                                "errorMessage": "Please enter blood or blood produce issues",
                                                                "imzTypeCode": [
                                                                    {
                                                                        "code": "CVD",
                                                                        "refId": "55416"
                                                                    }
                                                                ],
                                                                "answerText": Questions.question_id_8,
                                                                "answerValue": question_values(
                                                                    Questions.question_id_8)
                                                            },
                                                            {
                                                                "questionId": "9",
                                                                "questionText": "In the past 14 days, have you been in close contact with anyone who tested positive for COVID-19?",
                                                                "errorMessage": "Please enter immune system problems",
                                                                "imzTypeCode": [
                                                                    {
                                                                        "code": "CVD",
                                                                        "refId": "55418"
                                                                    }
                                                                ],
                                                                "answerText": Questions.question_id_9,
                                                                "answerValue": question_values(
                                                                    Questions.question_id_9)
                                                            },
                                                            {
                                                                "questionId": "10",
                                                                "questionText": "Do you currently have fever, chills, cough, shortness of breath, difficulty breathing, fatigue, muscle or body aches, headache, new loss of taste or smell, sore throat, nausea, vomiting, or diarrhea?",
                                                                "errorMessage": "Please enter immune-suppressing treatments",
                                                                "imzTypeCode": [
                                                                    {
                                                                        "code": "CVD",
                                                                        "refId": "55420"
                                                                    }
                                                                ],
                                                                "answerText": Questions.question_id_10,
                                                                "answerValue": question_values(
                                                                    Questions.question_id_10)

                                                            }
                                                        ]
                                                    },
                                                    "paymentMode": insurance_data,
                                                    "immunizationEligibilityAnswers": [
                                                        {
                                                            "questionId": "2",
                                                            "questionText": "Which group applies?",
                                                            "answerText": Questions.eligibility,
                                                            "answerFreeText": Questions.eligibility,
                                                            "answerValue": "1",
                                                            "imzTypeCode": [
                                                                {
                                                                    "code": "CVD",
                                                                    "refId": "57506"
                                                                }
                                                            ]
                                                        }
                                                    ],
                                                    "immunizationSchedule": [
                                                        {
                                                            "schedulerRefId": "CVS_" + str(store_id),
                                                            "schedulerRefType": "IMZ_STORE",
                                                            "reservationCode": first_dose_reserve_reservation_code,
                                                            "selectedTimezone": "America/New_York",
                                                            "selectedUTCTimestamp": first_dose_reserve_visit_date_time,
                                                            "selectedImmunization": [
                                                                {
                                                                    "code": "CVD",
                                                                    "type": "COVID",
                                                                    "doseNumber": "1",
                                                                    "ndcCode": "59267100002",
                                                                    "ndcName": "PFIZER COVID-19 VACCINE (EUA)",
                                                                    "allocationCode": first_dose_allocation_code
                                                                }
                                                            ],
                                                            "facility": {
                                                                "facilityId": store_id
                                                            }
                                                        },
                                                        {
                                                            "schedulerRefId": "CVS_" + store_id,
                                                            "schedulerRefType": "IMZ_STORE",
                                                            "reservationCode": second_dose_reserve_reservation_code,
                                                            "selectedTimezone": "America/New_York",
                                                            "selectedUTCTimestamp": second_dose_reserve_visit_date_time,
                                                            "selectedImmunization": [
                                                                {
                                                                    "code": "CVD",
                                                                    "type": "COVID",
                                                                    "doseNumber": "2",
                                                                    "ndcCode": "59267100002",
                                                                    "ndcName": "PFIZER COVID-19 VACCINE (EUA)",
                                                                    "allocationCode": second_dose_soft_allocation_code
                                                                }
                                                            ],
                                                            "facility": {
                                                                "facilityId": store_id
                                                            }
                                                        }
                                                    ],
                                                    "additionalLegalAnswers": [
                                                        {
                                                            "questionId": "race",
                                                            "answerValue": Patient.race_value,
                                                            "answerText": Patient.race
                                                        },
                                                        {
                                                            "questionId": "ethnicity",
                                                            "answerValue": Patient.ethnicity_value,
                                                            "answerText": Patient.ethnicity
                                                        }
                                                    ],
                                                    "isGuest": "Y",
                                                    "authType": "Guest_Auth",
                                                    "facilityId": store_id,
                                                    "sameDaySchedule": False,
                                                    "source": "instore-clinic",
                                                    "uiFlow": "CVD_DOSE_ONE_TWO",
                                                    "inStoreIndicator": "N"
                                                }
                                            }
                                        }

                                        if vaccine_select == 'PFIZER':
                                            print(utc2est(), site_print,
                                                  Colors.CYAN + "Reserving for Pfizer..." + Colors.END)
                                            submit_registration_post = s.post(submit_registration_url,
                                                                              json=submit_registration_PFIZER_form_data,
                                                                              headers=submit_registration_headers,
                                                                              )

                                            submit_response_status_desc = submit_registration_post.json()["responseMetaData"][
                                                "statusDesc"]

                                            if submit_response_status_desc == "Success":
                                                print(utc2est(), site_print,
                                                      Colors.GREEN + Colors.BOLD + "Your CVS Appointment has been Successfully Scheduled." + Colors.END)
                                                print(utc2est(), site_print,
                                                      Colors.WARNING + Colors.BOLD + 'Store Details ----------------' + Colors.END)
                                                print(utc2est(), site_print,
                                                      Colors.CYAN + 'CVS Address: ' + Colors.WARNING + Colors.BOLD + store_address + Colors.END)
                                                print(utc2est(), site_print,
                                                      Colors.WARNING + Colors.BOLD + 'Time Details ----------------' + Colors.END)
                                                print(utc2est(), site_print, Colors.CYAN + "First Dose Time:",
                                                      Colors.WARNING + Colors.BOLD + first_dose_times_time_slots + Colors.END)
                                                print(utc2est(), site_print, Colors.CYAN + "Second Dose Time:",
                                                      Colors.WARNING + Colors.BOLD + second_dose_times_time_slots + Colors.END)

                                                def webhook():
                                                    Webhook = DiscordWebhook(
                                                        url=Discord_Webhook.url)

                                                    embed = DiscordEmbed(title="Appointment Successfully Scheduled at CVS",
                                                                         url='https://www.cvs.com/immunizations/covid-19-vaccine',
                                                                         color=15987431)

                                                    embed.set_footer(text='Covid-19 Appointment Monitor')

                                                    embed.set_timestamp()

                                                    embed.add_embed_field(name='CVS Location:', color=15987431,
                                                                          value=store_address)
                                                    embed.add_embed_field(name='First Dose Date:', color=15987431,
                                                                          value=first_dose_times_time_slots)
                                                    embed.add_embed_field(name='Second Dose Date:', color=15987431,
                                                                          value=second_dose_times_time_slots)

                                                    Webhook.add_embed(embed)

                                                    Webhook.execute()

                                                if Discord_Webhook.url:
                                                    webhook()
                                                exit(1)
                                            if submit_response_status_desc != "Success":
                                                print(utc2est(), site_print,
                                                      Colors.FAIL + 'Your CVS Appointment Submission has been unsuccessfully' + Colors.END)
                                                print(utc2est(), site_print,
                                                      "CVS Submission Data ----------------" + Colors.END)
                                                print(submit_registration_post.status_code)
                                                print(submit_registration_PFIZER_form_data)
                                                exit(1)

    except ProxyError or MaxRetryError:
        print(utc2est(), site_print,
              Colors.FAIL + 'Something went wrong with your IP Address (ProxyError). Please restart the application' + Colors.END)
        input("Press Enter to close the application.")


if __name__ == '__main__':
    covid_monitor()
