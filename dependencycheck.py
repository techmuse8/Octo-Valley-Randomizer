import importlib.util

dependencies = ['ruamel.yaml', 'PyQt5', 'lms', 'oead', 
                'requests', 'packaging']
missingDependencies = []

def checkIsMissing(packageName):
    try:
        if importlib.util.find_spec(packageName) is None:
            missingDependencies.append(packageName)
            return False
        else:
            return True
    except ModuleNotFoundError:
        missingDependencies.append(packageName)
        return True