import os
import recommender, path
import pandas as pd
import shutil # Used to move files across directories.

from flask import Flask, request, render_template, send_from_directory

__author__ = 'Aazim Lakhani'

app = Flask(__name__)

#APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(os.path.abspath(''))
print('APP_ROOT : ' , APP_ROOT)

# import os
# dirname = os.path.dirname(__file__)
# print("dirname : " , dirname)
#filename = os.path.join(dirname, 'relative/path/to/file/you/want')



@app.route("/")
def index():
    #team_sheet = pd.read_excel(os.environ['PROJECT_DIR'] + 'rawdata\\Team List.xlsx', header=1, index_col=2)
    #team_sheet = pd.read_excel(APP_ROOT + path.team_list , header=1, index_col=2)
    #print(team_sheet.head())
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    # folder_name = request.form['upload-form']
    # print('folder_name : ', folder_name)
    '''
    # this is to verify that folder to upload to exists.
    if os.path.isdir(os.path.join(APP_ROOT, 'files/{}'.format(folder_name))):
        print("folder exist")
    '''
    #target = os.path.join(APP_ROOT, 'data/sm9/{}'.format(folder_name))
    #target = os.path.join(APP_ROOT, 'data/sm9/')
    #print(target)
    # if not os.path.isdir(target):
    #     os.mkdir(target)
    #print("request.files.getlist : ", request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        #print("{} is the file name".format(upload.filename))
        filename = upload.filename
        # # This is to verify files are supported
        start, ext = os.path.splitext(filename)
        dir = getDir(start)
        print('path.APP_ROOT : ', path.APP_ROOT)
        print('path.DIR_NAME :', path.DIR_NAME)
        print('dir :', dir)
        #target = os.path.join(path.APP_ROOT, dir)
        target = os.path.join(path.DIR_NAME,dir)
        #target = dirname + dir
        print('target : ', target)
        # print('Start : ', start)
        # print('ext : ', ext)
        #ext = os.path.splitext(filename)[1]
        # #if (ext == ".xlsx") or (ext == ".png"):
        # if ext == ".xlsx":
        #     print("File supported moving on...")
        # else:
        #     render_template("Error.html", message="Files uploaded are not supported...")
        #destination = "/".join([target, filename])
        destination = os.path.join(target, filename)
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    # return send_from_directory("images", filename, as_attachment=True)
    #return render_template("complete.html", image_name=filename)
    return render_template("complete.html")


def getDir(filename):
    # This is the file name. Use Switch to set target.
    filename_to_target = {
        'sm9_train': 'data/sm9/train',
        'sm9_predict': 'data/sm9/test',
        'sn_train': 'data/serviceNow/train',
        'sn_predict': 'data/serviceNow/test',
        'otpa': 'data/postprocess/otpa',
        'vacation calendar 2018': 'data/postprocess/vc',
        'global 2018': 'data/postprocess/global',
        'team list': 'data/postprocess/team',
        'client_base_to_team_mapper': 'data/postprocess/client_base_mapper'
    }
    file_type = [key for key in filename_to_target.keys() if filename.lower().startswith(key)]
    target = filename_to_target[file_type.pop()]
    # print(file_type.pop() )
    # print(file_type)
    #print('filename_to_target : ', )
    return target

@app.route("/train", methods=["POST"])
def train():
    print("Train method ")
    recommender.train()
    return render_template("complete.html")


@app.route("/predict", methods=["POST"])
def predict():
    print("Predict method")
    recommender.predict()
    move_to_archive()
    return render_template("complete.html")


def move_to_archive():
    print("Started executng move_to_archive ")
    src_to_dest = {
                   'data/sm9/test/' : 'data/sm9/test-archive',
                   'data/serviceNow/test/' : 'data/serviceNow/test-archive' ,
                    'data/postprocess/otpa/' : 'data/postprocess/otpa-archive'
                    }
    for src in src_to_dest.keys():
        print(src)
        files = os.listdir(os.path.join(path.DIR_NAME , src))
        for f in files:
            shutil.move(os.path.join(path.DIR_NAME , src , f) , os.path.join(path.DIR_NAME , src_to_dest[src]))
    print("Done executng move_to_archive ")

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


@app.route('/gallery')
def get_gallery():
    image_names = os.listdir('./images')
    print(image_names)
    return render_template("gallery.html", image_names=image_names)


if __name__ == "__main__":
    # Get port from environment variable or choose 9099 as local default
    port = int(os.getenv("PORT", 9099))
    # Run the app, listening on all IPs with our chosen port number
    #app.run(host='0.0.0.0', port=port, debug=True)
    app.run(port=4555, debug=True)