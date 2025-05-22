import glob
import subprocess


with open('photo.zip', 'wb') as archive_file:
    archive = subprocess.check_output(
        ['zip', '-r', '-'] + glob.glob('photo/*')
    )
    archive_file.write(archive)
