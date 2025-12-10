from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
import os
import json

# ========== App Config ==========
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'kunci_rahasia_rumahsakit_2024')

# Constants
BIAYA_PER_HARI = 500000
GAJI_POKOK_DOKTER = 15000000
BONUS_PER_PASIEN = 200000

# Database (configurable for persistence)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///rumahsakit.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========== Models ==========
class Ruangan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    terpakai = db.Column(db.Boolean, default=False)
    kategori_bpjs = db.Column(db.String(200))        # VVIP, VIP, BPJS Kelas 1, dsb
    kategori_perawatan = db.Column(db.String(50))   # rawat_inap, intensif, isolasi, dll


    # pasien_relasi otomatis via backref dari Pasien.ruangan


def seed_ruangan():
    
    if Ruangan.query.count() > 0:
        return  # sudah ada data, tidak ditambah lagi# sudah ada data, tidak ditambah lagi

    rooms = [

        # ======================
        # RAWAT INAP – VVIP
        # ======================
        {"nama": "Suite A01", "bpjs": "VVIP", "perawatan": "Rawat Inap"},
        {"nama": "Suite A02", "bpjs": "VVIP", "perawatan": "Rawat Inap"},
        {"nama": "Suite B01", "bpjs": "VVIP", "perawatan": "Rawat Inap"},
        {"nama": "Suite B02", "bpjs": "VVIP", "perawatan": "Rawat Inap"},
        # ======================
        # RAWAT INAP – VIP
        # ======================
        {"nama": "VIP A01", "bpjs": "VIP", "perawatan": "Rawat Inap"},
        {"nama": "VIP A02", "bpjs": "VIP", "perawatan": "Rawat Inap"},
        {"nama": "VIP B01", "bpjs": "VIP", "perawatan": "Rawat Inap"},
        {"nama": "VIP B02", "bpjs": "VIP", "perawatan": "Rawat Inap"},
        {"nama": "VIP C01", "bpjs": "VIP", "perawatan": "Rawat Inap"},
        {"nama": "VIP C02", "bpjs": "VIP", "perawatan": "Rawat Inap"},
        # ======================
        # RAWAT INAP – BPJS Kelas 1
        # ======================
        {"nama": "Anggrek 1A-01", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1A-02", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1A-03", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1B-01", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1B-02", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1B-03", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1C-01", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1C-02", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1C-03", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1D-01", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1D-02", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},
        {"nama": "Anggrek 1D-03", "bpjs": "BPJS Kelas 1", "perawatan": "Rawat Inap"},

        # ======================
        # RAWAT INAP – BPJS Kelas 2
        # ======================
        {"nama": "Mawar 2A-01", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2A-02", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2A-03", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2A-04", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2B-01", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2B-02", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2B-03", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2B-04", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2C-01", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2C-02", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2C-03", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},
        {"nama": "Mawar 2C-04", "bpjs": "BPJS Kelas 2", "perawatan": "Rawat Inap"},


        # ======================
        # RAWAT INAP – BPJS Kelas 3
        # ======================
        {"nama": "Melati 3A-01", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3A-02", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3A-03", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3A-04", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3A-05", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3B-01", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3B-02", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3B-03", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3B-04", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3B-05", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3C-01", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3C-02", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3C-03", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3C-04", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},
        {"nama": "Melati 3C-05", "bpjs": "BPJS Kelas 3", "perawatan": "Rawat Inap"},


        # ======================
        # RAWAT INAP – UMUM
        # ======================
        {"nama": "Lily 01", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Lily 02", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Lily 03", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Lily 04", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Lavender 01", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Lavender 02", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Lavender 03", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Lavender 04", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Peony 01", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Peony 02", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Peony 03", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Peony 04", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Dahlia 01", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Dahlia 02", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Dahlia 03", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        {"nama": "Dahlia 04", "bpjs": "Umum", "perawatan": "Rawat Inap"},
        # ======================
        # INTENSIF (ICU/NICU/PICU)
        # ======================
        {"nama": "ICU 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},
        {"nama": "ICU 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},
        {"nama": "ICU 03", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},
        {"nama": "ICU 04", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},
        
        {"nama": "PICU 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},
        {"nama": "PICU 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},
        
        {"nama": "NICU 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},
        {"nama": "NICU 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Intensif"},

        # ======================
        # ISOLASI
        # ======================
        {"nama": "Isolasi A", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Isolasi"},
        {"nama": "Isolasi B", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Isolasi"},
        {"nama": "Isolasi C", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Isolasi"},
        {"nama": "Isolasi D", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Isolasi"},
        # ======================
        # IBU & ANAK
        # ======================
        {"nama": "Ruang Bersalin 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Ibu & Anak"},
        {"nama": "Ruang Bersalin 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Ibu & Anak"},
        {"nama": "Ruang Nifas 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Ibu & Anak"},
        {"nama": "Ruang Nifas 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Ibu & Anak"},
        {"nama": "Perinatal 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Ibu & Anak"},
        {"nama": "Perinatal 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Ibu & Anak"},


        # ======================
        # ANAK
        # ======================
        {"nama": "Pediatric A01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Anak"},
        {"nama": "Pediatric A02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Anak"},

        # ======================
        # POST OPERASI
        # ======================
        {"nama": "Recovery Room 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Post Operasi"},
        {"nama": "Recovery Room 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Post Operasi"},
        {"nama": "Recovery Room 03", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Post Operasi"},
        {"nama": "Recovery Room 04", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Post Operasi"},
        {"nama": "Recovery Room 05", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Post Operasi"},
        {"nama": "Recovery Room 06", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Post Operasi"},
        # ======================
        # PSIKIATRI
        # ======================
        {"nama": "Psikiatri A01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Psikiatri"},
        {"nama": "Psikiatri A02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Psikiatri"},
        {"nama": "Psikiatri A03", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Psikiatri"},
        {"nama": "Psikiatri A04", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Psikiatri"},
        {"nama": "Psikiatri A05", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Psikiatri"},
        {"nama": "Psikiatri A06", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Psikiatri"},

        # ======================
        # GERIATRI (LANJUT USIA)
        # ======================
        {"nama": "Geriatri 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Geriatri"},
        {"nama": "Geriatri 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Geriatri"},
        {"nama": "Geriatri 03", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Geriatri"},
        {"nama": "Geriatri 04", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Geriatri"},

        # ======================
        # DARURAT (IGD)
        # ======================
        {"nama": "IGD Bed 01", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 02", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 03", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 04", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 05", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 06", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 07", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 08", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 09", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
        {"nama": "IGD Bed 10", "bpjs": ["Umum", "VIP", "VVIP", "BPJS Kelas 1", "BPJS Kelas 2", "BPJS Kelas 3"], "perawatan": "Darurat"},
    ]

    # Insert ke database
    for r in rooms:
        exists = Ruangan.query.filter_by(nama=r["nama"]).first()
        if not exists:
            db.session.add(Ruangan(
                nama=r["nama"],
                kategori_bpjs=json.dumps(r["bpjs"]),
                kategori_perawatan=r["perawatan"],
                terpakai=False
            ))

    db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pasien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    umur = db.Column(db.Integer, nullable=False)
    kategori_umur = db.Column(db.String(50))
    status_pasien = db.Column(db.String(50))  
    status_perawatan = db.Column(db.String(50))  
    diagnosa = db.Column(db.String(300), nullable=False)
    tanggal_masuk = db.Column(db.Date, nullable=False)
    tanggal_keluar = db.Column(db.Date, nullable=True)
    lama_rawat = db.Column(db.Integer, nullable=True)
    biaya_total = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=True)
    ruangan = db.Column(db.String(50))
    tgl_lahir = db.Column(db.Date, nullable=False)
    gol_darah = db.Column(db.String(5))
    jenis_kelamin = db.Column(db.String(20))
    alamat = db.Column(db.Text)
    no_telepon = db.Column(db.String(20))
    wali_pasien = db.Column(db.String(100))
    ruangan_id = db.Column(db.Integer, db.ForeignKey('ruangan.id'))
    ruangan = db.relationship("Ruangan", backref="pasien_relasi")
    
    def hitung_lama_rawat(self):
        if self.tanggal_keluar:
            return max(1, (self.tanggal_keluar - self.tanggal_masuk).days)
        return max(1, (date.today() - self.tanggal_masuk).days)

    def hitung_biaya(self):
        biaya_dasar = (self.lama_rawat or self.hitung_lama_rawat()) * BIAYA_PER_HARI
        biaya_tambahan = biaya_dasar * 0.2 if (self.umur or 0) >= 60 else 0
        return int(biaya_dasar + biaya_tambahan)

    def tentukan_status(self):
        kritis = [
            'jantung', 'stroke', 'kanker', 'tumor', 'koma', 'ginjal',
            'paru-paru', 'hiv', 'aids', 'ebola', 'leukemia', 'demam berdarah'
        ]
        diagnosa_lower = (self.diagnosa or "").lower()
        if any(p in diagnosa_lower for p in kritis):
            return 'Kritis'
        if (self.lama_rawat or 0) > 7:
            return 'Kritis'
        if self.status_perawatan and self.status_perawatan.lower() == 'intensif':
            return 'Kritis'
        return 'Kondisi Serius'
    
    def hitung_umur(self):
        """Menghitung umur pasien berdasarkan tgl_lahir"""
        if not self.tgl_lahir:
            return None
        today = date.today()
        umur = today.year - self.tgl_lahir.year - ((today.month, today.day) < (self.tgl_lahir.month, self.tgl_lahir.day))
        return umur

    def update_perhitungan(self):
        self.lama_rawat = self.hitung_lama_rawat()
        self.biaya_total = self.hitung_biaya()
        self.status = self.tentukan_status()
        self.umur = self.hitung_umur()

class Dokter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    spesialisasi = db.Column(db.String(200), nullable=False)
    jumlah_pasien = db.Column(db.Integer, nullable=False, default=0)
    gaji = db.Column(db.Integer, nullable=True)
    tanggal_bergabung = db.Column(db.Date, default=date.today)

    def hitung_gaji(self):
        return GAJI_POKOK_DOKTER + (self.jumlah_pasien * BONUS_PER_PASIEN)

    def update_gaji(self):
        self.gaji = self.hitung_gaji()

# ========== Helpers ==========
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Silakan login terlebih dahulu!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def seed_initial_data():
    """Seed default admin, sample pasien and dokter jika tabel kosong."""
    # Users
    if User.query.count() == 0:
        admin = User(username='admin')
        admin.set_password('admin123')
        admin.role = 'admin'
        db.session.add(admin)
        db.session.commit()

    # Pasien
    if Pasien.query.count() == 0:
        sample_pasien = [
            ('Budi Santoso', '1985-05-15', 'Demam Berdarah', '2024-12-01', '2024-12-06', 'Laki-laki', 'A', 'Jl. Keberkahan', '0800000000', 'Anto', None, None, 'Rawat Inap'),
            ('Siti Nurhaliza', '1992-08-11', 'Tifus', '2024-12-03', None, 'Perempuan', 'AB', 'Jl. Sunu', '0800000000', 'Tina', None, None, 'Rawat Inap'),
            ('Ahmad Yani', '1956-03-22', 'Jantung Koroner', '2024-11-26', None, 'Laki-laki', 'O', 'Jl. Malengkeri', '0800000000', 'Budi', None, None, 'Rawat Inap'),
            ('Dewi Lestari', '1999-01-30', 'Appendicitis', '2024-12-04', None, 'Perempuan', 'A', 'Jl. Cendrawasih', '0800000000', 'Lisa', None, None, 'Rawat Inap'),
        ]
        for nama, tgl_lahir_str, diagnosa, masuk, keluar, jenis_kelamin, gol_darah, alamat, no_telepon, wali_pasien, ruangan, status_pasien, status_perawatan in sample_pasien:
            tgl_lahir = datetime.strptime(tgl_lahir_str, '%Y-%m-%d').date()  
            t_masuk = datetime.strptime(masuk, '%Y-%m-%d').date()
            t_keluar = datetime.strptime(keluar, '%Y-%m-%d').date() if keluar else None
            p = Pasien(nama=nama, tgl_lahir=tgl_lahir, diagnosa=diagnosa, tanggal_masuk=t_masuk, tanggal_keluar=t_keluar, jenis_kelamin=jenis_kelamin, gol_darah=gol_darah, alamat=alamat, no_telepon=no_telepon, wali_pasien=wali_pasien, ruangan=ruangan, status_pasien=status_pasien, status_perawatan=status_perawatan)
            p.update_perhitungan()
            db.session.add(p)
        db.session.commit()

    # Dokter
    if Dokter.query.count() == 0:
        sample_dokter = [
            ('Dr. Agus Susanto, Sp.PD', 'Penyakit Dalam', 15),
            ('Dr. Rina Wijaya, Sp.A', 'Anak', 20),
            ('Dr. Hendra Gunawan, Sp.JP', 'Jantung', 12),
        ]
        for nama, spes, jumlah in sample_dokter:
            d = Dokter(nama=nama, spesialisasi=spes, jumlah_pasien=jumlah)
            d.update_gaji()
            db.session.add(d)
        db.session.commit()

# ========== Routes ==========

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ---- Auth ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Isi username dan password.', 'warning')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Selamat datang, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        if not username or not password:
            flash('Lengkapi username dan password.', 'warning')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Password tidak cocok.', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password minimal 6 karakter.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar.', 'danger')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# ---- Dashboard ----
@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_pasien': Pasien.query.count(),
        'total_dokter': Dokter.query.count(),
        'pasien_kritis': Pasien.query.filter_by(status='Kritis').count(),
        'pasien_stabil': Pasien.query.filter(Pasien.status != 'Kritis').count(),
        'pasien_masih_dirawat': Pasien.query.filter_by(tanggal_keluar=None).count(),
        'total_biaya': sum(p.biaya_total or 0 for p in Pasien.query.all()),
        'total_gaji': sum(d.gaji or 0 for d in Dokter.query.all())
    }
    return render_template('dashboard.html', stats=stats, username=session.get('username'))

# ---- Pasien ----

@app.route('/pasien')
@login_required
def pasien():
    search = request.args.get('search', '').strip()

    if search:
        q = f"%{search}%"
        pasien_list = Pasien.query.filter(
            (Pasien.nama.ilike(q)) | (Pasien.diagnosa.ilike(q))
        ).all()
    else:
        pasien_list = Pasien.query.order_by(Pasien.id.desc()).all()

    # Hitung umur untuk setiap pasien
    for p in pasien_list:
        if p.tgl_lahir:
            lahir = p.tgl_lahir
            today = date.today()
            umur = today.year - lahir.year - ((today.month, today.day) < (lahir.month, lahir.day))
            p.umur = umur  # tambahkan atribut sementara untuk template
        else:
            p.umur = None  # jika tanggal lahir tidak ada

    return render_template('pasien.html', pasien_list=pasien_list, search=search)


@app.route('/pasien/<int:pasien_id>')
@login_required
def detail_pasien(pasien_id):
    pasien = Pasien.query.get_or_404(pasien_id)
    # ensure perhitungan up-to-date
    pasien.update_perhitungan()
    db.session.commit()
    return render_template('pasien_detail.html', pasien=pasien)

@app.route('/pasien/tambah', methods=['GET', 'POST'])
@login_required
def tambah_pasien():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        diagnosa = request.form.get('diagnosa', '').strip()
        tanggal_masuk = request.form.get('tanggal_masuk', '').strip()
        tanggal_lahir = request.form.get('tgl_lahir', '').strip()
        golongan_darah = request.form.get('golongan_darah', '').strip()
        jenis_kelamin = request.form.get('jenis_kelamin', '').strip()
        alamat = request.form.get('alamat', '').strip()
        no_telepon = request.form.get('no_telepon', '').strip()
        wali_pasien = request.form.get('wali_pasien', '').strip()
        status_pasien = request.form.get('status_pasien', '').strip()
        status_perawatan = request.form.get('status_perawatan', '').strip()
        ruangan_id = request.form.get('ruangan')

        if not nama:
            flash('Nama pasien harus diisi.', 'warning')
            return redirect(url_for('tambah_pasien'))
        if not diagnosa:
            flash('Diagnosa harus diisi.', 'warning')
            return redirect(url_for('tambah_pasien'))
        if not tanggal_masuk:
            flash('Tanggal masuk harus diisi.', 'warning')
            return redirect(url_for('tambah_pasien'))
        if not tanggal_lahir:
            flash('Tanggal lahir harus diisi.', 'warning')
            return redirect(url_for('tambah_pasien'))
        if not jenis_kelamin:
            flash('Jenis kelamin harus dipilih.', 'warning')
            return redirect(url_for('tambah_pasien'))
        if not status_pasien:
            flash('Kelas (status pasien) harus dipilih.', 'warning')
            return redirect(url_for('tambah_pasien'))
        if not status_perawatan:
            flash('Status perawatan harus dipilih.', 'warning')
            return redirect(url_for('tambah_pasien'))
        if not ruangan_id:
            flash('Ruangan harus dipilih.', 'warning')
            return redirect(url_for('tambah_pasien'))

        try:
            t_masuk = datetime.strptime(tanggal_masuk, '%Y-%m-%d').date()
            tgl_lahir = datetime.strptime(tanggal_lahir, '%Y-%m-%d').date()
        except ValueError:
            flash('Format tanggal tidak valid!', 'danger')
            return redirect(url_for('tambah_pasien'))

        # Buat objek pasien (umur dihitung otomatis di update_perhitungan)
        p = Pasien(
            nama=nama,
            diagnosa=diagnosa,
            tanggal_masuk=t_masuk,
            tgl_lahir=tgl_lahir,
            gol_darah=golongan_darah,
            jenis_kelamin=jenis_kelamin,
            alamat=alamat,
            no_telepon=no_telepon,
            wali_pasien=wali_pasien,
            status_pasien=status_pasien,
            status_perawatan=status_perawatan,
            ruangan_id=ruangan_id
        )

        # Update semua perhitungan otomatis
        p.update_perhitungan()
        db.session.add(p)

        # Tandai ruangan sebagai terpakai
        if ruangan_id:
            room = Ruangan.query.get(int(ruangan_id))
            if room:
                room.terpakai = True

        db.session.commit()
        flash(f'Pasien {nama} berhasil ditambahkan!', 'success')
        return redirect(url_for('pasien'))

    today = date.today().strftime('%Y-%m-%d')
    return render_template('tambah_pasien.html', today=today)



@app.route('/pasien/edit/<int:pasien_id>', methods=['GET', 'POST'])
@login_required
def edit_pasien(pasien_id):
    pasien = Pasien.query.get_or_404(pasien_id)

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        diagnosa = request.form.get('diagnosa', '').strip()
        tanggal_masuk = request.form.get('tanggal_masuk', '').strip()
        tanggal_keluar = request.form.get('tanggal_keluar', '').strip()
        tgl_lahir = request.form.get('tgl_lahir', '').strip()
        jenis_kelamin = request.form.get('jenis_kelamin', '').strip()
        alamat = request.form.get('alamat', '').strip()
        gol_darah = request.form.get('gol_darah', '').strip()
        no_telepon = request.form.get('no_telepon', '').strip()
        wali_pasien = request.form.get('wali_pasien', '').strip()
        status_pasien = request.form.get('status_pasien', '').strip()
        status_perawatan = request.form.get('status_perawatan', '').strip()
        ruangan_id = request.form.get('ruangan')
        sudah_sembuh = request.form.get('sudah_sembuh')

        if not nama or not diagnosa or not tanggal_masuk or not tgl_lahir or not jenis_kelamin or not status_pasien or not status_perawatan:
            flash('Isi semua field yang wajib.', 'warning')
            return redirect(url_for('edit_pasien', pasien_id=pasien_id))

        try:
            pasien.nama = nama
            pasien.diagnosa = diagnosa
            pasien.tanggal_masuk = datetime.strptime(tanggal_masuk, '%Y-%m-%d').date()
            pasien.tanggal_keluar = datetime.strptime(tanggal_keluar, '%Y-%m-%d').date() if tanggal_keluar else None
            pasien.tgl_lahir = datetime.strptime(tgl_lahir, '%Y-%m-%d').date()
            pasien.jenis_kelamin = jenis_kelamin
            pasien.alamat = alamat
            pasien.gol_darah = gol_darah
            pasien.no_telepon = no_telepon
            pasien.wali_pasien = wali_pasien
            pasien.status_pasien = status_pasien
            pasien.status_perawatan = status_perawatan

            # Handle ruangan change
            if ruangan_id:
                old_ruangan = pasien.ruangan
                new_ruangan = Ruangan.query.get(int(ruangan_id))
                if new_ruangan and (not new_ruangan.terpakai or new_ruangan.id == (old_ruangan.id if old_ruangan else None)):
                    # Mark old room as available if it exists and different
                    if old_ruangan and old_ruangan.id != new_ruangan.id:
                        old_ruangan.terpakai = False
                    # Assign new room
                    pasien.ruangan_id = int(ruangan_id)
                    new_ruangan.terpakai = True
                else:
                    flash('Ruangan tidak tersedia atau sudah terpakai.', 'warning')
                    return redirect(url_for('edit_pasien', pasien_id=pasien_id))

            # Handle sudah sembuh checkbox
            if sudah_sembuh:
                pasien.tanggal_keluar = date.today()
                # Mark room as available
                if pasien.ruangan:
                    pasien.ruangan.terpakai = False

            # update otomatis umur, kategori umur, lama rawat, biaya, dan status
            pasien.update_perhitungan()
            db.session.commit()

            flash('Data pasien berhasil diupdate!', 'success')
            return redirect(url_for('detail_pasien', pasien_id=pasien_id))

        except ValueError:
            flash('Format tanggal tidak valid!', 'danger')
            return redirect(url_for('edit_pasien', pasien_id=pasien_id))

    return render_template('edit_pasien.html', pasien=pasien)

@app.route('/pasien/hapus/<int:pasien_id>')
@login_required
def hapus_pasien(pasien_id):
    pasien = Pasien.query.get_or_404(pasien_id)
    db.session.delete(pasien)
    db.session.commit()
    flash('Pasien berhasil dihapus!', 'success')
    return redirect(url_for('pasien'))

@app.route('/pasien/keluar/<int:id>')
def pasien_keluar(id):
    pasien = Pasien.query.get_or_404(id)

    if pasien.ruangan:        # akses via relasi
        pasien.ruangan.terpakai = False

    pasien.tanggal_keluar = date.today()

    db.session.commit()
    return redirect(url_for('pasien'))


# ---- Dokter ----
@app.route('/dokter')
@login_required
def dokter():
    search = request.args.get('search', '').strip()
    if search:
        q = f"%{search}%"
        dokter_list = Dokter.query.filter(
            (Dokter.nama.ilike(q)) | (Dokter.spesialisasi.ilike(q))
        ).all()
    else:
        dokter_list = Dokter.query.order_by(Dokter.id.desc()).all()
    return render_template('dokter.html', dokter_list=dokter_list, search=search)

@app.route('/dokter/tambah', methods=['GET', 'POST'])
@login_required
def tambah_dokter():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        spesialisasi = request.form.get('spesialisasi', '').strip()
        jumlah_pasien = request.form.get('jumlah_pasien', '0').strip()

        if not nama or not spesialisasi:
            flash('Isi semua field yang wajib.', 'warning')
            return redirect(url_for('tambah_dokter'))
        try:
            jumlah = int(jumlah_pasien)
            d = Dokter(nama=nama, spesialisasi=spesialisasi, jumlah_pasien=jumlah)
            d.update_gaji()
            db.session.add(d)
            db.session.commit()
            flash(f'Dokter {nama} berhasil ditambahkan!', 'success')
            return redirect(url_for('dokter'))
        except ValueError:
            flash('Jumlah pasien harus berupa angka.', 'danger')
            return redirect(url_for('tambah_dokter'))

    return render_template('tambah_dokter.html')

@app.route('/dokter/edit/<int:dokter_id>', methods=['GET', 'POST'])
@login_required
def edit_dokter(dokter_id):
    dokter = Dokter.query.get_or_404(dokter_id)
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        spesialisasi = request.form.get('spesialisasi', '').strip()
        jumlah_pasien = request.form.get('jumlah_pasien', '').strip()

        if not nama or not spesialisasi:
            flash('Isi semua field yang wajib.', 'warning')
            return redirect(url_for('edit_dokter', dokter_id=dokter_id))
        try:
            dokter.nama = nama
            dokter.spesialisasi = spesialisasi
            dokter.jumlah_pasien = int(jumlah_pasien)
            dokter.update_gaji()
            db.session.commit()
            flash('Data dokter berhasil diupdate!', 'success')
            return redirect(url_for('dokter'))
        except ValueError:
            flash('Jumlah pasien harus berupa angka.', 'danger')
            return redirect(url_for('edit_dokter', dokter_id=dokter_id))

    return render_template('edit_dokter.html', dokter=dokter)

@app.route('/dokter/hapus/<int:dokter_id>')
@login_required
def hapus_dokter(dokter_id):
    dokter = Dokter.query.get_or_404(dokter_id)
    db.session.delete(dokter)
    db.session.commit()
    flash('Dokter berhasil dihapus!', 'success')
    return redirect(url_for('dokter'))

@app.route('/get_ruangan/<bpjs>/<perawatan>')
def get_ruangan(bpjs, perawatan):
    patient_id = request.args.get('patient_id')
    semua = Ruangan.query.filter_by(
        kategori_perawatan=perawatan,
        terpakai=False
    ).all()

    # If editing, include the patient's current room even if occupied
    if patient_id:
        try:
            patient = Pasien.query.get(int(patient_id))
            if patient and patient.ruangan and patient.ruangan.kategori_perawatan == perawatan:
                # Check if current room matches BPJS
                try:
                    bpjs_list = json.loads(patient.ruangan.kategori_bpjs)
                except (TypeError, json.JSONDecodeError):
                    bpjs_list = [patient.ruangan.kategori_bpjs]
                if bpjs in bpjs_list:
                    semua.append(patient.ruangan)
        except ValueError:
            pass

    hasil = []
    for r in semua:
        try:
            bpjs_list = json.loads(r.kategori_bpjs)
        except (TypeError, json.JSONDecodeError):
            bpjs_list = [r.kategori_bpjs]  # fallback kalau bukan JSON

        # Periksa apakah BPJS pasien ada di daftar kategori ruangan
        if bpjs in bpjs_list:
            hasil.append({
                'id': r.id,
                'nama': r.nama,
                'perawatan': r.kategori_perawatan,
                'bpjs': bpjs_list
            })

    return jsonify(hasil)



    


# ========== Create DB & Seed ==========
with app.app_context():
    db.create_all()   # buat tabel jika belum ada
    seed_ruangan()    # isi ulang ruangan jika belum ada
    seed_initial_data()
  # isi admin/dokter/pasien jika kosong



# ========== Run ==========
if __name__ == '__main__':
    app.run(debug=True)
