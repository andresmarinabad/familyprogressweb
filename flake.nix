{
  description = "Entorno de desarrollo Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Selección de Python 3.13 (o 3.12 si prefieres)
        python3 = pkgs.python313;  # Cambiar a python3_12 si prefieres usar Python 3.12
        pythonPackages = python3.pkgs;  # Utiliza los paquetes de Python 3.13 o 3.12

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            # Infra 
            pkgs.opentofu

            # Intérprete de Python 3.13
            python3

            # Librerías solicitadas
            pythonPackages.jinja2
            pythonPackages.pytest
            pythonPackages.pytest-cov
            pythonPackages.time-machine
            pythonPackages.flask
            pythonPackages.resend

          ];

          # Comandos que se ejecutan al entrar al shell
          shellHook = ''
            export RESEND_KEY=
            export CRON_SECRET=
            echo "--- Entorno Python cargado ---"
          '';
        };
      });
}
