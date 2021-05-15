from cpt.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()
    if platform.system() == "Windows":
        builder.add(settings={"arch": "x86_64", "build_type": "Debug", "compiler": "Visual Studio", "compiler.version": 16, "compiler.runtime": "MDd"},
                    options={}, env_vars={}, build_requires={})
        builder.add(settings={"arch": "x86_64", "build_type": "Release", "compiler": "Visual Studio", "compiler.version": 16, "compiler.runtime": "MD"},
                    options={}, env_vars={}, build_requires={})
        builder.add(settings={"arch": "x86_64", "build_type": "RelWithDebInfo", "compiler": "Visual Studio", "compiler.version": 16, "compiler.runtime": "MD"},
                    options={}, env_vars={}, build_requires={})                    
    else:
        builder.add(settings={"arch": "x86_64", "build_type": "Debug"},
                    options={}, env_vars={}, build_requires={})
        builder.add(settings={"arch": "x86_64", "build_type": "Release"},
                    options={}, env_vars={}, build_requires={})
        builder.add(settings={"arch": "x86_64", "build_type": "RelWithDebInfo"},
                    options={}, env_vars={}, build_requires={})                    
    builder.run()
