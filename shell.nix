with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell {
  buildInputs = [
    python3
    pythonPackages.pip
    pythonPackages.praw
    pythonPackages.pandas
    pythonPackages.tqdm
    pythonPackages.pytest
  ];

}
