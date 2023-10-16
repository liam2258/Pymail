from flask import Flask, request, jsonify
from dotenv import load_dotenv
import smtplib, os, psycopg
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure email
sender_email = os.getenv("SENDER_EMAIL")
destination_email = os.getenv("RECEIVER_EMAIL")
app_password = os.getenv("API_KEY")

# Configure the SQL database connection
connection_string = os.getenv("DATABASE_URL")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/send', methods=['POST'])
def send_email():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        # Extracting values from http request
        name = data.get('Name')
        given_email = data.get('Contact')
        subject = data.get('Subject')
        message = data.get('Message')

        # If any values are missing return an error
        if not (name and given_email and subject and message):
            return jsonify({"error": "Incomplete JSON data"}), 400
        
        # Attempt to connect to the database and log requester info
        try:
            # Connect to the database using the connection string
            connection = psycopg.connect(connection_string)
            cursor = connection.cursor()

            # Insert data into your table (replace 'your_table' with your actual table name)
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, given_email))

            connection.commit()
            cursor.close()
            connection.close()

        # If inserting into the database fails return an error
        except Exception as error:
            return f"An error occurred: {str(error)}"

        # Create the email object to send
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = given_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # Attempt to send the email
        try:
            # Connect to Gmail's SMTP server
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            # Login to your Gmail account using the app password
            server.login(sender_email, app_password)
            # Send the email
            server.sendmail(sender_email, destination_email, msg.as_string())
            # Quit the server
            server.quit()
            return jsonify({"message": "Email sent"}), 200
        except Exception as error:
            return jsonify({"error": "Email not sent", "details": str(error)}), 500

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = os.getenv("PORT", 8000)
    httpd = make_server('', int(port), app)
    print(f"Serving on port {port}...")
    httpd.serve_forever()
