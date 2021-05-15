from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
from shutil import which
import fnmatch


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    # from whichcraft import which
    return which(name) is not None


class OatppConan(ConanFile):
    name = "oatpp"
    description = "Modern Web Framework for C++"
    homepage = "https://github.com/oatpp/oatpp"
    license = "Apache-2.0"
    topics = ("conan", "oat++", "oatpp", "web-framework")
    url = "https://github.com/conan-io/conan-center-index"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "oatpp can not be built as shared library on Windows")
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("oatpp requires GCC >=5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("oatpp-{0}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        if is_tool('Ninja'):
            self._cmake = CMake(self, generator='Ninja')
        else:
            self._cmake = CMake(self)
        self._cmake.definitions["OATPP_BUILD_TESTS"] = False
        self._cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug" or self.settings.build_type == "RelWithDebInfo":
                self.output.info("Searching for pdbs")
                patterns = ['oatpp']
                for root, dirs, files in os.walk(self._build_subfolder):
                    for pattern in patterns:
                        for filename in fnmatch.filter(files, pattern+'*.pdb'):      
                            self.copy(pattern=filename, dst=os.path.join("lib","oatpp-{}".format(self.version)),
                                      src=root, keep_path=False)                                      
                            self.output.info("Copied pdb: %s" % filename)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        include_dir = os.path.join(
            "include", "oatpp-{}".format(self.version), "oatpp")
        lib_dir = os.path.join("lib", "oatpp-{}".format(self.version))
        # oatpp
        self.cpp_info.components["_oatpp"].names["cmake_find_package"] = "oatpp"
        self.cpp_info.components["_oatpp"].names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.components["_oatpp"].includedirs = [include_dir]
        self.cpp_info.components["_oatpp"].libdirs = [lib_dir]
        self.cpp_info.components["_oatpp"].libs = ["oatpp"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_oatpp"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["_oatpp"].system_libs = [
                "ws2_32", "wsock32"]
        # oatpp-test
        self.cpp_info.components["oatpp-test"].names["cmake_find_package"] = "oatpp-test"
        self.cpp_info.components["oatpp-test"].names["cmake_find_package_multi"] = "oatpp-test"
        self.cpp_info.components["oatpp-test"].includedirs = [include_dir]
        self.cpp_info.components["oatpp-test"].libdirs = [lib_dir]
        self.cpp_info.components["oatpp-test"].libs = ["oatpp-test"]
        self.cpp_info.components["oatpp-test"].requires = ["_oatpp"]
