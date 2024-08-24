{ pkgs ? import <nixpkgs> {} }:
let

    webpackSrc = pkgs.fetchFromGitHub {
      owner = "webpack";
      repo = "webpack";
      rev = "v5.88.2"; # Tag or commit hash for v5.88.2
      sha256 = "sha256-WkimmZwtEdZKCsKhVstrFg/QMEj2JKWVAWNu6QdFyd8="; 
    };


    webpackCustom = pkgs.nodePackages.webpack.overrideAttrs (oldAttrs: rec {
      name = "webpack-5.88.2";
      src = pkgs.fetchFromGitHub {
        owner = "webpack";
        repo = "webpack";
        rev = "v5.88.2"; 
        sha256 = "sha256-WkimmZwtEdZKCsKhVstrFg/QMEj2JKWVAWNu6QdFyd8="; 
      };
      buildInputs = oldAttrs.buildInputs ++ [ pkgs.nodePackages.node-gyp-build ]; 
    });

in
pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.virtualenv
    pkgs.python3Packages.flask
    pkgs.python3Packages.requests
    pkgs.python3Packages.opencv4
    pkgs.opencv

    #(pkgs.python310Packages.preshed.overrideAttrs (oldAttrs: {
    #  src = pkgs.python310Packages.fetchPypi {
    #    pname = "preshed";
    #    version = "3.0.9";
    #    hash = "sha256-chhjxSRP/NJlGtCSiVGix8d7EC9OEaJRrYXTfudiFmA=";
    #  };

    #}))

    #pkgs.python310Packages.libtorrent-rasterbar
    #pkgs.python310Packages.tqdm
    #pkgs.python310Packages.pytesseract
    #pkgs.python310Packages.opencv4
    #pkgs.python310Packages.scikit-learn

    pkgs.python3Packages.openai
    pkgs.python3Packages.slack-sdk 
    pkgs.python3Packages.slack-bolt

  ];

  cmakeFlags = [
    "-DCMAKE_PREFIX_PATH=${pkgs.libtorrent-rasterbar}"
  ];
 
  shellHook = ''
    virtualenv venv
    source ./venv/bin/activate
  '';

    ##if [ ! -d "interrail" ]; then
    ##  git clone https://github.com/juliuste/interrail.git
    ##fi

    ##if [ -f "interrail/requirements.txt" ]; then
    ##  pip install -r interrail/requirements.txt
    ##fi
}
