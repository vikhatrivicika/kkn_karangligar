from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from laporan1 import generate_pdf
import mysql.connector
import os
import time
import hashlib
from datetime import datetime, timedelta, timezone

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='kkn_karangligar'
        )
        print("Database connection successful")
        return db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Function to check session timeout
def check_session_timeout():
    if 'loggedin' in session:
        login_time = session.get('login_time')
        if isinstance(login_time, str):
            login_time = datetime.fromisoformat(login_time)  # Convert string back to datetime
            elapsed_time = datetime.now(timezone.utc) - login_time
            if elapsed_time > timedelta(minutes=5):
                session.pop('loggedin', None)
                session.pop('id_tmu', None)
                session.pop('username_tmu', None)
                session.pop('login_time', None)
                flash('Session expired. Please log in again.', 'warning')
                return False
    return True

@app.route('/')
def index():
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id_ttp, judul_ttp, gambar_ttp FROM tbl_t_post WHERE active_ttp = '1' AND delected_ttp IS NULL")
        posts = cursor.fetchall()
        cursor.execute("SELECT * FROM tbl_m_data WHERE active_tmd = '1' AND delected_tmd IS NULL")
        data = cursor.fetchall()
        return render_template('index.html', posts=posts, data=data)
    return "Database connection error"

@app.route('/form_page/<int:id>', methods=['GET', 'POST'])
def form_page(id):
    if request.method == 'POST':
        nama = request.form['nama']
        umur = request.form['umur']
        alamat = request.form['alamat']

        # Generate PDF
        pdf_path, timestamp = generate_pdf(nama, umur, alamat, id)

        if pdf_path:
            db = get_db_connection()
            if db:
                cursor = db.cursor()
                file_name = os.path.basename(pdf_path)
                jenis_ttp = 'informasi'  # Misalnya jenis informasi
                cursor.execute("INSERT INTO tbl_t_pdf (file_ttp, jenis_ttp, created_time_ttp) VALUES (%s, %s, current_timestamp())", (file_name, jenis_ttp))
                db.commit()
                flash('PDF successfully created and saved to database!', 'success')
            else:
                flash('Database connection error. PDF not saved to database.', 'danger')
        else:
            flash('Failed to create PDF.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('form_page.html', id=id)

@app.route('/blog/<int:id>')
def blog(id):
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_t_post WHERE id_ttp = %s", (id,))
        post = cursor.fetchone()
        if post:
            return render_template('blog.html', post=post)
        else:
            return "Post not found"
    return "Database connection error"

@app.route('/informasi/<int:id>', methods=['GET', 'POST'])
def informasi(id):
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_m_data WHERE id_tmd = %s", (id,))
        post = cursor.fetchone()

        if post:
            file = post['nama_tmd']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)

            # Read the CSV/Excel file into a DataFrame
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            columns = df.columns.tolist()

            if request.method == 'POST':
                column = request.form['column']
                keyword = request.form['keyword']
                results = df[df[column].astype(str).str.contains(keyword, case=False, na=False)]
                if not results.empty:
                    results_html = results.to_html(classes='table table-bordered', index=False)
                else:
                    results_html = None
                return render_template('informasi.html', post=post, columns=columns, results_html=results_html, search_performed=True, no_results=results.empty)

            return render_template('informasi.html', post=post, columns=columns, search_performed=False)
    return "Database connection error"

@app.route('/admin')
def admin():
    if check_session_timeout() and 'loggedin' in session:
        return render_template('admin/index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password using MD5
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tbl_m_users WHERE username_tmu = %s AND password_tmu = %s", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                session['loggedin'] = True
                session['id_tmu'] = user['id_tmu']
                session['username_tmu'] = user['username_tmu']
                session['login_time'] = datetime.now(timezone.utc).isoformat()  # Simpan waktu login sebagai string
                return redirect(url_for('admin'))
            else:
                flash('Incorrect username/password!', 'danger')
                return render_template('login.html')
        return "Database connection error"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id_tmu', None)
    session.pop('username_tmu', None)
    session.pop('login_time', None)
    return redirect(url_for('index'))

@app.route('/admin/posts')
def admin_posts():
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tbl_t_post WHERE delected_ttp IS NULL")
            posts = cursor.fetchall()
            return render_template('admin/posts.html', posts=posts)
        return "Database connection error"
    return redirect(url_for('login'))

@app.route('/admin/add_post', methods=['GET', 'POST'])
def add_post():
    if check_session_timeout() and 'loggedin' in session:
        if request.method == 'POST':
            judul_ttp = request.form['judul_ttp']
            postingan_ttp = request.form['postingan_ttp']
            id_tml = request.form['id_tml']
            file = request.files['gambar_ttp']

            # Save the uploaded file
            filename = None
            if file:
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

            db = get_db_connection()
            if db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO tbl_t_post (judul_ttp, postingan_ttp, active_ttp, created_ttp, id_tml, gambar_ttp) VALUES (%s, %s, %s, %s, %s, %s)",
                            (judul_ttp, postingan_ttp, '1', int(time.time()), id_tml, filename))
                db.commit()
                flash('Post added successfully!', 'success')
                return redirect(url_for('admin_posts'))

        # Fetch labels to pass to the template
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tbl_m_label WHERE delected_tml IS NULL")
            labels = cursor.fetchall()
            return render_template('admin/add_post.html', labels=labels)
    return redirect(url_for('login'))

@app.route('/admin/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                judul_ttp = request.form['judul_ttp']
                postingan_ttp = request.form['postingan_ttp']
                id_tml = request.form['id_tml']
                file = request.files['gambar_ttp']
                
                # Save the uploaded file if it exists
                if file and file.filename != '':
                    filename = file.filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    cursor.execute("UPDATE tbl_t_post SET gambar_ttp = %s WHERE id_ttp = %s", (filename, id))

                cursor.execute("UPDATE tbl_t_post SET judul_ttp = %s, postingan_ttp = %s, id_tml = %s WHERE id_ttp = %s", 
                               (judul_ttp, postingan_ttp, id_tml, id))
                db.commit()
                flash('Post updated successfully!', 'success')
                return redirect(url_for('admin_posts'))
            
            cursor.execute("SELECT * FROM tbl_t_post WHERE id_ttp = %s", (id,))
            post = cursor.fetchone()
            
            cursor.execute("SELECT * FROM tbl_m_label")
            labels = cursor.fetchall()
            
            return render_template('admin/edit_post.html', post=post, labels=labels)
        return "Database connection error"
    return redirect(url_for('login'))

@app.route('/admin/delete_post/<int:id>', methods=['POST'])
def delete_post(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            Timestamp = datetime.now(timezone.utc)  # Mendefinisikan Timestamp dengan waktu saat ini
            cursor.execute("UPDATE tbl_t_post SET delected_ttp = %s, delected_time_ttp = %s WHERE id_ttp = %s", (session['id_tmu'], Timestamp, id))
            db.commit()
            flash('Post deleted successfully!', 'success')
            return redirect(url_for('admin_posts'))
        return "Kesalahan koneksi database"
    return redirect(url_for('login'))

@app.route('/admin/labels', methods=['GET', 'POST'])
def admin_labels():
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                label_name = request.form['label_name']
                cursor.execute("INSERT INTO tbl_m_label (nama_tml, created_tml) VALUES (%s, %s)", (label_name, session['id_tmu']))
                db.commit()
                flash('Label added successfully!', 'success')
                return redirect(url_for('admin_labels'))
            
            cursor.execute("SELECT * FROM tbl_m_label WHERE delected_tml IS NULL")
            labels = cursor.fetchall()
            return render_template('admin/labels.html', labels=labels)
        return "Database connection error"
    return redirect(url_for('login'))

@app.route('/admin/edit_label/<int:id>', methods=['GET', 'POST'])
def edit_label(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                label_name = request.form['label_name']
                cursor.execute("UPDATE tbl_m_label SET nama_tml = %s WHERE id_tml = %s", (label_name, id))
                db.commit()
                flash('Label updated successfully!', 'success')
                return redirect(url_for('admin_labels'))
            
            cursor.execute("SELECT * FROM tbl_m_label WHERE id_tml = %s", (id,))
            label = cursor.fetchone()
            return render_template('admin/edit_label.html', label=label)
        return "Database connection error"
    return redirect(url_for('login'))

@app.route('/admin/delete_label/<int:id>')
def delete_label(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            Timestamp = datetime.now(timezone.utc)  # Mendefinisikan Timestamp dengan waktu saat ini
            cursor.execute("UPDATE `tbl_m_label` SET `delected_tml`= %s, `delected_time_tml`= %s WHERE `id_tml`= %s", (session['id_tmu'], Timestamp, id))
            db.commit()
            flash('Label berhasil dihapus!', 'success')
            return redirect(url_for('admin_labels'))
        return "Kesalahan koneksi database"
    return redirect(url_for('login'))

# Endpoint to handle image uploads
@app.route('/upload', methods=['POST'])
def upload():
    if 'upload' in request.files:
        file = request.files['upload']
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        url = url_for('uploaded_file', filename=filename)
        return f"""
        <script>
        window.parent.CKEDITOR.tools.callFunction({request.args.get('CKEditorFuncNum')}, '{url}');
        </script>
        """
    return 'Upload failed'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/data', methods=['GET', 'POST'])
def admin_data():
    if check_session_timeout() and 'loggedin' in session:
        if request.method == 'POST':
            file = request.files['file']
            keterangan = request.form['keterangan']
            judul = request.form['judul']
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Save file details to the database
            db = get_db_connection()
            if db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO tbl_m_data (nama_tmd, judul_tmd, keterangan_tmd, active_tmd, created_tmd) VALUES (%s, %s, %s, %s, %s)", 
                               (filename, judul, keterangan, '1', int(time.time())))
                db.commit()
                flash('File uploaded and saved successfully!', 'success')
                return redirect(url_for('admin_data'))
        
        # Fetch data to pass to the template
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tbl_m_data WHERE delected_tmd IS NULL")
            data = cursor.fetchall()
            return render_template('admin/data.html', data=data)
    return redirect(url_for('login'))

@app.route('/admin/update_active/<int:id>', methods=['POST'])
def update_active(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            active = request.form['active']
            cursor = db.cursor()
            cursor.execute("UPDATE tbl_m_data SET active_tmd = %s WHERE id_tmd = %s", (active, id))
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Kesalahan koneksi database"})
    return jsonify({"success": False, "error": "Tidak terautentikasi"})

@app.route('/admin/update_post_active/<int:id>', methods=['POST'])
def update_post_active(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            active = request.form['active']
            cursor = db.cursor()
            cursor.execute("UPDATE tbl_t_post SET active_ttp = %s WHERE id_ttp = %s", (active, id))
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Kesalahan koneksi database"})
    return jsonify({"success": False, "error": "Tidak terautentikasi"})

@app.route('/admin/edit_data/<int:id>', methods=['GET', 'POST'])
def edit_data(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                judul = request.form['judul']
                keterangan = request.form['keterangan']
                cursor.execute("UPDATE tbl_m_data SET judul_tmd = %s, keterangan_tmd = %s WHERE id_tmd = %s", (judul, keterangan, id))
                db.commit()
                flash('Data updated successfully!', 'success')
                return redirect(url_for('admin_data'))

            cursor.execute("SELECT * FROM tbl_m_data WHERE id_tmd = %s", (id,))
            data = cursor.fetchone()
            return render_template('admin/edit_data.html', data=data)
        return "Database connection error"
    return redirect(url_for('login'))

@app.route('/admin/delete_data/<int:id>', methods=['POST'])
def delete_data(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            Timestamp = datetime.now(timezone.utc)  # Mendefinisikan Timestamp dengan waktu saat ini
            cursor.execute("UPDATE tbl_m_data SET delected_tmd = %s, delected_time_tmd = %s WHERE id_tmd = %s", (session['id_tmu'], Timestamp, id))
            db.commit()
            flash('Data deleted successfully!', 'success')
            return redirect(url_for('admin_data'))
        return "Kesalahan koneksi database"
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
