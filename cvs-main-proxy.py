import requests
import time
import re
from datetime import date
from datetime import datetime
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from json.decoder import JSONDecodeError
from discord_webhook import DiscordEmbed, DiscordWebhook

s = requests.Session()


class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def utc2est():
    current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return str(current) + ' EST'


site_print = colors.CYAN + "[VACCINE SEARCH]" + colors.END

today = date.today()

api_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'referer': 'https://www.cvs.com/',
    'origin': 'https://www.cvs.com',
    'x-api-key': 'rFd64We9AwyvAFzIXsoSp8bYuewNohOZ'
}

vaccine_codes = {
    'PFIZER1': "59267100002",
    'PFIZER': "59267100003",
}

# VALUE CONTROLS
# -------------------
proxy = ''  # 166.122.33.44:55555:axvacl:lewbbf

vaccine_controls = ["PFIZER1", "PFIZER"]

radius = input("Radius: ")

discord_webhook_url = ''


class set_proxy:
    (IPv4, Port, username, password) = proxy.split(':')

    ip = IPv4 + ':' + Port

    proxies = {
        "http": "http://" + username + ":" + password + "@" + ip,
        "https": "http://" + username + ":" + password + "@" + ip,
    }


home = input("Please enter your CVS location: ")


class patient_info:
    first_name = 'Jane'
    last_name = 'Doe'
    dob = '1980-03-09'  # ex. 2000-07-08
    gender = ''  # M or F
    email = 'janedoe@gmail.com'
    phone = '1231231234'  # ex. 6178626406
    address_1 = 'Jane Doe Road'
    address_2 = None
    city = 'Doe'
    state = 'MA'  # ex. MA
    zip_code = '12345'
    race = 'White'
    race_value = '2106-3'
    ethnicity = 'Not Hispanic or Latino or Spanish Origin'
    ethnicity_value = 'N'
    insurance_id = ''
    non_medicare = True


# patient questions values --> 1: Yes, 2: No, 3: I don't know
# (experimental) currently only works for "America/New_York" time zone
# ethnicity value --> U: Unknown, N: Not Hispanic..., Y: Is Hispanic...


class patient_questions:
    question_id_1 = "I don't know"
    question_id_2 = 'No'
    question_id_3 = 'No'
    question_id_4 = 'No'
    question_id_5 = 'No'
    question_id_6 = 'No'
    question_id_7 = 'No'
    question_id_8 = 'No'
    question_id_9 = 'No'
    question_id_10 = 'No'
    question_id_11 = 'No'
    question_id_12 = 'No'
    question_id_13 = 'No'
    eligibility = "Age 16+ with high-risk conditions"  # Can be custom. Doesn't need to be preset.


class patient_question_values:
    question_id_1 = 3
    question_id_2 = 2
    question_id_3 = 2
    question_id_4 = 2
    question_id_5 = 2
    question_id_6 = 2
    question_id_7 = 2
    question_id_8 = 2
    question_id_9 = 2
    question_id_10 = 2
    question_id_11 = 2
    question_id_12 = 2
    question_id_13 = 2
    eligibility = '1'  # Keep 1 for true


if patient_info.non_medicare:
    insurance_data = {
        "typeId": 6,
        "typeText": "Insurance",
        "insuranceData": [
            {
                "cardHolderFirstName": patient_info.first_name,
                "cardHolderLastName": patient_info.last_name,
                "groupId": None,
                "insuranceType": "secondary",
                "isPatientPrimaryCardholder": "Y",
                "memberId": patient_info.insurance_id,
                "provider": "Jane Doe's Insurance",
                "relationshipWithCardHolder": "1",
                "payerId": None
            }
        ]
    }

if not patient_info.non_medicare:
    insurance_data = {
        "typeId": 5,
        "typeText": "Medicare",
        "medicareData": {
            "memberId": patient_info.insurance_id
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
    print(utc2est(), site_print, colors.FAIL + "Please enter in a vaccine(s).", colors.END)
    exit(1)


def startup_print(vaccine_selection, cvs_location):
    print(utc2est(), site_print, colors.CYAN + "Monitor for CVS in", colors.WARNING + cvs_location,
          colors.CYAN + "has begun..." + colors.END)
    print(utc2est(), site_print, colors.CYAN + "Looking for:", str(vaccine_selection) + colors.END)


def covid_monitor():
    try:
        for monitor_loop in range(9999):

            # [First Dose] Monitor

            def monitor_loop_status(loop):
                if loop == 1:
                    print(utc2est(), site_print,
                          colors.BOLD + "No appointments available at the location you selected. Monitoring for appointments..." + colors.END)
                elif loop == 360:
                    print(utc2est(), site_print, colors.BOLD + "Still searching for appointments..." + colors.END)
                elif loop == 540:
                    print(utc2est(), site_print, colors.BOLD + "Still searching for appointments..." + colors.END)
                elif loop == 720:
                    print(utc2est(), site_print, colors.BOLD + "Still searching for appointments..." + colors.END)
                elif loop == 900:
                    print(utc2est(), site_print, colors.BOLD + "Still searching for appointments..." + colors.END)

            time.sleep(10)

            class monitor:
                headers = {
                    'accept': 'application/json',
                    'referer': 'https://www.cvs.com/vaccine/intake/store/cvd-store-select/first-dose-select',
                    'origin': 'https://www.cvs.com',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
                    'sec-ch-ua': '"Google Chrome";v="89"',
                    'sec-ch-ua-mobile': '?0',
                    'accept-type': 'application/json'
                }
                form_data = {
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
                url = 'https://www.cvs.com/Services/ICEAGPV1/immunization/1.0.0/getIMZStores'

            geo_code_get = s.post(monitor.url, json=monitor.form_data, headers=monitor.headers)

            if geo_code_get.status_code != 200:
                print(utc2est(), site_print,
                      colors.FAIL + colors.BOLD + "Request UNSUCCESSFULLY Received by the API. STATUS CODE:",
                      str(geo_code_get.status_code) + colors.END)
                exit(1)
            if monitor_loop == 0:
                if geo_code_get.status_code == 200:
                    print(utc2est(), site_print,
                          colors.CYAN + colors.BOLD + "Request Successfully Received by the API." + colors.END)

            class geo_code:
                status_desc = geo_code_get.json()["responseMetaData"]["statusDesc"]
                status_code = geo_code_get.json()["responseMetaData"]["statusCode"]

            unknown_error = re.findall('Inventory unavailable', geo_code.status_desc)
            if unknown_error:
                print(utc2est(), site_print,
                      colors.FAIL + colors.BOLD + "Something went wrong. Please contact the owner." + colors.END)
                print(utc2est(), site_print,
                      colors.FAIL + colors.BOLD + "Description:", geo_code.status_desc + colors.END)
                print(utc2est(), site_print,
                      colors.FAIL + colors.BOLD + "Status Code:", geo_code.status_code + colors.END)
                exit(1)

            if geo_code.status_desc == 'Failed calling getStoreDetails -Locations Not Found':
                print(utc2est(), site_print,
                      colors.FAIL + colors.BOLD + "The location you typed in could not be located or might be in a format that is unrecognizable. Please type in a new location. (Ex. 'Wayland, MA', '01778')" + colors.END)
                exit(1)

            if geo_code.status_desc == "No stores with immunizations found":
                monitor_loop_status(monitor_loop)
                continue

            if geo_code.status_desc == "Did you mean" or geo_code.status_desc == "Success":
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
                    time.sleep(3)

                    # [First Dose] Geo Code Submitting

                    getIMZStores = s.post(monitor.url, json=geo_form_data, headers=monitor.headers,
                                          proxies=set_proxy.proxies)

                    if getIMZStores.json()["responseMetaData"]["statusDesc"] == "No stores with immunizations found":
                        monitor_loop_status(IMZRetry)
                        continue

                    if getIMZStores.json()["responseMetaData"]["statusDesc"] == "Success":
                        print(utc2est(), site_print, colors.CYAN + "GEO LOCATION CODES FOUND:",
                              colors.WARNING + longitude + ",", latitude + colors.END)

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

                        print(utc2est(), site_print, colors.GREEN + "Appointment Time Slots have been found in",
                              colors.WARNING + home + colors.END)

                        print(utc2est(), site_print, colors.CYAN + "Available vaccination dates:",
                              colors.WARNING + str(available_dates) + colors.END)

                        print(utc2est(), site_print,
                              colors.CYAN + 'CVS Address: ' + colors.WARNING + store_address + colors.END)

                        break
                    break
                break
            break

        def dose_reserve():

            # Beginning Reservation Process
            print('---------------------- Reservation Process Beginning ----------------------')
            for NoADDates in range(len(available_dates)):

                # [First Dose] Soft Allocation

                class first_dose_soft:
                    url = 'https://www.cvs.com/services/ICEAGPV1/inventory/1.0.0/softAllocation'
                    fd_headers = {
                        'accept': 'application/json',
                        'referer': 'https://www.cvs.com/vaccine/intake/store/cvd-store-select/dose-select',
                        'origin': 'https://www.cvs.com',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
                        'sec-ch-ua': '"Google Chrome";v="89"',
                        'sec-ch-ua-mobile': '?0',
                        'accept-type': 'application/json'
                    }
                    form_data = {
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

                first_dose_SA = s.post(first_dose_soft.url, json=first_dose_soft.form_data,
                                       headers=first_dose_soft.fd_headers, proxies=set_proxy.proxies)

                class first_dose:
                    # General Variables
                    status_desc = first_dose_SA.json()["responseMetaData"]["statusDesc"]
                    status_code = first_dose_SA.json()["responseMetaData"]["statusCode"]

                    # Code Variables
                    ndc = first_dose_SA.json()["responsePayloadData"]["data"]["ndc"]
                    allocation_date = first_dose_SA.json()["responsePayloadData"]["data"]["allocationDate"]
                    allocation_code = first_dose_SA.json()["responsePayloadData"]["data"]["allocationCode"]

                    # PFIZER NDC Code Adaptation
                    if ndc == "59267100002" or "59267100003":
                        print(utc2est(), site_print,
                              colors.CYAN + "Reserving a PFIZER appointment..." + colors.END)
                        ndc = ["59267100002", "59267100003"]
                        __vaccine__ = 'PFIZER'

                    elif ndc == "59676058015":
                        print(utc2est(), site_print,
                              colors.CYAN + "Reserving a JOHNSON & JOHNSON appointment..." + colors.END)

                    elif ndc == "80777027399":
                        print(utc2est(), site_print,
                              colors.CYAN + "Reserving a MODERNA appointment..." + colors.END)

                # [First Dose] Available Time Slots

                time_url = 'https://api.cvshealth.com/scheduler/v3/clinics/availabletimeslots'
                fd_time_form_params = {
                    'visitStartDate': first_dose.allocation_date,
                    'clinicId': "CVS_" + store_id
                }

                first_dose_AT = s.get(time_url, params=fd_time_form_params, headers=api_headers)

                if first_dose_AT.json()["header"]["statusDescription"] == "No Available Timeslots Found for Reservation":
                    print(utc2est(), site_print, colors.WARNING + 'No Available Time Slots for',
                          first_dose.allocation_date + ". Trying another day..." + colors.END)
                    print(first_dose_AT.json())
                    continue

                if first_dose_AT.json()["header"]["statusDescription"] != "No Available Timeslots Found for Reservation":

                    class first_dose_times:
                        time_slots = first_dose_AT.json()["details"][0]["timeSlots"][0]

                    # [First Dose] Reserve

                    reserve_url = 'https://api.cvshealth.com/scheduler/v3/clinics/reservation'

                    fd_reserve_form_data = {
                        "reservation": {
                            "clinicId": "CVS_" + store_id,
                            "clinicType": "IMZ_STORE",
                            "visitDateTime": first_dose_times.time_slots
                        }
                    }

                    first_dose_R = s.post(reserve_url, json=fd_reserve_form_data, headers=api_headers,
                                          proxies=set_proxy.proxies)

                    class first_dose_reserve:
                        reservation_code = first_dose_R.json()["details"]["reservationCode"]
                        status_desc = first_dose_R.json()["header"]["statusDescription"]
                        visit_date_time = first_dose_R.json()["details"]["visitDateTime"]

                    # [First Dose] Reservation Frontend

                    if first_dose_reserve.status_desc == "Success":
                        print(utc2est(),
                              site_print,
                              colors.GREEN + '[First Dose] Reserved Session Successfully ----------------' + colors.END)
                        print(utc2est(), site_print, colors.CYAN + "Allocation Date:",
                              colors.WARNING + first_dose.allocation_date + colors.END)
                        print(utc2est(), site_print, colors.CYAN + "Allocation Time:",
                              colors.WARNING + first_dose_times.time_slots + colors.END)
                        print(utc2est(), site_print, colors.CYAN + "Visit Date and Time:",
                              colors.WARNING + first_dose_reserve.visit_date_time + colors.END)
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
                                    "ndc": first_dose.ndc,
                                    "firstDoseDate": first_dose.allocation_date,
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
                    sd_monitor_headers = {
                        'accept': 'application/json',
                        'referer': 'https://www.cvs.com/vaccine/intake/store/cvd-store-select/second-dose-select',
                        'origin': 'https://www.cvs.com',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
                        'sec-ch-ua': '"Google Chrome";v="89"',
                        'sec-ch-ua-mobile': '?0',
                        'accept-type': 'application/json'
                    }

                    second_dose_GIS = s.post(monitor.url, json=sd_monitor_form_data,
                                             headers=sd_monitor_headers,
                                             proxies=set_proxy.proxies)

                    if geo_code_get.status_code != 200:
                        print(utc2est(), site_print,
                              colors.FAIL + colors.BOLD + "Request UNSUCCESSFULLY Received by the API. STATUS CODE:",
                              str(geo_code_get.status_code) + colors.END)
                        exit(1)

                    class second_dose_monitor:
                        status_desc = second_dose_GIS.json()["responseMetaData"]["statusDesc"]
                        status_code = second_dose_GIS.json()["responseMetaData"]["statusCode"]

                    SD_unknown_error = re.findall('Inventory unavailable', second_dose_monitor.status_desc)
                    if SD_unknown_error:
                        print(utc2est(), site_print,
                              colors.FAIL + colors.BOLD + "Something went wrong. Please contact the owner." + colors.END)
                        print(utc2est(), site_print,
                              colors.FAIL + colors.BOLD + "Description:",
                              geo_code.status_desc + colors.END)
                        print(utc2est(), site_print,
                              colors.FAIL + colors.BOLD + "Status Code:",
                              geo_code.status_code + colors.END)
                        exit(1)

                    if second_dose_monitor.status_desc == "No stores with immunizations found":
                        print(utc2est(), site_print,
                              colors.WARNING + "There are no Second Dose Availabilities at the location you selected." + colors.END)

                    if second_dose_monitor.status_desc == "Success":

                        class sd_avail_dates:
                            available_dates = \
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
                                "allocationDate": sd_avail_dates.available_dates[0],
                                "ndc": first_dose.ndc,
                                "storeId": store_id,
                                "allocationType": "2",
                                "firstDoseDate": first_dose.allocation_date
                            }
                        }

                        second_dose_SA = s.post(first_dose_soft.url, json=sd_allocation_form_data,
                                                headers=first_dose_soft.fd_headers,
                                                proxies=set_proxy.proxies)

                        class second_dose_soft:
                            allocation_date = second_dose_SA.json()["responsePayloadData"]["data"][
                                "allocationDate"]
                            allocation_code = second_dose_SA.json()["responsePayloadData"]["data"][
                                "allocationCode"]

                        # [Second Dose] Available Time Slots

                        sd_time_form_params = {
                            'visitStartDate': second_dose_soft.allocation_date,
                            'clinicId': "CVS_" + store_id
                        }

                        second_dose_AT = s.get(time_url, params=sd_time_form_params, headers=api_headers,
                                               proxies=set_proxy.proxies)

                        class second_dose_times:
                            time_slots = second_dose_AT.json()["details"][0]["timeSlots"][0]

                        # [Second Dose] Reserve

                        sd_reserve_form_data = {
                            "reservation": {
                                "clinicId": "CVS_" + store_id,
                                "clinicType": "IMZ_STORE",
                                "visitDateTime": second_dose_times.time_slots
                            }
                        }

                        second_dose_R = s.post(reserve_url, json=sd_reserve_form_data, headers=api_headers,
                                               proxies=set_proxy.proxies)

                        class second_dose_reserve:
                            status_desc = second_dose_R.json()["header"]["statusDescription"]
                            reservation_code = second_dose_R.json()["details"]["reservationCode"]
                            visit_date_time = second_dose_R.json()["details"]["visitDateTime"]

                        # [Second Dose] Reservation Frontend

                        def sd_reservation_frontend():
                            print(utc2est(),
                                  site_print,
                                  colors.GREEN + '[Second Dose] Reserved Session Successfully ----------------' + colors.END)
                            print(utc2est(), site_print, colors.CYAN + "Available Dates:",
                                  colors.WARNING + str(sd_avail_dates.available_dates) + colors.END)
                            print(utc2est(), site_print, colors.CYAN + "Allocation Date:",
                                  colors.WARNING + second_dose_soft.allocation_date + colors.END)
                            print(utc2est(), site_print, colors.CYAN + "Allocation Time:",
                                  colors.WARNING + second_dose_times.time_slots + colors.END)
                            print(utc2est(), site_print, colors.CYAN + "Visit Date and Time:",
                                  colors.WARNING + second_dose_reserve.visit_date_time + colors.END)

                        if second_dose_reserve.status_desc == "Success":
                            sd_reservation_frontend()

                    # Submit Registration #

                    print('---------------------- Submission Process Beginning ----------------------')
                    print(utc2est(), site_print,
                          colors.CYAN + colors.BOLD + "Beginning Submission Stage..." + colors.END)

                    def submit_reservation():

                        class submit_registration:
                            url = 'https://www.cvs.com/Services/ICEAGPV1/immunization/1.0.0/submitImzRegistration'
                            headers = {
                                'accept': 'application/json',
                                'referer': 'https://www.cvs.com/vaccine/intake/store/consent',
                                'origin': 'https://www.cvs.com',
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
                                'sec-ch-ua': '"Google Chrome";v="89"',
                                'sec-ch-ua-mobile': '?0',
                                'accept-type': 'application/json',
                                'x-distil-ajax': 'xebztatfusvxtdxdzzerd'
                            }
                            PFIZER_form_data = {
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
                                            "firstName": patient_info.first_name,
                                            "lastName": patient_info.last_name,
                                            "DOB": patient_info.dob,
                                            "gender": patient_info.gender,
                                            "emailId": patient_info.email,
                                            "phoneNumber": patient_info.phone,
                                            "address": {
                                                "addressLine1": patient_info.address_1,
                                                "addressLine2": patient_info.address_2,
                                                "city": patient_info.city,
                                                "state": patient_info.state,
                                                "zip": patient_info.zip_code
                                            }
                                        },
                                        "immunizationAnswers": [
                                            {
                                                "questionId": "2",
                                                "questionText": "Have you ever had a severe allergic reaction (e.g., anaphylaxis) to something? For example, a reaction for which you were treated with epinephrine, or EpiPen, or for which you had to go to the hospital? If yes, what are you allergic to?",
                                                "answerValue": patient_question_values.question_id_2,
                                                "answerText": patient_questions.question_id_2,
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
                                                "answerValue": patient_question_values.question_id_3,
                                                "answerText": patient_questions.question_id_3,
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
                                                "answerValue": patient_question_values.question_id_4,
                                                "answerText": patient_questions.question_id_4,
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
                                                "answerValue": patient_question_values.question_id_5,
                                                "answerText": patient_questions.question_id_5,
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
                                                "answerValue": patient_question_values.question_id_6,
                                                "answerText": patient_questions.question_id_6,
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
                                                "answerValue": patient_question_values.question_id_7,
                                                "answerText": patient_questions.question_id_7,
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
                                                "answerValue": patient_question_values.question_id_11,
                                                "answerText": patient_questions.question_id_11,
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
                                                "answerValue": patient_question_values.question_id_12,
                                                "answerText": patient_questions.question_id_12,
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
                                                "answerValue": patient_question_values.question_id_13,
                                                "answerText": patient_questions.question_id_13,
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
                                                    "answerText": patient_questions.question_id_1,
                                                    "answerValue": patient_question_values.question_id_1
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
                                                    "answerText": patient_questions.question_id_8,
                                                    "answerValue": patient_question_values.question_id_8
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
                                                    "answerText": patient_questions.question_id_9,
                                                    "answerValue": patient_question_values.question_id_9
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
                                                    "answerText": patient_questions.question_id_10,
                                                    "answerValue": patient_question_values.question_id_10
                                                }
                                            ]
                                        },
                                        "paymentMode": insurance_data,
                                        "immunizationEligibilityAnswers": [
                                            {
                                                "questionId": "2",
                                                "questionText": "Which group applies?",
                                                "answerText": patient_questions.eligibility,
                                                "answerFreeText": patient_questions.eligibility,
                                                "answerValue": patient_question_values.eligibility,
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
                                                "reservationCode": first_dose_reserve.reservation_code,
                                                "selectedTimezone": "America/New_York",
                                                "selectedUTCTimestamp": first_dose_reserve.visit_date_time,
                                                "selectedImmunization": [
                                                    {
                                                        "code": "CVD",
                                                        "type": "COVID",
                                                        "doseNumber": "1",
                                                        "ndcCode": "59267100002",
                                                        "ndcName": "PFIZER COVID-19 VACCINE (EUA)",
                                                        "allocationCode": first_dose.allocation_code
                                                    }
                                                ],
                                                "facility": {
                                                    "facilityId": store_id
                                                }
                                            },
                                            {
                                                "schedulerRefId": "CVS_" + store_id,
                                                "schedulerRefType": "IMZ_STORE",
                                                "reservationCode": second_dose_reserve.reservation_code,
                                                "selectedTimezone": "America/New_York",
                                                "selectedUTCTimestamp": second_dose_reserve.visit_date_time,
                                                "selectedImmunization": [
                                                    {
                                                        "code": "CVD",
                                                        "type": "COVID",
                                                        "doseNumber": "2",
                                                        "ndcCode": "59267100002",
                                                        "ndcName": "PFIZER COVID-19 VACCINE (EUA)",
                                                        "allocationCode": second_dose_soft.allocation_code
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
                                                "answerValue": patient_info.race_value,
                                                "answerText": patient_info.race
                                            },
                                            {
                                                "questionId": "ethnicity",
                                                "answerValue": patient_info.ethnicity_value,
                                                "answerText": patient_info.ethnicity
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
                            JOHNSON_form_data = ''

                        if first_dose.__vaccine__ == 'PFIZER':
                            print(utc2est(), site_print, colors.CYAN + "Reserving for Pfizer..." + colors.END)
                            submit_registration_post = s.post(submit_registration.url,
                                                              json=submit_registration.PFIZER_form_data,
                                                              headers=submit_registration.headers,
                                                              proxies=set_proxy.proxies)

                            class submit_response:
                                try:
                                    status_desc = submit_registration_post.json()["responseMetaData"]["statusDesc"]
                                except JSONDecodeError:
                                    print(submit_registration.PFIZER_form_data)
                                    print(submit_registration_post.status_code)
                                    print(submit_registration_post.text)

                            if submit_response.status_desc == "Success":
                                print(utc2est(), site_print,
                                      colors.GREEN + colors.BOLD + "Your CVS Appointment has been Successfully Scheduled." + colors.END)
                                print(utc2est(), site_print,
                                      colors.WARNING + colors.BOLD + 'Store Details ----------------' + colors.END)
                                print(utc2est(), site_print,
                                      colors.CYAN + 'CVS Address: ' + colors.WARNING + colors.BOLD + store_address + colors.END)
                                print(utc2est(), site_print,
                                      colors.WARNING + colors.BOLD + 'Time Details ----------------' + colors.END)
                                print(utc2est(), site_print, colors.CYAN + "First Dose Time:",
                                      colors.WARNING + colors.BOLD + first_dose_times.time_slots + colors.END)
                                print(utc2est(), site_print, colors.CYAN + "Second Dose Time:",
                                      colors.WARNING + colors.BOLD + second_dose_times.time_slots + colors.END)

                                def webhook():
                                    Webhook = DiscordWebhook(
                                        url=discord_webhook_url)

                                    embed = DiscordEmbed(title="Appointment Successfully Scheduled at CVS",
                                                         url='https://www.cvs.com/immunizations/covid-19-vaccine',
                                                         color=15987431)

                                    embed.set_footer(text='Covid-19 Appointment Monitor')

                                    embed.set_timestamp()

                                    embed.add_embed_field(name='CVS Location:', color=15987431, value=store_address)
                                    embed.add_embed_field(name='First Dose Date:', color=15987431,
                                                          value=first_dose_times.time_slots)
                                    embed.add_embed_field(name='Second Dose Date:', color=15987431,
                                                          value=second_dose_times.time_slots)

                                    Webhook.add_embed(embed)

                                    Webhook.execute()

                                webhook()
                                exit(1)
                            if submit_response.status_desc != "Success":
                                print(utc2est(), site_print,
                                      colors.FAIL + 'Your CVS Appointment Submission has been unsuccessfully' + colors.END)
                                print(utc2est(), site_print, "CVS Submission Data ----------------" + colors.END)
                                print(submit_registration_post.status_code)
                                print(submit_registration.PFIZER_form_data)
                                exit(1)

                    submit_reservation()

        dose_reserve()

    except ProxyError:
        print(utc2est(), site_print,
              colors.FAIL + 'Something went wrong with your IP Address (ProxyError). Please restart the application' + colors.END)
        input("Press Enter to close the application.")
    except MaxRetryError:
        print(utc2est(), site_print,
              colors.FAIL + 'Something went wrong with your IP Address (MaxRetryError). Please restart the application' + colors.END)
        input("Press Enter to close the application.")


if __name__ == '__main__':
    startup_print(vaccine_controls, home)
    covid_monitor()
