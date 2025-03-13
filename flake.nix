{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };
  outputs = { self, nixpkgs, ... }@inputs: {
    packages.x86_64-linux = let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in rec {
      gabe-backgrounder = pkgs.writers.writePython3Bin "gabe-backgrounder" {
        libraries = with pkgs; [
          python312Packages.requests
        ];
        doCheck = false;
      } (builtins.readFile ./backgrounder.py);
      default = gabe-backgrounder;
    };
  };
}
