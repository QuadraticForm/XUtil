bl_info = {
    "name": "XUtil",
    "author": "xuxing",
    "version": (1,0,0),
    "blender": (3,20,2),
    "description": "",
    "category": "Object"}

import sys
import importlib

# 插件模组名（对应文件名）
modulesNames = ['XCurDist', 'XTransform', 'XCamera', 'XAnim', 'XProj', 'XShapeKey', 'XMisc', 'XImageUser', 'XUtilCommon']

# 注册模组，基本不用改
 
modulesFullNames = {}
for currentModuleName in modulesNames:
    if 'DEBUG_MODE' in sys.argv:
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
    else:
        modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'initialize'):
                sys.modules[currentModuleName].initialize()
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'uninitialize'):
                sys.modules[currentModuleName].uninitialize()
 
if __name__ == "__main__":
    register()