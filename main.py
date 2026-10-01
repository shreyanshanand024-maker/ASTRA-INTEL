from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pymupdf
import os
import re
from collections import Counter

# ============================================================
# ASTRA INTEL
# AI-Powered Defence Document Intelligence System
# ============================================================

# Tesseract OCR location
os.environ["TESSDATA_PREFIX"] = (
    r"C:\Program Files\Tesseract-OCR\tessdata"
)

app = FastAPI()


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    text = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        text
    )

    return text.strip()


# ============================================================
# SUMMARY
# ============================================================

def create_summary(text):

    text = clean_text(text)

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    useful_sentences = []

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) >= 50:

            useful_sentences.append(
                sentence
            )

    if not useful_sentences:

        return "No meaningful summary could be generated."

    return " ".join(
        useful_sentences[:5]
    )


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def extract_keywords(text):

    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        text.lower()
    )

    stop_words = {
        "this",
        "that",
        "with",
        "from",
        "which",
        "these",
        "those",
        "their",
        "there",
        "about",
        "would",
        "could",
        "should",
        "where",
        "when",
        "what",
        "have",
        "been",
        "were",
        "will",
        "your",
        "they",
        "them",
        "than",
        "then",
        "also",
        "into",
        "more",
        "some",
        "such",
        "using",
        "used",
        "course",
        "engineering",
        "computer",
        "science",
        "study",
        "students",
        "semester",
        "subject",
        "coursework",
        "university",
        "college"
    }

    filtered_words = []

    for word in words:

        if word not in stop_words:

            filtered_words.append(word)

    frequency = Counter(
        filtered_words
    )

    keywords = []

    for word, count in frequency.most_common(10):

        keywords.append(word)

    return keywords


# ============================================================
# TOPIC DETECTION
# ============================================================

def detect_topics(text):

    text = text.lower()

    topic_map = {

        "Artificial Intelligence": [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural network",
            "ai"
        ],

        "Programming": [
            "programming",
            "python",
            "c programming",
            "algorithm",
            "software",
            "coding"
        ],

        "Data Science": [
            "data science",
            "data analysis",
            "dataset",
            "statistics",
            "analytics"
        ],

        "Engineering": [
            "engineering",
            "technology",
            "design",
            "system",
            "development"
        ],

        "Mathematics": [
            "mathematics",
            "calculus",
            "algebra",
            "matrix",
            "equation"
        ],

        "Physics": [
            "physics",
            "quantum",
            "force",
            "energy",
            "motion"
        ],

        "Computer Science": [
            "computer science",
            "computing",
            "computer",
            "software"
        ]

    }

    detected = []

    for topic, keywords in topic_map.items():

        for keyword in keywords:

            if keyword in text:

                detected.append(topic)

                break

    if not detected:

        detected.append(
            "General Document"
        )

    return detected


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>

<html>

<head>

    <title>ASTRA INTEL</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <style>

        * {
            box-sizing: border-box;
        }

        body {

            margin: 0;

            font-family: Arial, sans-serif;

            background: #0b1220;

            color: white;

        }

        .header {

            padding: 25px 50px;

            background: #111c33;

            border-bottom: 1px solid #263653;

        }

        .header h1 {

            margin: 0;

            font-size: 32px;

        }

        .header p {

            color: #9aa9c2;

            margin-bottom: 0;

        }

        .container {

            max-width: 1100px;

            margin: auto;

            padding: 40px 50px;

        }

        .upload-box {

            background: #16233d;

            padding: 35px;

            border-radius: 18px;

            text-align: center;

            border: 1px solid #263653;

        }

        .upload-box h2 {

            margin-top: 0;

        }

        input[type="file"] {

            margin: 20px;

            padding: 12px;

            background: #0f1a2e;

            color: white;

            border-radius: 8px;

        }

        button {

            padding: 13px 28px;

            border: none;

            border-radius: 8px;

            background: #3b82f6;

            color: white;

            font-weight: bold;

            font-size: 16px;

            cursor: pointer;

        }

        button:hover {

            background: #2563eb;

        }

        .cards {

            display: flex;

            gap: 20px;

            margin-top: 30px;

            flex-wrap: wrap;

        }

        .card {

            background: #16233d;

            padding: 25px;

            border-radius: 15px;

            width: 220px;

            border: 1px solid #263653;

        }

        .card h3 {

            color: #9aa9c2;

            margin-top: 0;

        }

        .value {

            font-size: 35px;

            font-weight: bold;

            word-break: break-word;

        }

        .result {

            margin-top: 30px;

            background: #16233d;

            padding: 30px;

            border-radius: 15px;

            border: 1px solid #263653;

        }

        .result h2 {

            margin-top: 0;

        }

        #filename {

            color: #60a5fa;

            font-weight: bold;

        }

        #text {

            background: #0b1220;

            padding: 20px;

            border-radius: 10px;

            white-space: pre-wrap;

            max-height: 450px;

            overflow-y: auto;

            line-height: 1.6;

            color: #dbe4f0;

        }

        .summary {

            background: #0b1220;

            padding: 20px;

            border-radius: 10px;

            line-height: 1.7;

            color: #dbe4f0;

            margin-bottom: 25px;

        }

        .info-section {

            margin-top: 30px;

        }

        .keyword {

            display: inline-block;

            background: #243657;

            color: #93c5fd;

            padding: 8px 14px;

            margin: 5px;

            border-radius: 20px;

            font-size: 14px;

        }

        .topic {

            display: inline-block;

            background: #183b35;

            color: #6ee7b7;

            padding: 9px 15px;

            margin: 5px;

            border-radius: 20px;

            font-size: 14px;

        }

        .status {

            margin-top: 25px;

            color: #45e0a8;

            font-weight: bold;

        }

        .error {

            color: #ff6b6b;

            font-weight: bold;

        }

        .success {

            color: #45e0a8;

            font-weight: bold;

        }

        .loading {

            color: #60a5fa;

            font-weight: bold;

        }

        @media (max-width: 700px) {

            .container {

                padding: 25px;

            }

            .header {

                padding: 25px;

            }

            .card {

                width: 100%;

            }

        }

    </style>

</head>


<body>


    <div class="header">

        <h1>ASTRA INTEL</h1>

        <p>
            AI-Powered Defence Document
            Intelligence System
        </p>

    </div>


    <div class="container">


        <h2>
            Document Intelligence Dashboard
        </h2>


        <div class="upload-box">

            <h2>
                Upload Document
            </h2>

            <p>

                Upload a PDF document for
                automatic text extraction,
                OCR and intelligence analysis.

            </p>


            <input
                type="file"
                id="fileInput"
                accept=".pdf"
            >


            <br>


            <button
                onclick="uploadDocument()"
            >

                Analyze Document

            </button>


            <p id="message"></p>

        </div>


        <div class="cards">


            <div class="card">

                <h3>📄 Document</h3>

                <div
                    class="value"
                    id="documentName"
                >
                    -
                </div>

                <p>Uploaded file</p>

            </div>


            <div class="card">

                <h3>📑 Pages</h3>

                <div
                    class="value"
                    id="pageCount"
                >
                    0
                </div>

                <p>Total pages</p>

            </div>


            <div class="card">

                <h3>🔤 Words</h3>

                <div
                    class="value"
                    id="wordCount"
                >
                    0
                </div>

                <p>Extracted words</p>

            </div>


            <div class="card">

                <h3>🔑 Keywords</h3>

                <div
                    class="value"
                    id="keywordCount"
                >
                    0
                </div>

                <p>Detected keywords</p>

            </div>


        </div>


        <div class="result">


            <h2>
                🧠 Document Summary
            </h2>


            <div
                id="summary"
                class="summary"
            >

                Upload a PDF to generate
                a document summary.

            </div>


            <div class="info-section">

                <h2>
                    🔑 Key Keywords
                </h2>

                <div id="keywords">

                    No keywords detected yet.

                </div>

            </div>


            <div class="info-section">

                <h2>
                    📌 Detected Topics
                </h2>

                <div id="topics">

                    No topics detected yet.

                </div>

            </div>


            <div class="info-section">

                <h2>
                    📋 Extracted Intelligence
                </h2>


                <p>

                    File:

                    <span id="filename">

                        No document uploaded

                    </span>

                </p>


                <div id="text">

                    Upload a PDF to view
                    extracted information here.

                </div>

            </div>


            <p class="status">

                ● ASTRA INTEL SYSTEM ONLINE

            </p>


        </div>


    </div>


    <script>


        async function uploadDocument() {


            const fileInput =
                document.getElementById(
                    "fileInput"
                );


            const message =
                document.getElementById(
                    "message"
                );


            if (!fileInput.files.length) {

                message.textContent =
                    "Please select a PDF first.";

                message.className =
                    "error";

                return;

            }


            const file =
                fileInput.files[0];


            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".pdf")
            ) {

                message.textContent =
                    "Only PDF files are supported.";

                message.className =
                    "error";

                return;

            }


            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            message.textContent =
                "Analyzing document...";

            message.className =
                "loading";


            try {


                const response =
                    await fetch(
                        "/analyze",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    message.textContent =
                        data.detail ||
                        "Something went wrong.";

                    message.className =
                        "error";

                    return;

                }


                document.getElementById(
                    "documentName"
                ).textContent =
                    data.filename.substring(
                        0,
                        18
                    );


                document.getElementById(
                    "filename"
                ).textContent =
                    data.filename;


                document.getElementById(
                    "pageCount"
                ).textContent =
                    data.pages;


                document.getElementById(
                    "wordCount"
                ).textContent =
                    data.word_count;


                document.getElementById(
                    "keywordCount"
                ).textContent =
                    data.keywords.length;


                document.getElementById(
                    "summary"
                ).textContent =
                    data.summary;


                document.getElementById(
                    "text"
                ).textContent =
                    data.text;


                // --------------------------------
                // KEYWORDS
                // --------------------------------

                const keywordBox =
                    document.getElementById(
                        "keywords"
                    );


                keywordBox.innerHTML = "";


                if (
                    data.keywords.length === 0
                ) {

                    keywordBox.textContent =
                        "No keywords detected.";

                }
                else {

                    data.keywords.forEach(
                        function(keyword) {

                            const span =
                                document.createElement(
                                    "span"
                                );

                            span.className =
                                "keyword";

                            span.textContent =
                                keyword;

                            keywordBox.appendChild(
                                span
                            );

                        }
                    );

                }


                // --------------------------------
                // TOPICS
                // --------------------------------

                const topicBox =
                    document.getElementById(
                        "topics"
                    );


                topicBox.innerHTML = "";


                data.topics.forEach(
                    function(topic) {

                        const span =
                            document.createElement(
                                "span"
                            );

                        span.className =
                            "topic";

                        span.textContent =
                            topic;

                        topicBox.appendChild(
                            span
                        );

                    }
                );


                message.textContent =
                    "Document analyzed successfully.";

                message.className =
                    "success";


            }

            catch (error) {

                console.error(error);

                message.textContent =
                    "Unable to connect to server.";

                message.className =
                    "error";

            }

        }

    </script>


</body>

</html>
"""


# ============================================================
# PDF ANALYSIS
# ============================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...)
):


    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not file.filename:

        return {
            "detail":
            "No file selected."
        }


    if not file.filename.lower().endswith(".pdf"):

        return {
            "detail":
            "Only PDF files are supported."
        }


    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    contents = await file.read()


    if not contents:

        return {
            "detail":
            "The uploaded file is empty."
        }


    # --------------------------------------------------------
    # OPEN PDF
    # --------------------------------------------------------

    try:

        document = pymupdf.open(
            stream=contents,
            filetype="pdf"
        )

    except Exception as error:

        print(
            "PDF Error:",
            error
        )

        return {
            "detail":
            "Could not read this PDF."
        }


    # --------------------------------------------------------
    # EXTRACT TEXT
    # --------------------------------------------------------

    extracted_text = ""


    for page_number, page in enumerate(
        document,
        start=1
    ):


        print(
            f"Processing page {page_number}..."
        )


        # ----------------------------------------------------
        # NORMAL TEXT EXTRACTION
        # ----------------------------------------------------

        try:

            text = page.get_text(
                "text",
                sort=True
            )

        except Exception as error:

            print(
                "Text extraction error:",
                error
            )

            text = ""


        # ----------------------------------------------------
        # OCR IF NECESSARY
        # ----------------------------------------------------

        if not text.strip():

            print(
                f"OCR running on page {page_number}..."
            )


            try:

                # IMPORTANT:
                # Keep this statement on ONE line.

                text_page = page.get_textpage_ocr(
                    language="eng",
                    dpi=200,
                    full=True,
                    tessdata=r"C:\Program Files\Tesseract-OCR\tessdata"
                )


                text = page.get_text(
                    "text",
                    textpage=text_page,
                    sort=True
                )


            except Exception as error:

                print(
                    "OCR Error:",
                    error
                )

                text = (
                    "OCR failed on this page."
                )


        # ----------------------------------------------------
        # ADD PAGE TEXT
        # ----------------------------------------------------

        extracted_text += text

        extracted_text += "\n\n"


    # --------------------------------------------------------
    # PAGE COUNT
    # --------------------------------------------------------

    page_count = len(document)


    # --------------------------------------------------------
    # WORD COUNT
    # --------------------------------------------------------

    word_count = len(
        extracted_text.split()
    )


    # --------------------------------------------------------
    # CLOSE DOCUMENT
    # --------------------------------------------------------

    document.close()


    # --------------------------------------------------------
    # CHECK EMPTY DOCUMENT
    # --------------------------------------------------------

    if not extracted_text.strip():

        extracted_text = (
            "No readable text was found "
            "in this PDF."
        )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = create_summary(
        extracted_text
    )


    # --------------------------------------------------------
    # KEYWORDS
    # --------------------------------------------------------

    keywords = extract_keywords(
        extracted_text
    )


    # --------------------------------------------------------
    # TOPICS
    # --------------------------------------------------------

    topics = detect_topics(
        extracted_text
    )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "filename":
            file.filename,

        "pages":
            page_count,

        "word_count":
            word_count,

        "text":
            extracted_text,

        "summary":
            summary,

        "keywords":
            keywords,

        "topics":
            topics

    }