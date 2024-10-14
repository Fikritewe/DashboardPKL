import json
from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3

# Inisialisasi aplikasi Flask
app = Flask(__name__)
# Atur kunci rahasia untuk Flask
app.secret_key = 'secretkey'

# Fungsi untuk koneksi ke database
def get_db_connection():
    conn = sqlite3.connect('user_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists untuk tabel students
def create_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS students 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    major TEXT NOT NULL,
                    class TEXT NOT NULL,
                    school TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def create_absensi_table():
    conn = sqlite3.connect('user_database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS absensi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    tanggal TEXT NOT NULL,
                    jam TEXT NOT NULL,
                    status TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Panggil fungsi ini di awal aplikasi
create_absensi_table()


# Initialize table
create_table()

@app.route('/')
def dashboard():
    # Koneksi ke database SQLite
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    
    # Query untuk mendapatkan jumlah data siswa, aktivitas, dan proyek
    cursor.execute('SELECT COUNT(*) FROM students')
    jumlah_siswa = cursor.fetchone()[0]

    conn.close()

    # Kirim data ke template
    return render_template('dashboard.html', jumlah_siswa=jumlah_siswa)


@app.route('/index')
def index():
    return redirect(url_for('dashboard'))

@app.route('/projek')
def projek():
    return render_template('projek.html')


# Route login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'email' not in request.form or 'password' not in request.form:
            flash("Email dan password harus diisi!", 'error')
            return redirect('/login')

        with get_db_connection() as connection:
            cursor = connection.cursor()
            email = request.form['email']
            password = request.form['password']
            query = "SELECT password FROM users WHERE email = ?"
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            if result and result[0] == password:
                return render_template("dashboard.html")
            else:
                flash("Pengguna tidak ditemukan atau password salah.", 'error')

        return redirect('/login')

    return render_template('login_page.html')

# CRUD ROUTES

# Route untuk menampilkan data siswa
@app.route('/data')
def data_siswa():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('data_siswa.html', students=students)

# Route untuk menambahkan data siswa
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        major = request.form['major']
        student_class = request.form['class']
        school = request.form['school']

        conn = get_db_connection()
        conn.execute('INSERT INTO students (name, major, class, school) VALUES (?, ?, ?, ?)',
                     (name, major, student_class, school))
        conn.commit()
        conn.close()
        return redirect(url_for('data_siswa'))

    return render_template('create.html')

# Route untuk update data siswa
@app.route('/update/<int:id>', methods=('GET', 'POST'))
def update(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        major = request.form['major']
        student_class = request.form['class']
        school = request.form['school']

        conn.execute('UPDATE students SET name = ?, major = ?, class = ?, school = ? WHERE id = ?',
                     (name, major, student_class, school, id))
        conn.commit()
        conn.close()
        return redirect(url_for('data_siswa'))
    
    return render_template('update.html', student=student)

# Route untuk delete data siswa
@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('data_siswa'))

# ABSENSI ROUTES

@app.route('/absensi', methods=['GET', 'POST'])
def absensi():
    if request.method == 'POST':
        nama = request.form.get('nama')
        tanggal = request.form.get('date')
        jam = request.form.get('time')
        status = request.form.get('status')

        if not nama or not tanggal or not jam or not status:
            flash('Semua kolom harus diisi!', 'error')
            return redirect('/absensi')

        # Load data absensi terbaru dari file JSON
        daftar_absensi = read_absensi_from_file()

        # Tambahkan data ke daftar absensi (JSON)
        daftar_absensi.append({
            'nama': nama,
            'tanggal': tanggal,
            'jam': jam,
            'status': status
        })

        # Simpan ke file JSON
        write_absensi_to_file(daftar_absensi)

        # Simpan ke database
        with sqlite3.connect('user_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO absensi (nama, tanggal, jam, status) VALUES (?, ?, ?, ?)',
                           (nama, tanggal, jam, status))
            conn.commit()

        flash('Absensi berhasil disimpan!', 'success')
        return redirect('/daftar_absen')

    return render_template('absensi.html')




@app.route('/daftar_absen')
def daftar_absen():
    # Ambil data absensi dari database
    with sqlite3.connect('user_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nama, tanggal, jam, status FROM absensi')
        daftar_absensi = cursor.fetchall()

    # Tampilkan daftar absensi yang telah diisi
    return render_template('daftar_absen.html', absensi=daftar_absensi)


@app.route('/reset_absensi', methods=['POST'])
def reset_absensi():
    # Hapus semua data dari tabel absensi di database
    with sqlite3.connect('user_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM absensi')
        conn.commit()

    # Kosongkan file JSON
    write_absensi_to_file([])  # Mengosongkan daftar absensi

    flash('Daftar absensi berhasil direset!', 'success')
    return redirect('/daftar_absen')


# Fungsi untuk membaca dan menulis file absensi
json_file = 'absensi.json'
def read_absensi_from_file():
    try:
        with open(json_file, 'r') as f:
            absensi = json.load(f)
            print("Data absensi berhasil dibaca.")  # Debugging: tambahkan output ini
            return absensi
    except FileNotFoundError:
        print("File absensi.json tidak ditemukan. Menginisialisasi data kosong.")  # Debugging: jika file tidak ditemukan
        return []
    except json.JSONDecodeError:
        print("Error saat decoding file absensi.json. Menginisialisasi data kosong.")  # Debugging: jika terjadi error JSON
        return []


# Fungsi untuk menyimpan daftar absensi ke file JSON
def write_absensi_to_file(absensi_data):
    try:
        with open(json_file, 'w') as f:
            json.dump(absensi_data, f)  # Menyimpan daftar absensi
    except IOError:
        flash("Gagal menyimpan absensi. Silakan coba lagi.", 'error')



if __name__ == '__main__':
    app.run(debug=True, host="192.168.59.238")