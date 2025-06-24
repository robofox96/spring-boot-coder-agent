import os

PROJECT_PATH = "/Users/anuraggupta/IdeaProjects/TestProject"

def read_file(file: str) -> str:
    """ Read the content of a file and return it as a String.
    Args:
        file (str): The full path of the file to be read.
    Returns:
        str: The content of the file.
    Raises:
        Exception: If the file cannot be read, an exception is raised with the error message.
    """
    try:
        f = open(PROJECT_PATH + "/" + file, "r")
        return f.read()
    except Exception as e:
        raise Exception(f"Could Not Read File because of the following exception: {e}")

def create_or_update_file(file_name: str, file_contents: str) -> bool:
    """ Create or update a file with the given contents.
    Args:
        file_name (str): The full path of the file to be created or updated.
        file_contents (str): The contents to write into the file.
    Returns:
        bool: True if the file was created or updated successfully, False otherwise.
    Raises:
        Exception: If the file cannot be created or updated, an exception is raised with the error message.
    """
    try:
        if not file_name.startswith(PROJECT_PATH+ "/"):
            file_name = PROJECT_PATH + "/" + file_name
        directory = os.path.dirname(file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_name, "w") as f:
            f.write(file_contents)
        return True
    except:
        return False


def show_project_structure_util(path: str = PROJECT_PATH) -> list[str]:
    files: list[str] = []
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.isdir(path):
        print(f"Error {path} is not a directory")
        return []
    for file in os.listdir(path):
        # Skip hidden files and directories
        if file.startswith("."):
            continue
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            children: list[str] = show_project_structure_util(file_path)
            if len(children) > 0:
                for s in children:
                    files.append(s)
        else:
            files.append(file_path.replace(PROJECT_PATH + "/", ""))
    return files

def show_project_structure() -> list[str]:
    """ Show the project structure by listing all files in the given directory and its subdirectories.
    Returns:
        list[str]: A list of file paths in the directory and its subdirectories.
    """
    try:
        return show_project_structure_util(PROJECT_PATH)
    except Exception as e:
        raise Exception(f"Could not show project structure because of the following exception: {e}")

def build_project() -> str:
    """ Build the project using Maven.
    Returns:
        str: The output of the Maven build command.
    Raises:
        Exception: If the build fails, an exception is raised with the error message.
    """
    import subprocess
    result = subprocess.run(["mvn", "clean", "install"], cwd=PROJECT_PATH, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"{result.stdout}")
    return result.stdout