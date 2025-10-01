from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask import jsonify
import os
import uuid
import json
import os
import socket
import managements
import fitz

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
STATIC_UPLOADS = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
COVER_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'cover')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_UPLOADS, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def intro():
    return render_template('intro.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    
    return render_template('dashboard.html')

@app.route('/index', methods=['GET'])
def units():
    raw = managements.loadDatabase()

    data = {}
    try:
        for key, item in raw.items():
            q = item.get('Question', '') if isinstance(item, dict) else ''
            if q:
                unit_param = os.path.basename(q)
            else:
                unit_param = item.get('Name', '') if isinstance(item, dict) else ''

            try:
                item_url = url_for('unit_view', unit=unit_param) if unit_param else '#'
            except Exception:
                item_url = '#'

            if isinstance(item, dict):
                item['url'] = item_url
                data[key] = item
            else:
                data[key] = item
    except Exception:
        data = raw

    return render_template('index_second.html', data=data)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    unit = request.form.get('unit')
    desc = request.form.get('description')
    if not file:
        flash('No file uploaded', 'error')
        return redirect('/index')

    filename = f"{unit}-{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    try:
        out_path = managements.createDatabase(Name=unit, Description=desc, PDFFile=path)
        if not out_path:
            flash('Error creating unit: JSON output not found', 'error')
        else:
            flash('Unit created successfully', 'success')
    except Exception as e:  
        flash(f'Error creating unit: {e}', 'error')
    return redirect('/index')

@app.route('/clear_data', methods=['get'])
def clear_data():
    def _safe_clear(folder):
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except Exception:
                pass

    for folder in (DATA_FOLDER, UPLOAD_FOLDER, COVER_FOLDER):
        _safe_clear(folder)

    db_path = os.path.join(os.path.dirname(__file__), 'database.json')
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)
    except Exception:
        flash('Warning: database file could not be reset', 'warning')

    flash('All data cleared', 'success')
    return redirect('/index')


@app.route('/generate_cover', methods=['POST'])
def generate_cover():
    try:
        file = request.files.get('file')
        name = request.form.get('name', 'cover')
        description = request.form.get('description', '')

        if not file:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        tmp_name = f"tmp-{uuid.uuid4().hex[:8]}-{file.filename}"
        tmp_path = os.path.join(UPLOAD_FOLDER, tmp_name)
        file.save(tmp_path)

        try:
            doc = fitz.open(tmp_path)
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            out_name = f"{uuid.uuid4().hex[:10]}.png"
            out_path = os.path.join(STATIC_UPLOADS, out_name)
            pix.save(out_path)
            doc.close()
        except Exception as e:
            return jsonify({'success': False, 'error': f'PDF conversion failed: {e}'}), 500


        url = f"/static/uploads/{out_name}"
        return jsonify({'success': True, 'url': url, 'name': name, 'description': description})

    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
           
@app.route('/unit/<unit>')
def unit_view(unit):
    json_path = os.path.join(DATA_FOLDER, f"{unit}")
    if not os.path.exists(json_path):
        flash('Unit not found', 'error')
        return redirect('/index')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        
        questions = []
        for idx, item in enumerate(quiz_data):
            try:
                question_text = item.get('question', '').strip()
                options = item.get('options', [])
                correct_answer = item.get('correct_answer', '').strip()
                explanation = item.get('explanation', '').strip()
                
                if not question_text:
                    print(f"Question {idx}: Missing question text")
                    continue
                    
                if len(options) != 4:
                    print(f"Question {idx}: Must have exactly 4 options")
                    continue
                    
                if not correct_answer:
                    print(f"Question {idx}: Missing correct answer")
                    continue
                
                correct_text = None
                
                if correct_answer in options:
                    correct_text = correct_answer
                else:
                    for option in options:
                        if option.startswith(correct_answer):
                            correct_text = option
                            break
                    
                    if not correct_text:
                        letter_only = correct_answer.rstrip('.')
                        for option in options:
                            if option.startswith(letter_only + '.'):
                                correct_text = option
                                break
                
                if not correct_text:
                    print(f"Question {idx}: Correct answer '{correct_answer}' not found in options: {options}")
                    continue
                
                print(f"Question {idx}: Matched '{correct_answer}' to '{correct_text}'")
                
                questions.append({
                    'question': question_text,
                    'options': options,
                    'correct': correct_text,
                    'explanation': explanation
                })
                
            except Exception as e:
                print(f"Error processing question {idx}: {e}")
                continue
        
        print(f"Successfully loaded {len(questions)} questions from JSON")
        
        if not questions:
            flash('No valid questions found in JSON file', 'error')
            return redirect('/index')
            
        return render_template('quiz.html', unit=unit.split('.')[0], questions=questions)
        
    except json.JSONDecodeError as e:
        flash(f'Invalid JSON format: {str(e)}', 'error')
        return redirect('/index')
    except Exception as e:
        flash(f'Error reading quiz data: {str(e)}', 'error')
        return redirect('/index')

@app.route('/download/<unit>')
def download(unit):
    csv_path = os.path.join(DATA_FOLDER, f"{unit}.csv")
    if not os.path.exists(csv_path):
        flash('Unit not found', 'error')
        return redirect(url_for('index'))
    return send_from_directory(DATA_FOLDER, f"{unit}.csv", as_attachment=True)

@app.route('/contacts', methods=['GET'])
def contacts():
    return render_template('contacts.html')

if __name__ == '__main__':
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    app.run(host=ip_address, port=5000, debug=True)
