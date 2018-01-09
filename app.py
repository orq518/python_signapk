from werkzeug.utils import redirect
from flask import Flask, render_template, url_for
from flask import request, send_from_directory
import os


app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF', 'apk'])

# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 用于判断文件后缀
def allowed_file_apk(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] == "apk"

# # 用于测试上传，稍后用到
# @app.route('/upload')
# def upload_test():
#     return render_template('upload.html')
# 用于测试上传，稍后用到
@app.route('/error<err_msg>')
def error(err_msg):
    return render_template('error.html', err_msg=err_msg)


# 新建项目工程
@app.route('/new_project', methods=['POST'], strict_slashes=False)
def new_project():
    projectname = request.form.get('projectname')  # 项目名称
    keystore = request.files['keystore']  # 签名文件
    aliase = request.form.get('aliase')  # 别名
    storepass = request.form.get('storepass')  # keystore第一个密码
    keypass = request.form.get('keypass')  # keystore第二个密码

    if projectname.strip()=='' or aliase.strip()=='' or storepass.strip()==''or keypass.strip()=='':  # 判断字段是否为空
        return redirect(url_for('error', err_msg="必填项不能为空"))

    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'],projectname)

    print('file_dir：', file_dir)

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    if keystore:
        fname = keystore.filename
        print('keystore文件名：', fname)
        keystore.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
        return redirect(url_for('manage_file'))
    else:
        return redirect(url_for('error',err_msg="创建项目失败"))

# # 上传文件
# @app.route('/upload', methods=['POST'], strict_slashes=False)
# def api_upload():
#     file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
#     if not os.path.exists(file_dir):
#         os.makedirs(file_dir)
#     f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
#     if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
#         print('原始文件名：', f.filename)
#         fname = f.filename
#         print('文件名：', fname)
#         f.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
#         print("token：", fname)
#         return redirect(url_for('manage_file'))
#     else:
#         return redirect(url_for('error',err_msg="ss"))

# 上传apk文件
@app.route('/upload_apk<project_name>', methods=['POST'], strict_slashes=False)
def upload_apk(project_name):
    print('文件名project_name：', project_name)
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'],project_name)
    print('file_dir：', file_dir)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['apkfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if not allowed_file_apk(f.filename):  # 判断是否是允许上传的文件类型
        return redirect(url_for('error', err_msg="错误的文件类型"))
    if f:
        print('原始文件名：', f.filename)
        fname = "unsign_"+f.filename
        print('文件名：', fname)
        f.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
        return redirect(url_for('manage_file'))
    else:
        return redirect(url_for('error',err_msg="文件上传失败"))

# # 上传apk文件
# @app.route('/upload_apk<project_name>', methods=['POST'], strict_slashes=False)
# def upload_apk(project_name):
#     files_path = os.path.join(basedir, UPLOAD_FOLDER)
#     if not os.path.exists(files_path):
#         os.makedirs(files_path)
#     file_dir = files_path+"/"+project_name#项目的目录
#     if not os.path.exists(file_dir):
#         os.makedirs(file_dir)
#     f = request.files['apkfile']  # 从表单的file字段获取文件，apkfile为该表单的name值
#
#     if not allowed_file_apk(f.filename):  # 判断是否是允许上传的文件类型
#         return redirect(url_for('error', err_msg="错误的文件类型"))
#     if f:
#         print('原始文件名：', f.filename)
#         fname = "unsign_"+f.filename
#         print('文件名：', fname)
#         f.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
#         return redirect(url_for('manage_file'))
#     else:
#         return redirect(url_for('error',err_msg="文件上传失败"))

@app.route('/manage')
def manage_file():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    files_list = os.listdir(file_dir)
    print("读取文件路径：", files_list)
    return render_template('manage.html', files_list=files_list)

@app.route('/download_file<filename>')
def download(filename):
    print("下载文件名：", filename)
    if request.method == "GET":
        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        if os.path.isfile(os.path.join(file_dir, filename)):
            return send_from_directory(file_dir, filename, as_attachment=True)
            # send_from_directory方法，经过实测，需加参数as_attachment=True，否则对于图片格式、txt格式，
            # 会把文件内容直接显示在浏览器，对于xlsx等格式，虽然会下载，但是下载的文件名也不正确，切记切记

@app.route('/delete_file<filename>')
def delete(filename):
    print("下载文件名：", filename)
    if request.method == "GET":
        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        file_del=os.path.join(file_dir, filename)
        if os.path.isfile(file_del):
            os.remove(file_del)
            return redirect(url_for('manage_file'))



# @app.route('/open/<filename>')
# def open_file(filename):
#     file_url = photos.url(filename)
#     return render_template('browser.html', file_url=file_url)
#
#
# @app.route('/delete/<filename>')
# def delete_file(filename):
#     file_path = photos.path(filename)
#     os.remove(file_path)
#     return redirect(url_for('manage_file'))

# # 上传文件
# @app.route('/api/upload', methods=['POST'], strict_slashes=False)
# def api_upload():
#     file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
#     if not os.path.exists(file_dir):
#         os.makedirs(file_dir)
#     f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
#     if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
#         print('原始文件名：', f.filename)
#         fname = secure_filename(f.filename)
#         print('文件名：',fname)
#         ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
#         unix_time = int(time.time())
#         new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
#         f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
#         token= hashlib.md5(new_filename.encode('utf-8')).hexdigest()[:15]
#         print("token：",token)
#
#         return jsonify({"errno": 0, "errmsg": "上传成功", "token": token})
#     else:
#         return jsonify({"errno": 1001, "errmsg": "上传失败"})

if __name__ == '__main__':
    app.run(debug=True)
