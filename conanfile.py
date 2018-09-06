from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
from conans.util import files
import os

class DbusConan(ConanFile):
    name = "dbus"
    version = "1.12.10"
    DBUS_FOLDER_NAME = "dbus-%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False" # UNDONE ignore options now
    description = "D-Bus is a simple system for interprocess communication and coordination."
    generators = "cmake_find_package"
    
    def build_requirements(self):
      self.build_requires("expat/2.2.6@common/stable")

    def source(self):
      d_name = "dbus-%s.tar.gz" % self.version
      tools.download("https://dbus.freedesktop.org/releases/dbus/dbus-%s.tar.gz" % self.version, d_name)
      tools.unzip(d_name)
      os.unlink(d_name)
      if not tools.os_info.is_windows:
        self.run("chmod +x ./%s/configure" % self.DBUS_FOLDER_NAME)
      
      os.rename(self.DBUS_FOLDER_NAME, 'src')

    def build(self):
      cmake = CMake(self, parallel=True)
      
      # HACK Dbus use different names than conan cmake_find_package-generator and also ignore EXPAT_DEFINITIONS
      tools.replace_in_file("Findexpat.cmake", "expat_", "EXPAT_")
      tools.replace_in_file("Findexpat.cmake", "EXPAT_INCLUDE_DIRS", "EXPAT_INCLUDE_DIR")
      tools.replace_in_file("src/cmake/CMakeLists.txt", "find_package(EXPAT)", "find_package(EXPAT)\nadd_definitions(${EXPAT_DEFINITIONS})")
      
      cmake.configure(source_folder="src/cmake")
      cmake.build()

    def package(self):
      # Libraries
      self.copy("*.dll", dst="bin", keep_path=False)
      self.copy("*.lib", dst="lib", keep_path=False)

    def package_info(self):
        libs = None
        if self.settings.os == "Windows":
            libs = ["dbus"]
            if self.options.shared:
                self.cpp_info.defines =  ["DBUS_DLL"]
            else:
                libs = [i + "static" for i in libs]
            if self.settings.build_type == "Debug":
                libs = [i + "d" for i in libs]
            libs = [i + ".lib" for i in libs]
        else:
            libs = ["dbus"]
        self.cpp_info.libs = libs
        self.cpp_info.includedirs = ['include', 'include/dbus']  # Ordered list of include paths
        self.cpp_info.libdirs = ['lib']  # Directories where libraries can be found

        
