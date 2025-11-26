from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

#integrating gemini pro api to backend
genai.configure(api_key="AIzaSyDsGS-BqtpSpSEwaC9wiW6MACYyhj1CptA")
model = genai.GenerativeModel("gemini-2.5-pro")

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    emergency = False
    map_url = None

    # Checking the symptom severity level
    severity = None
    severity_class = ""
    disease = None
    remedies = None
    doctor_advice = None
    prevention = None

    # Keywords for checking emergency
    critical_symptoms = [
        "chest pain", 
        "shortness of breath", 
        "severe bleeding", 
        "unconscious", 
        "severe burns",
        "severe headache",
        "loss of consciousness"
    ]

    if request.method == "POST":
        symptoms = request.form["symptoms"]
        user_symptoms_lower = symptoms.lower()

        #working of ai-gemini which we have integrated with gemini-api
        prompt = f"""
        The user entered symptoms: {symptoms}

        Respond strictly in this format:

        Severity: <Low / Medium / High / Emergency>
        Possible Disease: <Disease name>
        Remedies: <Suggested remedies / medicines>
        When to seek doctor: <Advice>
        Prevention: <Tips>

        If the user has any of these critical symptoms, classify severity as Emergency:
        - Chest pain
        - Shortness of breath
        - Severe bleeding
        - Unconsciousness
        - Severe burns
        """

        # response of the ai-gemini
        response = model.generate_content(prompt)
        result = response.text

        # return result and checks severity
        lines = result.splitlines()
        for line in lines:
            if line.lower().startswith("severity:"):
                severity = line.split(":", 1)[1].strip()
            elif line.lower().startswith("possible disease:"):
                disease = line.split(":", 1)[1].strip()
            elif line.lower().startswith("remedies:"):
                remedies = line.split(":", 1)[1].strip()
            elif line.lower().startswith("when to seek doctor:"):
                doctor_advice = line.split(":", 1)[1].strip()
            elif line.lower().startswith("prevention:"):
                prevention = line.split(":", 1)[1].strip()

        # if critical symptoms present then this implement
        if any(cs in user_symptoms_lower for cs in critical_symptoms):
            severity = "Emergency"

        # shows red emergency page
        if severity:
            severity_class = severity.lower()  # low, medium, high, emergency

        # Set emergency and Google Maps URL
        if severity == "Emergency":
            emergency = True
            map_url = "https://www.google.com/maps/search/hospitals+near+me/"

        return render_template(
            "index.html",
            result=result,
            symptoms=symptoms,
            emergency=emergency,
            map_url=map_url,
            severity=severity,
            severity_class=severity_class,
            disease=disease,
            remedies=remedies,
            doctor_advice=doctor_advice,
            prevention=prevention
        )

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
