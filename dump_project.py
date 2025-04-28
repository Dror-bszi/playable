import os
import datetime

# === CONFIGURATION ===
HARDCODED_FOLDER_PATH = r"C:\Users\drorb\Documents\VScode\Python\projects\PlayAble"
# ======================

# === FOLDERS TO IGNORE ===
IGNORED_FOLDERS = {'.git'}
# ==========================

def dump_project(folder_path):
    # Get main folder name
    main_folder_name = os.path.basename(os.path.normpath(folder_path))
    
    # Get current time and date
    now = datetime.datetime.now()
    time_str = now.strftime("%H-%M")
    date_str = now.strftime("%d-%m-%Y")
    
    # Build filename
    output_filename = f"{main_folder_name}_{time_str}_{date_str}.txt"
    
    # Get Downloads folder path
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    output_file_path = os.path.join(downloads_folder, output_filename)

    # Get absolute path of this script
    script_path = os.path.abspath(__file__)

    with open(output_file_path, 'w', encoding='utf-8') as out_file:
        for root, dirs, files in os.walk(folder_path):
            # Skip ignored folders
            dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]
            
            for file in files:
                file_path = os.path.join(root, file)
                # Skip this script itself
                if os.path.abspath(file_path) == script_path:
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    content = f"[ERROR READING FILE: {e}]\n"

                # Write file path
                out_file.write("\n" + "="*80 + "\n")
                out_file.write(f"FILE: {file_path}\n")
                out_file.write("="*80 + "\n\n")
                
                # Write file content
                out_file.write(content)
                out_file.write("\n\n")  # extra newline after each file

    print(f"Project dumped successfully into: {output_file_path}")

if __name__ == "__main__":
    # Decide if using hardcoded path or asking user
    if HARDCODED_FOLDER_PATH and os.path.isdir(HARDCODED_FOLDER_PATH):
        folder_to_dump = HARDCODED_FOLDER_PATH
    else:
        folder_to_dump = input("Enter the path to the folder you want to dump: ").strip()

    if not os.path.isdir(folder_to_dump):
        print("Error: The folder does not exist. Please check the path and try again.")
    else:
        dump_project(folder_to_dump)
