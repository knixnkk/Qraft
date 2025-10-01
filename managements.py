import os
import fitz
from PIL import Image
import json
from Generate import Generate_Quizzes

def get_files_in_folder(folder_path: str) -> list[str]:
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def get_file_path(filename: str) -> str:
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, 'data', filename)

def load_file_content(filename: str) -> str:
    file_path = get_file_path(filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def getCover(pdf_file, filename):
    try:
        base_dir = os.path.dirname(__file__)

        cover_dir_rel = os.path.dirname(filename) or 'static/cover'
        if os.path.isabs(cover_dir_rel):
            full_cover_dir = cover_dir_rel
        else:
            full_cover_dir = os.path.join(base_dir, cover_dir_rel)

        os.makedirs(full_cover_dir, exist_ok=True)

        base_name = os.path.basename(filename)
        cover_filename = f"{base_name}.jpg"
        full_cover_path = os.path.join(full_cover_dir, cover_filename)

        doc = fitz.open(pdf_file)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.save(full_cover_path, "JPEG", quality=95)
        doc.close()

        rel_cover_path = os.path.join(cover_dir_rel, cover_filename).replace('\\', '/')
        print(f"Cover saved: {full_cover_path}")
        return rel_cover_path
    except Exception as e:
        print(f"Error creating cover for {pdf_file}: {e}")
        return None

def createDatabase(Name, Description, PDFFile):
    try:
        CoverImage = getCover(PDFFile, f"static/cover/{Name}")
        Question = Generate_Quizzes(FilePath=PDFFile, UnitName=Name)
        db_path = os.path.join(os.path.dirname(__file__), 'database.json')
        data = {}
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        new_id = str(len(data) + 1)
        data[new_id] = {
            "Name": Name,
            "PDF" : PDFFile,
            "Description": Description,
            "CoverImage": CoverImage if isinstance(CoverImage, str) else (CoverImage or ""),
            "Question": Question if isinstance(Question, str) else (Question or "")
        }
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Database updated with ID {new_id}")
        return new_id
    except Exception as e:
        print(f"Error: {e}")
        return None


def loadDatabase():
    db_path = os.path.join(os.path.dirname(__file__), 'database.json')
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

if __name__ == "__main__":
    createDatabase('GeneralPhysics-04','desc', 'uploads/Chapter 4.pdf')