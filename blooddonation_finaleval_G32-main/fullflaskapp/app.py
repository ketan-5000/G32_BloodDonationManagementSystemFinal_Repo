from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/about-us', methods=['GET'])
def about_us():
    about_info = {
        "application_name": "Blood Donation Management System",
        "description": "A platform to easily donate and request blood, connecting donors with those in urgent need.",
        "mission": "To save lives by simplifying blood donation and ensuring timely access for those in need.",
        "vision": "To build a connected community where safe blood is always available, everywhere.",
        "goals": [
            "Increase voluntary blood donations through awareness and accessibility.",
            "Ensure timely blood availability for patients in critical need.",
            "Build a reliable network of donors and healthcare partners.",
            "Leverage technology to streamline blood requests and donations."
        ],
    }
    return jsonify(about_info)



if __name__ == '__main__':
    app.run(debug=True)
