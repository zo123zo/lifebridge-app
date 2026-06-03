from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Enterprise In-Memory Database Node with pre-loaded historical "ALREADY Donated" statuses
system_database = {
    "donors": [
        {"id": 1, "name": "Sarah Jenkins", "hospital": "St. Jude Medical Center", "blood_type": "O+", "hla_marker": "A1-B7-DR1", "organ_available": "Kidney", "phone": "+1-555-0142", "history": "ALREADY Donated Liver"},
        {"id": 2, "name": "Marcus Vance", "hospital": "Mayo Clinic Facility", "blood_type": "A-", "hla_marker": "A3-B44-DR4", "organ_available": "Liver", "phone": "+1-555-0199", "history": "None - Active Availability"}
    ],
    "recipients": [
        {"id": 1, "name": "Robert Chen", "hospital": "Johns Hopkins Hospital", "blood_type": "O+", "hla_marker": "A1-B8-DR3", "organ_needed": "Kidney", "urgency_score": 9}
    ]
}

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "donors": system_database["donors"],
        "recipients": system_database["recipients"]
    })

@app.route('/api/donor', methods=['POST'])
def add_donor():
    data = request.json
    new_id = len(system_database["donors"]) + 1
    
    # Capitalize the custom history entry input cleanly
    history_status = data.get("history", "None - Active Availability")
    if history_status.strip().lower() in ["liver", "kidney", "heart", "lung"]:
        history_status = f"ALREADY Donated {history_status.capitalize()}"

    new_donor = {
        "id": new_id,
        "name": data.get("name"),
        "hospital": data.get("hospital"),
        "blood_type": data.get("blood_type"),
        "hla_marker": data.get("hla_marker"),
        "organ_available": data.get("organ"),
        "phone": data.get("phone", "N/A"),
        "history": history_status
    }
    system_database["donors"].append(new_donor)
    return jsonify({"success": True, "donor": new_donor})

@app.route('/api/recipient', methods=['POST'])
def add_recipient():
    data = request.json
    new_id = len(system_database["recipients"]) + 1
    new_recipient = {
        "id": new_id,
        "name": data.get("name"),
        "hospital": data.get("hospital"),
        "blood_type": data.get("blood_type"),
        "hla_marker": data.get("hla_marker"),
        "organ_needed": data.get("organ"),
        "urgency_score": int(data.get("urgency", 5))
    }
    system_database["recipients"].append(new_recipient)
    return jsonify({"success": True, "recipient": new_recipient})

@app.route('/api/match', methods=['GET'])
def match_allocation():
    matches = []
    for r in system_database["recipients"]:
        for d in system_database["donors"]:
            # Only match if the donor has an active organ ready (not already completely donated out)
            if "already" in d["history"].lower() and d["organ_available"].lower() in d["history"].lower():
                continue
                
            if r["organ_needed"].lower() == d["organ_available"].lower():
                score = 5
                blood_status = "Incompatible Matrix"
                
                if r["blood_type"] == d["blood_type"]:
                    score += 5
                    blood_status = "Identical Blood Type match"
                elif d["blood_type"] == "O-":
                    score += 3
                    blood_status = "Universal Donor Compatibility"
                    
                matches.append({
                    "organ": r["organ_needed"],
                    "donor_id": d["id"],
                    "donor_name": d["name"],
                    "recipient_id": r["id"],
                    "recipient_name": r["name"],
                    "blood_match": blood_status,
                    "hla_matches": "High Compatibility Loci",
                    "score": score + r["urgency_score"]
                })
    return jsonify(matches)

if __name__ == '__main__':
    app.run(debug=True, port=5001)