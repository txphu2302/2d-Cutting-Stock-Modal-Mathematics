from flask import Flask, request, jsonify, send_file
import matplotlib.pyplot as plt
from main import stock_cutter, draw_multiple_parent_rects
import io
import base64
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/cut-stock', methods=['POST'])
def cut_stock():
    # Get data from the client
    data = request.get_json()
    demand = data['demand']
    stocks = data['stocks']

    # Convert data to the format stock_cutter needs
    child_rects = [[int(w), int(h), int(q)] for w, h, q in demand]
    parent_rects = [[int(w), int(h), int(q)] for w, h, q in stocks]

    # Perform the stock cutting algorithm
    placements, sizes, placement_parents, expanded_parents, used_spaces_per_parent = stock_cutter(child_rects, parent_rects)


    # Generate a visualization
    fig = draw_multiple_parent_rects(placements, sizes, expanded_parents, placement_parents, used_spaces_per_parent)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    # Ensure static directory exists
    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Save image to a file for download
    image_path = os.path.join(static_dir, "result_image.png")
    with open(image_path, "wb") as f:
        f.write(buf.read())

    # Rewind buffer to encode as Base64
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    # Return results and image
    result = {
    'placements': placements,
    'sizes': sizes,
    'placement_parents': placement_parents,
    'expanded_parents': expanded_parents,
    'image': image_base64,
    'image_url': f"/{image_path}"
}

    return jsonify(result)



if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
