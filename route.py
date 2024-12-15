from flask import Flask, request, jsonify, send_file
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
from main import stock_cutter, draw_multiple_parent_rects
import io
import base64
import os

app = Flask(__name__)

# Define the static directory
STATIC_DIR = os.path.join(os.getcwd(), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/cut-stock', methods=['POST'])
def cut_stock():
    try:
        # Get data from the client
        data = request.get_json()
        if not data or 'demand' not in data or 'stock' not in data:
            return jsonify({"error": "Invalid input data"}), 400

        # Extract demand and stock dimensions
        demand = data['demand']
        stock = data['stock']

        # Validate and convert input
        try:
            child_rects = [[int(w), int(h), int(q)] for w, h, q in demand]
            parent_rect = [int(stock[0]), int(stock[1])]
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid dimensions or demand format"}), 400

        # Perform the stock cutting algorithm
        placements, sizes, parent_count, used_spaces_per_parent, filled_ratio, trim_loss = stock_cutter(child_rects, parent_rect)

        # Generate a visualization
        fig = draw_multiple_parent_rects(placements, sizes, parent_rect, parent_count, used_spaces_per_parent)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)  # Ensure Matplotlib figure is closed
        buf.seek(0)

        # Encode image as Base64 directly from buffer
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()  # Close the buffer

        # Save the image to the static directory for direct download
        image_path = os.path.join(STATIC_DIR, "result_image.png")
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # Return results and image
        result = {
            'sizes': sizes,
            'parent_count': parent_count,
            'filled_ratio': filled_ratio,
            'trim_loss': trim_loss,
            'image': image_base64,
            'image_url': f"/static/result_image.png"
        }
        return jsonify(result)

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
