import cv2
import numpy as np
import os
import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)

# Allow requests from Cloudflare Pages domain + localhost for dev
CORS(app, origins=[
    "http://localhost:*",
    "http://127.0.0.1:*",
    # Replace this with your actual Cloudflare Pages domain after deploy:
    "https://*.pages.dev",
    # And your custom domain if you add one later:
    # "https://yourdomain.com",
])

MAX_DIM = 1200  # Downscale large images to keep Render free tier happy


def color_quantisation(img, k, attempts=10):
    data = np.float32(img).reshape((-1, 3))
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
    _, label, center = cv2.kmeans(
        data, k, None, crit, attempts, cv2.KMEANS_RANDOM_CENTERS
    )
    center = np.uint8(center)
    return center[label.flatten()].reshape(img.shape)


def decode_image(data_url_or_b64: str) -> np.ndarray:
    """Accept either a data URL (data:image/...;base64,...) or raw base64."""
    if "," in data_url_or_b64:
        _, encoded = data_url_or_b64.split(",", 1)
    else:
        encoded = data_url_or_b64

    raw = base64.b64decode(encoded)
    buf = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def encode_image(img: np.ndarray, fmt: str = ".png") -> str:
    """Return a base64-encoded data URL."""
    success, buf = cv2.imencode(fmt, img)
    if not success:
        raise ValueError("Could not encode image")
    b64 = base64.b64encode(buf).decode("utf-8")
    mime = "image/png" if fmt == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def maybe_downscale(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    if max(h, w) > MAX_DIM:
        scale = MAX_DIM / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)),
                         interpolation=cv2.INTER_AREA)
    return img


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "cartoonizer-api"})


@app.route("/cartoonize", methods=["POST"])
def cartoonize():
    try:
        body = request.get_json(force=True)
        if not body or "image" not in body:
            return jsonify({"error": "Missing 'image' field"}), 400

        k = int(body.get("k", 15))
        k = max(2, min(64, k))  # clamp

        img = decode_image(body["image"])
        img = maybe_downscale(img)

        result = color_quantisation(img, k, attempts=10)

        h, w = result.shape[:2]
        out_b64 = encode_image(result, ".png")

        return jsonify({
            "image": out_b64,
            "width": w,
            "height": h,
            "k": k,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
