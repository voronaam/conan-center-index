from conans import ConanFile, tools
import os


class AmgClConan(ConanFile):
    name = "amgcl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ddemidov/amgcl"
    topics = ("mathematics", "opencl", "openmp", "cuda", "amg")
    license = "MIT"
    description = ("AMGCL is a header-only C++ library for solving large sparse linear systems"
                   " with algebraic multigrid (AMG) method.")
    settings = "compiler"
    no_copy_source = True
    options = {
        "with_eigen": [True, False],
        "with_blaze": [True, False],
    }
    default_options = {
        "with_eigen": False,
        "with_blaze": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.76.0")
        if self.options.with_eigen:
            self.requires("eigen/3.3.9")
        if self.options.with_blaze:
            self.requires("blaze/3.8")
        # TODO: Add when available: VexCL, ViennaCL, Scotch, Pastix, Metis

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder,
                  strip_root=True)

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        self.copy("*.hpp",
                  dst=os.path.join("include", "amgcl"),
                  src=os.path.join(self._source_subfolder, "amgcl"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.with_eigen:
            self.cpp_info.defines.append("AMGCL_HAVE_EIGEN")
