from flask import Flask, request, send_file
import pandas as pd
import pdfplumber
import io

app = Flask(__name__)

@app.route('/')
def home():
    return open("index.html").read()

@app.route('/upload', methods=['POST'])
def upload_pdf():
    pdf_file = request.files['pdf_file']
    
    with pdfplumber.open(pdf_file) as pdf:
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for i, df in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f'Table{i+1}', index=False)
        output.seek(0)

    return send_file(output, download_name="converted.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)