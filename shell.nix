{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    pycrypto
    flask
    requests
    # other python packages
  ];
  my-python = pkgs.python39.withPackages my-python-packages;
in my-python.env