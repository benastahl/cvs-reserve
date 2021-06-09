
class Patient:

    def __init__(self):
        self.first_name = 'Jane'
        self.last_name = 'Doe'
        self.dob = '1980-03-09'  # ex. 2000-07-08
        self.gender = ''  # M or F
        self.email = 'janedoe@gmail.com'
        self.phone = '1231231234'  # ex. 6178626406
        self.address_1 = 'Jane Doe Road'
        self.address_2 = None
        self.city = 'Doe'
        self.state = 'MA'  # ex. MA
        self.zip_code = '12345'
        self.race = 'White'
        self.race_value = '2106-3'
        self.ethnicity = 'Not Hispanic or Latino or Spanish Origin'
        self.ethnicity_value = 'N'
        self.insurance_id = ''
        self.non_medicare = True
        self.non_medicare_provider = "Jane Doe's non-medicare provider"


class Questions:

    def __init__(self):
        # QUESTION ID 1: Are you sick today?
        self.question_id_1 = "No"

        # QUESTION ID 2: Have you ever had a severe allergic reaction (e.g., anaphylaxis) to something? For example, a reaction for which you were treated with epinephrine, or EpiPen, or for which you had to go to the hospital? If yes, what are you allergic to?
        self.question_id_2 = "No"

        # QUESTION ID 3: Had you ever had a severe allergic reaction after receiving a COVID-19 vaccine?
        self.question_id_3 = "No"

        # QUESTION ID 4: Have you ever had a severe allergic reaction after receiving another vaccine or injectable medication?
        self.question_id_4 = "No"

        # QUESTION ID 5: Have you ever had a severe allergic reaction after receiving Polyethylene Glycol?
        self.question_id_5 = "No"

        # QUESTION ID 6: Have you ever had a severe allergic reaction related to receiving Polysorbate or products containing Polysorbate?
        self.question_id_6 = "No"

        # QUESTION ID 7: For women, are you currently pregnant or breastfeeding?
        self.question_id_7 = "No"

        # QUESTION ID 8: In the past 14 days, have you teste positive for COVID-19?
        self.question_id_8 = "No"

        # QUESTION ID 9: In the past 14 days, have you been in close contact with anyone who tested positive for COVID-19?
        self.question_id_9 = "No"

        # QUESTION ID 10: Do you currently have fever, chills, cough, shortness of breath, difficulty breathing, fatigue, muscle or body aches, headache, new loss of taste or smell, sore throat, nausea, vomiting, or diarrhea?
        self.question_id_10 = "No"

        # QUESTION ID 11: Do you have a bleeding disorder or are you taking a blood thinner?
        self.question_id_11 = "No"

        # QUESTION ID 12: Have you received any vaccines in the past 14 days?
        self.question_id_12 = "No"

        # QUESTION ID 13: Have you received monoclonal antibodies or convalescent plasma as part of a COVID-19 treatment in the past 90 days?
        self.question_id_13 = "No"

        # ELIGIBILITY: Why are you eligible? (Can be custom)
        self.eligibility = "Age 16+ with high-risk conditions"
