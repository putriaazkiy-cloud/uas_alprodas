from main import app, db, Pasien

with app.app_context():
    pasien_list = Pasien.query.all()
    for p in pasien_list:
        updated = False
        if p.jenis_kelamin and p.jenis_kelamin.startswith('#'):
            p.jenis_kelamin = p.jenis_kelamin[1:]
            updated = True
        if p.gol_darah and p.gol_darah.startswith('#'):
            p.gol_darah = p.gol_darah[1:]
            updated = True
        if p.alamat and p.alamat.startswith('#'):
            p.alamat = p.alamat[1:]
            updated = True
        if p.no_telepon and p.no_telepon.startswith('#'):
            p.no_telepon = p.no_telepon[1:]
            updated = True
        if p.wali_pasien and p.wali_pasien.startswith('#'):
            p.wali_pasien = p.wali_pasien[1:]
            updated = True
        if updated:
            print(f'Updated pasien {p.id}: {p.nama}')
    db.session.commit()
    print('Database cleanup completed.')
