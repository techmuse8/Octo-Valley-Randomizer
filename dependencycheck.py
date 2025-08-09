import importlib.util

dependencies = {
    "ruamel.yaml": "MIT",
    "PyQt5": "GPL v3",
    "lms": "MIT",
    "oead": "GPL v3",
    "requests": "Apache 2.0",
    "packaging": "Apache 2.0",
}
missingDependencies = []

def checkIsMissing(packageName, license):
    try:
        if importlib.util.find_spec(packageName) is None:
            missingDependencies.append(packageName + f' ({license})')
            return False
        else:
            return True
    except ModuleNotFoundError:
        missingDependencies.append(packageName)
        return True