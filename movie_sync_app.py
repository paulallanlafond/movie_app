import os

host_drive = r'C:\projects\movie_app\fake_files\drive_a'

destination_drive = r'C:\projects\movie_app\fake_files\drive_b'

# host_movies = movie for movie in glob.glob('{}'.format(host_drive))

host_movies = [
    os.path.join(root, name)
    for root, dirs, files in os.walk(host_drive)
    for name in files
    if name.endswith(('.txt'))
]

print host_movies
