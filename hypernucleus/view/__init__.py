from os.path import dirname, join, exists
def get_path(file_name):
    path_one = join("view", file_name)
    path_two = join(dirname(__file__), "main.ui")
    if exists(path_one):
        return path_one
    else:
        return path_two
main_path = get_path("main.ui")
settings_path = get_path("settings.ui")