{
  description = "Entorno de desarrollo Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { 
          inherit system;
          # config.allowUnfree = true;
        };
        pythonPackages = pkgs.python3Packages;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            # Infra 
            pkgs.opentofu

            # Intérprete de Python
            pkgs.python3

            # Librerías solicitadas
            pythonPackages.jinja2
            pythonPackages.pytest
            pythonPackages.pytest-cov
            pythonPackages.time-machine
            pythonPackages.flask
          ];

          # Comandos que se ejecutan al entrar al shell
          shellHook = ''
            echo "--- Entorno Python cargado ---"
          '';
        };
      });
}
