from flask import Flask, render_template, request, send_file, redirect, url_for
import fitz  # PyMuPDF
import os
import zipfile
import shutil
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert_pdf():
    if "pdf_file" not in request.files:
        return "No file uploaded", 400

    pdf_file = request.files["pdf_file"]
    pdf_name = os.path.splitext(pdf_file.filename)[0]
    session_id = str(uuid.uuid4())
    output_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(output_folder, exist_ok=True)

    # Save PDF temporarily
    pdf_path = os.path.join(output_folder, f"{pdf_name}.pdf")
    pdf_file.save(pdf_path)

    # Convert PDF pages to images
    doc = fitz.open(pdf_path)
    image_files = []
    max_pages = 2  # Only process first 2 pages
    for i, page in enumerate(doc, start=1):
        if i > max_pages:
            break
        pix = page.get_pixmap(dpi=300)
        img_name = f"page_{i}.png"
        img_path = os.path.join(output_folder, img_name)
        pix.save(img_path)
        image_files.append(url_for('static', filename=f'images/{session_id}/{img_name}'))
    doc.close()


    # Zip all images
    zip_path = os.path.join(output_folder, f"{pdf_name}_images.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for img in os.listdir(output_folder):
            if img.endswith('.png'):
                zipf.write(os.path.join(output_folder, img), img)

    return render_template("preview.html", images=image_files, zip_file=url_for('static', filename=f'images/{session_id}/{pdf_name}_images.zip'))
