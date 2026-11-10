"""Yalnız proje girdilerini ve son doğrulanmış sonuçları tek ZIP'e alır."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent


def main():
    identity = json.loads((ROOT / 'kimlik.json').read_text(encoding='utf-8'))
    validation = json.loads((ROOT / 'sonuclar/dogrulama.json').read_text(encoding='utf-8'))
    if validation['durum'] != 'BASARILI':
        raise ValueError('Doğrulanmamış sonuçlar paketlenemez')
    filenames = ['.gitattributes', '.gitignore', 'deney.py', 'rapor.py', 'notlar.py', 'dogrula.py', 'paketle.py', 'calistir.bat',
                 'requirements.txt', 'tahminler.json', 'kimlik.json', 'README.md',
                 'KAYNAK_VE_YZ_BEYANI.md', 'DENEY_NOTLARI.md']
    files = [ROOT / name for name in filenames]
    for folder in ['veri/orijinaller', 'veri/islenmis', 'sonuclar', 'output/pdf']:
        files.extend(sorted(path for path in (ROOT / folder).rglob('*') if path.is_file()))
    manifest = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    manifest_path = ROOT / 'DOSYA_KARMALARI.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    files.append(manifest_path)
    output = ROOT / 'teslim'
    output.mkdir(exist_ok=True)
    archive = output / f"YZM411_Odev1_{identity['ogrenci_no']}.zip"
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in files:
            z.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad is not None:
            raise ValueError(f'ZIP bütünlük hatası: {bad}')
        for filename, expected in manifest.items():
            if hashlib.sha256(z.read(filename)).hexdigest() != expected:
                raise ValueError(f'Paket dosyası karması yanlış: {filename}')
        if not any(name.endswith('_Rapor.pdf') for name in z.namelist()):
            raise ValueError('PDF paket içinde eksik')
    print(f'{archive.name}: {len(files)} dosya, {archive.stat().st_size / 1024**2:.2f} MiB; CRC ve SHA-256 kontrolleri başarılı.')


if __name__ == '__main__':
    main()
