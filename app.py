from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import io
import qrcode

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# ---- TOOLS CONFIG (used for homepage + search) ---- #

CATEGORIES = [
    "AI Tools",
    "PDF Tools",
    "File Tools",
    "Utilities",
    "Downloader Tools",
    "Text Tools",
    "Converters",
    "Calculators"
]

TOOLS = [
    # --- Existing Tools ---
    {
        "id": "bmi-calculator",
        "name": "BMI Calculator",
        "category": "Calculators",
        "description": "Calculate your Body Mass Index quickly.",
        "route": "bmi_calculator",
        "icon": "📏"
    },
    {
        "id": "word-counter",
        "name": "Word & Character Counter",
        "category": "Text Tools",
        "description": "Count words and characters in your text.",
        "route": "word_counter",
        "icon": "📝"
    },
    {
        "id": "qr-generator",
        "name": "QR Code Generator",
        "category": "Utilities",
        "description": "Generate QR codes instantly.",
        "route": "qr_generator",
        "icon": "🔳"
    },
    {
        "id": "text-summarizer",
        "name": "Simple Text Summarizer",
        "category": "AI Tools",
        "description": "Summarize long text quickly.",
        "route": "text_summarizer",
        "icon": "✨"
    },

    # --- New Tools ---
    {
        "id": "image-compressor",
        "name": "Image Compressor",
        "category": "File Tools",
        "description": "Compress JPG/PNG images instantly.",
        "route": "image_compressor",
        "icon": "🖼️"
    },
    {
        "id": "pdf-to-word",
        "name": "PDF to Word",
        "category": "PDF Tools",
        "description": "Convert PDF into an editable Word file.",
        "route": "pdf_to_word",
        "icon": "📄➡️📝"
    },
    {
        "id": "pdf-merge",
        "name": "PDF Merge",
        "category": "PDF Tools",
        "description": "Merge multiple PDF files into one.",
        "route": "pdf_merge",
        "icon": "📚"
    },
    {
        "id": "gst-calculator",
        "name": "GST Calculator",
        "category": "Calculators",
        "description": "Calculate GST and final amount.",
        "route": "gst_calculator",
        "icon": "💰"
    },
    {
        "id": "age-calculator",
        "name": "Age Calculator",
        "category": "Calculators",
        "description": "Calculate your age from DOB.",
        "route": "age_calculator",
        "icon": "🎂"
    },
    {
        "id": "unit-converter",
        "name": "Unit Converter",
        "category": "Converters",
        "description": "Convert units (km, m, cm).",
        "route": "unit_converter",
        "icon": "🔁"
    },
    {
        "id": "password-generator",
        "name": "Password Generator",
        "category": "Text Tools",
        "description": "Generate strong passwords.",
        "route": "password_generator",
        "icon": "🔐"
    },
    {
        "id": "youtube-thumbnail",
        "name": "YouTube Thumbnail Downloader",
        "category": "Downloader Tools",
        "description": "Download HD YouTube thumbnails.",
        "route": "youtube_thumbnail",
        "icon": "🎥"
    }
]

# Sort tools alphabetically by name
TOOLS = sorted(TOOLS, key=lambda x: x["name"])


CATEGORIES = sorted(list({tool["category"] for tool in TOOLS}))


# Utility: group tools by category
def group_tools_by_category():
    grouped = {}
    for tool in TOOLS:
        grouped.setdefault(tool["category"], []).append(tool)
    return grouped


@app.context_processor
def inject_globals():
    # Available in all templates
    return {
        "TOOLS": TOOLS,
        "CATEGORIES": CATEGORIES,
        "site_name": "ToolifyHub",
        "site_tagline": "All Your Favorite Online Tools in One Place",
    }


# ---------- ROUTES ---------- #

@app.route("/")
def index():
    query = request.args.get("q", "").strip().lower()
    tools = TOOLS
    if query:
        tools = [
            t for t in TOOLS
            if query in t["name"].lower()
            or query in t["description"].lower()
            or query in t["category"].lower()
        ]
    grouped = {}
    for tool in tools:
        grouped.setdefault(tool["category"], []).append(tool)
    return render_template("index.html", grouped_tools=grouped, query=query)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # In real use, send email or store message
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        if name and email and message:
            flash("Thank you! Your message has been received.", "success")
        else:
            flash("Please fill out all fields.", "error")
    return render_template("contact.html")


# ---------- TOOL: BMI CALCULATOR ---------- #

@app.route("/tool/bmi-calculator", methods=["GET", "POST"])
def bmi_calculator():
    result = None
    status = None
    if request.method == "POST":
        try:
            height_cm = float(request.form.get("height_cm", "0"))
            weight_kg = float(request.form.get("weight_kg", "0"))
            if height_cm <= 0 or weight_kg <= 0:
                raise ValueError
            height_m = height_cm / 100.0
            bmi = weight_kg / (height_m ** 2)
            bmi = round(bmi, 2)

            if bmi < 18.5:
                status = "Underweight"
            elif bmi < 24.9:
                status = "Normal weight"
            elif bmi < 29.9:
                status = "Overweight"
            else:
                status = "Obese"

            result = bmi
        except ValueError:
            flash("Please enter valid numeric values.", "error")

    return render_template("tool_bmi.html", result=result, status=status)


# ---------- TOOL: WORD & CHARACTER COUNTER ---------- #

@app.route("/tool/word-counter", methods=["GET", "POST"])
def word_counter():
    text = ""
    word_count = 0
    char_count = 0
    if request.method == "POST":
        text = request.form.get("text", "")
        words = text.split()
        word_count = len(words)
        char_count = len(text)
    return render_template(
        "tool_word_counter.html",
        text=text,
        word_count=word_count,
        char_count=char_count,
    )


# ---------- TOOL: QR CODE GENERATOR ---------- #

@app.route("/tool/qr-generator", methods=["GET", "POST"])
def qr_generator():
    qr_image = None
    input_text = ""
    if request.method == "POST":
        input_text = request.form.get("input_text", "").strip()
        if input_text:
            # Generate QR code into memory
            img = qrcode.make(input_text)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            # Instead of sending download immediately, we embed it as data URL
            # To keep it simple, we'll send it as a file response when user clicks "Download"
            # For inline display, we store it in session or create another route.
            # Here we directly return a file only on dedicated route (see /qr-image)
            qr_image = True  # flag to show download button
        else:
            flash("Please enter some text or URL.", "error")
    return render_template(
        "tool_qr.html",
        input_text=input_text,
        qr_image=qr_image,
    )


@app.route("/tool/qr-generator/download", methods=["POST"])
def qr_download():
    input_text = request.form.get("input_text", "").strip()
    if not input_text:
        flash("No text provided for QR code.", "error")
        return redirect(url_for("qr_generator"))

    img = qrcode.make(input_text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=True,
        download_name="qrcode.png",
    )


# ---------- TOOL: SIMPLE TEXT SUMMARIZER ---------- #

def simple_summarize(text, max_sentences=3):
    """
    Very basic summarizer:
    - Split into sentences by '.'
    - Take first N non-empty sentences
    """
    sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".")]
    sentences = [s for s in sentences if s]
    return ". ".join(sentences[:max_sentences]) + ("." if sentences[:max_sentences] else "")


@app.route("/tool/text-summarizer", methods=["GET", "POST"])
def text_summarizer():
    original_text = ""
    summary = ""
    if request.method == "POST":
        original_text = request.form.get("text", "").strip()
        if original_text:
            summary = simple_summarize(original_text, max_sentences=3)
        else:
            flash("Please paste some text to summarize.", "error")
    return render_template(
        "tool_text_summarizer.html",
        original_text=original_text,
        summary=summary,
    )
from PIL import Image

@app.route("/tool/image-compressor", methods=["GET", "POST"])
def image_compressor():
    compressed_image = None
    if request.method == "POST":
        file = request.files.get("image")
        if file:
            img = Image.open(file)
            buffer = io.BytesIO()
            img.save(buffer, "JPEG", optimize=True, quality=40)
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name="compressed.jpg")
    return render_template("tool_image_compressor.html")
from docx import Document
import PyPDF2

@app.route("/tool/pdf-to-word", methods=["GET", "POST"])
def pdf_to_word():
    if request.method == "POST":
        file = request.files.get("pdf")
        if file:
            reader = PyPDF2.PdfReader(file)
            doc = Document()
            for page in reader.pages:
                doc.add_paragraph(page.extract_text())
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name="converted.docx")
    return render_template("tool_pdf_to_word.html")
@app.route("/tool/pdf-merge", methods=["GET", "POST"])
def pdf_merge():
    if request.method == "POST":
        files = request.files.getlist("pdfs")
        merger = PyPDF2.PdfMerger()
        for f in files:
            merger.append(f)
        buffer = io.BytesIO()
        merger.write(buffer)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="merged.pdf")
    return render_template("tool_pdf_merge.html")

@app.route("/tool/gst-calculator", methods=["GET", "POST"])
def gst_calculator():
    amount = gst = final = None
    if request.method == "POST":
        amount = float(request.form.get("amount"))
        rate = float(request.form.get("rate"))
        gst = amount * (rate / 100)
        final = amount + gst
    return render_template("tool_gst_calculator.html", amount=amount, gst=gst, final=final)

from datetime import datetime

@app.route("/tool/age-calculator", methods=["GET", "POST"])
def age_calculator():
    age = None
    if request.method == "POST":
        dob = request.form.get("dob")
        birth = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return render_template("tool_age_calculator.html", age=age)


@app.route("/tool/unit-converter", methods=["GET", "POST"])
def unit_converter():
    result = None
    if request.method == "POST":
        value = float(request.form.get("value"))
        unit = request.form.get("unit")
        if unit == "km_m":
            result = value * 1000
        elif unit == "m_km":
            result = value / 1000
        elif unit == "cm_m":
            result = value / 100
        elif unit == "m_cm":
            result = value * 100
    return render_template("tool_unit_converter.html", result=result)

import random
import string

@app.route("/tool/password-generator", methods=["GET", "POST"])
def password_generator():
    pwd = None
    if request.method == "POST":
        length = int(request.form.get("length"))
        chars = string.ascii_letters + string.digits + string.punctuation
        pwd = ''.join(random.choice(chars) for _ in range(length))
    return render_template("tool_password_generator.html", pwd=pwd)
@app.route("/tool/youtube-thumbnail", methods=["GET", "POST"])
def youtube_thumbnail():
    thumbnail_url = None
    backup = None

    if request.method == "POST":
        url = request.form.get("url")

        # Extract video ID
        video_id = url.split("v=")[-1].split("&")[0]

        # Max resolution
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        # Backup resolution
        backup = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    return render_template(
        "tool_youtube_thumbnail.html",
        thumbnail_url=thumbnail_url,
        backup=backup
    )

import requests

@app.route("/download-thumbnail")
def download_thumbnail():
    url = request.args.get("url")

    # Fetch image bytes
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        return send_file(
            io.BytesIO(response.content),
            mimetype="image/jpeg",
            as_attachment=True,
            download_name="thumbnail.jpg"
        )
    return "Download failed", 400

from flask import Response

@app.route("/robots.txt")
def robots_txt():
    content = """User-agent: *
Allow: /
Sitemap: https://yourdomain.com/sitemap.xml
"""
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    pages = [
        "index",
        "about",
        "contact",
        "bmi_calculator",
        "word_counter",
        "qr_generator",
        "text_summarizer",
        "image_compressor",
        "pdf_to_word",
        "pdf_merge",
        "gst_calculator",
        "age_calculator",
        "unit_converter",
        "password_generator",
        "youtube_thumbnail",
    ]

    import datetime
    urls = []
    for p in pages:
        loc = url_for(p, _external=True)
        urls.append(f"<url><loc>{loc}</loc><lastmod>{datetime.date.today()}</lastmod></url>")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""
    return Response(xml, mimetype="application/xml")

# ---------- MAIN ---------- #

if __name__ == "__main__":
    app.run(debug=True)
