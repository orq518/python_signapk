from werkzeug.utils import redirect
from flask import Flask, render_template, url_for
from flask import request, send_from_directory
import os,time


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

    config = open(os.path.join(file_dir,"config_keystore.txt"), "w")
    try:
        config.write("aliase="+aliase+"#"+"storepass="+storepass+"#"+"keypass=" + keypass)
    finally:
        config.close()
    if keystore:
        fname = "keystore_"+keystore.filename
        print('keystore文件名：', fname)
        keystore.save(os.path.join(file_dir, fname))
        return redirect(url_for('manage_file'))
    else:
        return redirect(url_for('error',err_msg="创建项目失败"))


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
        #先删除以前的文件
        projects_list = os.listdir(file_dir)
        for file in projects_list:
            if file.startswith('unsign_'):#未签名文件
                file_del = os.path.join(file_dir, file)
                if os.path.isfile(file_del):
                    os.remove(file_del)
            elif file.startswith('signed_'):#已经签名apk
                file_del = os.path.join(file_dir, file)
                if os.path.isfile(file_del):
                    os.remove(file_del)

        f.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
        return redirect(url_for('manage_file'))
    else:
        return redirect(url_for('error',err_msg="文件上传失败"))


@app.route('/manage')
def manage_file():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    projects_list = os.listdir(file_dir)
    projects=[]
    print("读取项目列表：", projects_list)
    for project in projects_list:
        project_dir = os.path.join(file_dir,project)
        projects_content = os.listdir(project_dir)
        print("读取项目内容：", projects_content)
        project_dict = {}
        project_dict['project_name'] = ""+project
        for file in projects_content:
            if file.startswith('keystore_'):#读取keystore文件名
                project_dict['keystore_name']=file
                project_dict['keystore_path']=os.path.join(project_dir,file)
            elif file.startswith('unsign_'):#未签名文件
                project_dict['unsign_apk_name']=file
                project_dict['unsign_apk_path']=os.path.join(project_dir, file)
            elif file.startswith('signed_'):#已经签名apk
                project_dict['signed_apk_name']=file
                project_dict['signed_apk_path']=os.path.join(project_dir, file)
            elif file.startswith('config_'):#keystore配置文件
                config_file_path=os.path.join(project_dir, file)
                print('config_file_path:',config_file_path)
                config_file = open(config_file_path)
                if not config_file:
                    pass
                # "aliase=" + aliase + "#" + "storepass=" + storepass + "#" + "keypass=" + keypass
                try:
                    context = config_file.read()
                    data=context.split('#')
                    for text in data:
                        t=text.split('=')
                        if len(t)==2:
                            project_dict[t[0]]=t[1]
                finally:
                    config_file.close()
                projects.append(project_dict)

    return render_template('manage.html', projects_list=projects)

@app.route('/download_file/<project_name>/<file_name>')
def download(project_name,file_name):
    print("下载的工程和文件", project_name, file_name)
    if request.method == "GET":
        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        file_download = os.path.join(file_dir, project_name)
        if os.path.isfile(os.path.join(file_download, file_name)):
            print("下载的file_dir:", file_dir)
            return send_from_directory(file_download, file_name, as_attachment=True)
            #中文路径不好使
            # send_from_directory方法，经过实测，需加参数as_attachment=True，否则对于图片格式、txt格式，
            # 会把文件内容直接显示在浏览器，对于xlsx等格式，虽然会下载，但是下载的文件名也不正确，切记切记

#apk签名
@app.route('/sign_apk/<project_name>')
def sign_apk(project_name):
    print("下载的工程和文件", project_name)
    if request.method == "GET":
        project_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'],project_name)
        projects_content = os.listdir(project_dir)
        print("读取项目列表：", projects_content)
        project_dict = {}
        for file in projects_content:
            if file.startswith('keystore_'):  # 读取keystore文件名
                project_dict['keystore_name'] = file
                project_dict['keystore_path'] = os.path.join(project_dir, file)
            elif file.startswith('unsign_'):  # 未签名文件
                project_dict['unsign_apk_name'] = file
                project_dict['unsign_apk_path'] = os.path.join(project_dir, file)
            elif file.startswith('config_'):  # keystore配置文件
                config_file_path = os.path.join(project_dir, file)
                print('config_file_path:', config_file_path)
                config_file = open(config_file_path)
                if not config_file:
                    pass
                # "aliase=" + aliase + "#" + "storepass=" + storepass + "#" + "keypass=" + keypass
                try:
                    context = config_file.read()
                    data = context.split('#')
                    for text in data:
                        t = text.split('=')
                        if len(t) == 2:
                            project_dict[t[0]] = t[1]
                finally:
                    config_file.close()
        time_signed = time.strftime('%m_%d_%H_%M', time.localtime(time.time()))
        sign_apk_path=os.path.join(project_dir, 'signed_apk_'+time_signed+'.apk')
        # signcmd = 'jarsigner -sigalg SHA1withRSA -digestalg SHA1 -keystore "%s" -storepass "%s" -signedjar "%s" "%s" "%s"' % (
        # keystore, keypass, signedFile, f, keyalias)
        # signcmd = 'jarsigner -verbose -keystore /Users/ruiqiangou/Downloads/ucfpay_keystore -storepass ucfpay2014 -keypass ucfpay201407 -signedjar /Users/ruiqiangou/Downloads/北方金融网-—signed.apk -digestalg SHA1 -sigalg SHA256withRSA  /Users/ruiqiangou/Downloads/北方金融网_legu.apk ucfpay'
        signcmd = 'jarsigner -verbose -keystore "%s" -storepass "%s" -keypass "%s" -signedjar "%s" -digestalg SHA1 -sigalg SHA256withRSA  "%s" "%s"' % (
        project_dict['keystore_path'], project_dict['storepass'], project_dict['keypass'],sign_apk_path, project_dict['unsign_apk_path'], project_dict['aliase'])
        os.system(signcmd)  # v1签名命令
        return redirect(url_for('manage_file'))




@app.route('/delete_file/<project_name>/<file_name>')
def delete(project_name,file_name):
    print("删除的工程和文件", project_name,file_name)
    if request.method == "GET":
        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        file_del=os.path.join(file_dir, project_name,file_name)
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
