{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    sqlite3
    pycrypto
    # other python packages
  ];
  my-python = pkgs.python39.withPackages my-python-packages;
in my-python.env