{ sources ? import ./nix/sources.nix
, system ? builtins.currentSystem
, pkgs ? import sources.nixpkgs { inherit system; }
, python ? "python310"
, ...
}:

let
  ## Our base Python:
  thisPython = pkgs.${python}.override {
    packageOverrides = pself: psuper: {
      flake8-pyproject = pself.buildPythonPackage rec {
        pname = "flake8_pyproject";
        version = "1.2.3";
        format = "wheel";
        src = pself.fetchPypi {
          inherit pname version format;
          python = "py3";
          sha256 = "sha256-Ykn+U1RSBa9edoN2RNyAtMEAN+c6Dl24f/Vi11+1vUo=";
        };
        propagatedBuildInputs = [
          pself.flake8
          pself.tomli
        ];
      };
    };
  };

  ## Our project definition:
  thisProject = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).project;

  ## Our package:
  thisPackage = thisPython.pkgs.buildPythonPackage {
    pname = thisProject.name;
    version = thisProject.version;
    format = "pyproject";

    src = ./.;

    propagatedBuildInputs = [
      thisPython.pkgs.python-dateutil
    ];
  };

  ## Our Python with production and development packages:
  thisPythonWithDeps = thisPython.withPackages (ps: with ps;
    thisPackage.propagatedBuildInputs ++ [
      ## Development tools:
      ps.black
      ps.build
      ps.flake8
      ps.flake8-pyproject
      ps.ipython
      ps.isort
      ps.mypy
      ps.pip
      ps.pylint
      ps.pytest
      ps.pytest-cov
      ps.sphinx
      ps.sphinx-rtd-theme
      ps.sphinxcontrib-apidoc
      ps.tox
      ps.twine
      ps.wheel

      ## Types:
      ps.types-python-dateutil
    ]
  );

  ## Our Nix shell:
  thisShell = pkgs.mkShell {
    packages = [
      ## Python dependency with packages for development purposes:
      thisPythonWithDeps
    ];

    shellHook = ''
      ## Make sure that we emulate Python development (or editable) mode:
      pip install -e . --prefix $TMPDIR/
    '';
  };
in
if pkgs.lib.inNixShell then thisShell else thisPackage
