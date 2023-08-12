from flask import Flask, request, jsonify
import heapq
import random

app = Flask(__name__)

# Precompute graph distances
GRAPH_DISTANCES = {
    "Start": {"Route A": 10, "Route B": 20, "Route C": 15},
    "Route A": {"End": 5},
    "Route B": {"End": 10},
    "Route C": {"End": 7},
    "End": {},
}

def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances[end]

def make_traffic_decisions(gps_data, mobile_app_data, congestion_data):
    decisions = []

    # Create a set of preferred routes for efficient lookup
    preferred_routes_set = set(route for user in mobile_app_data for route in user["preferred_routes"])

    for vehicle in gps_data:
        vehicle_id = vehicle["vehicle_id"]
        speed = vehicle["speed"]

        # Determine the vehicle's preferred routes
        preferred_routes = preferred_routes_set.intersection(next((user["preferred_routes"] for user in mobile_app_data if user["user_id"] == "U001"), []))

        # Find the shortest path considering congestion levels
        shortest_path = min(preferred_routes, key=lambda route: dijkstra(GRAPH_DISTANCES, "Start", route), default=None)

        # Simulate decision-making based on speed and shortest path
        if speed < 10:
            decision = f"Vehicle {vehicle_id}: Slow traffic detected, consider alternate route."
        else:
            if shortest_path:
                decision = f"Vehicle {vehicle_id}: Take {shortest_path} to avoid congestion."
            else:
                congestion_location = random.choice(congestion_data)["location"]
                decision = f"Vehicle {vehicle_id}: No preferred route available. Consider avoiding {congestion_location} due to congestion."

        decisions.append(decision)

    return decisions

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Traffic Management System!"


@app.route('/traffic-management', methods=['POST'])
def traffic_management():
    try:
        data = request.json

        gps_data = data.get('gps_data', [])
        mobile_app_data = data.get('mobile_app_data', [])
        congestion_data = data.get('congestion_data', [])

        traffic_decisions = make_traffic_decisions(gps_data, mobile_app_data, congestion_data)

        response = {
            'success': True,
            'traffic_decisions': traffic_decisions
        }

        return jsonify(response)

    except Exception as e:
        error_response = {
            'success': False,
            'error': str(e)
        }
        return jsonify(error_response), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
