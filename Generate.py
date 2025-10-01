import os
import time
import google.generativeai as genai

genai.configure(api_key="GEMINI-API-KEY")

def Generate_Quizzes(FilePath: str, UnitName: str) -> str:
    print(f"Uploading file {FilePath}...")
    uploaded_file = genai.upload_file(
        path=FilePath,
        display_name="Document to summarize"
    )
    print(f"Uploaded file '{uploaded_file.display_name}' as: {uploaded_file.uri}")
    print("Waiting for file to be processed...")
    while uploaded_file.state == "PROCESSING":
        time.sleep(5)
        uploaded_file = genai.get_file(name=uploaded_file.name)
        print(".", end="", flush=True)

    if uploaded_file.state == "FAILED":
        print("\nFile processing failed.")
    else:
        print(f"\nFile processing complete. State: {uploaded_file.state}")
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = "ช่วยสร้างคำถามจำนวนากที่สุดที่คุณสามารถทำได้ สำหรับฝึกจำสูตรฟที่เกี่ยวกับเอกสารฉบับนี้หน่อย ในรูปแบบคำถามปรนัย 4 ตัวเลือก โดยมีตัวเลือกที่ถูกต้อง 1 ตัวเลือก และตัวเลือกที่ผิด 3 ตัวเลือก ลักษณะคำถามเป็นภาษาไทยทั้งหมดและเป็นรูปแบบ json ตอบเฉพาะในรูปแบบ json เท่านั้น, ข้อมูลใน json ประกอบด้วย question, options, correct_answer, explanation "

        response = model.generate_content([uploaded_file, prompt])
        text = response.text or ""
        print(f"Model response length: {len(text)}")
        snippet = text[:400].replace('\n', ' ') if text else ''
        print(f"Model response snippet: {snippet}")

        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].strip()

        print(response.text)
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        out_path = os.path.join(data_dir, f"{UnitName}.json")
        if not text:
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass
            raise RuntimeError("No JSON content returned from model. See model logs above.")

        with open(out_path, "w+", encoding="utf-8") as f:
            f.write(text)

        try:
            genai.delete_file(uploaded_file.name)
        except Exception:
            pass

        print("\nFile deleted from API.")
        return out_path

if __name__ == "__main__":
    test_file_path = "Chapter 4.pdf"
    if os.path.exists(test_file_path):
        Generate_Quizzes(test_file_path, "unit-4")
    else:
        print(f"Test file '{test_file_path}' does not exist.")