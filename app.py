
from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from gradio_client import Client, file
from zipfile import ZipFile
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = Client("https://pragnakalp-ocr-image-to-text.hf.space/--replicas/qf1w1/")

# File path for storing links
LINKS_FILE = 'links.json'

# Load links from file
def load_links():
    try:
        with open(LINKS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Return an empty dictionary if the file doesn't exist
        return {}

# Save links to file
def save_links(links):
    with open(LINKS_FILE, 'w') as file:
        json.dump(links, file)

# Initialize links dictionary
links = load_links()

command=None 

def process_images(files):
    clusters = {}
    print(files)
    for file in files:
        # Extract text using OCR
        text = extract_text(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        print(text)
        # Check for patterns like #A1 or #B1 in the extracted text
        for word in text.split():
            if word.startswith("#") and len(word) >= 3 and word[1].isalpha() and word[2:].isdigit():
                global command
                command = word[1]
                cluster = int(word[2:])
                if command == "A":
                    # Proceed with normal functionality
                    if cluster not in clusters:
                        clusters[cluster] = []
                    clusters[cluster].append(file)
                elif command == "X":
                    # Handle the functionality related to command B
                    print("Executing X")
                    return handle_command_b(cluster)#added return
                break  # Stop processing the text after finding the first pattern
    return clusters


def handle_command_b(cluster_code):
    # Assuming you have a dictionary to store links associated with cluster codes
    print("cluster code",cluster_code)
    global links
    #links = {
    #    11: "https://www.google.co.in/",
#        2: "http://example.com/link2",
#        # Add more links as needed
#    }   
    print(1 in links)
    print('1' in links)
    print(str(1) in links)
    x=str(cluster_code)
    if x in links:
        link = links[str(cluster_code) ]
        # Redirect the user to the associated link
        print("link is present",link)
        return redirect(link)
    else:
        # If no link is stored, allow the user to add a link
        # Here you can redirect the user to a page where they can add a link
        # or display a form to input a link
        return redirect(url_for('add_link', cluster=cluster_code))


@app.route('/')
def index():
    return render_template('index.html', links=links)

@app.route('/add_link/<cluster>', methods=['GET', 'POST'])
def add_link(cluster):
    links=load_links()
    if request.method == 'POST':
        link = request.form['link']
        links[cluster] = link
        print(links)
        save_links(links)
        return redirect(url_for('index'))
    else:
        print(links)
        return render_template('add_link.html', cluster=cluster)

def extract_text(image_path):
    # Make prediction using Gradio client to extract text
    result = client.predict(
        "PaddleOCR",
        file(image_path),
        api_name="/predict"
    )
    print(result)
    return result


@app.route('/upload', methods=['POST'])
def upload():
    global links
    print(links)
    print(request.files)
    if 'file' not in request.files:
        return "No file part"
    

    files = request.files.getlist('file')
    print("files are ",files)

    for file in files:
        print("names are",file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    clusters = process_images(files)
    global command
    print(command)
    if(command=='X'):#
        print(links)
        return clusters #
    zip_files = []
    for cluster, image_files in clusters.items():
        with ZipFile(f'{cluster}.zip', 'w') as zipf:
            for image in image_files:
                zipf.write(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
        zip_files.append(f'{cluster}.zip')
    
    return render_template('download.html', zip_files=zip_files)

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)



































""""
from flask import Flask, render_template, request, send_file
import os
from gradio_client import Client, file
from zipfile import ZipFile

app = Flask(__name__)

client = Client("https://pragnakalp-ocr-image-to-text.hf.space/--replicas/qf1w1/")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_text(image_path):
    # Make prediction using Gradio client to extract text
    result = client.predict(
        "PaddleOCR",
        file(image_path),
        api_name="/predict"
    )
    print(result)
    return result



def process_images(files):
    clusters = {}
    for file in files:
        # Extract text using OCR
        text = extract_text(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        # Check for patterns like #A1 in the extracted text
        for word in text.split():
            if word.startswith("#") and len(word) >= 3 and word[1].isalpha() and word[2:].isdigit():
                # Extract command and cluster code and store image in the corresponding cluster
                command = word[1]
                cluster = int(word[2:])
                print("Cluster name",cluster)
                if cluster not in clusters:
                    clusters[cluster] = []
                clusters[cluster].append(file)
                break  # Stop processing the text after finding the first pattern
    return clusters


@app.route('/')
def index():
    return render_template('index.html')

'''
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    files = request.files.getlist('file')
    
    for file in files:
        # Extract text using OCR)
        text = extract_text(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        # Check for patterns like #A1 in the extracted text
        for word in text.split():
            if word.startswith("#") and len(word) >= 3 and word[1].isalpha() and word[2:].isdigit():
                # Extract command and cluster code
                command = word[1]
                cluster = int(word[2:])
                # Create subfolder based on cluster code if it doesn't exist
                subfolder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(cluster))
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
                # Save image to the corresponding subfolder
                file.save(os.path.join(subfolder_path, file.filename))
                break  # Stop processing the text after finding the first pattern
    
    return "Upload and processing completed successfully"
'''

'''
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    files = request.files.getlist('file')
    
    # Dictionary to store images grouped by cluster code
    cluster_images = {}

    for file in files:
        # Extract text using OCR
        text = extract_text(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        # Check for patterns like #AB in the extracted text
        for word in text.split():
            if word.startswith("#") and len(word) >= 3 and word[1].isalpha() and word[2:].isdigit():
                # Extract command and cluster code
                command = word[1]
                cluster = int(word[2:])
                # Create folder for cluster if it doesn't exist
                cluster_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(cluster))
                if not os.path.exists(cluster_folder):
                    os.makedirs(cluster_folder)
                # Save image to the cluster folder
                file.save(os.path.join(cluster_folder, file.filename))
                break  # Stop processing the text after finding the first pattern

    return "Files uploaded successfully."
'''

#working version-1
'''
@app.route('/upload', methods=['POST'])
def upload():
    print(request.files)
    if 'file' not in request.files:
        return "No file part"
    
    files = request.files.getlist('file')
    
    for file in files:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    
    clusters = process_images(files)
    
    zip_files = []
    for cluster, image_texts in clusters.items():
        with ZipFile(f'{cluster}.zip', 'w') as zipf:
            for image, text in image_texts:
                # Save image to zip file along with text
                zipf.write(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
                # Create a text file containing the extracted text
                with open(os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(image.filename)[0] + '.txt'), 'w') as text_file:
                    text_file.write(text)
        zip_files.append(f'{cluster}.zip')
    
    return render_template('download.html', zip_files=zip_files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    files = request.files.getlist('file')
    
    for file in files:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    
    clusters = process_images(files)
    
    zip_files = []
    for cluster, cluster_files in clusters.items():
        with ZipFile(f'{cluster}.zip', 'w') as zipf:
            for file in cluster_files:
                # Save image to zip file
                zipf.write(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        zip_files.append(f'{cluster}.zip')
    
    return render_template('download.html', zip_files=zip_files)




@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)




'''

"""