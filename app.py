from flask import Flask, request, jsonify
from collections import deque, defaultdict


app = Flask(__name__)

transactions = deque()
balances = defaultdict(int)

@app.route('/add', methods=['POST'])
def app_points():
    data = request.json
    payer = data['payer']
    points = data['points']
    timestamp = data['timestamp']
    transactions.append({'payer': payer, 'points': points, 'timestamp': timestamp})
    balances[payer] += points
    return '', 200


@app.route('/spend', methods=['POST'])
def spend_points():
    points_to_spend = request.json['points']
    if sum(balances.values()) < points_to_spend:
        return 'Insufficient points', 400
    
    spent_points = defaultdict(int)
    while points_to_spend >0:
        curtransaction = transactions.popleft()
        payer = curtransaction['payer']
        points = curtransaction['points']
        timestamp = curtransaction['timestamp']
        spendable_points = min(points, points_to_spend, balances[payer])
        balances[payer] -= spendable_points
        points_to_spend -= spendable_points
        spent_points[payer] -= spendable_points
        if points - spendable_points > 0:
            transactions.appendleft({'payer': payer, 'points': points-spendable_points, 'timestamp': timestamp})
    
    return jsonify([{"payer": k, "points": v} for k, v in spent_points.items()]), 200


@app.route('/balance', methods=['GET'])
def get_balance():
    return jsonify(balances), 200

if __name__ == "__main__":
    app.run(port=8000)
