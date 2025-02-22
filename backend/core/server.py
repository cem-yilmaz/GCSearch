from flask import Flask, request, jsonify
from flask_cors import CORS
from example import reverse_string

app = Flask(__name__)
CORS(app)   

@app.route('/reverse', methods=['POST'])
def reverse_text():
    data = request.get_json()
    string = data['string']
    reversed_string = reverse_string(string)
    return jsonify({
        'original': string,
        'reversed': reversed_string
    })

if __name__ == '__main__':
    app.run(debug=True)