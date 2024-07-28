from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import mysql.connector
import os
import time
import hashlib
from datetime import datetime, timedelta, timezone
import pandas as pd
import json
import fitz  # PyMuPDF
import io

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Configuration for file uploads
BASE_UPLOAD_FOLDER = 'uploads'
UPLOAD_FOLDER_TEMPLATES = os.path.join(BASE_UPLOAD_FOLDER, 'templates')
UPLOAD_FOLDER_HASIL = os.path.join(BASE_UPLOAD_FOLDER, 'hasil')
UPLOAD_FOLDER_DATA = os.path.join(BASE_UPLOAD_FOLDER, 'data')
UPLOAD_FOLDER_POST_THUMBNAILS = os.path.join(BASE_UPLOAD_FOLDER, 'post_thumbnails')
UPLOAD_FOLDER_PROFIL = os.path.join(BASE_UPLOAD_FOLDER, 'profil')

# Create directories if they do not exist
os.makedirs(UPLOAD_FOLDER_TEMPLATES, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_HASIL, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_DATA, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_POST_THUMBNAILS, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_PROFIL, exist_ok=True)

app.config['UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_TEMPLATES'] = UPLOAD_FOLDER_TEMPLATES
app.config['UPLOAD_FOLDER_HASIL'] = UPLOAD_FOLDER_HASIL
app.config['UPLOAD_FOLDER_DATA'] = UPLOAD_FOLDER_DATA
app.config['UPLOAD_FOLDER_POST_THUMBNAILS'] = UPLOAD_FOLDER_POST_THUMBNAILS
app.config['UPLOAD_FOLDER_PROFIL'] = UPLOAD_FOLDER_PROFIL

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
            if elapsed_time > timedelta(hours=1):
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
        cursor.execute("SELECT p.id_ttp, p.judul_ttp, p.gambar_ttp, l.nama_tml FROM tbl_t_post p JOIN tbl_m_label l ON p.id_tml = l.id_tml WHERE p.active_ttp = '1' AND p.delected_ttp IS NULL")
        posts = cursor.fetchall()
        cursor.execute("SELECT * FROM tbl_m_data WHERE active_tmd = '1' AND delected_tmd IS NULL")
        data = cursor.fetchall()
        cursor.execute("SELECT * FROM tbl_m_laporan WHERE active_tmla = '1' AND delected_tmla IS NULL")
        laporan = cursor.fetchall()
        cursor.execute("SELECT * FROM tbl_m_profil")
        profile = cursor.fetchone()

        if profile:
            profile['kepala_desa_tmpo'] = json.loads(profile['kepala_desa_tmpo'])
            profile['kantor_tmpo'] = json.loads(profile['kantor_tmpo'])

        print(profile)

        return render_template('index.html', posts=posts, data=data, laporan=laporan, profil=profile)
    return "Database connection error"


@app.route('/form_page/<int:id>', methods=['GET', 'POST'])
def form_page(id):
    if not check_session_timeout():
        return redirect(url_for('login'))

    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)

        # Ambil detail JSON dari tbl_m_struktur
        cursor.execute("SELECT detail_json_tms FROM tbl_m_struktur WHERE id_tmla = %s", (id,))
        result = cursor.fetchone()

        # Ambil nama surat dan file dari tbl_m_laporan
        cursor.execute("SELECT judul_tmla, file_tmla FROM tbl_m_laporan WHERE id_tmla = %s", (id,))
        surat = cursor.fetchone()

        if result:
            fields = json.loads(result['detail_json_tms'])
        else:
            fields = []

        nama_surat = surat['judul_tmla'] if surat else 'Surat'
        pdf_template_path = os.path.join(app.config['UPLOAD_FOLDER_TEMPLATES'], surat['file_tmla']) if surat else None

        if request.method == 'POST':
            # Process the form submission
            form_data = {field['name']: request.form.get(field['name']) for field in fields}
            form_data_json = json.dumps(form_data)
            
            # Save form_data to tbl_t_pdf
            cursor.execute("INSERT INTO tbl_t_pdf (file_ttp, id_tmla, json_ttp, created_time_ttp) VALUES (%s, %s, %s, current_timestamp())",
                           ('', id, form_data_json))
            db.commit()

            # Generate PDF
            pdf_id = cursor.lastrowid
            output_folder = app.config['UPLOAD_FOLDER_HASIL']
            new_filename = f"{nama_surat}_{pdf_id}.pdf"
            pdf_path = generate_pdf_from_data(pdf_id, pdf_template_path, output_folder, new_filename)

            # Update tbl_t_pdf with file path
            filename = os.path.basename(pdf_path)
            cursor.execute("UPDATE tbl_t_pdf SET file_ttp = %s WHERE id_ttp = %s", (filename, pdf_id))
            db.commit()

            return redirect(url_for('index'))

        return render_template('form_page.html', fields=fields, nama_surat=nama_surat)
    return "Database connection error"


@app.route('/blog/<int:id>')
def blog(id):
    if not check_session_timeout():
        return redirect(url_for('login'))
    
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
    if not check_session_timeout():
        return redirect(url_for('login'))
    
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_m_data WHERE id_tmd = %s", (id,))
        post = cursor.fetchone()

        if post:
            file = post['nama_tmd']
            file_path = os.path.join(app.config['UPLOAD_FOLDER_DATA'], file)

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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                if 'label_name' in request.form:
                    # Handle label submission
                    label_name = request.form['label_name']
                    cursor.execute("INSERT INTO tbl_m_label (nama_tml, created_tml) VALUES (%s, %s)", (label_name, session['id_tmu']))
                    db.commit()
                    return redirect(url_for('admin'))
                elif 'file' in request.files:
                    # Handle file upload
                    file = request.files['file']
                    keterangan = request.form['keterangan']
                    judul = request.form['judul']
                    filename = file.filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER_DATA'], filename)
                    file.save(filepath)
                    cursor.execute("INSERT INTO tbl_m_data (nama_tmd, judul_tmd, keterangan_tmd, active_tmd, created_tmd) VALUES (%s, %s, %s, %s, %s)",
                                   (filename, judul, keterangan, '1', int(time.time())))
                    db.commit()
                    return redirect(url_for('admin'))
                elif 'informasi_tmpo' in request.form:
                    # Handle profile update
                    informasi = request.form['informasi_tmpo']
                    facebook = request.form['facebook_tmpo']
                    instagram = request.form['instagram_tmpo']
                    visi = request.form['visi_tmpo']
                    misi = request.form['misi_tmpo']
                    
                    kepala_desa = {}
                    kepala_desa['nama'] = request.form['kepala_desa_nama']
                    kepala_desa['jabatan'] = request.form['kepala_desa_jabatan']
                    
                    if 'kepala_desa_foto' in request.files:
                        file = request.files['kepala_desa_foto']
                        if file and file.filename != '':
                            filename = file.filename
                            filepath = os.path.join(app.config['UPLOAD_FOLDER_PROFIL'], filename)
                            file.save(filepath)
                            kepala_desa['foto'] = filename
                        else:
                            cursor.execute("SELECT kepala_desa_tmpo FROM tbl_m_profil WHERE id_tmpo=1")
                            current_data = cursor.fetchone()
                            if current_data:
                                current_kepala_desa = json.loads(current_data['kepala_desa_tmpo'])
                                kepala_desa['foto'] = current_kepala_desa.get('foto', '')

                    kepala_desa_json = json.dumps(kepala_desa)
                    
                    kantor = json.dumps({
                        "kode_pos": request.form['kantor_kode_pos'],
                        "alamat": request.form['kantor_alamat'],
                        "notelepon": request.form['kantor_notelepon'],
                        "email": request.form['kantor_email']
                    })
                    
                    if 'struktur_tmpo' in request.files:
                        file = request.files['struktur_tmpo']
                        if file and file.filename != '':
                            struktur_filename = file.filename
                            struktur_filepath = os.path.join(app.config['UPLOAD_FOLDER_PROFIL'], struktur_filename)
                            file.save(struktur_filepath)
                            struktur = struktur_filename
                        else:
                            cursor.execute("SELECT struktur_tmpo FROM tbl_m_profil WHERE id_tmpo=1")
                            current_data = cursor.fetchone()
                            if current_data:
                                struktur = current_data.get('struktur_tmpo', '')

                    cursor.execute("""
                        UPDATE tbl_m_profil SET 
                            informasi_tmpo=%s, 
                            facebook_tmpo=%s, 
                            instagram_tmpo=%s, 
                            visi_tmpo=%s, 
                            misi_tmpo=%s, 
                            kepala_desa_tmpo=%s, 
                            struktur_tmpo=%s, 
                            kantor_tmpo=%s 
                        WHERE id_tmpo=1
                    """, (informasi, facebook, instagram, visi, misi, kepala_desa_json, struktur, kantor))
                    db.commit()
                    flash('Profil berhasil diperbarui!', 'success')
                    return redirect(url_for('admin'))
                else:
                    # Handle filtering for PDFs
                    query = """
                        SELECT pdf.id_ttp, pdf.file_ttp, laporan.judul_tmla, pdf.created_time_ttp
                        FROM tbl_t_pdf pdf 
                        JOIN tbl_m_laporan laporan ON pdf.id_tmla = laporan.id_tmla
                    """
                    filters = []
                    judul_laporan = request.form.get('judul_laporan')
                    start_date = request.form.get('start_date')
                    end_date = request.form.get('end_date')

                    if judul_laporan:
                        filters.append(f"pdf.id_tmla = {judul_laporan}")
                    if start_date and end_date:
                        filters.append(f"pdf.created_time_ttp BETWEEN '{start_date}' AND '{end_date}'")

                    if filters:
                        query += " WHERE " + " AND ".join(filters)

                    cursor.execute(query)
                    pdfs = cursor.fetchall()
            else:
                # Default query to fetch all data
                query = """
                    SELECT pdf.id_ttp, pdf.file_ttp, laporan.judul_tmla, pdf.created_time_ttp
                    FROM tbl_t_pdf pdf 
                    JOIN tbl_m_laporan laporan ON pdf.id_tmla = laporan.id_tmla
                """
                cursor.execute(query)
                pdfs = cursor.fetchall()

            # Fetch unique judul_laporan values for the filter dropdown
            cursor.execute("SELECT id_tmla, judul_tmla FROM tbl_m_laporan")
            judul_laporan_values = cursor.fetchall()

            # Fetch posts
            cursor.execute("SELECT * FROM tbl_t_post WHERE delected_ttp IS NULL")
            posts = cursor.fetchall()

            # Fetch labels
            cursor.execute("SELECT * FROM tbl_m_label WHERE delected_tml IS NULL")
            labels = cursor.fetchall()

            # Fetch data
            cursor.execute("SELECT * FROM tbl_m_data WHERE delected_tmd IS NULL")
            data = cursor.fetchall()

            # Fetch laporan
            cursor.execute("SELECT * FROM tbl_m_laporan WHERE delected_tmla IS NULL")
            laporan = cursor.fetchall()

            # Fetch profile
            cursor.execute("SELECT * FROM tbl_m_profil WHERE id_tmpo=1")
            profil = cursor.fetchall()  # Fetch as list of dictionaries
            if profil:
                profil[0]['kepala_desa_tmpo'] = json.loads(profil[0]['kepala_desa_tmpo'])
                profil[0]['kantor_tmpo'] = json.loads(profil[0]['kantor_tmpo'])

            return render_template('admin/index.html', posts=posts, labels=labels, data=data, laporan=laporan, pdfs=pdfs, judul_laporan_values=judul_laporan_values, profil=profil)
        return "Database connection error"
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
                filepath = os.path.join(app.config['UPLOAD_FOLDER_POST_THUMBNAILS'], filename)
                file.save(filepath)

            db = get_db_connection()
            if db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO tbl_t_post (judul_ttp, postingan_ttp, active_ttp, created_ttp, id_tml, gambar_ttp) VALUES (%s, %s, %s, %s, %s, %s)",
                            (judul_ttp, postingan_ttp, '1', int(time.time()), id_tml, filename))
                db.commit()
                return redirect(url_for('admin'))

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
                    filepath = os.path.join(app.config['UPLOAD_FOLDER_POST_THUMBNAILS'], filename)
                    file.save(filepath)
                    cursor.execute("UPDATE tbl_t_post SET gambar_ttp = %s WHERE id_ttp = %s", (filename, id))

                cursor.execute("UPDATE tbl_t_post SET judul_ttp = %s, postingan_ttp = %s, id_tml = %s WHERE id_ttp = %s", 
                               (judul_ttp, postingan_ttp, id_tml, id))
                db.commit()
                return redirect(url_for('admin'))
            
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
            return redirect(url_for('admin'))
        return "Kesalahan koneksi database"
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
                return redirect(url_for('admin'))
            
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
            return redirect(url_for('admin'))
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
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/uploads/post_thumbnails/<filename>')
def uploaded_post_thumbnail(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_POST_THUMBNAILS'], filename, as_attachment=True)

@app.route('/uploads/pdf/<filename>')
def uploaded_post_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_HASIL'], filename, as_attachment=True)

@app.route('/uploads/profil/<filename>')
def uploaded_profil(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_PROFIL'], filename, as_attachment=True)


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
                return redirect(url_for('admin'))

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
            return redirect(url_for('admin'))
        return "Kesalahan koneksi database"
    return redirect(url_for('login'))

@app.route('/admin/laporan/add', methods=['POST'])
def admin_laporan_add():
    if check_session_timeout() and 'loggedin' in session:
        judul_tmla = request.form['judul_tmla']
        file = request.files['file_tmla']

        if file:
            file_tmla = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER_TEMPLATES'], file_tmla))

        db = get_db_connection()
        if db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO tbl_m_laporan (judul_tmla, file_tmla, active_tmla, created_tmla) VALUES (%s, %s, 1, %s)",
                        (judul_tmla, file_tmla, int(time.time())))
            db.commit()
            flash('Data added successfully!')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/admin/laporan/edit/<int:id>', methods=['GET', 'POST'])
def admin_laporan_edit(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if request.method == 'POST':
            judul_tmla = request.form['judul_tmla']

            if db:
                cursor = db.cursor()
                cursor.execute("UPDATE tbl_m_laporan SET judul_tmla=%s WHERE id_tmla=%s",
                                (judul_tmla, id))
                db.commit()
                flash('Data updated successfully!')
            return redirect(url_for('admin'))
        else:
            if db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT * FROM tbl_m_laporan WHERE id_tmla=%s", (id,))
                laporan = cursor.fetchone()
                if laporan:
                    return render_template('admin/edit_laporan.html', laporan=laporan)
            return "Database connection error"
    return redirect(url_for('login'))

@app.route('/admin/laporan/delete/<int:id>', methods=['POST'])
def admin_laporan_delete(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)

            Timestamp = datetime.now(timezone.utc)  # Mendefinisikan Timestamp dengan waktu saat ini
            cursor.execute("UPDATE tbl_m_laporan SET delected_tmla = %s, delected_time_tmla = %s WHERE id_tmla = %s", (session['id_tmu'], Timestamp, id))
            db.commit()

            flash('Data deleted successfully!')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/admin/update_laporan_active/<int:id>', methods=['POST'])
def admin_update_laporan_active(id):
    if check_session_timeout() and 'loggedin' in session:
        active = request.form['active']
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            cursor.execute("UPDATE tbl_m_laporan SET active_tmla=%s WHERE id_tmla=%s", (active, id))
            db.commit()
            return jsonify(success=True)
        return jsonify(success=False, error="Database connection error")
    return jsonify(success=False, error="Tidak terautentikasi")

@app.route('/admin/laporan/detail/<int:id>', methods=['GET', 'POST'])
def admin_laporan_detail(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                detail_json = request.json
                detail_json_str = json.dumps(detail_json['fields'])
                id_tmla = detail_json['id_tmla']
                
                cursor.execute("SELECT COUNT(*) as count FROM tbl_m_struktur WHERE id_tmla = %s", (id_tmla,))
                result = cursor.fetchone()
                
                if result['count'] > 0:
                    cursor.execute("UPDATE tbl_m_struktur SET detail_json_tms = %s WHERE id_tmla = %s", (detail_json_str, id_tmla))
                else:
                    cursor.execute("INSERT INTO tbl_m_struktur (id_tmla, detail_json_tms) VALUES (%s, %s)", (id_tmla, detail_json_str))
                
                db.commit()
                return jsonify({'message': 'Detail laporan berhasil disimpan!'}), 200

            cursor.execute("SELECT * FROM tbl_m_struktur WHERE id_tmla = %s", (id,))
            struktur = cursor.fetchone()
            detail_json = struktur['detail_json_tms'] if struktur else '[]'
            is_update = bool(struktur)  # Menentukan apakah ini adalah update atau insert
            return render_template('admin/laporan_detail.html', id_tmla=id, detail_json=detail_json, is_update=is_update)
    return redirect(url_for('login'))

@app.route('/admin/save_detail_laporan', methods=['POST'])
def save_detail_laporan():
    if check_session_timeout() and 'loggedin' in session:
        detail_laporan = request.json
        id_tmla = detail_laporan['id_tmla']
        fields_json = json.dumps(detail_laporan['fields'])
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM tbl_m_struktur WHERE id_tmla = %s", (id_tmla,))
            result = cursor.fetchone()
            
            if result[0] > 0:  # Akses menggunakan indeks numerik
                cursor.execute("UPDATE tbl_m_struktur SET detail_json_tms = %s WHERE id_tmla = %s", (fields_json, id_tmla))
            else:
                cursor.execute("INSERT INTO tbl_m_struktur (id_tmla, detail_json_tms) VALUES (%s, %s)", (id_tmla, fields_json))
                
            db.commit()
            return jsonify(success=True)
        return jsonify(success=False, error="Database connection error")
    return jsonify(success=False, error="Tidak terautentikasi")

def generate_pdf_from_data(pdf_id, template_path, output_folder, new_filename):
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_t_pdf WHERE id_ttp = %s", (pdf_id,))
        pdf_data = cursor.fetchone()

        cursor.execute("SELECT detail_json_tms FROM tbl_m_struktur WHERE id_tmla = %s", (pdf_data['id_tmla'],))
        struktur_data = cursor.fetchone()

        if pdf_data and struktur_data:
            form_data = json.loads(pdf_data['json_ttp'])
            struktur = json.loads(struktur_data['detail_json_tms'])

            # Open the PDF template
            doc = fitz.open(template_path)
            page = doc[0]  # Use the first page of the template

            for field in struktur:
                x_points = field.get('position', {}).get('x', 0)
                y_points = field.get('position', {}).get('y', 0)
                text = form_data.get(field['name'], '')
                fontsize = field.get('font_size', 12)

                # Ensure numerical values are correctly typed
                try:
                    x_points = float(x_points)
                    y_points = float(y_points)
                    fontsize = float(fontsize)
                except ValueError as e:
                    print(f"ValueError: {e}")
                    continue

                if field['type'] == 'text':
                    page.insert_text((x_points, y_points), text, fontname='helv', fontsize=fontsize)
                elif field['type'] == 'select':
                    # Insert selected option's label text
                    for option in field['options']:
                        if option['value'] == text:
                            page.insert_text((x_points, y_points), option['label'], fontname='helv', fontsize=fontsize)
                            break

            # Save the filled PDF to a new file
            new_pdf_path = os.path.join(output_folder, new_filename)
            doc.save(new_pdf_path)

            return new_pdf_path

    return None


@app.route('/admin/tbl_t_pdf', methods=['GET', 'POST'])
def admin_tbl_t_pdf():
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            
            # Default query to fetch all data
            query = """
                SELECT pdf.id_ttp, pdf.file_ttp, laporan.judul_tmla, pdf.created_time_ttp 
                FROM tbl_t_pdf pdf 
                JOIN tbl_m_laporan laporan ON pdf.id_tmla = laporan.id_tmla
            """
            filters = []
            
            # Apply filters if POST request
            if request.method == 'POST':
                judul_laporan = request.form.get('judul_laporan')
                start_date = request.form.get('start_date')
                end_date = request.form.get('end_date')
                
                if judul_laporan:
                    filters.append(f"pdf.id_tmla = {judul_laporan}")
                if start_date and end_date:
                    filters.append(f"pdf.created_time_ttp BETWEEN '{start_date}' AND '{end_date}'")
                
                if filters:
                    query += " WHERE " + " AND ".join(filters)
            
            cursor.execute(query)
            pdfs = cursor.fetchall()
            
            # Fetch unique judul_laporan values for the filter dropdown
            cursor.execute("SELECT id_tmla, judul_tmla FROM tbl_m_laporan")
            judul_laporan_values = cursor.fetchall()
            
            return render_template('admin/laporan_masyarakat.html', pdfs=pdfs, judul_laporan_values=judul_laporan_values)
    return redirect(url_for('login'))

@app.route('/admin/edit_pdf/<int:id>', methods=['GET', 'POST'])
def edit_pdf(id):
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                json_data = json.loads(request.form['json_data'])

                # Update JSON data in the database
                cursor.execute("UPDATE tbl_t_pdf SET json_ttp = %s WHERE id_ttp = %s", (json.dumps(json_data), id))
                db.commit()

                # Fetch the existing PDF template information from tbl_t_pdf
                cursor.execute("SELECT id_tmla, file_ttp FROM tbl_t_pdf WHERE id_ttp = %s", (id,))
                pdf_record = cursor.fetchone()

                # Fetch the template file from tbl_m_laporan
                cursor.execute("SELECT file_tmla FROM tbl_m_laporan WHERE id_tmla = %s", (pdf_record['id_tmla'],))
                laporan_record = cursor.fetchone()
                template_path = os.path.join(app.config['UPLOAD_FOLDER_TEMPLATES'], laporan_record['file_tmla'])

                # Generate a new filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                base_filename, file_extension = os.path.splitext(pdf_record['file_ttp'])
                new_filename = f"{base_filename}-edit-{timestamp}{file_extension}"


                # Generate the updated PDF from the template and save it with the new filename
                new_pdf_path = generate_pdf_from_data(id, template_path, app.config['UPLOAD_FOLDER_HASIL'], new_filename)

                # Update the file name in the database if the PDF generation was successful
                if new_pdf_path:
                    cursor.execute("UPDATE tbl_t_pdf SET file_ttp = %s WHERE id_ttp = %s", (new_filename, id))
                    db.commit()

                return redirect(url_for('admin'))

            cursor.execute("""
                SELECT pdf.id_ttp, pdf.json_ttp, pdf.id_tmla
                FROM tbl_t_pdf pdf 
                JOIN tbl_m_laporan laporan ON pdf.id_tmla = laporan.id_tmla 
                WHERE pdf.id_ttp = %s
            """, (id,))
            pdf = cursor.fetchone()

            cursor.execute("SELECT detail_json_tms FROM tbl_m_struktur WHERE id_tmla = %s", (pdf['id_tmla'],))
            struktur = cursor.fetchone()
            detail_json = json.loads(struktur['detail_json_tms']) if struktur else []

            return render_template('admin/edit_pdf.html', pdf=pdf, detail_json=pdf['json_ttp'], structure=detail_json)
        return "Database connection error"
    return redirect(url_for('login'))


@app.route('/admin/change_password', methods=['GET', 'POST'])
def change_password():
    if check_session_timeout() and 'loggedin' in session:
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            if new_password != confirm_password:
                flash('New passwords do not match!', 'danger')
                return redirect(url_for('change_password'))
            
            db = get_db_connection()
            if db:
                cursor = db.cursor(dictionary=True)
                user_id = session['id_tmu']
                cursor.execute("SELECT password_tmu FROM tbl_m_users WHERE id_tmu = %s", (user_id,))
                user = cursor.fetchone()
                
                hashed_current_password = hashlib.md5(current_password.encode()).hexdigest()
                if user and user['password_tmu'] == hashed_current_password:
                    hashed_new_password = hashlib.md5(new_password.encode()).hexdigest()
                    cursor.execute("UPDATE tbl_m_users SET password_tmu = %s WHERE id_tmu = %s", (hashed_new_password, user_id))
                    db.commit()
                    flash('Password changed successfully!', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('Current password is incorrect!', 'danger')
        return render_template('admin/change_password.html')
    return redirect(url_for('login'))


# @app.route('/admin/profil', methods=['GET', 'POST'])
# def admin_profil():
    if check_session_timeout() and 'loggedin' in session:
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            if request.method == 'POST':
                informasi = request.form['informasi_tmpo']
                facebook = request.form['facebook_tmpo']
                instagram = request.form['instagram_tmpo']
                visi = request.form['visi_tmpo']
                misi = request.form['misi_tmpo']
                
                kepala_desa = {}
                kepala_desa['nama'] = request.form['kepala_desa_nama']
                kepala_desa['jabatan'] = request.form['kepala_desa_jabatan']
                
                if 'kepala_desa_foto' in request.files:
                    file = request.files['kepala_desa_foto']
                    if file and file.filename != '':
                        filename = file.filename
                        filepath = os.path.join(app.config['UPLOAD_FOLDER_PROFIL'], filename)
                        file.save(filepath)
                        kepala_desa['foto'] = filename
                    else:
                        cursor.execute("SELECT kepala_desa_tmpo FROM tbl_m_profil WHERE id_tmpo=1")
                        current_data = cursor.fetchone()
                        if current_data:
                            current_kepala_desa = json.loads(current_data['kepala_desa_tmpo'])
                            kepala_desa['foto'] = current_kepala_desa.get('foto', '')

                kepala_desa_json = json.dumps(kepala_desa)
                
                kantor = json.dumps({
                    "kode_pos": request.form['kantor_kode_pos'],
                    "alamat": request.form['kantor_alamat'],
                    "notelepon": request.form['kantor_notelepon'],
                    "email": request.form['kantor_email']
                })
                
                if 'struktur_tmpo' in request.files:
                    file = request.files['struktur_tmpo']
                    if file and file.filename != '':
                        struktur_filename = file.filename
                        struktur_filepath = os.path.join(app.config['UPLOAD_FOLDER_PROFIL'], struktur_filename)
                        file.save(struktur_filepath)
                        struktur = struktur_filename
                    else:
                        cursor.execute("SELECT struktur_tmpo FROM tbl_m_profil WHERE id_tmpo=1")
                        current_data = cursor.fetchone()
                        if current_data:
                            struktur = current_data.get('struktur_tmpo', '')

                cursor.execute("""
                    UPDATE tbl_m_profil SET 
                        informasi_tmpo=%s, 
                        facebook_tmpo=%s, 
                        instagram_tmpo=%s, 
                        visi_tmpo=%s, 
                        misi_tmpo=%s, 
                        kepala_desa_tmpo=%s, 
                        struktur_tmpo=%s, 
                        kantor_tmpo=%s 
                    WHERE id_tmpo=1
                """, (informasi, facebook, instagram, visi, misi, kepala_desa_json, struktur, kantor))
                db.commit()
                flash('Profil berhasil diperbarui!', 'success')
                return redirect(url_for('admin_profil'))

            cursor.execute("SELECT * FROM tbl_m_profil WHERE id_tmpo=1")
            profil = cursor.fetchall()  # Fetch as list of dictionaries
            if profil:
                profil[0]['kepala_desa_tmpo'] = json.loads(profil[0]['kepala_desa_tmpo'])
                profil[0]['kantor_tmpo'] = json.loads(profil[0]['kantor_tmpo'])

            return render_template('admin/profil.html', profil=profil)
    return redirect(url_for('login'))

@app.route('/profil_desa')
def profil_desa():
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_m_profil WHERE id_tmpo=1")
        profile = cursor.fetchone()

        if profile:
            profile['kepala_desa_tmpo'] = json.loads(profile['kepala_desa_tmpo'])
            profile['kantor_tmpo'] = json.loads(profile['kantor_tmpo'])

        return render_template('profil_desa.html', profil=profile)
    return "Database connection error"


if __name__ == '__main__':
    app.run(debug=True)
