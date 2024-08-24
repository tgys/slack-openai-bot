{ pkgs ? import <nixpkgs> {} }:
let
in
pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.virtualenv
    pkgs.python3Packages.flask
    pkgs.python3Packages.requests
    pkgs.python3Packages.opencv4
    pkgs.opencv

    pkgs.python3Packages.openai
    pkgs.python3Packages.slack-sdk 
    pkgs.python3Packages.slack-bolt

  ];

  shellHook = ''
    virtualenv venv
    source ./venv/bin/activate
  '';
}
